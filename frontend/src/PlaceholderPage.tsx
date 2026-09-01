export default function PlaceholderPage({ title }: { title: string }) {
  return (
    <main className="placeholder-page">
      <section className="panel">
        <h1>{title}</h1>
        <p className="hint">此栏是占位。本演示只实现助手，以及设置里的模型密钥。</p>
        <p className="hint">真实柜台的开台、订单、座位、会员请自行接入，不要从本仓库寻找业务实现。</p>
      </section>
    </main>
  )
}
