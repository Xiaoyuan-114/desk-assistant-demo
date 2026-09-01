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

function tabFromHash(): Tab {
  const id = window.location.hash.replace('#', '')
  return TABS.some((item) => item.id === id) ? (id as Tab) : 'agent'
}

export default function App() {
  const [tab, setTab] = useState<Tab>(tabFromHash)

  function openTab(next: Tab) {
    setTab(next)
    window.location.hash = next
  }
  return (
    <div className={tab === 'agent' ? 'app app--agent' : 'app'}>
      <header className="topbar">
        <div className="brand-block">
          <span className="brand-mark" aria-hidden="true">柜</span>
          <div className="brand-text">
            <strong>柜台助手演示</strong>
            <small>仅助手可用</small>
          </div>
        </div>
        <nav className="topbar-nav" aria-label="主导航">
          {TABS.map((item) => (
            <button
              key={item.id}
              type="button"
              className={tab === item.id ? 'nav-active' : 'nav-btn'}
              onClick={() => openTab(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>
        <div className="topbar-right">
          <div className="status">演示</div>
        </div>
      </header>
      {tab === 'agent' && <AgentPage />}
      {tab === 'settings' && <SettingsPage />}
      {tab !== 'agent' && tab !== 'settings' && (
        <PlaceholderPage title={TABS.find((item) => item.id === tab)?.label || ''} />
      )}
    </div>
  )
}
