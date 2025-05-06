import discord
from discord.ext import tasks, commands
import aiohttp
import asyncio
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

# ボイスチャンネルID
CHANNEL_IDS = {
    "GMT": 1367887693446643804,
    "GST": 1367887745086787594,
    "GGT": 1367888140534153266,
}

# CoinGecko API用ID
COINGECKO_IDS = {
    "GMT": "stepn",
    "GST": "green-satoshi-token",
    "GGT": "go-game-token"
}

# トークン絵文字
EMOJIS = {
    "GMT": "🟡",
    "GST": "⚪",
    "GGT": "🟣"
}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    update_prices.start()

@tasks.loop(minutes=5)
async def update_prices():
    print("Updating prices...")
    async with aiohttp.ClientSession() as session:
        for token in ["GMT", "GST", "GGT"]:
            coingecko_id = COINGECKO_IDS[token]
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd,jpy"
            try:
                async with session.get(url) as response:
                    data = await response.json()
                    usd = data[coingecko_id]['usd']
                    jpy = data[coingecko_id]['jpy']

                    # 金額のフォーマット調整
                    price_text = f"{EMOJIS[token]}{token}: ${usd:.4f} / ¥{jpy:.2f}"

                    # チャンネル名更新
                    channel = bot.get_channel(CHANNEL_IDS[token])
                    if channel:
                        await channel.edit(name=price_text)
                        await asyncio.sleep(2)  # API制限対策のディレイ
                    else:
                        print(f"Channel not found for {token}")
            except Exception as e:
                print(f"Error updating {token}: {e}")

# 起動
if __name__ == "__main__":
    asyncio.run(bot.start(TOKEN))
