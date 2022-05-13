import discord
from discord.ext import commands
from discord.utils import get
import traceback
import sys

bot = commands.Bot(command_prefix="?")


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


initial_extensions = ['cogs.voice']

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()

token = 'OTczMjU2MTUwODEwMjMwODU1.GDV6cn.3Icq2bvoQQJ7VtLzk1VNDaEEfAN6AZSdgOuHW4'

bot.run(token)