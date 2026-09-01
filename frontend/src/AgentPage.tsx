import { FormEvent, KeyboardEvent, useCallback, useEffect, useId, useRef, useState, type ReactNode } from 'react'
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

const CHIPS = ['今天营业额', '支付方式', '开台时段'] as const
const RAIL_KEY = 'demo.agentRail'
const PLACEHOLDERS = new Set(['确认', '好的', '确定', '是'])

function readRail(): boolean {
  try {
    return localStorage.getItem(RAIL_KEY) !== '0'
  } catch {
    return true
  }
}

function ChatBubbleIcon() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M6.2 6.2h11.6A1.8 1.8 0 0 1 19.6 8v7.2a1.8 1.8 0 0 1-1.8 1.8H10.2L6.4 19.8V17H6.2A1.8 1.8 0 0 1 4.4 15.2V8a1.8 1.8 0 0 1 1.8-1.8Z" />
    </svg>
  )
}

function RailGlyph({ collapsed }: { collapsed: boolean }) {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.8">
      <rect x="4.2" y="5" width="15.6" height="14" rx="2" />
      <path d="M9.4 5v14" />
      {collapsed ? <path d="M13.2 10.2 16 12l-2.8 1.8" /> : <path d="M16 10.2 13.2 12 16 13.8" />}
    </svg>
  )
}

function CopyGlyph() {
  return (
    <svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true" fill="none">
      <rect x="8.2" y="8.2" width="10.4" height="10.4" rx="2" stroke="currentColor" strokeWidth="1.7" />
      <path d="M15.6 8.2V6.8A1.6 1.6 0 0 0 14 5.2H6.8A1.6 1.6 0 0 0 5.2 6.8V14A1.6 1.6 0 0 0 6.8 15.6H8.2" stroke="currentColor" strokeWidth="1.7" />
    </svg>
  )
}

function ThreadMark({ id }: { id: number }) {
  return (
    <span className={`agent-thread-mark agent-thread-mark--${id % 4}`} aria-hidden="true">
      <svg viewBox="0 0 24 24" width="12" height="12">
        <path d="M6.4 7.1h11.2A1.4 1.4 0 0 1 19 8.5v6.2a1.4 1.4 0 0 1-1.4 1.4h-6.2L7.6 18.6V16H6.4A1.4 1.4 0 0 1 5 14.7V8.5a1.4 1.4 0 0 1 1.4-1.4Z" fill="currentColor" />
      </svg>
    </span>
  )
}

function formatThreadTime(iso?: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  return new Intl.DateTimeFormat('zh-CN', {
    timeZone: 'Asia/Shanghai',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(d)
}

function followUps(lastUser: string): string[] {
  if (lastUser.includes('营业')) return ['支付方式', '开台时段', '近7天趋势']
  if (lastUser.includes('支付')) return ['今天营业额', '近7天趋势']
  if (lastUser.includes('时段') || lastUser.includes('客流')) return ['今天营业额', '支付方式']
  if (lastUser.includes('趋势')) return ['今天营业额', '座位图']
  return ['今天营业额', '支付方式', '开台时段']
}

function SafeMarkdown({ text }: { text: string }) {
  const lines = text.replace(/\r\n/g, '\n').split('\n')
  const blocks: ReactNode[] = []
  lines.forEach((line, i) => {
    if (!line.trim()) return
    blocks.push(<p key={i}>{line}</p>)
  })
  return <div className="agent-md">{blocks}</div>
}

function fitTextarea(el: HTMLTextAreaElement | null) {
  if (!el) return
  el.style.height = '0px'
  const line = parseFloat(getComputedStyle(el).lineHeight) || 22
  const pad = parseFloat(getComputedStyle(el).paddingTop) + parseFloat(getComputedStyle(el).paddingBottom)
  el.style.height = `${Math.min(el.scrollHeight, line * 5 + pad)}px`
}

export default function AgentPage() {
  const [threads, setThreads] = useState<{ id: number; title: string; updated_at: string }[]>([])
  const [threadId, setThreadId] = useState<number | null>(null)
  const [rows, setRows] = useState<Row[]>([])
  const [draft, setDraft] = useState('')
  const [busy, setBusy] = useState(false)
  const [status, setStatus] = useState('')
  const [needKey, setNeedKey] = useState(false)
  const [railOpen, setRailOpen] = useState(readRail)
  const [historyOpen, setHistoryOpen] = useState(false)
  const [pendingDeleteId, setPendingDeleteId] = useState<number | null>(null)
  const [toast, setToast] = useState('')
  const scroller = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const composerRef = useRef<HTMLFormElement>(null)
  const titleId = useId()
  const hasThread = rows.length > 0 || busy
  const listed = threads.filter((row) => row.title.trim() && !PLACEHOLDERS.has(row.title.trim()))

  const refreshList = useCallback(async () => {
    setThreads(await fetchThreads())
  }, [])

  useEffect(() => {
    void refreshList()
    void fetchLlm().then((s) => setNeedKey(!s.configured))
  }, [refreshList])

  useEffect(() => {
    const el = scroller.current
    if (el) el.scrollTop = el.scrollHeight
  }, [rows, status])

  useEffect(() => {
    fitTextarea(inputRef.current)
  }, [draft])

  useEffect(() => {
    const composer = composerRef.current
    const thread = scroller.current
    if (!composer || !thread) return
    const sync = () => thread.style.setProperty('--agent-composer-space', `${composer.offsetHeight}px`)
    sync()
    const ro = new ResizeObserver(sync)
    ro.observe(composer)
    return () => ro.disconnect()
  }, [hasThread, draft])

  function showToast(text: string) {
    setToast(text)
    window.setTimeout(() => setToast(''), 1600)
  }

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
    setHistoryOpen(false)
  }

  function startNew() {
    setThreadId(null)
    setRows([])
    setHistoryOpen(false)
    inputRef.current?.focus()
  }

  async function send(text: string) {
    const content = text.trim()
    if (!content || busy) return
    const prior = rows.filter((r) => !r.error).map((r) => ({ role: r.role, content: r.text }))
    const userId = `u-${Date.now()}`
    const assistantId = `a-${Date.now()}`
    setDraft('')
    setBusy(true)
    setRows((cur) => [...cur, { id: userId, role: 'user', text: content }, { id: assistantId, role: 'assistant', text: '' }])
    let reply = ''
    let visuals: AgentVisual[] = []
    let pending: AgentPending | null = null
    try {
      await chatStream([...prior, { role: 'user', content }], threadId, (ev) => {
        if (ev.type === 'status') setStatus(ev.text)
        if (ev.type === 'delta') {
          reply += ev.text
          setStatus('')
          setRows((cur) => cur.map((row) => (row.id === assistantId ? { ...row, text: reply, visuals, pending } : row)))
        }
        if (ev.type === 'visuals') {
          visuals = ev.visuals
          setRows((cur) => cur.map((row) => (row.id === assistantId ? { ...row, visuals } : row)))
        }
        if (ev.type === 'pending') {
          pending = ev.pending_confirmation
          setRows((cur) => cur.map((row) => (row.id === assistantId ? { ...row, pending, text: reply } : row)))
        }
        if (ev.type === 'done') {
          setThreadId(ev.thread_id)
          reply = ev.reply
          visuals = ev.visuals || visuals
          setRows((cur) => cur.map((row) => (row.id === assistantId ? { ...row, text: reply, visuals, pending } : row)))
        }
      })
      await refreshList()
    } catch (err) {
      const message = err instanceof Error ? err.message : '助手暂时不可用'
      setRows((cur) => cur.map((row) => (row.id === assistantId ? { ...row, text: message, error: true } : row)))
    } finally {
      setBusy(false)
      setStatus('')
      inputRef.current?.focus()
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault()
    void send(draft)
  }

  function onKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.nativeEvent.isComposing) return
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      void send(draft)
    }
  }

  function setRail(open: boolean) {
    setRailOpen(open)
    try {
      localStorage.setItem(RAIL_KEY, open ? '1' : '0')
    } catch {
      /* ignore */
    }
  }

  function askDelete(id: number) {
    if (pendingDeleteId === id) {
      setPendingDeleteId(null)
      void deleteThread(id).then(() => {
        if (threadId === id) startNew()
        void refreshList()
        showToast('已删除这条对话')
      })
      return
    }
    setPendingDeleteId(id)
    window.setTimeout(() => setPendingDeleteId((cur) => (cur === id ? null : cur)), 2400)
  }

  const lastUser = [...rows].reverse().find((row) => row.role === 'user')?.text ?? ''
  const lastAssistant = [...rows].reverse().find((row) => row.role === 'assistant')
  const showFollowUps = hasThread && !busy && lastAssistant && !lastAssistant.error && !lastAssistant.pending

  function historyChrome(kind: 'desk' | 'drawer') {
    return (
      <>
        <div className="agent-history-toolbar">
          <button type="button" className="agent-new-row" onClick={startNew}>
            <ChatBubbleIcon />
            新对话
          </button>
          {kind === 'desk' && (
            <button type="button" className="agent-rail-btn" aria-label="收起侧栏" onClick={() => setRail(false)}>
              <RailGlyph collapsed={false} />
            </button>
          )}
        </div>
        <p className="agent-history-label">最近</p>
        <div className="agent-history-body">
          {listed.length === 0 ? (
            <p className="agent-history-empty">还没有记录，问一句就会出现在这里</p>
          ) : (
            <ul className="agent-history-list">
              {listed.map((row) => (
                <li key={row.id}>
                  <button
                    type="button"
                    className={`agent-history-item${threadId === row.id ? ' is-current' : ''}`}
                    onClick={() => void openThread(row.id)}
                  >
                    <ThreadMark id={row.id} />
                    <span className="agent-history-copy">
                      <span className="agent-history-title">{row.title}</span>
                      <span className="agent-history-meta">
                        <span className="agent-history-time">{formatThreadTime(row.updated_at)}</span>
                      </span>
                    </span>
                  </button>
                  <button
                    type="button"
                    className={`agent-history-del${pendingDeleteId === row.id ? ' is-confirm' : ''}`}
                    aria-label="删除会话"
                    title={pendingDeleteId === row.id ? '再点一次删除' : '删除会话'}
                    onClick={(e) => {
                      e.stopPropagation()
                      askDelete(row.id)
                    }}
                  >
                    ×
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </>
    )
  }

  return (
    <main className="agent-page">
      <div className={`agent-desk${railOpen ? '' : ' agent-desk--rail-off'}`}>
        <aside className="agent-history" aria-label="最近对话">
          {historyChrome('desk')}
        </aside>
        <div className="agent-rail">
          <button type="button" className="agent-rail-btn" aria-label="展开侧栏" onClick={() => setRail(true)}>
            <RailGlyph collapsed />
          </button>
        </div>
        {historyOpen && (
          <div className="agent-history-drawer">
            <button type="button" className="agent-history-scrim" aria-label="关闭历史" onClick={() => setHistoryOpen(false)} />
            <aside className="agent-history agent-history--drawer" aria-label="最近对话">
              {historyChrome('drawer')}
            </aside>
          </div>
        )}
        <div className="agent-shell">
          <div className="agent-column">
            <div className="agent-head">
              <div className="agent-head-main">
                <h1 id={titleId}>柜台助手</h1>
                <p className="agent-lead">
                  一句话查营业、支付、客流。座位与开台未接入。
                  {needKey ? ' 还没有密钥：打开上方「设置」粘贴 API Key。' : ''}
                </p>
              </div>
              <div className="agent-head-actions">
                <button type="button" className="ghost-btn compact agent-history-toggle" onClick={() => setHistoryOpen(true)}>
                  历史
                </button>
              </div>
            </div>
            <div className="agent-thread" ref={scroller} aria-live="polite" aria-labelledby={titleId}>
              {!hasThread && (
                <div className="agent-empty">
                  <p>还没有对话。点下面的按钮，或者直接向我提问</p>
                </div>
              )}
              {rows.map((row) => (
                <div key={row.id} className={`agent-row agent-row--${row.role}`}>
                  {row.role === 'assistant' ? <div className="agent-avatar">助</div> : null}
                  <div className={`agent-turn${row.pending ? ' agent-turn--card' : ''}`}>
                    <article className={`agent-msg agent-msg--${row.role}${row.error ? ' agent-msg--error' : ''}${row.pending ? ' agent-msg--card' : ''}`}>
                      {row.role === 'assistant' ? (
                        row.text ? <SafeMarkdown text={row.text} /> : <p className="hint">{status || '正在处理…'}</p>
                      ) : (
                        <p>{row.text}</p>
                      )}
                      {row.visuals && row.visuals.length > 0 && <AgentVisuals visuals={row.visuals} />}
                      {row.pending && (
                        <div className="agent-confirm-card panel">
                          <h2>{row.pending.title}</h2>
                          <p className="hint">{row.pending.message}</p>
                          {row.pending.compare_rows.length > 0 && (
                            <dl className="agent-compare">
                              {row.pending.compare_rows.map((line) => (
                                <div key={`${line.label}-${line.old}-${line.new}`} className="agent-compare-row">
                                  <dt>{line.label}</dt>
                                  <dd>
                                    <span>{line.old}</span>
                                    <span className="agent-compare-arrow">→</span>
                                    <strong>{line.new}</strong>
                                  </dd>
                                </div>
                              ))}
                            </dl>
                          )}
                          <div className="agent-confirm-actions">
                            <button type="button" className="ghost-btn" onClick={() => void cancelPreview(row.pending!.preview_id)}>
                              取消
                            </button>
                            <button
                              type="button"
                              className="primary-btn"
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
                    {row.text && (
                      <div className="agent-msg-tools">
                        <button
                          type="button"
                          className="agent-msg-tool"
                          aria-label="复制"
                          title="复制"
                          onClick={() => void navigator.clipboard.writeText(row.text).then(() => showToast('已复制'))}
                        >
                          <CopyGlyph />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
            <form className="agent-composer" ref={composerRef} onSubmit={onSubmit}>
              {!hasThread && (
                <div className="agent-suggest">
                  <p className="agent-suggest-label">为你推荐</p>
                  <div className="agent-chips agent-chips--stack" aria-label="为你推荐">
                    {CHIPS.map((chip) => (
                      <button key={chip} type="button" className="agent-suggest-btn" disabled={busy} onClick={() => void send(chip)}>
                        {chip}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              {showFollowUps && (
                <div className="agent-suggest">
                  <p className="agent-suggest-label">可以接着问</p>
                  <div className="agent-chips agent-chips--stack" aria-label="可以接着问">
                    {followUps(lastUser).slice(0, 3).map((chip) => (
                      <button key={chip} type="button" className="agent-suggest-btn" disabled={busy} onClick={() => void send(chip)}>
                        {chip}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              <div className="agent-composer-card">
                <label className="agent-composer-field">
                  <span className="sr-only">对助手说</span>
                  <textarea
                    ref={inputRef}
                    rows={1}
                    value={draft}
                    onChange={(e) => setDraft(e.target.value)}
                    onKeyDown={onKeyDown}
                    placeholder="例如：今天营业额多少"
                    autoComplete="off"
                    enterKeyHint="send"
                    disabled={busy}
                  />
                </label>
                <button type="submit" className="primary-btn agent-send" disabled={busy || !draft.trim()}>
                  {busy ? '…' : '发送'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
      {toast && <p className="agent-toast" role="status">{toast}</p>}
    </main>
  )
}
