import { FormEvent, useEffect, useState } from 'react'
import { fetchLlm, saveLlm, testLlm, type LlmStatus } from './api'

export default function SettingsPage() {
  const [status, setStatus] = useState<LlmStatus | null>(null)
  const [url, setUrl] = useState('')
  const [model, setModel] = useState('deepseek-chat')
  const [key, setKey] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hint, setHint] = useState<string | null>(null)
  const [tested, setTested] = useState(false)

  useEffect(() => {
    void fetchLlm().then((data) => {
      setStatus(data)
      setUrl(data.base_url)
      setModel(data.model || 'deepseek-chat')
    })
  }, [])

  async function onTest() {
    setBusy(true)
    setError(null)
    try {
      await testLlm({ api_key: key || undefined, base_url: url, model })
      setTested(true)
      setHint('测试通过，可以保存。')
    } catch (err) {
      setTested(false)
      setError(err instanceof Error ? err.message : '测试失败')
    } finally {
      setBusy(false)
    }
  }

  async function onSave(e: FormEvent) {
    e.preventDefault()
    if (key && !tested) {
      setError('新密钥请先测试再保存')
      return
    }
    setBusy(true)
    setError(null)
    try {
      const data = await saveLlm({
        api_key: key || undefined,
        base_url: url,
        model,
      })
      setStatus(data)
      setKey('')
      setTested(false)
      setHint('已保存。可以到助手里提问。')
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存失败')
    } finally {
      setBusy(false)
    }
  }

  async function onClear() {
    setBusy(true)
    try {
      const data = await saveLlm({ clear: true })
      setStatus(data)
      setHint('已清除本机保存的密钥，将回退服务端 .env')
    } catch (err) {
      setError(err instanceof Error ? err.message : '清除失败')
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="settings">
      <h1>模型密钥</h1>
      <p className="hint">密钥只存在本机后端（SQLite 或 .env），不会出现在对话记录里。刷新后密码框为空。</p>
      <p className="status" role="status">
        {status == null
          ? '读取中…'
          : status.configured
            ? `已配置 · ${status.source === 'settings' ? '本机设置' : '服务端 .env'}${
                status.last4 ? ` · ****${status.last4}` : ''
              }`
            : '未配置'}
      </p>
      <form onSubmit={(e) => void onSave(e)}>
        <label>
          接口地址
          <input value={url} onChange={(e) => { setUrl(e.target.value); setTested(false) }} placeholder="https://api.deepseek.com" />
        </label>
        <label>
          模型名
          <input value={model} onChange={(e) => { setModel(e.target.value); setTested(false) }} />
        </label>
        <label>
          API Key
          <input
            type="password"
            value={key}
            onChange={(e) => { setKey(e.target.value); setTested(false) }}
            placeholder={status?.configured ? '已保存，留空则不改密钥' : '在此粘贴密钥'}
            autoComplete="new-password"
          />
        </label>
        <div className="actions">
          <button type="button" className="ghost" disabled={busy} onClick={() => void onTest()}>
            测试
          </button>
          <button type="submit" className="primary" disabled={busy}>
            保存
          </button>
          {status?.source === 'settings' && (
            <button type="button" className="ghost" disabled={busy} onClick={() => void onClear()}>
              清除本机密钥
            </button>
          )}
        </div>
      </form>
      {error && <p className="error">{error}</p>}
      {hint && <p className="ok">{hint}</p>}
    </main>
  )
}
