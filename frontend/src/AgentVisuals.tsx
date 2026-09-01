import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { formatMoney, type AgentVisual, type PaymentMix } from './api'

const MIX_COLORS = { cash: '#d62828', scan: '#2563eb', card: '#0f766e' }
const MIX_LABELS = { cash: '现金', scan: '扫码', card: '刷卡' } as const

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? (value as Record<string, unknown>) : {}
}

function VisualChart({ visual }: { visual: AgentVisual }) {
  const data = asRecord(visual.data)
  if (visual.kind === 'trend') {
    const points = (Array.isArray(data.points) ? data.points : []).map((row) => {
      const item = asRecord(row)
      return { date: String(item.date || '').slice(5), revenue: Number(item.total_revenue || 0) }
    })
    return (
      <div className="dash-chart-panel agent-visual-panel">
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={points}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e8e4dc" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip formatter={(v: number | string) => `¥${formatMoney(String(v))}`} />
            <Line type="monotone" dataKey="revenue" name="营收" stroke="#d62828" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    )
  }
  if (visual.kind === 'traffic') {
    const hours = (Array.isArray(data.hours) ? data.hours : []).map((row) => {
      const item = asRecord(row)
      return { hour: `${item.hour}:00`, count: Number(item.open_count || 0) }
    })
    return (
      <div className="dash-chart-panel agent-visual-panel">
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={hours}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e8e4dc" />
            <XAxis dataKey="hour" tick={{ fontSize: 11 }} interval={1} />
            <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
            <Tooltip />
            <Bar dataKey="count" name="开台数" fill="#d62828" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    )
  }
  if (visual.kind === 'pay_mix') {
    const mix = asRecord(data.payment_mix) as unknown as PaymentMix
    const mixData = (['cash', 'scan', 'card'] as const)
      .map((key) => ({
        key,
        name: MIX_LABELS[key],
        value: Number(mix?.[key]?.amount || 0),
        ratio: mix?.[key]?.ratio || 0,
      }))
      .filter((d) => d.value > 0)
    return (
      <div className="dash-chart-panel agent-visual-panel">
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie data={mixData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={48} outerRadius={78}>
              {mixData.map((d) => (
                <Cell key={d.key} fill={MIX_COLORS[d.key]} />
              ))}
            </Pie>
            <Tooltip formatter={(v: number | string) => `¥${formatMoney(String(v))}`} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    )
  }
  return (
    <div className="seat-stub">
      <p>{String(data.message || '座位图未接入。请实现座位占用查询接口。')}</p>
      <p className="hint">演示仓没有选座界面，也不会画出店内座位。</p>
    </div>
  )
}

export default function AgentVisuals({ visuals }: { visuals: AgentVisual[] }) {
  if (!visuals.length) return null
  return (
    <div className="agent-visuals">
      {visuals.map((visual, index) => (
        <section key={`${visual.kind}-${index}`} className="agent-visual">
          <h3>{visual.title}</h3>
          <VisualChart visual={visual} />
        </section>
      ))}
    </div>
  )
}
