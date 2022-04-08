import discord
from discord.ext import commands
import requests

class MemeAPI(commands.Cog):
    def __init__(self, bot):
      self.bot = bot

    @commands.command()
    async def meme(self, ctx, *query):
        if query is not None and len(query) > 1:
            query = ctx.message.content[5:].strip()
            response = requests.get(f"https://meme-api.herokuapp.com/gimme/{query}").json()
        else:
            response = requests.get(f"https://meme-api.herokuapp.com/gimme").json()
        await ctx.send(response["preview"].pop())

class Math(commands.Cog):
    def __init__(self, bot):
      self.bot = bot

    @commands.command()
    async def math(self, ctx, query):
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