# Discord Token Price Bot

このBotは、CoinGecko APIを使用してGMT / GST / GGTの価格（USD/JPY）を5分ごとに取得し、Discordの各ボイスチャンネル名を更新します。Renderの無料プランで24時間稼働可能です。

## 🔧 環境変数（Renderの「Environment」タブに設定）

- `DISCORD_TOKEN`：Discord Botトークン
- `GMT_CHANNEL_ID`：GMT用のVCチャンネルID（例：1367887693446643804）
- `GST_CHANNEL_ID`：GST用のVCチャンネルID（例：1367887745086787594）
- `GGT_CHANNEL_ID`：GGT用のVCチャンネルID（例：1367888140534153266）

## 🚀 Render設定手順

1. Render にログインし、New → Web Service を選択
2. GitHubリポジトリを接続
3. **Start Command** に以下を入力：
   ```bash
   python3 run.py
