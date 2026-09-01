# 柜台助手演示

可独立运行的柜台对话助手演示：填入 OpenAI 兼容 API Key 后即可使用。  
本仓库**不包含**真实收银、选座、改价、核销或任何门店账本。那些能力只留工具接口，演示适配器返回占位说明。

## 别人怎么跑

需要本机已装 Python 3.11+ 和 Node 20+。不需要注册或登录。

```bash
# 仓库根目录
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS / Linux: source .venv/bin/activate
pip install -r backend/requirements.txt

# 终端 1：后端（在仓库根目录激活 venv 后）
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 终端 2：前端
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

打开 http://127.0.0.1:5173（默认停在**助手**）。  
导航里收银台 / 订单 / 图纸 / 零售 / 其他 / 会员 / 看板是占位页。  
**设置**只用来填模型密钥：粘贴 Key → 测试 → 保存，然后回助手提问。

也可以把密钥写在仓库根目录的 `.env`（从 `.env.example` 复制）。**不要把 `.env` 或 `backend/data/*.sqlite` 提交到 git。**

## 演示里能做什么

- 一句连问营业额、支付方式、开台时段：同一条回复给出**演示数字**和趋势 / 客流 / 支付图（标明演示数据）。
- 「座位图」：占位说明，请自行实现 `seat_occupancy`，**没有座位图、不能选座**。
- 「开台 / 结算 / 改价」：弹出确认卡外形，写明未接入 POS；确认不会改任何账。

## 接到真实柜台

实现 `backend/app/pos_port.py` 里的 `PosPort`，在 `app/main.py` 换成你的适配器。  
演示用的是 `DemoPosAdapter`（内存假数据 + 写入 stub）。

## 本仓库故意没有

真实订单 / 结算 / 座位坐标 / 选座表单 / 套餐改价逻辑 / 第三方核销 / 门店品牌图 / 课程提示词 / API Key。
