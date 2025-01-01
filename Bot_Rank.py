import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()
TOKEN = os.getenv('TOKEN_BOT')
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)


roles_color = {
    "Immortal": 0xFF0000, 
    "Radiant": 0xFFD700,    
    "Diamond": 0x800080,  
    "Ascendant" : 0x008000, 
    "Platinum": 0x0000FF,  
    "Gold": 0xFFFF00,        
    "Silver": 0xD3D3D3,    
    "Bronze": 0x6F4F37,
    "Iron" : 0xA9A9A9
}

def obtener_rango_con_selenium(nickname):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('enable-unsafe-swiftshader')
        options.add_argument("window-size=800x600")
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        formatted_nickname = nickname.replace('#', '%23')
        url = f'https://tracker.gg/valorant/profile/riot/{formatted_nickname}/overview'

        driver.get(url)

        wait = WebDriverWait(driver, 10)
        rank_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.stat__label")))  
        if rank_element.text.strip() == 'Rating':
            rank_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.stat__value")))
        rank = rank_element.text.strip().split(' ')[0]

        driver.quit()
        return rank

    except Exception as e:
        print(f"Error: {e}")
        return None
    

@bot.command(name="rank")
async def asignar_rango(ctx, *, nickname):
    await ctx.send(f"Consultando el rango para el jugador: {nickname}...")
    rango = obtener_rango_con_selenium(nickname)

    if rango:
        
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name=rango)
        
        if not role:
            role = await guild.create_role(name=rango)

        color = roles_color.get(rango.split(' ')[0])
        if color is None:
            await ctx.send(f"No se encontró un icono para el rol `{rango}`.")
            return
        
        member = ctx.author
        await member.add_roles(role)
        await role.edit(color=color)
        await ctx.send(f"Se te ha asignado el rol: {rango}")
    else:
        await ctx.send("No se pudo obtener el rango del jugador. Verifica el nickname.")


@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

bot.run(TOKEN)