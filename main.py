import discord
from discord.ext import commands
import requests
import googlesearch
import base64
from Music import *

song_queue = []
bot = commands.Bot(command_prefix="-")
bot.add_cog(Music(bot, song_queue))

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

participants = []

""" @bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.author in participants:
        if message.content == answer:
            await message.channel.send('Hello!')
    await bot.process_commands(message) """


def get_trivia_categories():
    category_response = requests.get("https://opentdb.com/api_category.php").json()
    categories = {}
    # construct a new dict with the structure {"Name of category": id}
    for i in category_response["trivia_categories"]:
        categories[i["name"]] = i["id"]
    return categories


def set_up_trivia(ctx, options):
    """Sets up the trivia questions.
    
    Parameters
    -
    * `ctx` - this is supplied in the trivia bot command.
    * `options` - this is supplied in the trivia bot command. 
    The parameter specifies that amount of questions (required) and the category (optional).

    returns a list of trivia questions.
    """
    categories = get_trivia_categories()
    options_lst = options.split()

    # If user only gave amount of questions
    if len(options_lst) == 1:
        response = requests.get(f"https://opentdb.com/api.php?amount={options_lst[0]}&encode=base64").json()
    # If user gave nr. of questions and category as a name
    elif len(options_lst) == 2 and not options_lst[1].isnumeric():
        response = requests.get(f"https://opentdb.com/api.php?amount={options_lst[0]}&category={categories.get(options_lst[1])}&encode=base64").json()
    # If user gave nr. of questions and category as an ID
    else:
        response = requests.get(f"https://opentdb.com/api.php?amount={options_lst[0]}&category={options_lst[1]}&encode=base64").json()


    question_lst = []
    participants.append(ctx.message.author)

    for i in range(0, len(response["results"])):
        question_data = {}
        # Decode to bytes
        category_base64 = base64.b64decode(response["results"][i]["category"])
        question_base64 = base64.b64decode(response["results"][i]["question"])
        answer_base64 = base64.b64decode(response["results"][i]["correct_answer"])

        # Encode bytes to ASCII and add to Dict
        question_data["category"] = category_base64.decode()
        question_data["question"] = question_base64.decode()
        question_data["answer"] = answer_base64.decode()
        question_lst.append(question_data)
    return question_lst

async def start_trivia(ctx, trivia_questions):
    # Respond only to users who are participating
    if ctx.author in participants:

        score = {}
        # Dict of player scores, structure is {"Participant name": score}
        for i in range(0, len(participants)):
            score[participants[i]] = 0

        for i in range(0, len(trivia_questions)):
            category = trivia_questions[i]["category"]
            question = trivia_questions[i]["question"]
            correct_answer = trivia_questions[i]["answer"]
            print(correct_answer)
            await ctx.send(question)

            def check(msg):
                return ctx.author == msg.author #To make sure it is the only message author is getting
            
            given_answer = await bot.wait_for("message", check=check)
            #if given_answer.author in participants:
            if given_answer.content == correct_answer.lower() or given_answer.content == correct_answer:
                score[given_answer.author] += 1
                
                await ctx.send(f"`+1 {given_answer.author}`")
        else:
            pass
    # Player scores embed
    score_embed = discord.Embed(title="Scores", colour=discord.Colour.green())
    for player in participants:
        score_embed.add_field(name=player, value=f"Score: {score.get(player)}/{len(trivia_questions)}", inline=True)
    await ctx.send(embed=score_embed)
    participants.clear() # Clear the participants list upon ending the trivia



@bot.command()
async def trivia(ctx, *options):
    categories = get_trivia_categories()

    if "info" in options:
        trivia_guide = """To start playing, you must use the command `-trivia start 10`, where '10' is number of questions. This can be set to any number you desire. 
        You can also specify the category by using its ID, e.g. `-trivia start 20 27`. 
        This will create 20 questions from the 'Animals' category. Enjoy! """
        embed = discord.Embed(title="Trivia Guide", colour=discord.Colour.green(), description=trivia_guide)
        for key in categories:
            embed.add_field(name=key, value=f"ID: {categories.get(key)}", inline=True)
        await ctx.send(embed=embed)
    elif "start" in options:
        try:
            options = ctx.message.content[13:].strip()
            trivia_questions = set_up_trivia(ctx, options)
            await start_trivia(ctx, trivia_questions)
        except:
            await ctx.send("Oh no! Something went wrong, use `-trivia info` for a guide on how to play.")
    else:
        await ctx.send("Use `-trivia info` for a guide on how to play.")

f = open("token", "r")
bot.run(f.read())

