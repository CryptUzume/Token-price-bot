import os
import logging
import requests
import asyncio
from discord.ext import commands, tasks
from dotenv import load_dotenv

# ログ設定
logging.basicConfig(level=logging.INFO)

# トークンとチャンネルIDの設定
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

CHANNEL_IDS = {
    "stepn": {"id": 1367887693446643804, "emoji": "🟡", "symbol": "GMT"},
    "green-satoshi-token": {"id": 1367887745086787594, "emoji": "⚪", "symbol": "GST"},
    "go-game-token": {"id": 1367888140534153266, "emoji": "🟣", "symbol": "GGT"},
}

# CoinGecko APIエンドポイント
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"

# Bot設定
intents = commands.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


async def fetch_prices():
    ids = ",".join(CHANNEL_IDS.keys())
    params = {
        "ids": ids,
        "vs_currencies": "usd,jpy"
    }

    retry_wait = 30  # 初回リトライ待機時間（秒）
    max_retries = 5

    for attempt in range(max_retries):
        try:
            response = requests.get(COINGECKO_API_URL, params=params, timeout=10)

            if response.status_code == 200:
                return response.json()

            elif response.status_code == 429:
                logging.warning(f"[RATE LIMIT] 429 Too Many Requests - Retry in {retry_wait} sec")
                await asyncio.sleep(retry_wait)
                retry_wait *= 2  # 指数バックオフ

            else:
                logging.error(f"[ERROR] API returned status code: {response.status_code}")
                break

        except Exception as e:
            logging.error(f"[EXCEPTION] Failed to fetch prices: {e}")
            break

    return None


@tasks.loop(minutes=5)
async def update_channel_names():
    logging.info("[START] Updating token prices...")

    prices = await fetch_prices()
    if not prices:
        logging.error("[FAILED] No price data fetched.")
        return

    for token_id, data in CHANNEL_IDS.items():
        price_data = prices.get(token_id)
        if not price_data:
            logging.warning(f"[MISSING DATA] No price found for {token_id}")
            continue

        usd = price_data.get("usd")
        jpy = price_data.get("jpy")

        if usd is None or jpy is None:
            logging.warning(f"[INCOMPLETE] Missing USD or JPY price for {token_id}")
            continue

        name = f"{data['emoji']} {data['symbol']} ${usd:.4f} ¥{jpy:.2f}"

        try:
            channel = bot.get_channel(data["id"])
            if channel:
                await channel.edit(name=name)
                logging.info(f"[SUCCESS] Updated {data['symbol']} to {name}")
            else:
                logging.error(f"[NOT FOUND] Channel ID {data['id']} not found")
        except Exception as e:
            logging.error(f"[EXCEPTION] Failed to update channel {data['id']}: {e}")


@bot.event
async def on_ready():
    logging.info(f"Bot logged in as {bot.user}")
    update_channel_names.start()


if __name__ == "__main__":
    load_dotenv()
    if not DISCORD_TOKEN:
        logging.error("DISCORD_TOKEN is not set in environment variables.")
    else:
        bot.run(DISCORD_TOKEN)
