export default function PlaceholderPage({ title }: { title: string }) {
  return (
    <main className="placeholder">
      <h1>{title}</h1>
      <p>此栏是占位。本演示只实现助手（以及设置里的模型密钥）。</p>
      <p>真实柜台的开台、订单、座位、会员等请自行接入，不要从本仓库寻找业务实现。</p>
    </main>
  )
}
