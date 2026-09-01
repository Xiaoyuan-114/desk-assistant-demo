export type PaymentMix = {
  cash: { amount: string; ratio: number }
  scan: { amount: string; ratio: number }
  card: { amount: string; ratio: number }
}

export type AgentVisual = {
  kind: 'trend' | 'traffic' | 'pay_mix' | 'seats_stub'
  title: string
  data: Record<string, unknown>
}

export type AgentPending = {
  preview_id: string
  tool_name: string
  title: string
  message: string
  compare_rows: { label: string; old: string; new: string }[]
  wired?: boolean
}

export type LlmStatus = {
  configured: boolean
  source: 'settings' | 'env' | 'none'
  last4: string | null
  base_url: string
  model: string
}

type ApiOk<T> = { ok: true; data: T }
type ApiErr = { ok: false; error: string }

async function parse<T>(res: Response): Promise<T> {
  const body = (await res.json()) as ApiOk<T> | ApiErr
  if (!res.ok || !('ok' in body) || body.ok === false) {
    throw new Error(('error' in body && body.error) || '请求失败')
  }
  return body.data
}

export function formatMoney(value: string | number): string {
  const n = Number(value)
  if (Number.isNaN(n)) return String(value)
  return n.toFixed(2)
}

export async function fetchLlm(): Promise<LlmStatus> {
  return parse(await fetch('/api/v1/settings/llm'))
}

export async function testLlm(payload: {
  api_key?: string
  base_url?: string
  model?: string
}): Promise<void> {
  await parse(await fetch('/api/v1/settings/llm/test', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }))
}

export async function saveLlm(payload: {
  api_key?: string
  base_url?: string
  model?: string
  clear?: boolean
}): Promise<LlmStatus> {
  return parse(await fetch('/api/v1/settings/llm', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }))
}

export async function fetchThreads() {
  return parse<{ id: number; title: string; updated_at: string }[]>(
    await fetch('/api/v1/agent/threads'),
  )
}

export async function fetchThread(id: number) {
  return parse<{
    id: number
    title: string
    messages: {
      id: number
      role: string
      text: string
      error: boolean
      pending?: { visuals?: AgentVisual[] } & Partial<AgentPending>
    }[]
  }>(await fetch(`/api/v1/agent/threads/${id}`))
}

export async function deleteThread(id: number) {
  await parse(await fetch(`/api/v1/agent/threads/${id}`, { method: 'DELETE' }))
}

export type StreamEvent =
  | { type: 'status'; text: string }
  | { type: 'delta'; text: string }
  | { type: 'pending'; pending_confirmation: AgentPending }
  | { type: 'visuals'; visuals: AgentVisual[] }
  | { type: 'done'; thread_id: number; reply: string; visuals?: AgentVisual[] }
  | { type: 'error'; message: string }

export async function chatStream(
  messages: { role: string; content: string }[],
  threadId: number | null,
  onEvent: (ev: StreamEvent) => void,
): Promise<void> {
  const res = await fetch('/api/v1/agent/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
    body: JSON.stringify({ messages, thread_id: threadId ?? undefined }),
  })
  if (!res.ok || !res.body) {
    await parse(res)
    throw new Error('助手流式接口不可用')
  }
  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buf = ''
  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buf += decoder.decode(value, { stream: true })
    const blocks = buf.split('\n\n')
    buf = blocks.pop() ?? ''
    for (const block of blocks) {
      for (const line of block.split('\n')) {
        if (!line.startsWith('data:')) continue
        const raw = line.slice(5).trim()
        if (!raw) continue
        const event = JSON.parse(raw) as StreamEvent
        onEvent(event)
        if (event.type === 'error') throw new Error(event.message)
      }
    }
  }
}

export async function confirmPreview(previewId: string) {
  return parse<{ reply: string }>(
    await fetch('/api/v1/agent/confirm', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ preview_id: previewId }),
    }),
  )
}

export async function cancelPreview(previewId: string) {
  await parse(
    await fetch('/api/v1/agent/cancel-preview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ preview_id: previewId }),
    }),
  )
}
