from discord.ext import commands
from imgurpython import ImgurClient
import random
import os
from discord.utils import find

imgur_id = os.getenv('IMGUR_ID')
img_key = os.getenv('IMGUR_KEY')
imgur = ImgurClient(imgur_id, img_key)

class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='gay')
    async def gay(self, ctx):
        chance = random.randint(0, 100)
        response = f'🏳️‍🌈 🏳️‍🌈 {ctx.message.author.display_name} is {chance}% gay 🏳️‍🌈 🏳️‍🌈!'
        if chance == 69:
            response = f'🏳️‍🌈 🏳️‍🌈 {ctx.message.author.display_name} is {chance}% gay 🏳️‍🌈 🏳️‍🌈!' \
                       f'\n( ͡° ͜ʖ ͡°) Nice ( ͡° ͜ʖ ͡°)'
        elif chance == 100:
            response = f'🏳️‍🌈 🏳️‍🌈 {ctx.message.author.display_name} is {chance}% gay 🏳️‍🌈 🏳️‍🌈!' \
                       f'\n:tada::confetti_ball: Congrats! :confetti_ball::tada:'
        elif chance == 0:
            response = f'🏳️‍🌈 🏳️‍🌈 {ctx.message.author.display_name} is {chance}% gay 🏳️‍🌈 🏳️‍🌈!' \
                       f'\n:pensive: Homophobia strikes again :pensive:'
        await ctx.send(response)

    @commands.command(name='simp')
    async def simp(self, ctx):
        chance = random.randint(0, 100)
        response = f':clown: {ctx.message.author.display_name} is {chance}% simp! :clown:'
        if chance == 69:
            response = f':clown: {ctx.message.author.display_name} is {chance}% simp! :clown:\n( ͡° ͜ʖ ͡°) Nice ( ͡° ͜ʖ ͡°)'
        elif chance == 100:
            response = f':clown: {ctx.message.author.display_name} is {chance}% simp! :clown:' \
                       f'\n:pensive::sweat_drops: I\'m sorry, but you\re a huge simp. :sweat_drops::pensive:'
        elif chance == 0:
            response = f':clown: {ctx.message.author.display_name} is {chance}% simp! :clown:' \
                       f'\n:ok_hand: That\'s good :ok_hand:'
        await ctx.send(response)

    @commands.command(name='vine')
    async def nine_nine(self, ctx):
        vine_quotes = [
            'YEET',
            'You not my dad!\nYou always wanna hear something!\nUgly ass fucking.',
            'i so pale',
            'BITCH I HOPE THE FUCK YOU DO!',
            'Road work ahead?\nUh yeah, I sure hope it does!',
            'It is Wednesday my dudes.\naaaaaaAAAAAAAAA',
            'We all die we either kill ourselves or get killed.',
            'DON\'T FUCK WITH ME. I GOT THE POWER OF GOD AND ANIME ON MY SIDE!\nAAAAAAAAAAAA'
        ]

        response = random.choice(vine_quotes)
        await ctx.send(response)

    @commands.command(name='pic', pass_context=True, aliases=['picture', 'image', 'img', 'pics', 'images'])
    async def picture(self, ctx, *text: str):
        rand = random.randint(0, 29)
        if text == ():
            await ctx.send('**Please enter a search term**')
        elif text[0] != ():
            items = imgur.gallery_search(" ".join(text[0:len(text)]), advanced=None, sort='viral', window='all', page=0)
            await ctx.send(items[rand].link)

    @commands.Cog.listener()
    async def on_message(self, message):
        if 'hbd' in message.content.lower():
            await message.channel.send('Happy Birthday! 🎈🎉')
        elif 'tableflip' in message.content.lower():
            await message.channel.send('(╯°□°）╯︵ ┻━┻')
        elif 'unflip' in message.content.lower():
            await message.channel.send('┬─┬ ノ( ゜-゜ノ)')
        elif ('pog' or 'poggers' or 'pogchamp') in message.content.lower():
            await message.channel.send('https://i.imgur.com/GSnu7jF.png')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        general = find(lambda x: x.name == 'general', guild.text_channels)
        if general and general.permissions_for(guild.me).send_messages:
            await general.send('Hello {}!'.format(guild.name))

def setup(bot):
    bot.add_cog(Random(bot))