import discord
from discord.ext import commands
import requests
import base64

class Trivia(commands.Cog):
    def __init__(self, bot, participants):
        self.bot = bot
        self.participants = participants
    
    def get_trivia_categories(self):
        category_response = requests.get("https://opentdb.com/api_category.php").json()
        categories = {}
        # construct a new dict with the structure {"Name of category": id}
        for i in category_response["trivia_categories"]:
            categories[i["name"]] = i["id"]
        return categories

    def set_up_trivia(self, ctx, options):
        """Sets up the trivia questions.
        
        Parameters
        -
        * `ctx` - this is supplied in the trivia bot command.
        * `options` - this is supplied in the trivia bot command. 
        The parameter specifies that amount of questions (required) and the category (optional).

        returns a list of trivia questions.
        """
        options_lst = options.split()
        # If too many arguments given to command
        if len(options_lst) > 2:
            raise Exception() 

        categories = self.get_trivia_categories()

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
        self.participants.append(ctx.message.author)

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

    async def start_trivia(self, ctx, trivia_questions):
        # Respond only to users who are participating
        if ctx.author in self.participants:

            score = {}
            # Dict of player scores, structure is {"Participant name": score}
            for i in range(0, len(self.participants)):
                score[self.participants[i]] = 0

            for i in range(0, len(trivia_questions)):
                category = trivia_questions[i]["category"]
                question = trivia_questions[i]["question"]
                correct_answer = trivia_questions[i]["answer"]
                print(correct_answer)
                await ctx.send(question)

                def check(msg):
                    return ctx.author == msg.author #To make sure it is the only message author is getting
                
                given_answer = await self.bot.wait_for("message", check=check)
                #if given_answer.author in participants:
                if given_answer.content == correct_answer.lower() or given_answer.content == correct_answer:
                    score[given_answer.author] += 1
                    
                    await ctx.send(f"`+1 {given_answer.author}`")
            else:
                pass
        # Player scores embed
        score_embed = discord.Embed(title="Scores", colour=discord.Colour.green())
        for player in self.participants:
            score_embed.add_field(name=player, value=f"Score: {score.get(player)}/{len(trivia_questions)}", inline=True)
        await ctx.send(embed=score_embed)
        self.participants.clear() # Clear the participants list upon ending the trivia

    @commands.command()
    async def trivia(self, ctx, *options):
        categories = self.get_trivia_categories()

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
                trivia_questions = self.set_up_trivia(ctx, options)
                await self.start_trivia(ctx, trivia_questions)
            except:
                await ctx.send("Oh no! Something went wrong, use `-trivia info` for a guide on how to play.")
        else:
            await ctx.send("Use `-trivia info` for a guide on how to play.")