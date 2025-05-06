import discord
from discord.ext import tasks, commands
import aiohttp
import asyncio
import os
from flask import Flask
from threading import Thread

# Flaskアプリ（UptimeRobot用の簡単な応答）
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# Discord Bot設定
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

CHANNEL_IDS = {
    "GMT": 1367887693446643804,
    "GST": 1367887745086787594,
    "GGT": 1367888140534153266,
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
                    price_text = f"{EMOJIS[token]}{token}: ${usd:.4f} / ¥{jpy:.2f}"
                    channel = bot.get_channel(CHANNEL_IDS[token])
                    if channel:
                        await channel.edit(name=price_text)
                        await asyncio.sleep(2)
                    else:
                        print(f"Channel not found for {token}")
            except Exception as e:
                print(f"Error updating {token}: {e}")

if __name__ == "__main__":
    # Flaskを別スレッドで起動
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Discord Bot起動
    asyncio.run(bot.start(TOKEN))

