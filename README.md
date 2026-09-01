<p align="center">
  <img src="./assets/readme/hero.svg" width="100%" alt="柜台助手演示：填入 API Key 即可提问，导航其它栏是占位，没有真实收银账本。">
</p>

填入 OpenAI 兼容密钥就能对话。页面默认停在**助手**；收银台、订单、图纸等栏位还在，但是占位。不需要登录。

<p align="center">
  <img src="./assets/readme/proof-assistant.png" width="100%" alt="助手页：默认选中助手，提示去设置粘贴 API Key，并给出营业额、支付方式、开台时段等推荐问法。">
</p>

<p align="center">
  <img src="./assets/readme/proof-settings.png" width="100%" alt="设置页：状态为未配置，可填写接口地址、模型名和 API Key，然后测试保存。">
</p>

这是一个可独立运行的演示壳。问营业、支付、客流会返回**演示数字**和图表。座位图是说明卡。开台 / 结算 / 改价只弹出确认卡外形，点确认也不会改账。

<p align="center">
  <img src="./assets/readme/workflow.svg" width="100%" alt="第一次成功路径：设置里粘贴密钥，回到助手提问，得到演示数字与图或未接入确认卡。">
</p>

<p align="center">
  <img src="./assets/readme/section-use.svg" width="100%" alt="开始使用">
</p>

需要本机已装 Python 3.11+ 和 Node 20+。

```bash
# 仓库根目录
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS / Linux: source .venv/bin/activate
pip install -r backend/requirements.txt

# 终端 1
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 终端 2
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

打开 http://127.0.0.1:5173 → **设置** 粘贴 Key → 测试 → 保存 → **助手** 提问。

也可以把密钥写在仓库根目录的 `.env`（从 `.env.example` 复制）。不要提交 `.env` 或 `backend/data/*.sqlite`。

<p align="center">
  <img src="./assets/readme/section-scope.svg" width="100%" alt="演示范围">
</p>

| 可以 | 不要指望从本仓库得到 |
| --- | --- |
| 一句连问营业额、支付方式、开台时段 | 真实订单、结算、套餐改价 |
| 看趋势 / 客流 / 支付图（标明演示） | 店内座位坐标、选座表单 |
| 看到写入动作的确认卡外形 | 第三方核销、门店品牌图、课程提示词、API Key |

<p align="center">
  <img src="./assets/readme/section-wire.svg" width="100%" alt="接到柜台">
</p>

实现 `backend/app/pos_port.py` 里的 `PosPort`，在 `backend/app/main.py` 换成你的适配器。演示用的是内存假数据 `DemoPosAdapter`。

## License

MIT
