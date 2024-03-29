import discord
from discord.ext import commands
import googlesearch
from Cogs.Music import *
from Cogs.Trivia import *
from Cogs.Misc import *

song_queue = []
participants = []
bot = commands.Bot(command_prefix="-")
bot.add_cog(Music(bot, song_queue))
bot.add_cog(Trivia(bot, participants))
bot.add_cog(JokesAndMeme(bot))
bot.add_cog(Math(bot))

bot_commands = [i for i in bot.all_commands.keys()]

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    for guild in bot.guilds:
        channel = discord.utils.get(guild.text_channels, name="general")
    await channel.send("Bot is online")

# Give prompt if command is unknown.
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send(error)
    await bot.process_commands(error)

# TODO Removed for now since it is useless, may reintroduce later
""" @bot.command()
async def search(ctx, query):
    cookies = {"CONSENT":"YES+shp.gws-20210330-0-RC1.de+FX+412"}
    query = ctx.message.content[7:].strip()
    url = f"https://www.google.com/search?q={query}"
    page = requests.get(url, cookies=cookies)
    data = page.text
    soup = BeautifulSoup(data, 'html.parser')
    div = soup.find("div", {"class":"BNeawe iBp4i AP7Wnd"})

    await ctx.send(f"Here is what I found: {div.text}") """

@bot.command()
async def wiki(ctx, query):
    """Finds a Wikipedia article."""
    query = ctx.message.content[5:].strip()
    url = f"https://en.wikipedia.org/wiki/{query}"
    for i in googlesearch.search(url, tld="co.in", num=10, stop=1, pause=2): 
        result = i 
    await ctx.send(f"Here is what I found: {result}")



f = open("token", "r")
bot.run(f.read())

