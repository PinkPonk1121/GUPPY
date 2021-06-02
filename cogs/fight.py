import discord
from discord.ext import commands
from Database import db as db
import random
import asyncio

intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Initiate current pet ID to prevent the repetition of pe ID
global ID
out = db.record("SELECT * FROM petstat ORDER BY PetID DESC LIMIT 1;")
if out is None:
    ID = 0
else:
    ID = int(out[0]) + 1
playing = []

class ClassName(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # adding data to our data base, specifically when generating new pet
    def add_db(self, ID, species, hp, atk, defend, spd, mana, ele_type, lv, tier, exp, hunger, fun, skill1, skill1_mana, pic):
        db.execute("INSERT INTO petstat (PetID, species, hp, atk, defend, speed, mana, ele_type, pet_level, tier, exp,"
                   "hunger, fun, skill1, skill1_mana, pic) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                   ID, species, hp, atk, defend, spd, mana, ele_type, lv, tier, exp, hunger, fun, skill1, skill1_mana,
                   pic)
        db.commit()

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
        await ctx.send(embed=embed)


    # This function will increase pet stats when they level up
    async def level_up(self, ID):
        from random import randint
        hp, mana, atk, defend, speed = db.record("SELECT hp, mana, atk, defend, speed FROM petstat WHERE PetID = (?)",
                                                 ID)
        hp += 5
        mana += 5
        atk += randint(2, 4)
        defend += randint(2, 4)
        speed += randint(2, 4)
        db.execute("UPDATE petstat SET hp = (?), mana = (?), atk = (?), defend = (?), speed = (?) WHERE PetID = (?);",
                   hp, mana, atk, defend, speed, ID)
        db.commit()

    # When the pet reach a certain level(10,20) they will evolve to the stronger form using this function
    async def evolve(self, ctx, ID):
        species, pic1 = db.record("SELECT species, pic FROM petstat WHERE PetID = (?)", ID)
        species_next = db.record("SELECT nextevo FROM petlist WHERE species = (?)", species)
        hp1, mana1, atk1, defend1, speed1 = db.record(
            "SELECT hp, mana, atk, defend, speed FROM petstat WHERE PetID = (?)",
            ID)
        hp2, mana2, atk2, defend2, speed2, pic = db.record("SELECT hp, mana, atk, defend, speed, "
                                                           "pic FROM petlist WHERE species = (?)", species_next[0])
        hp = hp1 + hp2
        mana = mana1 + mana2
        atk = atk1 + atk2
        defend = defend1 + defend2
        speed = speed1 + speed2

        embed = discord.Embed(colour=discord.Colour.magenta())
        embed.set_thumbnail(url=pic)
        embed.set_author(name=f'{species} evolved!')
        embed.add_field(name=' \u200b', value=f"{species} has evolved into {species_next[0]}!")
        await ctx.send(embed=embed)

        db.execute(
            "UPDATE petstat SET species = (?), pic = (?), hp = (?), mana = (?), atk = (?), defend = (?), speed = (?)"
            " WHERE PetID = (?);", species_next[0], pic, hp, mana, atk, defend, speed, ID)
        db.commit()

    # this function will be called after every increasing of the exp to check if the pet is level up (up to 30)
    # if the pet reach certain exp (LV*100) it will be level up and if it reach lv 5,10,15,20 it will get new skills
    # if they reach lv 10 or 20 they will evolve into a stronger form
    async def check_level_up(self, ctx, ID):
        exp, level, ele_type, pet_img, pet_spe = db.record(
            "SELECT exp, pet_level, ele_type, pic, species FROM petstat WHERE PetID = (?)", ID)
        if exp >= level * 100 and level < 30:
            exp = exp - (level * 100)
            level += 1
            await self.level_up(ID)
            level_skill = (5, 10, 15, 20)

            embed = discord.Embed(colour=discord.Colour.gold())
            embed.set_thumbnail(url=pet_img)
            embed.set_author(name='Level Up!')
            embed.add_field(name=' \u200b', value=f"{pet_spe} has leveled up!\nLevel {level - 1} --> {level}")
            await ctx.send(embed=embed)

            # evolve
            if (level == 10 or level == 20) and pet_spe != "GUPPY":
                tier, nothing = db.record("SELECT tier, hunger FROM petstat WHERE PetID = (?)", ID)
                tier += 1
                hunger, fun = 100, 100
                db.execute("UPDATE petstat SET tier = (?), hunger = (?), fun = (?) WHERE PetID = (?);", tier, hunger,
                           fun, ID)
                db.commit()
                await self.evolve(ctx, ID)

            # get new skill
            if level in level_skill:
                await self.add_skill(ctx, level, ID, ele_type)
            db.execute("UPDATE petstat SET exp = (?), pet_level = (?) WHERE PetID = (?);", exp, level, ID)
            db.commit()


    # this function will be called after every increasing exp of the user.
    # if the player reach (LV*100) they will be level up (up to lv5)
    # After each level up, they can adopt one more pet (max 5)
    async def user_level_check(self, ctx, User_ID):
        user_level, user_exp = db.record("SELECT UserLevel, User_exp FROM userpet WHERE UserID = (?)", User_ID)
        if user_exp >= user_level * 100 and user_level < 5:
            exp = user_exp - (user_level * 100)
            user_level += 1
            await self.adopt_more(ctx, User_ID, user_level)
            db.execute("UPDATE userpet SET User_exp = (?), UserLevel = (?) WHERE UserID = (?);", exp, user_level,
                       User_ID)
            db.commit()

            embed = discord.Embed(colour=discord.Colour.gold())
            embed.set_thumbnail(url=ctx.message.author.avatar_url)
            embed.set_author(name='Level Up!')
            embed.add_field(name=' \u200b',
                            value=f"{ctx.message.author.display_name} has leveled up!\n"
                                  f"Level {user_level - 1} --> {user_level}")
            await ctx.send(embed=embed)

    # when pet reached level 5, 10, 15, 20 they will get new skill by calling this function
    async def add_skill(self, ctx, lv, ID, ele_type):
        choice = db.record("SELECT skill, skill_mana FROM skill_list WHERE ele_type = (?) AND level = (?)",
                           ele_type, lv)
        existed = db.record(
            "SELECT skill1, skill1_mana, skill2, skill2_mana, species, pic FROM petstat WHERE PetID = (?)",
            ID)
        # if skill2 slot is empty, skill will be automatically added.
        if existed[2] is None:
            db.execute("UPDATE petstat SET skill2 = (?), skill2_mana = (?) WHERE PetID = (?);", choice[0], choice[1],
                       ID)
            db.commit()

            embed = discord.Embed(colour=discord.Colour.dark_purple())
            embed.set_thumbnail(url=existed[5])
            embed.set_author(name='New Skill!')
            embed.add_field(name=' \u200b', value=f":magic_wand: {existed[4]} has learned {choice[0]} :magic_wand:")
            return await ctx.send(embed=embed)
        else:
            # skill2 slot is occupied
            await self.skill_list(ctx, existed, choice, ID)

    # if both skill1 and skill2 slots of the pet are occupied, this function will be called for the player to replace
    # the existed skill or choose to ignore.
    async def skill_list(self, ctx, existed, choice, ID):
        embed = discord.Embed(
            colour=discord.Colour.green())
        embed.set_thumbnail(url='https://i.imgur.com/oGnVbWc.png')
        embed.set_author(name='**Your current skills**')

        embed.add_field(name=existed[0], value=f"{existed[1]} Mana", inline=True)
        embed.add_field(name=existed[2], value=f"{existed[3]} Mana", inline=True)
        embed.add_field(name='-------------------', value=':crossed_swords: **New skill**', inline=False)
        embed.add_field(name=str(choice[0]), value=str(choice[1]) + " Mana", inline=False)
        embed.set_footer(
            text=f'Choose 1️⃣ to replace {existed[0]}, choose 2️⃣ to replace {existed[1]}, choose 🚫 to ignore')
        message = await ctx.send(embed=embed)

        emojis_skill = ['1️⃣', '2️⃣', '🚫']
        global skill_adding
        skill_adding = False

        # add emojis to the message
        for emoji in emojis_skill:
            await message.add_reaction(emoji)

        # selecting the skill
        while skill_adding is False:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60)
            emoji = reaction.emoji
            if user.id == ctx.message.author.id:
                if emoji == "1️⃣":
                    db.execute("UPDATE petstat SET skill1 = (?), skill1_mana = (?) WHERE PetID = (?);",
                               choice[0], choice[1], ID)
                    db.commit()
                    await ctx.send(f":magic_wand: {choice[0]} replaced {existed[4]}\'s {existed[0]} :magic_wand:")
                    skill_adding = True
                elif emoji == "2️⃣":
                    db.execute("UPDATE petstat SET skill2 = (?), skill2_mana = (?) WHERE PetID = (?);",
                               choice[0], choice[1], ID)
                    db.commit()
                    await ctx.send(f":magic_wand: {choice[0]} replaced {existed[4]}\'s {existed[2]} :magic_wand:")
                    skill_adding = True
                elif emoji == "🚫":
                    await ctx.send(f":magic_wand: {existed[4]} did not learn a new skill :magic_wand:")
                    skill_adding = True

                else:
                    return

    # this function will be called when the player level up, they can adopt more pet! (6 pets to be selected)
    async def adopt_more(self, ctx, user_id, user_lv):
        embed = discord.Embed(colour=discord.Colour.orange())
        embed.set_image(url='https://imgur.com/SS7rD0s.png')
        embed.set_author(name='LEVEL UP! You can now adopt another pet!')
        embed.add_field(name='1. Hedgeroc - Earth:seedling: ', value='\u200b', inline=False)
        embed.add_field(name='2. Fillow - Water:droplet:', value='\u200b', inline=False)
        embed.add_field(name='3. Flutterbug - Wind:cloud_tornado:', value='\u200b', inline=False)
        embed.add_field(name='4. Chicalit - Fire:flame:', value='\u200b', inline=False)
        embed.add_field(name='5. Dianny - Dark:crescent_moon:', value='\u200b', inline=False)
        embed.add_field(name='6. Kitsunni - Light:sunny:', value='\u200b', inline=False)
        embed.set_footer(text='Please choose your pet by select the following emojis:  1, 2, 3, 4, 5 or 6')
        message = await ctx.send(embed=embed)

        pet_order = ["Pet2", "Pet3", "Pet4", "Pet5"]
        emojis_adopt_more = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣']
        global adopt_more
        adopt_more = False

        for emoji in emojis_adopt_more:
            await message.add_reaction(emoji)

        while adopt_more is False:
            reaction, user = await self.bot.wait_for('reaction_add')
            emoji = reaction.emoji
            if user.id == ctx.message.author.id:
                if emoji == "1️⃣":
                    pet = await self.generate_pet(1)
                    db.execute(f"UPDATE userpet SET {pet_order[user_lv - 2]} = (?) WHERE UserID = (?);", pet, user_id)
                    db.commit()
                    await self.petshow(ctx, pet)
                    adopt_more = True
                elif emoji == "2️⃣":
                    pet = await self.generate_pet(2)
                    db.execute(f"UPDATE userpet SET {pet_order[user_lv - 2]} = (?) WHERE UserID = (?);", pet, user_id)
                    db.commit()
                    await self.petshow(ctx, pet)
                    adopt_more = True
                elif emoji == "3️⃣":
                    pet = await self.generate_pet(3)
                    db.execute(f"UPDATE userpet SET {pet_order[user_lv - 2]} = (?) WHERE UserID = (?);", pet, user_id)
                    db.commit()
                    await self.petshow(ctx, pet)
                    adopt_more = True
                elif emoji == "4️⃣":
                    pet = await self.generate_pet(4)
                    db.execute(f"UPDATE userpet SET {pet_order[user_lv - 2]} = (?) WHERE UserID = (?);", pet, user_id)
                    db.commit()
                    await self.petshow(ctx, pet)
                    adopt_more = True
                elif emoji == "5️⃣":
                    pet = await self.generate_pet(5)
                    db.execute(f"UPDATE userpet SET {pet_order[user_lv - 2]} = (?) WHERE UserID = (?);", pet, user_id)
                    db.commit()
                    await self.petshow(ctx, pet)
                    adopt_more = True
                elif emoji == "6️⃣":
                    pet = await self.generate_pet(6)
                    db.execute(f"UPDATE userpet SET {pet_order[user_lv - 2]} = (?) WHERE UserID = (?);", pet, user_id)
                    db.commit()
                    await self.petshow(ctx, pet)
                    adopt_more = True
                else:
                    return




    # this function is created to generate pet, after adopted by the user
    async def generate_pet(self, selected):
        global ID
        if type(selected) is not int or selected <= 0:
            return
        elif selected == 1:
            species, hp, atk, defend, speed, mana, ele_type, pics = db.record(
                "SELECT species, hp, atk, defend, speed, mana, ele_type, pic FROM petlist WHERE species = (?);",
                "Hedgeroc")
            self.add_db(ID, species, hp, atk, defend, speed, mana, ele_type, 1, 1, 0, 50, 50, 'Rocky Roll', 3, pics)
        elif selected == 2:
            species, hp, atk, defend, speed, mana, ele_type, pics = db.record(
                "SELECT species, hp, atk, defend, speed, mana, ele_type, pic FROM petlist WHERE species = ?",
                "Fillow")
            self.add_db(ID, species, hp, atk, defend, speed, mana, ele_type, 1, 1, 0, 50, 50, 'Bubble bounce', 5, pics)
        elif selected == 3:
            species, hp, atk, defend, speed, mana, ele_type, pics = db.record(
                "SELECT species, hp, atk, defend, speed, mana, ele_type, pic FROM petlist WHERE species = ?",
                "Flutterbug")
            self.add_db(ID, species, hp, atk, defend, speed, mana, ele_type, 1, 1, 0, 50, 50, "Windy wave", 6, pics)
        elif selected == 4:
            species, hp, atk, defend, speed, mana, ele_type, pics = db.record(
                "SELECT species, hp, atk, defend, speed, mana, ele_type, pic FROM petlist WHERE species = ?",
                "Chicalit")
            self.add_db(ID, species, hp, atk, defend, speed, mana, ele_type, 1, 1, 0, 50, 50, 'Flare kick', 4, pics)
        elif selected == 5:
            species, hp, atk, defend, speed, mana, ele_type, pics = db.record(
                "SELECT species, hp, atk, defend, speed, mana, ele_type, pic FROM petlist WHERE species = ?",
                "Dianny")
            self.add_db(ID, species, hp, atk, defend, speed, mana, ele_type, 1, 1, 0, 50, 50, 'Dark kiss', 5, pics)
        elif selected == 6:
            species, hp, atk, defend, speed, mana, ele_type, pics = db.record(
                "SELECT species, hp, atk, defend, speed, mana, ele_type, pic FROM petlist WHERE species = ?",
                "Kitsunni")
            self.add_db(ID, species, hp, atk, defend, speed, mana, ele_type, 1, 1, 0, 50, 50, 'Shining dash', 5, pics)
        ID += 1
        return ID - 1

    # the '!adopt' command is for the first-time user to adopt their first pet.
    @commands.command(name='adopt')
    async def adopt(self, ctx):
        # noinspection PyBroadException
        try:
            # check if the user have already adopted their first pet
            db.execute("INSERT OR IGNORE INTO userpet (UserID) VALUES (?);", ctx.message.author.id)
            db.commit()
            status = db.record("SELECT Pet1 FROM userpet WHERE UserID = (?);", ctx.message.author.id)
            emoji = '<:fillow:782947475061211137>'
            if status[0] is not None:
                await ctx.send(f"You already have a pet!{emoji}")
            else:
                # show list of pet to be adopted
                pet1 = discord.Embed(
                    colour=discord.Colour.orange())
                pet1.set_image(
                    url='https://i.imgur.com/RnUaQI3.png')
                pet1.set_author(name='Choose your first pet!')
                pet1.add_field(name='1. Hedgeroc - Earth:seedling: ', value='\u200b', inline=False)
                pet1.add_field(name='2. Fillow - Water:droplet:', value='\u200b', inline=False)
                pet1.add_field(name='3. Flutterbug - Wind:cloud_tornado:', value='\u200b', inline=False)
                pet1.add_field(name='4. Chicalit - Fire:flame:', value='\u200b', inline=False)
                pet1.set_footer(text='Please choose your pet by select the following emojis:  1, 2, 3, or 4\n '
                                     'YOU CAN ONLY ADOPT YOUR FIRST PET ONCE!')
                message = await ctx.send(embed=pet1)

                emojis_adopt = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
                global Past
                Past = False

                # add emoji to the message
                for emoji in emojis_adopt:
                    await message.add_reaction(emoji)

                # take the emoji input from user to generate the specific pet.
                while Past is False:
                    reaction, user = await self.bot.wait_for('reaction_add')
                    emoji = reaction.emoji
                    if user.id == ctx.message.author.id:
                        # to prevent other user from selecting emoji and you can only pick once
                        if emoji == "1️⃣":
                            pet = await self.generate_pet(1)
                            db.execute("UPDATE userpet SET Pet1 = (?) WHERE UserID = (?);", pet,
                                       ctx.message.author.id)
                            db.commit()
                            await self.petshow(ctx, pet)
                            Past = True
                        elif emoji == "2️⃣":
                            pet = await self.generate_pet(2)
                            db.execute("UPDATE userpet SET Pet1 = (?) WHERE UserID = (?);", pet,
                                       ctx.message.author.id)
                            db.commit()
                            await self.petshow(ctx, pet)
                            Past = True
                        elif emoji == "3️⃣":
                            pet = await self.generate_pet(3)
                            db.execute("UPDATE userpet SET Pet1 = (?) WHERE UserID = (?);", pet,
                                       ctx.message.author.id)
                            db.commit()
                            await self.petshow(ctx, pet)
                            Past = True
                        elif emoji == "4️⃣":
                            pet = await self.generate_pet(4)
                            db.execute("UPDATE userpet SET Pet1 = (?) WHERE UserID = (?);", pet,
                                       ctx.message.author.id)
                            db.commit()
                            await self.petshow(ctx, pet)
                            Past = True
                        else:
                            return

        except Exception:
            await ctx.send("You have already adopted your first pet!")

    # This command !adv will initiate the fight by randoming your opponent according to your current pet level.
    @commands.command(name='adv', aliases=['adventure', 'fight'])
    @commands.cooldown(15, 600, commands.BucketType.user)
    async def adventure(self, ctx):
        # noinspection PyBroadException
        try:
            player = ctx.message.author

            # check if the player have already adopt their first pet
            check = db.record("SELECT Pet1 FROM userpet WHERE UserID = (?);", ctx.message.author.id)
            if check[0] is None:
                return await ctx.send("You currently have no pets!\nGet one by typing `!adopt`")

            # check if the active pet have hunger and fun above 25%, if not they cannot fight
            check_fun = db.record("SELECT hunger, fun FROM petstat WHERE PetID = (?);", check[0])
            if check_fun[0] < 25 or check_fun[1] < 25:
                return await ctx.send(f"Your pet is not happy, try to feed or play with them!\nYour pet cannot enter"
                                      f" fights if their hunger or fun is below 25\n(Current **Hunger** = *{check_fun[0]}* "
                                      f"| Current **Fun** = *{check_fun[1]}*)")

            # create chance system depend on the level of the pet
            c_pet = db.record('SELECT pet_level FROM petstat WHERE PetID = (?)', check[0])

            if c_pet[0] <= 5:
                chance = (c_pet[0] * random.randint(1, 8)) + random.randint(-3, 11)  # Range (-3, 51)
            elif c_pet[0] <= 10:
                chance = (c_pet[0] * random.randint(3, 5)) + random.randint(-5, 11)  # Range (13, 61)
            elif c_pet[0] <= 15:
                chance = (c_pet[0] * random.randint(4, 5)) + random.randint(-5, 10)  # Range (39, 85)
            elif c_pet[0] <= 20:
                chance = (c_pet[0] * random.randint(4, 5)) + random.randint(-5, 10)  # Range (59, 110)
            else:
                chance = (c_pet[0] * random.randint(4, 5)) + random.randint(-40, 20)  # Range (44, 100+)

            if chance <= 20:
                found_monster = "Snaily"
            elif chance <= 45:
                found_monster = "Vamphart"
            elif chance <= 65:
                found_monster = "Philodon"
            elif chance <= 95:
                found_monster = "Pozzumbie"
            else:
                found_monster = "Toxicobra"

            # prevent player from using !adv while in the fight
            if player not in playing:
                playing.append(player)
            else:
                return await ctx.send('You are adventuring!')

            # there is lower than 10% chance that you will not find any monster
            if (chance % 11) == 0:
                playing.remove(ctx.message.author)
                return await ctx.send("No monsters found!")
            else:
                temp_mon = db.record(
                    'SELECT species, hp, atk, defend, speed, mana, pet_level, skill1, skill1_mana, skill2,'
                    ' skill2_mana, pic FROM monster WHERE species = (?)', found_monster)
                temp_pet = db.record(
                    'SELECT species, hp, atk, defend, speed, mana, pet_level, skill1, skill1_mana, skill2,'
                    ' skill2_mana, pic FROM petstat WHERE PetID = (?)', check[0])

                # show our active pet and found monster
                await self.fight_mon_show(ctx, temp_mon[11], temp_mon[0], temp_mon[6], temp_mon[1], temp_mon[5],
                                     found_monster)
                await self.fight_pet_show(ctx, temp_pet[11], temp_pet[0], temp_pet[6], temp_pet[1], temp_pet[5], temp_pet[7],
                                     temp_pet[8], temp_pet[9], temp_pet[10], check[0])

                # call fight function
                await self.fight(ctx, found_monster, check[0])

        except Exception:
            return await ctx.send("You currently have no pets!\nGet one by typing `!adopt`")
        
    # function to calculate when we attack or using skill and the monster attack back
    async def atk_atk(self, ctx, check, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1, p_skill1_mana,
                      p_skill2,p_skill2_mana, m_atk, p_defend, m_species, m_hp, m_mana):
        if m_atk >= p_defend:
            dmg = m_atk - p_defend // 2 + random.randint(1, 3)
            p_hp -= dmg
        else:
            dmg = p_defend // m_atk + random.randint(1, 3)
            p_hp -= dmg
        await ctx.send(f':boom: **{m_species}** attacked **{p_species}** for *{dmg}* HP!')
        await self.fight_pet_show(ctx, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1,
                                  p_skill1_mana, p_skill2, p_skill2_mana, check)
        return p_hp, m_hp, p_mana, m_mana

    # function to calculate when we attack or using skill and the monster use skill1 back
    async def atk_skill1(self, ctx, check, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1, p_skill1_mana,
                         p_skill2, p_skill2_mana, m_atk, p_defend, m_skill1, m_pet_level, m_mana, m_skill1_mana,
                         m_species, m_hp):

        skill_dmg = db.record('SELECT damage FROM skill_list WHERE skill = (?)', m_skill1)
        temp_dmg = ((m_atk + m_pet_level) // (p_defend + p_pet_level)) + 1
        dmg = (skill_dmg[0] * temp_dmg) + m_pet_level + random.randint(5, 8)
        p_hp -= dmg
        m_mana -= m_skill1_mana
        if m_mana < 0:
            m_mana = 0
        await ctx.send(
            f':crystal_ball: **{m_species}** used **{m_skill1}** on **{p_species}** and dealt *{dmg}* HP!')
        await self.fight_pet_show(ctx, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1,
                                  p_skill1_mana, p_skill2, p_skill2_mana, check)
        return p_hp, m_hp, p_mana, m_mana

    # function to calculate when we attack or using skill and the monster use skill2 back
    async def atk_skill2(self, ctx, check, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1, p_skill1_mana,
                         p_skill2,
                         p_skill2_mana, m_atk, p_defend, m_skill2, m_pet_level, m_mana, m_skill2_mana,
                         m_species, m_hp):
        skill_dmg = db.record('SELECT damage FROM skill_list WHERE skill = (?)', m_skill2)
        temp_dmg = ((m_atk + m_pet_level) // (p_defend + p_pet_level)) + 1
        dmg = (skill_dmg[0] * temp_dmg) + m_pet_level + random.randint(5, 8)
        p_hp -= dmg
        m_mana -= m_skill2_mana
        if m_mana < 0:
            m_mana = 0
        await ctx.send(
            f':crystal_ball: **{m_species}** used **{m_skill2}** on **{p_species}** and dealt *{dmg}* HP!')
        await self.fight_pet_show(ctx, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1,
                                  p_skill1_mana, p_skill2, p_skill2_mana, check)
        return p_hp, m_hp, p_mana, m_mana

    # function to call the sub-functions of attacking
    async def atk(self, ctx, check, op, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1, p_skill1_mana,
                  p_skill2,
                  p_skill2_mana, m_atk, p_defend, m_species, m_skill1, m_pet_level, m_mana, m_skill1_mana,
                  m_skill2, m_skill2_mana, m_hp):
        switcher = {
            "atk": self.atk_atk(ctx, check, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1, p_skill1_mana,
                           p_skill2,
                           p_skill2_mana, m_atk, p_defend, m_species, m_hp, m_mana),
            "skill1": self.atk_skill1(ctx, check, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1,
                                 p_skill1_mana,
                                 p_skill2,
                                 p_skill2_mana, m_atk, p_defend, m_skill1, m_pet_level, m_mana, m_skill1_mana,
                                 m_species, m_hp),
            "skill2": self.atk_skill2(ctx, check, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1,
                                 p_skill1_mana,
                                 p_skill2,
                                 p_skill2_mana, m_atk, p_defend, m_skill2, m_pet_level, m_mana, m_skill2_mana,
                                 m_species, m_hp)
        }
        func = switcher.get(op, lambda: 'Invalid')
        return await func

    # function to calculate when we defend and the monster use attack back
    async def def_atk(self, ctx, check, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1, p_skill1_mana,
                      p_skill2,
                      p_skill2_mana, m_atk, p_defend, m_species, m_pic, m_pet_level, m_hp, m_mana, found_monster):
        if m_atk >= p_defend:
            dmg = ((m_atk // 2) - p_defend) + random.randint(1, 3)
            if dmg <= 0:
                dmg = random.randint(1, 3)
            p_hp -= dmg
        elif m_atk < p_defend:
            dmg = random.randint(1, 3)
            p_hp -= dmg
        await ctx.send(f':shield: **{p_species}** defended itself from **{m_species}**\'s attack!')
        await ctx.send(f':boom: **{m_species}** attack **{p_species}** and dealt *{dmg}* HP!')
        await self.fight_mon_show(ctx, m_pic, m_species, m_pet_level, m_hp, m_mana, found_monster)
        await self.fight_pet_show(ctx, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1,
                                  p_skill1_mana, p_skill2, p_skill2_mana, check)
        return p_hp, m_hp, p_mana, m_mana

    # function to calculate when we defend and the monster use skill1 back
    async def def_skill1(self, ctx, check, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1, p_skill1_mana,
                         p_skill2,
                         p_skill2_mana, m_atk, p_defend, m_skill1, m_pet_level, m_mana, m_skill1_mana,
                         m_species, m_pic, m_hp, found_monster):

        skill_dmg = db.record('SELECT damage FROM skill_list WHERE skill = (?)', m_skill1)
        dmg = (skill_dmg[0] * (m_atk // (p_defend * 2))) + m_pet_level
        p_hp -= dmg
        m_mana -= m_skill1_mana
        if m_mana < 0:
            m_mana = 0
        await ctx.send(
            f':crystal_ball: **{m_species}** used **{m_skill1}** on **{p_species}** and dealt *{dmg}* HP!')
        await self.fight_mon_show(ctx, m_pic, m_species, m_pet_level, m_hp, m_mana, found_monster)
        await self.fight_pet_show(ctx, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1,
                                  p_skill1_mana, p_skill2, p_skill2_mana, check)
        return p_hp, m_hp, p_mana, m_mana

    # function to calculate when we defend and the monster use skill2 back
    async def def_skill2(self, ctx, check, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1, p_skill1_mana,
                         p_skill2,
                         p_skill2_mana, m_atk, p_defend, m_skill2, m_pet_level, m_mana, m_skill2_mana,
                         m_species, m_pic, m_hp, found_monster):

        skill_dmg = db.record('SELECT damage FROM skill_list WHERE skill = (?)', m_skill2)
        dmg = (skill_dmg[0] * (m_atk // (p_defend * 2))) + m_pet_level
        p_hp -= dmg
        m_mana -= m_skill2_mana
        if m_mana < 0:
            m_mana = 0
        await ctx.send(
            f':crystal_ball: **{m_species}** used **{m_skill2}** on **{p_species}** and dealt *{dmg}* HP!')
        await self.fight_mon_show(ctx, m_pic, m_species, m_pet_level, m_hp, m_mana, found_monster)
        await self.fight_pet_show(ctx, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1,
                                  p_skill1_mana, p_skill2, p_skill2_mana, check)
        return p_hp, m_hp, p_mana, m_mana

    # function to call the sub-functions of defending
    async def defending(self, ctx, check, op, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1, p_skill1_mana,
                        p_skill2,
                        p_skill2_mana, m_atk, p_defend, m_species, m_skill1, m_pet_level, m_mana, m_skill1_mana,
                        m_skill2, m_skill2_mana, m_pic, m_hp, found_monster):
        switcher = {
            "atk": self.def_atk(ctx, check, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1, p_skill1_mana,
                           p_skill2,
                           p_skill2_mana, m_atk, p_defend, m_species, m_pic, m_pet_level, m_hp, m_mana, found_monster),
            "skill1": self.def_skill1(ctx, check, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1,
                                 p_skill1_mana,
                                 p_skill2,
                                 p_skill2_mana, m_atk, p_defend, m_skill1, m_pet_level, m_mana, m_skill1_mana,
                                 m_species, m_pic, m_hp, found_monster),
            "skill2": self.def_skill2(ctx, check, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1,
                                 p_skill1_mana,
                                 p_skill2,
                                 p_skill2_mana, m_atk, p_defend, m_skill2, m_pet_level, m_mana, m_skill2_mana,
                                 m_species, m_pic, m_hp, found_monster)
        }
        func = switcher.get(op, lambda: 'Invalid')
        return await func

    # function fight will wait for user in put 1, 2, 3, 4, 5 and will undergo the calculating process
    async def fight(self, ctx, found_monster, check):
        global playing
        fight_done = False

        # to check if the user is the one who type.
        def check_au(message):
            return message.author == ctx.message.author

        # create a temporaly stats in the fight
        p_species, p_hp, p_atk, p_defend, p_mana, p_pet_level, p_skill1, p_skill1_mana, p_skill2, p_skill2_mana, p_pic, \
        get_exp, get_hun, get_fun = db.record('SELECT species, hp, atk, defend, mana, pet_level, skill1, skill1_mana, '
                                              'skill2, skill2_mana, pic, exp, hunger, fun FROM petstat '
                                              'WHERE PetID = (?)', check)
        m_species, m_hp, m_atk, m_defend, m_mana, m_pet_level, m_skill1, m_skill1_mana, m_skill2, m_skill2_mana, m_pic = \
            db.record('SELECT species, hp, atk, defend, mana, pet_level, skill1, skill1_mana, skill2,'
                      ' skill2_mana, pic FROM monster WHERE species = (?)', found_monster)

        get_exp_usr, lvl_usr, money = db.record('SELECT User_exp, UserLevel, money FROM userpet WHERE UserID = (?)',
                                         ctx.message.author.id)



        # fighting algorithm
        while fight_done is False:

            # if our pet or monster ran out of HP, the fight stop
            if m_hp <= 0 or p_hp <= 0:
                if m_hp <= 0:
                    # if we win
                    ran_exp = random.randint(35, 40) * m_pet_level // p_pet_level + 1
                    plus_exp = get_exp + ran_exp
                    money_gained = random.randint(5, 20)
                    money += money_gained
                    de_hun = get_hun - random.randint(1, 10)
                    de_fun = get_fun - 1
                    ran_exp_plus = random.randint(1, 2)
                    plus_exp_usr = get_exp_usr + ran_exp_plus
                    db.execute('UPDATE petstat SET exp = (?), hunger = (?), fun = (?) WHERE PetID = (?)', plus_exp,
                               de_hun, de_fun, check)
                    db.execute('UPDATE userpet SET user_exp = (?), money = (?) WHERE UserID = (?)', plus_exp_usr,
                               money, ctx.message.author.id)
                    db.commit()
                    playing.remove(ctx.message.author)
                    fight_done = True
                    await ctx.send(f':tada: **{ctx.message.author.display_name}**\'s **{p_species}** won the battle!\n'
                                   f'**{p_species}**\'s exp has increase by *{ran_exp}* !'
                                   f' **{p_species}** currently has *{plus_exp}*/*{p_pet_level * 100}* exp.\n'
                                   f'Your exp has increase by *{ran_exp_plus}* !'
                                   f' You currently have *{get_exp_usr + ran_exp_plus}*/*{lvl_usr * 100}* exp.\n'
                                   f'You have also gained **{money_gained} gupps** :coin:')
                    await self.user_level_check(ctx, ctx.message.author.id)
                    await self.check_level_up(ctx, check)

                else:
                    # if we lose
                    plus_exp = get_exp + 5
                    de_hun = get_hun - random.randint(10, 20)
                    de_fun = get_fun - random.randint(10, 20)
                    db.execute('UPDATE petstat SET exp = (?), hunger = (?), fun = (?) WHERE PetID = (?)', plus_exp,
                               de_hun, de_fun, check)
                    db.commit()
                    playing.remove(ctx.message.author)
                    fight_done = True
                    await ctx.send(
                        f':skull_crossbones: **{ctx.message.author.display_name}**\'s **{p_species}** lost the battle!\n '
                        f'Cheer up! **{p_species}** gained 5 exp!'
                        f' **{p_species}** currently has *{plus_exp}*/*{p_pet_level * 100}* exp.')
                    await self.check_level_up(ctx, check)

            else:
                try:
                    message = await self.bot.wait_for('message', timeout=150, check=check_au)

                    if m_mana > 0:
                        # if mana is enough
                        op = random.choice(['atk', 'def', 'skill1', 'skill2'])

                    elif m_mana <= 0 or m_mana - m_skill1_mana < 0 or m_mana - m_skill2_mana < 0:
                        # if mana is not enough for the fight
                        op = random.choice(['atk', 'def'])

                    if '1' == message.content.lower():
                        # we are attacking
                        if op in ('atk', 'skill1', 'skill2'):
                            # player to monster
                            if p_atk >= m_defend:
                                dmg = (p_atk - (m_defend // 2)) + random.randint(-3, 3)
                                m_hp -= dmg
                            else:
                                dmg = (m_defend // p_atk) + random.randint(-3, 3)
                                if dmg <= 0:
                                    dmg = random.randint(1, 3)
                                m_hp -= dmg
                            await ctx.send(f':crossed_swords: **{p_species}** attacked **{m_species}** for *{dmg}* HP!')
                            await self.fight_mon_show(ctx, m_pic, m_species, m_pet_level, m_hp, m_mana, found_monster)

                            # monster to player
                            p_hp, m_hp, p_mana, m_mana = await self.atk(ctx, check, op, p_pic, p_species, p_pet_level, p_hp,
                                                                   p_mana, p_skill1, p_skill1_mana, p_skill2,
                                                                   p_skill2_mana,
                                                                   m_atk, p_defend, m_species, m_skill1, m_pet_level,
                                                                   m_mana, m_skill1_mana, m_skill2, m_skill2_mana, m_hp)

                        else:
                            # monster is defending
                            if p_atk >= m_defend:
                                dmg = ((p_atk // 2) - m_defend) + random.randint(-3, 3)
                                if dmg <= 0:
                                    dmg = random.randint(1, 3)
                                m_hp -= dmg
                            else:
                                dmg = random.randint(1, 3)
                                m_hp -= dmg
                            await ctx.send(f':tongue: **{m_species}** defended from itself **{p_species}**\'s attack!')
                            await ctx.send(
                                f':crossed_swords: **{p_species}** attacked **{m_species}** and dealt *{dmg}* HP!')
                            await self.fight_mon_show(ctx, m_pic, m_species, m_pet_level, m_hp, m_mana, found_monster)
                            await self.fight_pet_show(ctx, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1,
                                                 p_skill1_mana,
                                                 p_skill2, p_skill2_mana, check)

                    elif '2' == message.content.lower():
                        # we are defending

                        # player to monsters
                        await ctx.send(f':shield: **{p_species}** will take less damage in this turn!')
                        if m_mana <= 0:
                            op = random.choice(['atk', 'def'])

                        # monster to player
                        if op in ('atk', 'skill1', 'skill2'):
                            p_hp, m_hp, p_mana, m_mana = await self.defending(ctx, check, op, p_pic, p_species, p_pet_level,
                                                                         p_hp, p_mana, p_skill1, p_skill1_mana,
                                                                         p_skill2,
                                                                         p_skill2_mana, m_atk, p_defend, m_species,
                                                                         m_skill1, m_pet_level, m_mana, m_skill1_mana,
                                                                         m_skill2, m_skill2_mana, m_pic, m_hp, found_monster)
                        else:
                            # monster is defending
                            await ctx.send(f':crystal_ball: **{m_species}** chose to defend as well!')
                            await self.fight_mon_show(ctx, m_pic, m_species, m_pet_level, m_hp, m_mana, found_monster)
                            await self.fight_pet_show(ctx, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1,
                                                 p_skill1_mana,
                                                 p_skill2, p_skill2_mana, check)

                    elif '3' == message.content.lower():
                        # we are using skill1
                        if p_mana <= 0 or p_mana - p_skill1_mana < 0:
                            # if we do not have enough mana
                            await ctx.send(f'**{p_species}** does not have enough mana!')
                            await self.fight_mon_show(ctx, m_pic, m_species, m_pet_level, m_hp, m_mana, found_monster)
                            await self.fight_pet_show(ctx, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1,
                                                 p_skill1_mana,
                                                 p_skill2, p_skill2_mana, check)

                        elif op in ('atk', 'skill1', 'skill2'):
                            # player to monster
                            skill_dmg = db.record('SELECT damage FROM skill_list WHERE skill = (?)', p_skill1)
                            temp_dmg = ((p_atk + p_pet_level) // (m_defend + m_pet_level)) + 1
                            dmg = (skill_dmg[0] * temp_dmg) + p_pet_level + random.randint(5, 8)
                            m_hp -= dmg
                            p_mana -= p_skill1_mana
                            await ctx.send(
                                f':magic_wand: **{p_species}** used **{p_skill1}** on **{m_species}** dealt *{dmg}* HP!')
                            await self.fight_mon_show(ctx, m_pic, m_species, m_pet_level, m_hp, m_mana, found_monster)

                            # mon on player
                            p_hp, m_hp, p_mana, m_mana = await self.atk(ctx, check, op, p_pic, p_species, p_pet_level, p_hp,
                                                                   p_mana, p_skill1, p_skill1_mana, p_skill2,
                                                                   p_skill2_mana,
                                                                   m_atk, p_defend, m_species, m_skill1, m_pet_level,
                                                                   m_mana, m_skill1_mana, m_skill2, m_skill2_mana, m_hp)

                        else:
                            # if monster is defending
                            skill_dmg = db.record('SELECT damage FROM skill_list WHERE skill = (?)', p_skill1)
                            dmg = (skill_dmg[0] * (p_atk // (m_defend * 2))) + p_pet_level
                            m_hp -= dmg
                            p_mana -= p_skill1_mana
                            if p_mana < 0:
                                p_mana = 0
                            await ctx.send(f':tongue: **{m_species}** defended from itself **{p_species}**\'s skill!')
                            await ctx.send(
                                f':crystal_ball: **{p_species}** used **{p_skill1}** on **{m_species}** dealt *{dmg}* HP!')
                            await self.fight_mon_show(ctx, m_pic, m_species, m_pet_level, m_hp, m_mana, found_monster)
                            await self.fight_pet_show(ctx, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1,
                                                 p_skill1_mana,
                                                 p_skill2, p_skill2_mana, check)

                    elif '4' == message.content.lower():
                        # if we are using skill2
                        if p_skill2 is None:
                            await ctx.send(f'**{p_species}** does not have a second skill!')

                        elif p_mana <= 0 or p_mana - p_skill2_mana < 0:
                            await ctx.send(f':weary: **{p_species}** does not have enough mana!')
                            await self.fight_mon_show(ctx, m_pic, m_species, m_pet_level, m_hp, m_mana, found_monster)
                            await self.fight_pet_show(ctx, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1,
                                                 p_skill1_mana,
                                                 p_skill2, p_skill2_mana, check)

                        elif op in ('atk', 'skill1', 'skill2'):
                            # player to monster
                            skill_dmg = db.record('SELECT damage FROM skill_list WHERE skill = (?)', p_skill2)
                            temp_dmg = ((p_atk + p_pet_level) // (m_defend + m_pet_level)) + 1
                            dmg = (skill_dmg[0] * temp_dmg) + p_pet_level + random.randint(5, 8)
                            m_hp -= dmg
                            p_mana -= p_skill2_mana
                            if p_mana < 0:
                                p_mana = 0
                            await ctx.send(
                                f':magic_wand: **{p_species}** used **{p_skill2}** on **{m_species}** dealt *{dmg}* HP!')
                            await self.fight_mon_show(ctx, m_pic, m_species, m_pet_level, m_hp, m_mana, found_monster)

                            # mon on player
                            p_hp, m_hp, p_mana, m_mana = await self.atk(ctx, check, op, p_pic, p_species, p_pet_level, p_hp,
                                                                   p_mana, p_skill1, p_skill1_mana, p_skill2,
                                                                   p_skill2_mana,
                                                                   m_atk, p_defend, m_species, m_skill1, m_pet_level,
                                                                   m_mana, m_skill1_mana, m_skill2, m_skill2_mana, m_hp)

                        else:
                            # if monster is defending
                            skill_dmg = db.record('SELECT damage FROM skill_list WHERE skill = (?)', p_skill2)
                            dmg = (skill_dmg[0] * (p_atk // (m_defend * 2))) + p_pet_level
                            m_hp -= dmg
                            p_mana -= p_skill2_mana
                            if p_mana < 0:
                                p_mana = 0
                            await ctx.send(f':tongue: **{m_species}** defended itself from **{p_species}**\'s skill!')
                            await ctx.send(
                                f':crystal_ball: **{p_species}** used **{p_skill2}** on **{m_species}** dealt *{dmg}* HP!')
                            await self.fight_mon_show(ctx, m_pic, m_species, m_pet_level, m_hp, m_mana, found_monster)
                            await self.fight_pet_show(ctx, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1,
                                                 p_skill1_mana,
                                                 p_skill2, p_skill2_mana, check)

                    elif '5' == message.content.lower():
                        # we choose to run away
                        await ctx.send(f':dash: **{p_species}** ran away!')
                        playing.remove(ctx.message.author)
                        fight_done = True

                except asyncio.TimeoutError:
                    # when the user have not finished their fight in 2 minutes 30 seconds
                    await ctx.send('You took too long!')
                    playing.remove(ctx.message.author)
                    fight_done = True

    # show monster in the fight
    async def fight_mon_show(self, ctx, m_pic, m_species, m_pet_level, m_hp, m_mana, found_monster):
        max_stat = db.record('SELECT hp, mana FROM monster WHERE species = (?)', found_monster)
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_thumbnail(url=m_pic)
        embed.set_author(name=f'{ctx.message.author.display_name}\'s Enemy')
        embed.add_field(name='Name  ', value=str(m_species))
        embed.add_field(name='LV  ', value=str(m_pet_level))
        if m_hp < 0:
            m_hp = 0
        embed.add_field(name='HP  ', value=f'{m_hp}/{max_stat[0]}', inline=True)
        embed.add_field(name='Mana  ', value=f'{m_mana}/{max_stat[1]}', inline=True)
        embed.set_footer(text='Type 1 to attack, 2 to  defend, 3 to use skill 1, 4 to use skill 2, 5 to run')
        await ctx.send(embed=embed)

    # show pet in the fight
    async def fight_pet_show(self, ctx, p_pic, p_species, p_pet_level, p_hp, p_mana, p_skill1, p_skill1_mana, p_skill2,
                             p_skill2_mana, check):
        max_stat = db.record('SELECT hp, mana FROM petstat WHERE PetID = (?)', check)
        embed = discord.Embed(colour=discord.Colour.green())
        embed.set_thumbnail(url=p_pic)
        embed.set_author(name=f'{ctx.message.author.display_name}\'s pet stat!')
        embed.add_field(name='Name  ', value=str(p_species))
        embed.add_field(name='LV  ', value=str(p_pet_level))
        if p_hp < 0:
            p_hp = 0
        embed.add_field(name='HP  ', value=f'{p_hp}/{max_stat[0]}', inline=True)
        embed.add_field(name='Mana  ', value=f'{p_mana}/{max_stat[1]}', inline=True)
        embed.add_field(name='-------------------', value=':crossed_swords: **Skills**', inline=False)
        embed.add_field(name=str(p_skill1), value=f'{p_skill1_mana} Mana', inline=True)
        embed.add_field(name=str(p_skill2), value=f'{p_skill2_mana} Mana', inline=True)
        embed.set_footer(text='Type 1 to attack, 2 to  defend, 3 to use skill 1, 4 to use skill 2, 5 to run')
        await ctx.send(embed=embed)

    # to prevent player from spamming adventure, they can only using !adv command 15 times per 10 mins
    @adventure.error
    async def adv_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"Your pet is tired, please try again in {int(error.retry_after) // 60} mins"
                f" {int(error.retry_after) % 60} secs\n")
        else:
            raise error

    # same function as pet_show but shorter, called by '!remove' and '!swap'
    async def petshow_short(self, ctx):
        pet1, pet2, pet3, pet4, pet5 = None, None, None, None, None
        pet_1 = discord.Embed(
            colour=discord.Colour.blue())
        pet_1.set_thumbnail(url='https://i.imgur.com/zpZTv7a.png')
        pet_1.set_author(name='Here are your team members!')
        user_pet = db.record("SELECT Pet1, Pet2, Pet3, Pet4, Pet5 FROM userpet WHERE UserID = (?);",
                             ctx.message.author.id)
        if user_pet[1] is None and user_pet[0] is not None:
            return await ctx.send("This is your only pet!"), pet1, pet2, pet3, pet4, pet5
        if user_pet[0] is None:
            return await ctx.send(
                "You currently have no pets!\nGet one by typing `!adopt`"), pet1, pet2, pet3, pet4, pet5
        if user_pet[0] is not None:
            pet1 = db.record("SELECT species, pet_level, ele_type FROM petstat WHERE PetID = (?);", user_pet[0])
            pet_1.add_field(name=f"1. {pet1[0]} | ID: {user_pet[0]}",
                            value=f"LV: {pet1[1]} | Type: {pet1[2]}", inline=True)
        if user_pet[1] is not None:
            pet2 = db.record("SELECT species, pet_level, ele_type FROM petstat WHERE PetID = (?);", user_pet[1])
            pet_1.add_field(name=f"2. {pet2[0]} | ID: {user_pet[1]}",
                            value=f"LV: {pet2[1]} | Type: {pet2[2]}", inline=True)
        if user_pet[2] is not None:
            pet3 = db.record("SELECT species, pet_level, ele_type FROM petstat WHERE PetID = (?);", user_pet[2])
            pet_1.add_field(name=f"3. {pet3[0]} | ID: {user_pet[2]}",
                            value=f"LV: {pet3[1]} | Type: {pet3[2]}", inline=True)
        if user_pet[3] is not None:
            pet4 = db.record("SELECT species, pet_level, ele_type FROM petstat WHERE PetID = (?);", user_pet[3])
            pet_1.add_field(name=f"4. {pet4[0]} | ID: {user_pet[3]}",
                            value=f"LV: {pet4[1]} | Type: {pet4[2]}", inline=True)
        if user_pet[4] is not None:
            pet5 = db.record("SELECT species, pet_level, ele_type FROM petstat WHERE PetID = (?);", user_pet[4])
            pet_1.add_field(name=f"5. {pet5[0]} | ID: {user_pet[4]}",
                            value=f"LV: {pet5[1]} | Type: {pet5[2]}", inline=True)

        pet_1.set_footer(
            text='Please choose the pet to remove by select the following emojis: 1, 2, 3, 4 or 5 ')
        return await ctx.send(embed=pet_1), pet1, pet2, pet3, pet4, pet5

    # swapping position of other pet with the first pet
    @commands.command(name='swap', aliases=['sw'])
    async def swap(self, ctx):
        # noinspection PyBroadException
        try:
            if ctx.message.author in playing:
                return await ctx.send("You are in the middle of the fight :rage::rage::rage:")

            check = db.record("SELECT UserID FROM userpet WHERE UserID = (?);", ctx.message.author.id)
            if check[0] is None:
                db.execute("INSERT INTO userpet (UserID) VALUES (?);", ctx.message.author.id)
                db.commit()
                await ctx.send("You currently have no pets!")
            else:
                message, pet1, pet2, pet3, pet4, pet5 = await self.petshow_short(ctx)

            if pet1 is None:
                return

            emojis_swap = ['2️⃣', '3️⃣', '4️⃣', '5️⃣']
            global done_swap
            done_swap = False

            for to_swap in emojis_swap:
                await message.add_reaction(to_swap)

            while done_swap is False:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60)
                to_swap = reaction.emoji
                if user.id == ctx.message.author.id:
                    s = db.record("SELECT Pet1, Pet2, Pet3, Pet4, Pet5 FROM userpet WHERE UserID = (?)",
                                  ctx.message.author.id)

                    # swap 2 with 1
                    if to_swap == '2️⃣' and pet2:
                        if s[1] is None:
                            return
                        else:
                            db.execute('UPDATE userpet SET Pet1 = (?), Pet2 = (?) WHERE UserID = (?)', s[1], s[0],
                                       ctx.message.author.id)
                            db.commit()
                            done_swap = True

                    # swap 3 with 1
                    elif to_swap == '3️⃣' and pet3:
                        if s[2] is None:
                            return
                        else:
                            db.execute('UPDATE userpet SET Pet1 = (?), Pet3 = (?) WHERE UserID = (?)', s[2], s[0],
                                       ctx.message.author.id)
                            db.commit()
                            done_swap = True

                    # swap 4 with 1
                    elif to_swap == '4️⃣' and pet4:
                        if s[3] is None:
                            return
                        else:
                            db.execute('UPDATE userpet SET Pet1 = (?), Pet4 = (?) WHERE UserID = (?)', s[3], s[0],
                                       ctx.message.author.id)
                            db.commit()
                            done_swap = True

                    # swap 5 with 1
                    elif to_swap == '5️⃣' and pet5:
                        if s[4] is None:
                            return
                        else:
                            db.execute('UPDATE userpet SET Pet1 = (?), Pet5 = (?) WHERE UserID = (?)', s[4], s[0],
                                       ctx.message.author.id)
                            db.commit()
                            done_swap = True
                    else:
                        return
                    await ctx.send("Done!")

        except Exception:
            await ctx.send("Try again")

    # removing the selected pet from team
    @commands.command(name='remove', aliases=['rm'])
    async def remove(self, ctx):
        # noinspection PyBroadException
        try:
            if ctx.message.author in playing:
                return await ctx.send("You are in the middle of the fight :rage::rage::rage:")
            check = db.record("SELECT UserID FROM userpet WHERE UserID = (?);", ctx.message.author.id)
            if check[0] is None:
                db.execute("INSERT INTO userpet (UserID) VALUES (?);", ctx.message.author.id)
                db.commit()
                await ctx.send("You currently have no pets!")
            else:
                message, pet1, pet2, pet3, pet4, pet5 = await self.petshow_short(ctx)

            if pet1 is None:
                return

            emojis_remove = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
            global done_removing
            done_removing = False

            for to_remove in emojis_remove:
                await message.add_reaction(to_remove)

            while done_removing is False:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60)
                emoji = reaction.emoji
                if user.id == ctx.message.author.id:
                    a = db.record("SELECT Pet1, Pet2, Pet3, Pet4, Pet5 FROM userpet WHERE UserID = (?)",
                                  ctx.message.author.id)

                    # remove pet
                    if to_remove == '1️⃣' and pet1:
                        db.execute('DELETE FROM petstat WHERE PetID = (?)', a[0])
                        # moving the other pet forward
                        db.execute('UPDATE userpet SET Pet1 = (?), Pet2 = (?), Pet3 = (?), Pet4 = (?),'
                                   ' Pet5 = (?) WHERE UserID = (?)', a[1], a[2], a[3], a[4], None,
                                   ctx.message.author.id)
                        db.commit()
                        await ctx.send("Pet removed!")

                    elif to_remove == '2️⃣' and pet2:
                        db.execute('DELETE FROM petstat WHERE PetID = (?)', a[1])
                        # moving the other pet forward
                        db.execute('UPDATE userpet SET Pet2 = (?), Pet3 = (?), Pet4 = (?),'
                                   ' Pet5 = (?) WHERE UserID = (?)', a[2], a[3], a[4], None, ctx.message.author.id)
                        db.commit()
                        await ctx.send("Pet removed!")

                    elif to_remove == '3️⃣' and pet3:
                        db.execute('DELETE FROM  WHERE PetID = (?)', a[2])
                        # moving the other pet forward
                        db.execute('UPDATE userpet SET Pet3 = (?), Pet4 = (?),'
                                   ' Pet5 = (?) WHERE UserID = (?)', a[3], a[4], None, ctx.message.author.id)
                        db.commit()
                        await ctx.send("Pet removed!")

                    elif to_remove == '4️⃣' and pet4:
                        db.execute('DELETE FROM petstat WHERE PetID = (?)', a[3])
                        # moving the other pet forward
                        db.execute('UPDATE userpet SET Pet4 = (?), Pet5 = (?) WHERE UserID = (?)', a[4], None,
                                   ctx.message.author.id)
                        db.commit()
                        await ctx.send("Pet removed!")

                    elif to_remove == '5️⃣' and pet5:
                        db.execute('DELETE FROM petstat WHERE PetID = (?)', a[4])
                        db.execute("UPDATE userpet SET Pet5 = (?) WHERE UserID = (?);", None, ctx.message.author.id)
                        db.commit()
                        await ctx.send("Pet removed!")

                    else:
                        return
                    done_removing = True

        except Exception:
            await ctx.send("You don't have any pets. Please try again.")


def setup(bot):
    bot.add_cog(ClassName(bot))
