import discord
import asyncio
from discord.ext import commands
import traceback
import sqlite3
import validators
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions


class voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        conn = sqlite3.connect('temp.db')
        c = conn.cursor()
        guildID = member.guild.id
        c.execute("SELECT voiceChannelID FROM guild WHERE guildID = ?", (guildID,))
        voice = c.fetchone()
        if voice is None:
            pass
        else:
            voiceID = voice[0]
            try:
                if after.channel.id == voiceID:
                    c.execute("SELECT * FROM voiceChannel WHERE userID = ?", (member.id,))
                    cooldown = c.fetchone()
                    if cooldown is None:
                        pass
                    else:
                        await asyncio.sleep(0)
                    c.execute("SELECT voiceCategoryID FROM guild WHERE guildID = ?", (guildID,))
                    voice = c.fetchone()
                    c.execute("SELECT channelName, channelLimit FROM userSettings WHERE userID = ?", (member.id,))
                    setting = c.fetchone()
                    c.execute("SELECT channelLimit FROM guildSettings WHERE guildID = ?", (guildID,))
                    guildSetting = c.fetchone()
                    if setting is None:
                        name = f"salle de {member.name}"
                        if guildSetting is None:
                            limit = 0
                        else:
                            limit = guildSetting[0]
                    else:
                        if guildSetting is None:
                            name = setting[0]
                            limit = setting[1]
                        elif guildSetting is not None and setting[1] == 0:
                            name = setting[0]
                            limit = guildSetting[0]
                        else:
                            name = setting[0]
                            limit = setting[1]
                    categoryID = voice[0]
                    id = member.id
                    category = self.bot.get_channel(categoryID)
                    channel2 = await member.guild.create_voice_channel(name, category=category)
                    channelID = channel2.id
                    await member.move_to(channel2)
                    await channel2.set_permissions(self.bot.user, connect=True, read_messages=True)
                    await channel2.edit(name=name, user_limit=limit)
                    c.execute("INSERT INTO voiceChannel VALUES (?, ?)", (id, channelID))
                    conn.commit()

                    def check(a, b, c):
                        return len(channel2.members) == 0

                    await self.bot.wait_for('voice_state_update', check=check)
                    await channel2.delete()
                    await asyncio.sleep(3)
                    c.execute('DELETE FROM voiceChannel WHERE userID=?', (id,))
            except:
                pass
        conn.commit()
        conn.close()

    @commands.command()
    @has_permissions(administrator=True)
    async def setup(self, ctx):
        conn = sqlite3.connect('temp.db')
        c = conn.cursor()
        guildID = ctx.guild.id
        id = ctx.author.id
        if ctx.author.id:
            new_cat = await ctx.guild.create_category_channel("Crée Ton Channel Modifiable")
            channel = await ctx.guild.create_voice_channel("Crée Ton Channel Modifiable", category=new_cat)
            c.execute("SELECT * FROM guild WHERE guildID = ? AND ownerID=?", (guildID, id))
            voice = c.fetchone()
            if voice is None:
                c.execute("INSERT INTO guild VALUES (?, ?, ?, ?)", (guildID, id, channel.id, new_cat.id))
            else:
                c.execute(
                    "UPDATE guild SET guildID = ?, ownerID = ?, voiceChannelID = ?, voiceCategoryID = ? WHERE guildID = ?",
                    (guildID, id, channel.id, new_cat.id, guildID))
            await ctx.channel.send("**Le système a été configuré avec succès !😄😄**")
        else:
            await ctx.channel.send(f"{ctx.author.mention} Vous n'êtes pas autorisé à utiliser cette commande! 🥺")
        conn.commit()
        conn.close()

    @commands.command()
    async def setlimit(self, ctx, num):
        conn = sqlite3.connect('temp.db')
        c = conn.cursor()
        if ctx.author.id == ctx.guild.owner.id:
            c.execute("SELECT * FROM guildSettings WHERE guildID = ?", (ctx.guild.id,))
            voice = c.fetchone()
            if voice is None:
                c.execute("INSERT INTO guildSettings VALUES (?, ?, ?)",
                          (ctx.guild.id, f"{ctx.author.name}'s channel", num))
            else:
                c.execute("UPDATE guildSettings SET channelLimit = ? WHERE guildID = ?", (num, ctx.guild.id))
            await ctx.send("Vous avez modifié la limite de canaux par défaut pour votre serveur!")
        else:
            await ctx.channel.send(f"{ctx.author.mention} Vous n'êtes pas autorisé à utiliser cette commande! 🥺")
        conn.commit()
        conn.close()

    @commands.command()
    async def lock(self, ctx):
        conn = sqlite3.connect('temp.db')
        c = conn.cursor()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await ctx.channel.send(
                f"{ctx.author.mention} Vous n'avez pas de chambre ou vous n'êtes pas propriétaire de la chambre! 😱")
        else:
            channelID = voice[0]
            role = ctx.guild.default_role
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=False)
            await ctx.channel.send(f'{ctx.author.mention} La chambre a été verrouillée! 🔒')
        conn.commit()
        conn.close()

    @commands.command()
    async def unlock(self, ctx):
        conn = sqlite3.connect('temp.db')
        c = conn.cursor()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await ctx.channel.send(
                f"{ctx.author.mention} Vous n'avez pas de chambre ou vous n'êtes pas propriétaire de la chambre! 😱")
        else:
            channelID = voice[0]
            role = ctx.guild.default_role
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=None)
            await ctx.channel.send(f'{ctx.author.mention} La salle a été déverrouillée! 🔓')
        conn.commit()
        conn.close()

    @commands.command(aliases=["allow"])
    async def permit(self, ctx, member: discord.Member):
        conn = sqlite3.connect('temp.db')
        c = conn.cursor()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await ctx.channel.send(
                f"{ctx.author.mention} Vous n'avez pas de chambre ou vous n'êtes pas propriétaire de la chambre! 😱")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(member, connect=True)
            await ctx.channel.send(f'{ctx.author.mention} tu as permis {member.name} accéder à la chambre ✅')
        conn.commit()
        conn.close()

    @commands.command(aliases=["deny"])
    async def reject(self, ctx, member: discord.Member):
        conn = sqlite3.connect('temp.db')
        c = conn.cursor()
        id = ctx.author.id
        guildID = ctx.guild.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await ctx.channel.send(
                f"{ctx.author.mention} Vous n'avez pas de chambre ou vous n'êtes pas propriétaire de la chambre! 😱")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            for members in channel.members:
                if members.id == member.id:
                    c.execute("SELECT voiceChannelID FROM guild WHERE guildID = ?", (guildID,))
                    voice = c.fetchone()
                    channel2 = self.bot.get_channel(voice[0])
                    await member.move_to(channel2)
            await channel.set_permissions(member, connect=False, read_messages=True)
            await ctx.channel.send(f"{ctx.author.mention} tu as refusé {member.name} depuis l'accès à la chambre ❌")
        conn.commit()
        conn.close()

    @commands.command()
    async def limit(self, ctx, limit):
        conn = sqlite3.connect('temp.db')
        c = conn.cursor()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await ctx.channel.send(
                f"{ctx.author.mention} Vous n'avez pas de chambre ou vous n'êtes pas propriétaire de la chambre! 😱")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.edit(user_limit=limit)
            await ctx.channel.send(f'{ctx.author.mention} Vous avez ajusté la limite à ' + '{}!'.format(limit))
            c.execute("SELECT channelName FROM userSettings WHERE userID = ?", (id,))
            voice = c.fetchone()
            if voice is None:
                c.execute("INSERT INTO userSettings VALUES (?, ?, ?)", (id, f'{ctx.author.name}', limit))
            else:
                c.execute("UPDATE userSettings SET channelLimit = ? WHERE userID = ?", (limit, id))
        conn.commit()
        conn.close()

    @commands.command()
    async def name(self, ctx, name):
        conn = sqlite3.connect('temp.db')
        c = conn.cursor()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await ctx.channel.send(
                f"{ctx.author.mention} Vous n'avez pas de chambre ou vous n'êtes pas propriétaire de la chambre.! 😱")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.edit(name=name)
            await ctx.channel.send(f'{ctx.author.mention} Vous avez nommé la pièce ' + '{}!'.format(name))
            c.execute("SELECT channelName FROM userSettings WHERE userID = ?", (id,))
            voice = c.fetchone()
            if voice is None:
                c.execute("INSERT INTO userSettings VALUES (?, ?, ?)", (id, name, 0))
            else:
                c.execute("UPDATE userSettings SET channelName = ? WHERE userID = ?", (name, id))
        conn.commit()
        conn.close()

    @commands.command()
    async def claim(self, ctx):
        x = False
        conn = sqlite3.connect('temp.db')
        c = conn.cursor()
        channel = ctx.author.voice.channel
        if channel == None:
            await ctx.channel.send(f"{ctx.author.mention} Vous n'êtes pas dans la pièce! 😞")
        else:
            id = ctx.author.id
            c.execute("SELECT userID FROM voiceChannel WHERE voiceID = ?", (channel.id,))
            voice = c.fetchone()
            if voice is None:
                await ctx.channel.send(
                    f"{ctx.author.mention} Vous n'avez pas de chambre ou vous n'êtes pas propriétaire de la chambre! 😱")
            else:
                for data in channel.members:
                    if data.id == voice[0]:
                        owner = ctx.guild.get_member(voice[0])
                        await ctx.channel.send(f"{ctx.author.mention} Cette chambre appartient à {owner.mention}!")
                        x = True
                if x == False:
                    await ctx.channel.send(f"{ctx.author.mention} Vous possédez déjà cette pièce! ✅")
                    c.execute("UPDATE voiceChannel SET userID = ? WHERE voiceID = ?", (id, channel.id))
            conn.commit()
            conn.close()

    @commands.command()
    async def ghost(self, ctx):
        conn = sqlite3.connect('temp.db')
        c = conn.cursor()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await ctx.channel.send(
                f"{ctx.author.mention} Vous n'avez pas de chambre ou vous n'êtes pas propriétaire de la chambre! 😱")
        else:
            channelID = voice[0]
            role = discord.utils.get(ctx.guild.roles, name='@everyone')
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=False, read_messages=False)
            await ctx.channel.send(f'{ctx.author.mention} La pièce a été masquée! ')
        conn.commit()
        conn.close()

    @commands.command()
    async def unghost(self, ctx):
        conn = sqlite3.connect('temp.db')
        c = conn.cursor()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await ctx.channel.send(
                f"{ctx.author.mention} Vous n'avez pas de chambre ou vous n'êtes pas propriétaire de la chambre! 😱")
        else:
            channelID = voice[0]
            role = discord.utils.get(ctx.guild.roles, name='@everyone')
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=True, read_messages=True)
            await ctx.channel.send(f'{ctx.author.mention} La pièce a été dévoilée! ')
        conn.commit()
        conn.close()

    @commands.command()
    async def owner(self, ctx, member: discord.Member):
        conn = sqlite3.connect('temp.db')
        c = conn.cursor()
        id = ctx.author.id
        guildID = ctx.guild.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await ctx.channel.send(
                f"{ctx.author.mention} Vous n'avez pas de chambre ou vous n'êtes pas propriétaire de la chambre! 😱")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            for members in channel.members:
                if members.id == member.id:
                    c.execute("SELECT voiceChannelID FROM guild WHERE guildID = ?", (guildID,))
                    voice = c.fetchone()
                    channel2 = self.bot.get_channel(voice[0])
            await channel.set_permissions(member, connect=True, manage_channels=True)
            await ctx.channel.send(f'{ctx.author.mention} donné {member.name} gestion de salle!')
        conn.commit()
        conn.close()

    @commands.command()
    async def unowner(self, ctx, member: discord.Member):
        conn = sqlite3.connect('temp.db')
        c = conn.cursor()
        id = ctx.author.id
        guildID = ctx.guild.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await ctx.channel.send(
                f"{ctx.author.mention} Vous n'avez pas de chambre ou vous n'êtes pas propriétaire de la chambre! 😱")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            for members in channel.members:
                if members.id == member.id:
                    c.execute("SELECT voiceChannelID FROM guild WHERE guildID = ?", (guildID,))
                    voice = c.fetchone()
                    channel2 = self.bot.get_channel(voice[0])
            await channel.set_permissions(member, connect=True, manage_channels=False)
            await ctx.channel.send(f'{ctx.author.mention} annulé {member.name} gestion de salle!')
        conn.commit()
        conn.close()


def setup(bot):
    bot.add_cog(voice(bot))
