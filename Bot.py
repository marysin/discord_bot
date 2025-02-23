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

def extract_pokemon_data(message):
    """ 使用正則表達式解析寶可夢資訊 """
    pattern = re.compile(
        r":flag_(\w+): \*\*\*(.*?)\*\*\* .*?IV(\d+) \((A\d+/D\d+/S\d+)\) \*\*CP(\d+)\*\* \*\*L(\d+)\*\* (♂|♀)? .*? \(DSP in (\d+m)\) - \*(.*?)\*"
    )
    
    match = pattern.search(message)
    if match:
        flag_code, pokemon_en, iv, iv_details, cp, level, gender, dsp_time, location = match.groups()
        
        # 國家對應
        country_flags = {
            "br": "🇧🇷 巴西",
            "us": "🇺🇸 美國",
            "jp": "🇯🇵 日本",
            "es": "🇪🇸 西班牙",
            "cn": "🇨🇳 中國",
            "fr": "🇫🇷 法國",
            "de": "🇩🇪 德國",
            "ru": "🇷🇺 俄羅斯",
            "ar": "🇦🇷 阿根廷"
        }
        country = country_flags.get(flag_code, f"🌍 未知 ({flag_code})")

        # 英文寶可夢轉換成中文（可自行擴展）
        pokemon_translations = {
            "Torchic": "火稚雞",
            "Pikachu": "皮卡丘",
            "Bulbasaur": "妙蛙種子"
        }
        pokemon_zh = pokemon_translations.get(pokemon_en, pokemon_en)

        return {
            "country": country,
            "pokemon_en": pokemon_en,
            "pokemon_zh": pokemon_zh,
            "iv": iv,
            "iv_details": iv_details,
            "cp": cp,
            "level": level,
            "gender": gender or "未知",
            "dsp_time": dsp_time,
            "location": location.strip()
        }
    return None

def extract_coordinates(url):
    """ 解析 `Click for Coords` 內的經緯度 """
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        lat = soup.find("meta", {"name": "latitude"})["content"]
        lon = soup.find("meta", {"name": "longitude"})["content"]
        return lat, lon
    except:
        return None, None

@client.event
async def on_message(message):
    """ 監聽來源頻道的訊息 """
    if message.author == client.user:
        return

    if message.channel.name != SOURCE_CHANNEL_NAME:
        return

    print(f"📩 收到訊息: {message.content}")

    # 解析寶可夢資訊
    pokemon_data = extract_pokemon_data(message.content)
    if not pokemon_data:
        return
    
    # 抓取 `Click for Coords` 連結
    coord_link = None
    for embed in message.embeds:
        if "Click for Coords" in embed.description:
            coord_link = embed.url
            break

    lat, lon = None, None
    if coord_link:
        lat, lon = extract_coordinates(coord_link)

    # 格式化訊息
    final_message = f"""
    {pokemon_data['country']} **{pokemon_data['pokemon_zh']} ({pokemon_data['pokemon_en']})**
    IV: {pokemon_data['iv']} ({pokemon_data['iv_details']})
    CP: {pokemon_data['cp']} | L: {pokemon_data['level']}
    性別: {pokemon_data['gender']}
    消失時間: {pokemon_data['dsp_time']}
    地點: {pokemon_data['location']}
    座標: {lat}, {lon}
    """

    print("📤 發送到目標頻道:", final_message)

    # 發送到目標頻道
    target_channel = discord.utils.get(message.guild.channels, name=TARGET_CHANNEL_NAME)
    if target_channel:
        await target_channel.send(final_message)
    else:
        print(f"❌ 找不到目標頻道: {TARGET_CHANNEL_NAME}")

client.run(TOKEN)
