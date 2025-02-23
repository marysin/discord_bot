import discord
import requests
import re
from bs4 import BeautifulSoup

TOKEN = "你的_DISCORD_BOT_TOKEN"
SOURCE_CHANNEL_NAME = "來源頻道名稱"  # 你要監聽的頻道
TARGET_CHANNEL_NAME = "目標頻道名稱"  # 你要轉發的頻道

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
client = discord.Client(intents=intents)

# ✅ **確保機器人啟動**
@client.event
async def on_ready():
    print(f"✅ 機器人已上線！名稱：{client.user.name} | ID: {client.user.id}")

@client.event
async def on_message(message):
    """ 監聽來源頻道的訊息 """
    if message.author == client.user:
        return

    if message.channel.name != SOURCE_CHANNEL_NAME:
        return

    print(f"📩 收到訊息: {message.content}")

    await message.channel.send("✅ 我收到訊息了！")

# **啟動機器人**
client.run(TOKEN)
