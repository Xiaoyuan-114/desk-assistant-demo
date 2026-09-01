import { FormEvent, useEffect, useRef, useState } from 'react'
import AgentVisuals from './AgentVisuals'
import {
  cancelPreview,
  chatStream,
  confirmPreview,
  deleteThread,
  fetchLlm,
  fetchThread,
  fetchThreads,
  type AgentPending,
  type AgentVisual,
} from './api'

type Row = {
  id: string
  role: 'user' | 'assistant'
  text: string
  visuals?: AgentVisual[]
  pending?: AgentPending | null
  error?: boolean
}

const CHIPS = ['今天营业额是多少', '主要以什么方式支付', '开台时段主要是什么', '近7天趋势', '座位图']

export default function AgentPage() {
  const [threads, setThreads] = useState<{ id: number; title: string }[]>([])
  const [threadId, setThreadId] = useState<number | null>(null)
  const [rows, setRows] = useState<Row[]>([])
  const [draft, setDraft] = useState('')
  const [busy, setBusy] = useState(false)
  const [status, setStatus] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [needKey, setNeedKey] = useState(false)
  const scroller = useRef<HTMLDivElement>(null)

  async function refreshList() {
    setThreads(await fetchThreads())
  }

  useEffect(() => {
    void refreshList()
    void fetchLlm().then((s) => setNeedKey(!s.configured))
  }, [])

  useEffect(() => {
    scroller.current?.scrollTo({ top: scroller.current.scrollHeight })
  }, [rows, status])

  async function openThread(id: number) {
    const detail = await fetchThread(id)
    setThreadId(detail.id)
    setRows(
      detail.messages.map((m) => ({
        id: String(m.id),
        role: m.role === 'user' ? 'user' : 'assistant',
        text: m.text,
        visuals: m.pending?.visuals,
        pending: m.pending?.preview_id
          ? {
              preview_id: m.pending.preview_id,
              tool_name: m.pending.tool_name || '',
              title: m.pending.title || '',
              message: m.pending.message || '',
              compare_rows: m.pending.compare_rows || [],
            }
          : null,
        error: m.error,
      })),
    )
  }

  function startNew() {
    setThreadId(null)
    setRows([])
    setError(null)
  }

  async function send(text: string) {
    const content = text.trim()
    if (!content || busy) return
    setBusy(true)
    setError(null)
    setDraft('')
    setRows((cur) => [...cur, { id: `u-${Date.now()}`, role: 'user', text: content }])
    let reply = ''
    let visuals: AgentVisual[] = []
    let pending: AgentPending | null = null
    try {
      await chatStream(
        [...rows.filter((r) => r.role === 'user' || r.role === 'assistant').map((r) => ({
          role: r.role,
          content: r.text,
        })), { role: 'user', content }],
        threadId,
        (ev) => {
          if (ev.type === 'status') setStatus(ev.text)
          if (ev.type === 'delta') reply += ev.text
          if (ev.type === 'visuals') visuals = ev.visuals
          if (ev.type === 'pending') pending = ev.pending_confirmation
          if (ev.type === 'done') {
            setThreadId(ev.thread_id)
            reply = ev.reply
            visuals = ev.visuals || visuals
          }
        },
      )
      setRows((cur) => [
        ...cur,
        { id: `a-${Date.now()}`, role: 'assistant', text: reply, visuals, pending },
      ])
      await refreshList()
    } catch (err) {
      setError(err instanceof Error ? err.message : '助手暂时不可用')
    } finally {
      setBusy(false)
      setStatus('')
    }
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    await send(draft)
  }

  return (
    <main className="agent">
      <aside className="rail">
        <button type="button" className="ghost" onClick={startNew}>
          新对话
        </button>
        <ul>
          {threads.map((row) => (
            <li key={row.id}>
              <button type="button" className={row.id === threadId ? 'on' : ''} onClick={() => void openThread(row.id)}>
                {row.title}
              </button>
              <button
                type="button"
                className="tiny"
                onClick={() => void deleteThread(row.id).then(() => { if (threadId === row.id) startNew(); void refreshList() })}
              >
                删
              </button>
            </li>
          ))}
        </ul>
      </aside>
      <section className="desk">
        <header>
          <h1>柜台助手</h1>
          <p>演示数据可查营业与客流。座位与开台未接入真实柜台。</p>
          {needKey && <p className="error">还没有密钥：打开上方「设置」，粘贴 API Key 并测试保存后即可提问。不需要登录。</p>}
        </header>
        <div className="thread" ref={scroller}>
          {rows.length === 0 && !busy && (
            <div className="empty">
              <p>还没有对话。可以直接问，或点下面的推荐。</p>
              <div className="chips">
                {CHIPS.map((chip) => (
                  <button key={chip} type="button" disabled={busy} onClick={() => void send(chip)}>
                    {chip}
                  </button>
                ))}
              </div>
            </div>
          )}
          {rows.map((row) => (
            <article key={row.id} className={`bubble bubble-${row.role}`}>
              <p>{row.text}</p>
              {row.visuals && <AgentVisuals visuals={row.visuals} />}
              {row.pending && (
                <div className="pending">
                  <h2>{row.pending.title}</h2>
                  <p>{row.pending.message}</p>
                  <div className="pending-actions">
                    <button
                      type="button"
                      className="ghost"
                      onClick={() => void cancelPreview(row.pending!.preview_id)}
                    >
                      取消
                    </button>
                    <button
                      type="button"
                      className="primary"
                      onClick={() =>
                        void confirmPreview(row.pending!.preview_id).then((res) => {
                          setRows((cur) =>
                            cur.map((item) =>
                              item.id === row.id
                                ? { ...item, pending: null, text: `${item.text}\n${res.reply}` }
                                : item,
                            ),
                          )
                        })
                      }
                    >
                      确认（不会改账）
                    </button>
                  </div>
                </div>
              )}
            </article>
          ))}
          {busy && <p className="loading">{status || '正在处理…'}</p>}
        </div>
        {error && <p className="error">{error}</p>}
        <form className="composer" onSubmit={(e) => void onSubmit(e)}>
          <textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder="例如：今天营业额是多少"
            rows={2}
            disabled={busy}
          />
          <button type="submit" className="primary" disabled={busy || !draft.trim()}>
            发送
          </button>
        </form>
      </section>
    </main>
  )
}
