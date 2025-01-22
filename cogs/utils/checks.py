from dotenv import load_dotenv
import os
from discord.ext import commands


load_dotenv()

def is_owner_check(message):
    return message.author.id == os.getenv('BOT_OWNER')

def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx.message))
