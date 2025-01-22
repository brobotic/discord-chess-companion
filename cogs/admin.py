from discord.ext import commands
from .utils import checks, reactions


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='reload', hidden=True)
    @checks.is_owner()
    async def _reload(self, ctx, module):
        try:
            await self.bot.unload_extension(module)
            await self.bot.load_extension(module)
        except Exception as e:
            await ctx.send('{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.message.add_reaction(reactions.THUMBS_UP_REACTION)

    @commands.command(name='load', hidden=True)
    @checks.is_owner()
    async def _load(self, ctx, module):
        try:
            await self.bot.load_extension(module)
        except Exception as e:
            await ctx.send('{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.message.add_reaction(reactions.THUMBS_UP_REACTION)

    @commands.command(name='purge', hidden=True)
    @checks.is_owner()
    async def _purge(self, ctx):
        # TODO might be good to have a confirmation
        await ctx.channel.purge()

async def setup(bot):
    await bot.add_cog(AdminCog(bot))