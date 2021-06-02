from discord.ext import commands
import discord

class Shopping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='shop', aliases=['s', 'shopping', 'store', 'sh'])
    async def store(self, ctx):
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_thumbnail(url=
            'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/259/shopping-cart_1f6d2.png')
        embed.set_author(name='GUPPY SHOP')
        embed.add_field(name='1. **GUPPY**', value=str('Price: `100,000` gupps'), inline=False)
        embed.set_footer(text='To buy any goods type `!shop` followed by the name of the product EX: `!shop GUPPY`')
        await ctx.send(embed=embed)
        return


def setup(bot):
    bot.add_cog(Shopping(bot))