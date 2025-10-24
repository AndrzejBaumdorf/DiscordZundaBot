# main.py
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# 環境変数の読み込み
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # VOICEVOX利用時に必要

# Botの初期化
bot = commands.Bot(
    command_prefix="!z ",
    intents=intents,
    help_command=None
)

# Cogをロード
async def load_extensions():
    await bot.load_extension("cogs.zundaCommands")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game("VOICEVOXでしゃべるよ！"))

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
