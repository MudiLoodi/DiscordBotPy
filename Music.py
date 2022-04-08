import discord
from discord.ext import commands
import youtube_dl


class Music(commands.Cog):
    def __init__(self, bot, song_queue):
        self.bot = bot
        self.song_queue = song_queue

    @commands.command()
    async def join(self, ctx):
        """Joins the voice channel of the user who invoked the command."""
        if (ctx.voice_client):  # If the bot is in a voice channel
            await ctx.voice_client.disconnect()  # Leave the channel
        if (ctx.author.voice != None):
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.send(f"Joined VC `{channel}` \N{MICROPHONE}")
        else:
            await ctx.send(f"You are not in a voice channel.")

    @commands.command()
    async def leave(self, ctx):
        """Leaves voice channel."""
        if (ctx.voice_client):  # If the bot is in a voice channel
            ctx.voice_client.stop()  # stop if playing audio
            await ctx.voice_client.disconnect()  # Leave the channel
            await ctx.send(f"Bot left VC `{ctx.author.voice.channel}`")
        else:  # But if it isn't
            await ctx.send("I'm not in a voice channel.")


    def get_audio_stream(self, source_url):
        """Creates FFmpegPCMAudio stream from url."""
        audio_stream = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(source_url, before_options="-re"), volume=0.6)
        return audio_stream


    def search_yt_video(self, query):
        """Searches for a video and returns FFmpegPCMAudio, video title, thumbnail
        and YT URL if given a key word search.

            Parameters
            ------------
            * `query`: URL or key words. This is supplied by the caller bot command `play`. 

            Defaults to `ytsearch`if given an invalid URL.
        """
        ydl_opts = {'format': 'bestaudio',
                    'noplaylist': 'True', 'default_search': 'ytsearch:'}
        ytdl = youtube_dl.YoutubeDL(ydl_opts)
        video_info = ytdl.extract_info(query, download=False)
        if "https" in query:
            audio_url = video_info["url"]  # filter URL from dict
            title = video_info["title"]
            youtube_url = video_info["webpage_url"]
            thumbnail = video_info["thumbnail"]
        else:
            # If given a non-url, it will default to ytsearch.
            # extract_info with ytsearch returns a different dict
            # compared to if we use extract_info with a url.
            audio_url = video_info["entries"][0]["url"]
            title = video_info["entries"][0]["title"]
            youtube_url = video_info["entries"][0]["webpage_url"]
            thumbnail = video_info["entries"][0]["thumbnail"]
        audio_stream = self.get_audio_stream(audio_url)

        return audio_stream, title, youtube_url, thumbnail

    def play_next(self, ctx):
        #print("Before pop", song_queue)
        if len(self.song_queue) != 0:
            stream = self.song_queue.pop(0) # get the last added song, which will be at index 0
            #print("After pop", song_queue)
            self.bot.voice_clients[0].play(stream, after=self.play_next)

    @commands.command()
    async def play(self, ctx, query):
        """Plays the audio from a video.

            Parameters
            --------
            * `query`: URL or key words.
        """
        if (ctx.voice_client):  # if the bot is in a voice channel
            # this is so we dont need to use "" when giving multiple words to the play command
            query = ctx.message.content[6:].strip()
            audio_stream, title, youtube_url, video_thumbnail = self.search_yt_video(query) # get all video info
            ctx.voice_client.stop() # stop current song
            # an embed that links to the video
            #url_embed = discord.Embed(title=title, url=youtube_url,colour=discord.Colour.green())
            #url_embed.set_image(url=video_thumbnail)

            if "https" not in query: # if given a non-url
                await ctx.send(f"Searching \N{RIGHT-POINTING MAGNIFYING GLASS} `{query}`")
                #await ctx.send(f"Now playing `{title}` \N{MUSICAL NOTE}", embed=url_embed)
                await ctx.send(f"Now playing `{title}` \N{MUSICAL NOTE}")
            else:
                await ctx.send(f"Now playing `{title}` \N{MUSICAL NOTE}")

            ctx.voice_client.play(audio_stream, after=self.play_next)

        else:
            await ctx.send("I'm not in a voice channel, use the `-join` command to make me join.")

    @commands.command()
    async def stop(self, ctx):
        """Stops audio from playing."""
        if (ctx.voice_client):
            ctx.voice_client.stop()
            await ctx.send(f"Stopped playing.")

    @commands.command()
    async def pause(self, ctx):
        """Pauses audio."""
        if (ctx.voice_client):
            ctx.voice_client.pause()
            await ctx.send(f"Song is paused.")

    @commands.command()
    async def unpause(self, ctx):
        """Resumes audio."""
        if (ctx.voice_client):
            ctx.voice_client.resume()

    @commands.command() 
    async def que(self, ctx, query):
        """Adds song to the queue."""
        if (ctx.voice_client):  # if the bot is in a voice channel
            query = ctx.message.content[5:].strip()
            audio_stream, title, youtube_url, video_thumbnail = self.search_yt_video(query) # get all video info
            self.song_queue.append(audio_stream)
            await ctx.send(f"Song queued `{title}` \N{MUSICAL NOTE}")
    
    # TODO Implement this once queue is actually working
    """ @bot.command()
    async def skip(ctx):
        #if (song_queue != []): # if we have songs in queue
        ctx.voice_client.stop()
            #stream = song_queue.pop(0) # get the last added song
            #ctx.voice_client.play(stream[0]) """