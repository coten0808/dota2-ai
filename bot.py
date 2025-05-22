import os
import logging
import requests
from discord import Client, Intents, Embed
import google.generativeai as genai
from discord.ext import commands
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設置日誌記錄
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# API 設置
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OPENDOTA_API_URL = "https://api.opendota.com/api"

# 配置 Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    # 列出可用的模型
    for m in genai.list_models():
        logger.info(f"可用模型: {m.name}")
    
    model = genai.GenerativeModel('gemini-1.5-pro')
    # 測試 API 是否正常工作
    response = model.generate_content("測試")
    logger.info("Gemini API 測試成功")
except Exception as e:
    logger.error(f"Gemini API 配置錯誤: {str(e)}")
    raise

# 創建 Discord 機器人實例
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# 英雄名稱對照表
HERO_ALIASES = {
    # 力量英雄
    "axe": ["斧王", "斧头", "ax"],
    "earthshaker": ["撼地者", "es", "小牛", "震撼者"],
    "pudge": ["帕吉", "胖子", "屠夫", "hooks"],
    "sand king": ["沙王", "sk", "sand"],
    "sven": ["斯温", "sv", "流浪剑客", "流浪"],
    "tiny": ["小小", "山岭巨人", "山岭"],
    "kunkka": ["船长", "海军上将", "船"],
    "dragon knight": ["龙骑士", "dk", "dragon"],
    
    # 敏捷英雄
    "anti-mage": ["敌法师", "am", "敌法", "反魔法师"],
    "drow ranger": ["卓尔游侠", "dr", "drow", "黑暗游侠"],
    "juggernaut": ["主宰", "剑圣", "jugg", "奶棒人"],
    "mirana": ["米拉娜", "白虎", "priestess", "potm"],
    "morphling": ["变体精灵", "morph", "水人"],
    "phantom lancer": ["幻影长矛手", "pl", "猴子"],
    "vengeful spirit": ["复仇之魂", "vs", "venge"],
    "riki": ["力丸", "隐形刺客", "隐刺"],
    
    # 智力英雄
    "crystal maiden": ["水晶室女", "cm", "冰女"],
    "puck": ["帕克", "仙女龙", "精灵龙"],
    "storm spirit": ["风暴之灵", "蓝猫", "storm"],
    "zeus": ["宙斯", "zeus", "电狗"],
    "lina": ["莉娜", "火女", "火凤凰"],
    "shadow shaman": ["暗影萨满", "ss", "小Y"],
    "tinker": ["修补匠", "tk", "叮叮"],
    "nature's prophet": ["先知", "np", "树精"],
    
    # 更多英雄...可以继续添加
}

def find_hero_name(search_term):
    """查找英雄的标准名称"""
    search_term = search_term.lower()
    
    # 直接匹配
    for hero_name, aliases in HERO_ALIASES.items():
        if search_term == hero_name or search_term in aliases:
            return hero_name
    
    # 模糊匹配
    for hero_name, aliases in HERO_ALIASES.items():
        if any(search_term in alias for alias in aliases) or search_term in hero_name:
            return hero_name
    
    return search_term  # 如果找不到匹配，返回原始搜索词

async def generate_response(prompt):
    try:
        generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        if response.text:
            return response.text
        else:
            logger.error("Gemini API 返回空回應")
            return "抱歉，我無法生成回應。請稍後再試。"
    except Exception as e:
        logger.error(f"生成回應時發生錯誤: {str(e)}")
        return f"抱歉，處理請求時發生錯誤: {str(e)}"

@bot.event
async def on_ready():
    logger.info(f'{bot.user} 已成功登入！')

@bot.command(name='discuss')
async def discuss(ctx, *, question):
    """討論 Dota 2 相關問題"""
    prompt = f"""作為一個 Dota 2 專家，請回答以下問題。請提供詳細且專業的回答：

問題：{question}

回答時請注意：
1. 使用專業的遊戲術語
2. 提供具體的遊戲策略和建議
3. 如果適用，可以提供相關的遊戲機制解釋
4. 盡可能提供實用的遊戲技巧"""
    
    response = await generate_response(prompt)
    await ctx.send(response)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        prompt = f"""作為一個友善的 Dota 2 助手，請回答以下問題：

{message.content}

請提供專業且易懂的回答。"""
        response = await generate_response(prompt)
        await message.channel.send(response)

    await bot.process_commands(message)

@bot.command(name='hero')
async def hero_guide(ctx, *, hero_name):
    """獲取英雄攻略"""
    standard_name = find_hero_name(hero_name)
    prompt = f"""作為一個 Dota 2 專家，請提供關於 {standard_name} ({hero_name}) 的詳細攻略：

請包含以下資訊：
1. 英雄定位和角色
2. 技能加點建議
3. 核心出裝推薦
4. 對線技巧
5. 團戰定位
6. 優勢與劣勢
7. 克制與被克制英雄
8. 適合的玩家風格

請提供專業且實用的建議。"""
    
    response = await generate_response(prompt)
    await ctx.send(response)

@bot.command(name='build')
async def item_build(ctx, *, hero_name):
    """獲取英雄出裝建議"""
    standard_name = find_hero_name(hero_name)
    prompt = f"""作為一個 Dota 2 專家，請提供 {standard_name} ({hero_name}) 的詳細出裝建議：

請包含：
1. 前期必備裝備
2. 核心裝備搭配
3. 情況裝推薦
4. 後期豪華裝備
5. 不同位置的出裝選擇
6. 各階段裝備時機
7. 裝備搭配邏輯解釋

請根據當前版本提供最優化的建議。"""
    
    response = await generate_response(prompt)
    await ctx.send(response)

@bot.command(name='counter')
async def counter_pick(ctx, *, hero_name):
    """獲取英雄克制建議"""
    standard_name = find_hero_name(hero_name)
    prompt = f"""作為一個 Dota 2 專家，請分析 {standard_name} ({hero_name}) 的克制關係：

請提供：
1. 最佳克制英雄推薦
2. 被哪些英雄克制
3. 克制原理說明
4. 應對策略
5. 線上對抗技巧
6. 團戰處理方式
7. 裝備應對建議

請提供具體且實用的建議。"""
    
    response = await generate_response(prompt)
    await ctx.send(response)

@bot.command(name='pro')
async def pro_player(ctx, *, hero_name):
    """獲取職業選手比賽資訊"""
    standard_name = find_hero_name(hero_name)
    try:
        # 使用 OpenDota API 獲取職業比賽資訊
        url = f"{OPENDOTA_API_URL}/heroes/{standard_name}/matches"
        response = requests.get(url)
        data = response.json()
        
        prompt = f"""作為一個 Dota 2 專家，請分析 {standard_name} ({hero_name}) 在職業比賽中的表現：

請提供：
1. 近期比賽趨勢
2. 知名選手操作特點
3. 職業比賽常見戰術
4. 關鍵操作要點
5. 推薦觀看的比賽視頻
6. 學習重點提示

請提供專業的分析和建議。"""
        
        response = await generate_response(prompt)
        await ctx.send(response)
        
    except Exception as e:
        await ctx.send(f"抱歉，獲取職業比賽資訊時發生錯誤：{str(e)}")

@bot.command(name='meta')
async def meta_analysis(ctx):
    """獲取當前版本分析"""
    prompt = """作為一個 Dota 2 專家，請分析當前版本的遊戲環境：

請提供：
1. 強勢英雄推薦
2. 熱門戰術分析
3. 版本特點說明
4. 重要改動影響
5. 推薦玩法建議
6. 排位建議
7. 各分段適合英雄

請提供最新且實用的版本分析。"""
    
    response = await generate_response(prompt)
    await ctx.send(response)

@bot.command(name='lane')
async def lane_guide(ctx, *, hero_name):
    """獲取對線指南"""
    standard_name = find_hero_name(hero_name)
    prompt = f"""作為一個 Dota 2 專家，請提供 {standard_name} ({hero_name}) 的詳細對線指南：

請包含：
1. 各路線定位建議
2. 對線要點
3. 補刀技巧
4. 控線方法
5. 視野運用
6. 關鍵時間點
7. 遊走時機
8. 打野技巧（如適用）

請提供具體且實用的對線建議。"""
    
    response = await generate_response(prompt)
    await ctx.send(response)

@bot.command(name='combo')
async def skill_combo(ctx, *, hero_name):
    """獲取技能連招指南"""
    standard_name = find_hero_name(hero_name)
    prompt = f"""作為一個 Dota 2 專家，請提供 {standard_name} ({hero_name}) 的技能連招指南：

請包含：
1. 基礎連招順序
2. 進階連招技巧
3. 裝備配合連招
4. 團戰關鍵連招
5. 單殺連招組合
6. 特殊情況處理
7. 連招時機選擇

請提供詳細的操作說明。"""
    
    response = await generate_response(prompt)
    await ctx.send(response)

@bot.command(name='commands')
async def show_commands(ctx):
    """顯示所有可用指令"""
    embed = Embed(title="Dota 2 機器人指令列表", color=0x00ff00, description="以下是所有可用的指令：")
    
    commands_info = {
        "!hero [英雄名稱]": "獲取英雄詳細攻略（例如：!hero 影魔）",
        "!build [英雄名稱]": "獲取英雄出裝建議（例如：!build 小狗）",
        "!counter [英雄名稱]": "獲取英雄克制建議（例如：!counter 斧王）",
        "!pro [英雄名稱]": "獲取職業選手比賽資訊（例如：!pro 巫師）",
        "!meta": "獲取當前版本分析",
        "!lane [英雄名稱]": "獲取對線指南（例如：!lane 火女）",
        "!combo [英雄名稱]": "獲取技能連招指南（例如：!combo 帕克）",
        "!discuss [問題]": "討論任何 Dota 2 相關問題（例如：!discuss 如何提高補刀？）",
        "!commands": "顯示此幫助訊息"
    }
    
    for cmd, desc in commands_info.items():
        embed.add_field(name=cmd, value=desc, inline=False)
    
    embed.set_footer(text="提示：使用 @ 提及機器人也可以直接對話")
    try:
        await ctx.send(embed=embed)
    except Exception as e:
        logger.error(f"發送幫助訊息時發生錯誤：{str(e)}")
        # 如果發送 embed 失敗，改用純文字訊息
        help_text = "**Dota 2 機器人指令列表**\n\n"
        for cmd, desc in commands_info.items():
            help_text += f"{cmd}: {desc}\n"
        help_text += "\n提示：使用 @ 提及機器人也可以直接對話"
        await ctx.send(help_text)

# 運行機器人
if __name__ == "__main__":
    if not DISCORD_TOKEN or not GEMINI_API_KEY:
        logger.error("請設置必要的環境變數：DISCORD_TOKEN 和 GEMINI_API_KEY")
    else:
        bot.run(DISCORD_TOKEN)