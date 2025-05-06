# bot.py
import discord
from discord.ext import commands, tasks
import os
import requests
import asyncio

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_IDS = {
    "GMT": int(os.getenv("GMT_CHANNEL_ID")),
    "GST": int(os.getenv("GST_CHANNEL_ID")),
    "GGT": int(os.getenv("GGT_CHANNEL_ID"))
}
COINGECKO_IDS = {
    "GMT": "stepn",
    "GST": "green-satoshi-token",
    "GGT": "go-game-token"
}
EMOJIS = {
    "GMT": "🟡",
    "GST": "⚪",
    "GGT": "🟣"
}

async def fetch_price(token_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies=usd,jpy"
    try:
        response = requests.get(url)
        data = response.json()
        return data[token_id]["usd"], data[token_id]["jpy"]
    except Exception as e:
        print(f"Error fetching {token_id}: {e}")
        return None, None

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    update_prices.start()

@tasks.loop(minutes=5)
async def update_prices():
    for symbol, channel_id in CHANNEL_IDS.items():
        token_id = COINGECKO_IDS[symbol]
        emoji = EMOJIS[symbol]
        usd, jpy = await fetch_price(token_id)
        if usd and jpy:
            channel = bot.get_channel(channel_id)
            try:
                await channel.edit(name=f"{emoji} {symbol}: ${usd:.3f}/¥{int(jpy)}")
                await asyncio.sleep(2)  # レート制限対策
            except Exception as e:
                print(f"Error editing {symbol} channel: {e}")

def start_bot():
    bot.run(TOKEN)
