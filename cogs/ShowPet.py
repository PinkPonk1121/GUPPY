import discord
from discord.ext import commands
from Database import db as db
import random

intents = discord.Intents.all()
client = discord.Client(intents=intents)

class ShowPet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # this command !team will show all your team members
    @commands.command(name='team')
    async def team(self, ctx):
        # noinspection PyBroadException
        try:
            check = db.record("SELECT UserID, Pet1 FROM userpet WHERE UserID = (?);", ctx.message.author.id)

            if check[1] is None and check[0] is not None:
                await ctx.send("You currently have no pets!\nGet one by typing `!adopt`")
            else:
                embed = discord.Embed(
                    colour=discord.Colour.blue())
                embed.set_thumbnail(url='https://i.imgur.com/zpZTv7a.png')
                embed.set_author(name='Here are your team members!')
                user_pet = db.record("SELECT Pet1, Pet2, Pet3, Pet4, Pet5 FROM userpet WHERE UserID = (?);",
                                     ctx.message.author.id)

                if user_pet[0] is not None:
                    pet1 = db.record("SELECT species, pet_level, ele_type, exp, hunger, fun FROM petstat "
                                     "WHERE PetID = (?);", user_pet[0])
                    embed.add_field(name=f"1. {pet1[0]} | ID: {user_pet[0]} | LV {pet1[1]}",
                                    value=f"Type: {pet1[2]} | EXP: {pet1[3]}/{pet1[1] * 100} "
                                          f"| Hunger: {pet1[4]}/100 | Fun: {pet1[5]}/100",
                                    inline=False)
                if user_pet[1] is not None:
                    pet2 = db.record("SELECT species, pet_level, ele_type, exp, hunger, fun FROM petstat "
                                     "WHERE PetID = (?);", user_pet[1])
                    embed.add_field(name=f"2. {pet2[0]} | ID: {user_pet[1]} | LV {pet2[1]}",
                                    value=f"Type: {pet2[2]} | EXP: {pet2[3]}/{pet2[1] * 100} "
                                          f"| Hunger: {pet2[4]}/100 | Fun: {pet2[5]}/100",
                                    inline=False)
                if user_pet[2] is not None:
                    pet3 = db.record("SELECT species, pet_level, ele_type, exp, hunger, fun FROM petstat "
                                     "WHERE PetID = (?);", user_pet[2])
                    embed.add_field(name=f"3. {pet3[0]} | ID: {user_pet[2]} | LV {pet3[1]}",
                                    value=f"Type: {pet3[2]} | EXP: {pet3[3]}/{pet3[1] * 100} "
                                          f"| Hunger: {pet3[4]}/100 | Fun: {pet3[5]}/100",
                                    inline=False)
                if user_pet[3] is not None:
                    pet4 = db.record("SELECT species, pet_level, ele_type, exp, hunger, fun FROM petstat "
                                     "WHERE PetID = (?);", user_pet[3])
                    embed.add_field(name=f"4. {pet4[0]} | ID: {user_pet[3]} | LV {pet4[1]}",
                                    value=f"Type: {pet4[2]} | EXP: {pet4[3]}/{pet4[1] * 100} "
                                          f"| Hunger: {pet4[4]}/100 | Fun: {pet4[5]}/100",
                                    inline=False)
                if user_pet[4] is not None:
                    pet5 = db.record("SELECT species, pet_level, ele_type, exp, hunger, fun FROM petstat "
                                     "WHERE PetID = (?);", user_pet[4])
                    embed.add_field(name=f"5. {pet5[0]} | ID: {user_pet[4]} | LV {pet5[1]}",
                                    value=f"Type: {pet5[2]} | EXP: {pet5[3]}/{pet5[1] * 100} "
                                          f"| Hunger: {pet5[4]}/100 | Fun: {pet5[5]}/100",
                                    inline=False)

                embed.set_footer(
                    text='Please choose the pet to show stats by select the following emojis:  1, 2, 3, 4 or 5 ')
                message = await ctx.send(embed=embed)

                emojis_team = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
                global done
                done = False

                for emoji in emojis_team:
                    await message.add_reaction(emoji)

                while done is False:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60)
                    emoji = reaction.emoji
                    if user.id == ctx.message.author.id:
                        if emoji == "1️⃣" and pet1:
                            await self.petshow(ctx, user_pet[0])
                            done = True
                        elif emoji == "2️⃣" and pet2:
                            await self.petshow(ctx, user_pet[1])
                            done = True
                        elif emoji == "3️⃣" and pet3:
                            await self.petshow(ctx, user_pet[2])
                            done = True
                        elif emoji == "4️⃣" and pet4:
                            await self.petshow(ctx, user_pet[3])
                            done = True
                        elif emoji == '5️⃣' and pet5:
                            await self.petshow(ctx, user_pet[4])
                            done = True
                        else:
                            return

        except Exception:
            await ctx.send("Please try again.")

    #  this command !stat show stats of your active pet (first pet in the team)
    @commands.command(name='stat', aliases=['st', 'stats'])
    async def stat(self, ctx):
        # noinspection PyBroadException
        try:
            user_pet = db.record("SELECT UserID, Pet1 FROM userpet WHERE UserID = (?);", ctx.message.author.id)
            await self.petshow(ctx, user_pet[1])
        except Exception:
            return await ctx.send("You currently have no pets!\nGet one by typing `!adopt`")

    # shortcut to feed the first pet, you can use '!team' and click the first pet to feed it as well
    @commands.command(name='feed')
    async def feed(self, ctx):
        # noinspection PyBroadException
        try:
            # get hunger of the first pet from database
            check = db.record("SELECT Pet1 FROM userpet WHERE UserID = (?);", ctx.message.author.id)
            p_spe, p_hun = db.record("SELECT species, hunger FROM petstat WHERE PetID = (?)", check[0])

            # check if hunger level is full or not and if the user have pet
            if p_hun < 100 and check[0]:
                hunger = p_hun + random.randint(20, 45)
                if hunger >= 100:
                    hunger = 100
                # update database
                db.execute("UPDATE petstat SET hunger = (?) WHERE PetID = (?)", hunger, check[0])
                db.commit()
                await ctx.send(f"{p_spe} is now {hunger}% full!")

            elif p_hun == 100:
                await ctx.send(f"{p_spe} is full!")

            else:
                await ctx.send('Please try again')
        except Exception:
            return await ctx.send("You currently have no pets!\nGet one by typing `!adopt`")

    # shortcut to play with the first pet, you can use '!team' and click the first pet to play with it as well
    @commands.command(name='play')
    async def play(self, ctx):
        # noinspection PyBroadException
        try:
            # get fun of the first pet from database
            check = db.record("SELECT Pet1 FROM userpet WHERE UserID = (?);", ctx.message.author.id)
            p_spe, p_fun = db.record("SELECT species, fun FROM petstat WHERE PetID = (?)", check[0])

            # check if fun level is full or not and if the user have pet
            if p_fun < 100 and check[0]:
                fun = p_fun + random.randint(20, 45)
                if fun >= 100:
                    fun = 100
                # update database
                db.execute("UPDATE petstat SET fun = (?) WHERE PetID = (?)", fun, check[0])
                db.commit()
                await ctx.send(f"{p_spe} is now {fun}% happy!")

            elif p_fun == 100:
                await ctx.send(f"{p_spe} is very happy!")

            else:
                await ctx.send('Please try again')
        except Exception:
            return await ctx.send("You currently have no pets!\nGet one by typing `!adopt`")

    # this command !lv will show your current level, exp, and your active pet
    @commands.command(name='lv', aliases=['level', 'lvl'])
    async def user_lv_show(self, ctx):

        # noinspection PyBroadException
        try:
            user = ctx.message.author.id
            user_level, user_exp, petid = db.record("SELECT UserLevel, User_exp, Pet1 FROM userpet WHERE UserID = (?)",
                                                    user)
            pet1, petlv = db.record("SELECT species, pet_level FROM petstat WHERE PetID = (?)", petid)
            percent_exp = round((user_exp / (user_level * 100)) * 10)
            rem_exp = 10 - percent_exp

            embed = discord.Embed(colour=discord.Colour.gold())
            embed.set_thumbnail(url=ctx.message.author.avatar_url)
            embed.set_author(name=f'{ctx.message.author.display_name}\'s Profile')
            embed.add_field(name='Level', value=f"{user_level}")
            embed.add_field(name='Active Pet', value=f"**{pet1}** | LV: {petlv}")
            embed.add_field(name='EXP', value=f"{user_exp}/{user_level * 100}\n{'▮' * percent_exp}{'▯' * rem_exp}",
                            inline=False)
            await ctx.send(embed=embed)

        except Exception:
            await ctx.send(f"You have to adopt your first pet first by typing `!adopt`")


    # This function is to show all of pet information when called by '!team'
    async def petshow(self, ctx, id=None):
        stats = db.record(
            "SELECT species, hp, atk, defend, speed, mana, ele_type, pet_level, tier, exp, hunger, fun,"
            " skill1, skill1_mana, skill2, skill2_mana, pic FROM petstat WHERE PetID = (?)", id)

        # show pet as embed message
        embed = discord.Embed(
            colour=discord.Colour.green())
        embed.set_thumbnail(url=stats[16])
        embed.set_author(name="Stats - " + str(id) + " (" + str(stats[0]) + ")  LV." + str(stats[7]))
        embed.add_field(name='Type  ', value=str(stats[6]), inline=True)
        embed.add_field(name='HP  ', value=str(stats[1]) + '/' + str(stats[1]), inline=True)
        embed.add_field(name='Mana  ', value=str(stats[5]) + '/' + str(stats[5]), inline=True)

        embed.add_field(name='Attack  ', value=str(stats[2]), inline=True)
        embed.add_field(name='Defense  ', value=str(stats[3]), inline=True)
        embed.add_field(name='Speed  ', value=str(stats[4]), inline=True)

        embed.add_field(name='-------------------', value=':crossed_swords: **Skills**', inline=False)
        embed.add_field(name=str(stats[12]), value=str(stats[13]) + " Mana", inline=True)
        embed.add_field(name=str(stats[14]), value=str(stats[15]) + " Mana", inline=True)
        embed.add_field(name='-------------------', value=':meat_on_bone: **States**', inline=False)
        embed.add_field(name='Tier  ', value=str(stats[8]), inline=True)
        embed.add_field(name='Exp  ', value=str(stats[9]) + "/" + str(stats[7] * 100), inline=True)
        embed.add_field(name='Hunger ', value=str(stats[10]) + '/' + str(100), inline=True)
        embed.add_field(name='Fun  ', value=str(stats[11]) + '/' + str(100), inline=True)
        embed.set_footer(text='Please select an action!')
        action_message = await ctx.send(embed=embed)

        # add emoji feed and play
        emoji_action = ['🍖', '🎾']
        global action_done
        action_done = False

        for action_emoji in emoji_action:
            await action_message.add_reaction(action_emoji)

        while action_done is False:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60)
            action_emoji = reaction.emoji

            if user.id == ctx.message.author.id:
                # player choose to feed the pet
                if action_emoji == '🍖':
                    await self.feed(ctx)
                    action_done = True

                # player choose to play with the pet
                elif action_emoji == '🎾':
                    await self.play(ctx)
                    action_done = True
                else:
                    return


def setup(bot):
    bot.add_cog(ShowPet(bot))
