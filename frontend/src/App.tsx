import { useState } from 'react'
import AgentPage from './AgentPage'
import PlaceholderPage from './PlaceholderPage'
import SettingsPage from './SettingsPage'

const TABS = [
  { id: 'cashier', label: '收银台' },
  { id: 'orders', label: '订单' },
  { id: 'drawings', label: '图纸' },
  { id: 'retail', label: '零售' },
  { id: 'other', label: '其他' },
  { id: 'members', label: '会员' },
  { id: 'dashboard', label: '看板' },
  { id: 'agent', label: '助手' },
  { id: 'settings', label: '设置' },
] as const

type Tab = (typeof TABS)[number]['id']

export default function App() {
  const [tab, setTab] = useState<Tab>('agent')
  return (
    <div className={tab === 'agent' ? 'app app-agent' : 'app'}>
      <header className="topbar">
        <div className="brand">
          <strong>柜台助手演示</strong>
          <span>仅助手可用</span>
        </div>
        <nav>
          {TABS.map((item) => (
            <button
              key={item.id}
              type="button"
              className={tab === item.id ? 'nav-on' : 'nav-btn'}
              onClick={() => setTab(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </header>
      {tab === 'agent' && <AgentPage />}
      {tab === 'settings' && <SettingsPage />}
      {tab !== 'agent' && tab !== 'settings' && (
        <PlaceholderPage title={TABS.find((item) => item.id === tab)?.label || ''} />
      )}
    </div>
  )
}
