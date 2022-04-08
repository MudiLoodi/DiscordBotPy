import discord
from discord.ext import commands
import googlesearch
from Cogs.Music import *
from Cogs.Trivia import *

song_queue = []
participants = []
bot = commands.Bot(command_prefix="-")
bot.add_cog(Music(bot, song_queue))
bot.add_cog(Trivia(bot, participants))

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    for guild in bot.guilds:
        channel = discord.utils.get(guild.text_channels, name="general")
    await channel.send("Bot is online")

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

@bot.command()
async def math(ctx, query):
    """Basic arithmetic."""
    query = ctx.message.content[5:].replace(" ", "") # Remove all whitespaces
    query_list = [i for i in query] # each item in list is a char from the query
    operator = ""
    for char in query_list: # get the operator
        if char not in "0123456789":
            operator = char

    left = "" # left side of equation, i.e left of operator
    right = "" # right side of equation, i.e right of operator
    
    op_index = query_list.index(operator) # get index of operator
    
    left = int(left.join(query_list[:op_index])) # the left side is everything up to (not incl.) the operator
    right = int(right.join(query_list[op_index+1:])) # the right side is everything after the operator

    match operator:
        case ("+"):
            await ctx.send(f"{left} + {right} = {left + right}")
        case ("-"):
            await ctx.send(f"{left} - {right} = {left - right}")
        case ("*"):
            await ctx.send(f"{left} * {right} = {left * right}")
        case ("/"):
            if left == 0:
                await ctx.send("You can't divide by 0 you retard.")
            else:
                await ctx.send(f"{left} / {right} = {left / right}")
        case _:
            pass

f = open("token", "r")
bot.run(f.read())

