import os
import discord
import random

from discord.ext import commands
from dotenv import load_dotenv

initial_extensions =['cogs.Random', 'cogs.ShowPet', 'cogs.fight', 'cogs.shop']

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')
intents = discord.Intents.all()
client = discord.Client(intents=intents)

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

@bot.event
async def on_ready():
    print("Bot Online!")

# remove default help command of the bot
bot.remove_command('help')

# the '!help' command is for the user to see all commands the bot can execute
# aliases is the alternative ways user can type as command to access the help command
@bot.command(pass_context=True, name='help', aliases=['h', 'menu'])
async def help(ctx):
    emoji_list = ['<:fillow:782947475061211137>','<:chicalit:782981070176911411>','<:hedgeroc:782983223768383498>',
             '<:kitsunni:782982459145977916>','<:dianny:782981070102331402>','<:flutterbug:782981069988560897>']
    embed = discord.Embed(colour=discord.Colour.green())
    embed.set_author(name=f'GUPPY Command List')
    embed.set_thumbnail(url='https://i.imgur.com/TitdBes.png')
    embed.add_field(name='Pet Commands', value='Pet commands for GUPPY', inline=False)
    embed.add_field(name=f'{random.choice(emoji_list)} `!adopt`', value=f'Adopt your first pet')
    embed.add_field(name=':restroom: `!team`', value='Check your team\'s stats, feed and play with them')
    embed.add_field(name=':bar_chart: `!stat`, `!st`', value='Check your first pet\'s stats')
    embed.add_field(name=':mens: `!lv`, `!level`, `!lvl`', value='Check your level')
    embed.add_field(name=':dagger: `!adv`, `!adventure`, `!fight`', value='Adventure and fight monsters')
    embed.add_field(name=':meat_on_bone: `!feed`', value='Feed your first pet')
    embed.add_field(name=':tennis: `!play`', value='Play with your first pet')
    embed.add_field(name=':arrows_counterclockwise: `!swap`, `!sw`', value='Swap team order')
    embed.add_field(name=':no_entry_sign: `!remove`, `!rm`', value='Remove a pet')
    embed.add_field(name='Silly Commands', value='Not pet commands for GUPPY', inline=False)
    embed.add_field(name=':rainbow_flag: `!gay`', value='How gay are you?')
    embed.add_field(name=':clown: `!simp`', value='Are you a simp?')
    embed.add_field(name=':rofl: `!vine`', value='Random vine quotes')
    embed.add_field(name=':camera: `!pic`', value='Search for a random image')
    await ctx.send(embed=embed)


@bot.command(pass_context=True, name='welser')
async def welcomeserver(ctx):
    embed = discord.Embed(colour=discord.Colour.teal())
    embed.set_author(name=f'Rules')
    embed.set_thumbnail(url='https://i.imgur.com/m2g78q7.png')
    embed.add_field(name='\u200b', value='Please read all the rules before posting anything', inline=False)
    embed.add_field(name='1. Follow Discord TOS', value=f'Please follow Discord\'s Terms of Services and Guidelines\n'
                                                        f'https://discordapp.com/terms\n'
                                                        f'https://discordapp.com/guidelines', inline=False)
    embed.add_field(name='2. Do not spam', value=f'Do not spam multiple messages, images, or copypastas in this server.\n'
                                                 f'The only exception is when you post it in the <#783182357623472163> channel',
                    inline=False)
    embed.add_field(name='3. No NFSW or Hateful Content', value=f'Do not post any NFSW, hateful content, or otherwise discriminatory in nature',
                    inline=False)
    embed.add_field(name='4. Do not exploit bugs or loopholes', value=f'If found, please report it to <#782920417345404938>',
                    inline=False)
    embed.add_field(name='5. No begging',
                    value=f'Do not beg for gupps, pets, levels, or any other item.',
                    inline=False)
    embed.add_field(name='5. Be respectful',
                    value=f'Treat everyone with respect.',
                    inline=False)
    embed.add_field(name='\u200b',
                    value=f'Breaking any rules will result in a warning. After 3 warnings, you will be temporarily banned from the server. '
                          f'If found to be breaking the rules after the temporary ban, you will be permanently banned from the server',
                    inline=False)
    await ctx.send(embed=embed)

    embed = discord.Embed(colour=discord.Colour.teal())
    embed.set_author(name=f'Welcome!')
    embed.set_thumbnail(url='https://i.imgur.com/TitdBes.png')
    embed.add_field(name='\u200b', value='I am GUPPY, a pet bot and a meme bot all in one!\nFor more information please type `!help` or `!h` for a list of commands.', inline=False)
    embed.add_field(name=':information_source: Help', value=f'If you need help, please post in <#782920417345404938>', inline=False)
    embed.add_field(name=':video_game: Begin Playing', value=f'Begin playing GUPPY by typing `!adopt`!',
                    inline=False)
    embed.add_field(name='<:fillow:782947475061211137> Invite GUPPY to your server!', value=f'https://bit.ly/3qrKqPg',
                    inline=False)
    embed.add_field(name='<:chicalit:782981070176911411> Invite your friends to our server!', value=f'https://discord.gg/jJAJyDkgg2',
                    inline=False)
    await ctx.send(embed=embed)


@bot.command(pass_context=True, name='welcome', aliases=['w', 'wel'])
async def welcome(ctx):
    embed = discord.Embed(colour=discord.Colour.teal())
    embed.set_author(name=f'Welcome!')
    embed.set_thumbnail(url='https://i.imgur.com/TitdBes.png')
    embed.add_field(name='\u200b', value='I am GUPPY, a pet bot and a meme bot all in one!\nFor more information please type `!help` or `!h` for a list of commands.', inline=False)
    embed.add_field(name=':information_source: Help', value=f'If you need help, feel free to join our server below!', inline=False)
    embed.add_field(name=':video_game: Begin Playing', value=f'Begin playing GUPPY by typing `!adopt`!',
                    inline=False)
    embed.add_field(name='<:chicalit:782981070176911411> Join the GUPPY server!', value=f'https://discord.gg/jJAJyDkgg2',
                    inline=False)
    await ctx.send(embed=embed)


bot.run(TOKEN)
