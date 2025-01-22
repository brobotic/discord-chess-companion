import asyncio
from config import Config
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging
import os
import sys
import traceback


def get_prefix(bot, message):
    prefixes = [config.prefix]

    if not message.guild:
        return '.'

    return commands.when_mentioned_or(*prefixes)(bot, message)


config = Config()
load_dotenv()
print(f'Loaded {config} with prefix {config.prefix}')

logging.basicConfig(level=config.log_level)

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True

bot = commands.Bot(command_prefix=get_prefix, description='Discord bot rewrite', intents=intents)
bot.remove_command('help')

async def main():
    async with bot:
        if len(config.initial_extensions) > 0:
            for extension in config.initial_extensions:
                try:
                    await bot.load_extension(extension)
                    print(f'Loaded extension: {extension}')
                except Exception as e:
                    print(f'Failed to load extension {extension}.', file=sys.stderr)
                    traceback.print_exc()

        await bot.start(os.getenv('BOT_TOKEN'), reconnect=True)


@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\ndiscord.py version: {discord.__version__}\n')

    bot_status_env = os.environ.get('BOT_STATUS')
    if bot_status_env:
        bot_status = bot_status_env
    else:
        bot_status = config.status

    await bot.change_presence(activity=discord.Game(name=bot_status))


asyncio.run(main())