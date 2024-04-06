import nextcord
from nextcord.ext import commands
import yt_dlp as youtube_dl

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def play(self, ctx, url: str):
        channel = ctx.author.voice.channel
        if not channel:
            await ctx.send("Musisz być na kanale głosowym, aby użyć tej komendy.")
            return

        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()

        voice_client = await channel.connect()

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'noplaylist': True,
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # Wybór URL strumienia audio bezpośrednio z informacji o formatach
            audio_url = next((format['url'] for format in info['formats'] if format['format_id'] == '140'), None)  # '140' to m4a audio o stałej przepływności 128kbps
            if not audio_url:  # Jeżeli nie znaleziono odpowiedniego formatu, użyj domyślnego URL
                audio_url = info['url']

        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -loglevel debug',
        }

        voice_client.play(nextcord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS))

    @commands.command()
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()

def setup(bot):
    bot.add_cog(Music(bot))
