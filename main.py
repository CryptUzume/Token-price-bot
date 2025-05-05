import os
import asyncio
import logging
import requests
import discord

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))
CHANNEL_IDS = {
    "stepn": int(os.getenv("CHANNEL_ID_GMT")),
    "green-satoshi-token": int(os.getenv("CHANNEL_ID_GST")),
    "go-game-token": int(os.getenv("CHANNEL_ID_GGT")),
}

SYMBOLS = {
    "stepn": "⚪ GMT",
    "green-satoshi-token": "⚪ GST",
    "go-game-token": "🟣 GGT",
}

client = discord.Client(intents=discord.Intents.default())

def fetch_prices():
    ids = ",".join(CHANNEL_IDS.keys())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd,jpy"
    response = requests.get(url)
    if response.status_code == 429:
        raise Exception("429 Too Many Requests")
    response.raise_for_status()
    return response.json()

async def update_token_prices_periodically():
    await client.wait_until_ready()
    await asyncio.sleep(30)  # 起動時に30秒待機（レート制限対策）

    while not client.is_closed():
        try:
            logger.info("[DEBUG] Fetching prices for: %s", ",".join(CHANNEL_IDS.keys()))
            prices = fetch_prices()

            for token_id, channel_id in CHANNEL_IDS.items():
                try:
                    data = prices.get(token_id)
                    if not data:
                        logger.warning(f"No data for {token_id}")
                        continue

                    usd = data["usd"]
                    jpy = data["jpy"]
                    name = f"{SYMBOLS[token_id]}: ${usd:.3f} / ¥{jpy:.2f}"

                    channel = client.get_channel(channel_id)
                    if channel:
                        await channel.edit(name=name)
                        logger.info(f"Updated channel {SYMBOLS[token_id]}: {name}")
                    else:
                        logger.warning(f"Channel not found for {token_id}")
                except Exception as e:
                    logger.error(f"[ERROR] Failed to update channel {SYMBOLS[token_id]}: {e}")

        except Exception as e:
            logger.error(f"[ERROR] Failed to fetch token prices: {e}")

        await asyncio.sleep(300)  # 5分待機

@client.event
async def on_ready():
    logger.info(f"Logged in as {client.user}")
    client.loop.create_task(update_token_prices_periodically())

client.run(TOKEN)
