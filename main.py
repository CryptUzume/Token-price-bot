import discord
import requests
import time
import asyncio
import os
from discord.ext import tasks

TOKEN = 'MTM2Nzc1MjAxMDUyNjM2MzY4OA.GGBLbl.NUln4ZJJas3uQN-V9TUOkzwZBEYDoEOa4d0bzM'
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# チャンネルIDの指定
CHANNEL_IDS = {
    "GMT": 1367887693446643804,
    "GST": 1367887745086787594,
    "GGT": 1367888140534153266
}

# CoinGeckoのIDと表示名
TOKENS = {
    "GMT": {"id": "stepn", "symbol": "GMT"},
    "GST": {"id": "green-satoshi-token", "symbol": "GST"},
    "GGT": {"id": "Go-Game-token", "symbol": "GGT"}
}

async def fetch_prices():
    """CoinGecko APIから価格情報を取得"""
    url = "https://api.coingecko.com/api/v3/simple/price"
    ids = ",".join([info["id"] for info in TOKENS.values()])
    params = {
        "ids": ids,
        "vs_currencies": "usd"
    }

    for attempt in range(3):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[{attempt+1}/3] API取得エラー: {e}")
            if attempt < 2:
                await asyncio.sleep(10)
            else:
                return None

@tasks.loop(minutes=5)
async def update_channels():
    print("価格更新中...")
    prices = await fetch_prices()
    if prices is None:
        print("価格の取得に失敗しました。次のループを待機します。")
        return

    for token_name, info in TOKENS.items():
        token_id = info["id"]
        symbol = info["symbol"]
        price = prices.get(token_id, {}).get("usd")
        if price is not None:
            channel_id = CHANNEL_IDS[token_name]
            channel = client.get_channel(channel_id)
            if channel:
                try:
                    await channel.edit(name=f"{symbol} ${price:.4f}")
                    print(f"{symbol} チャンネル名更新完了: ${price:.4f}")
                except Exception as e:
                    print(f"{symbol} チャンネルの更新に失敗: {e}")
            else:
                print(f"{symbol} チャンネルが見つかりません")
        else:
            print(f"{symbol} の価格データが取得できませんでした")

@client.event
async def on_ready():
    print(f'ログイン成功: {client.user}')
    update_channels.start()

client.run(TOKEN)
