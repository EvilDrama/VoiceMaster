import discord
from discord.ext import commands
from discord.utils import get
import traceback
import sys

def bot_d():
    
    bot = commands.Bot(command_prefix="?")

    
    token = 'OTczMjU2MTUwODEwMjMwODU1.GDV6cn.3Icq2bvoQQJ7VtLzk1VNDaEEfAN6AZSdgOuHW4'
    
    bot.run(token)