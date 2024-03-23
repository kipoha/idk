import os
import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix='.', intents=disnake.Intents.all(), reload=True)
bot.remove_command('help')

@bot.event
async def on_ready():
    await bot.change_presence(status=disnake.Status.online, activity=disnake.Game('idk'))
    print(f"{bot.user} is activated")


for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        bot.load_extension(f"cogs.{file[:-3]}")

bot.run('ur token')