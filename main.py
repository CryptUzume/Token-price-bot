import os
import discord
import requests
from discord.ext import commands, tasks
from dotenv import load_dotenv
import time

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_IDS = {
    "stepn": 1367887693446643804,  # GMT 🟡
    "green-satoshi-token": 1367887745086787594,  # GST ⚪
    "Go-Game-token": 1367888140534153266  # GGT 🟣
}
EMOJIS = {
    "stepn": "🟡",
    "green-satoshi-token": "⚪",
    "Go-Game-token": "🟣"
}

API_URL = "https://api.coingecko.com/api/v3/simple/price"
HEADERS = {"Accept": "application/json"}

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")
    update_prices.start()

@tasks.loop(minutes=5)
async def update_prices():
    token_ids = ",".join(CHANNEL_IDS.keys())
    params = {
        "ids": token_ids,
        "vs_currencies": "usd,jpy"
    }

    try:
        response = requests.get(API_URL, headers=HEADERS, params=params)
        if response.status_code == 429:
            print("429 Too Many Requests - sleeping for 60 seconds...")
            time.sleep(60)
            return
        response.raise_for_status()
        prices = response.json()
    except Exception as e:
        print(f"Failed to fetch prices: {e}")
        return

    for token_id, channel_id in CHANNEL_IDS.items():
        emoji = EMOJIS.get(token_id, "")
        price_info = prices.get(token_id)
        if price_info:
            usd_price = price_info.get("usd")
            jpy_price = price_info.get("jpy")
            if usd_price is not None and jpy_price is not None:
                new_name = f"{emoji} {usd_price:.4f} USD / {jpy_price:.2f} JPY"
                try:
                    channel = await bot.fetch_channel(channel_id)
                    await channel.edit(name=new_name)
                    print(f"Updated {token_id} channel to: {new_name}")
                except Exception as e:
                    print(f"Failed to update channel {channel_id}: {e}")

bot.run(TOKEN)
