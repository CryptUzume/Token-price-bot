import os
import asyncio
import logging
import discord
import requests
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Please set DISCORD_BOT_TOKEN in the Secrets tab")

# トークン名とCoinGeckoのIDをマッピング
TOKEN_IDS = {
    'GMT': 'stepn',
    'GST': 'green-satoshi-token',
    'GGT': 'go-game-token'
}

# チャンネルIDを設定
CHANNEL_IDS = {
    'GMT': 1367887693446643804,
    'GST': 1367887745086787594,
    'GGT': 1367888140534153266,
}

# 表示用の絵文字
TOKEN_EMOJIS = {
    'GMT': '🟡',
    'GST': '⚪',
    'GGT': '🟣'
}

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")
    update_prices.start()

@tasks.loop(minutes=5)
async def update_prices():
    try:
        # 一括でリクエスト
        ids = ','.join(TOKEN_IDS.values())
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd,jpy"
        logger.info(f"[DEBUG] Fetching prices for: {ids}")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        for symbol, coingecko_id in TOKEN_IDS.items():
            try:
                usd_price = data[coingecko_id]['usd']
                jpy_price = data[coingecko_id]['jpy']
                emoji = TOKEN_EMOJIS.get(symbol, '')
                new_name = f"{emoji} {symbol}: ${usd_price:.3f} / ¥{jpy_price:.2f}"
                channel_id = CHANNEL_IDS[symbol]
                channel = await bot.fetch_channel(channel_id)
                await channel.edit(name=new_name)
                logger.info(f"Updated channel {symbol}: {new_name}")
                await asyncio.sleep(5)  # 少し待機してレート制限回避
            except Exception as e:
                logger.error(f"[ERROR] Failed to update {symbol}: {e}")
                await asyncio.sleep(10)
    except Exception as e:
        logger.error(f"[ERROR] Failed to fetch token prices: {e}")
        await asyncio.sleep(10)

bot.run(TOKEN)
