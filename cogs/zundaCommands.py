import discord
from discord.ext import commands
import requests, asyncio, tempfile, os

VOICEVOX_URL = os.getenv("VOICEVOX_URL", "http://localhost:50021")
SPEAKER_ID = 3  # ずんだもん
FFMPEG_PATH = "/usr/bin/ffmpeg"

class ZundaCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reading_enabled = False
        self.playing_lock = asyncio.Lock()

    @commands.group(
        name="zunda",
        brief="🫛ずんだもん読み上げコマンド🫛",
        invoke_without_command=True
    )
    async def zunda_group(self, ctx):
        await ctx.send("`!z zunda on` で接続")

    @zunda_group.command(name="on")
    # 読み上げモードをオンにするコマンド
    async def on(self, ctx):
        if not ctx.author.voice:
            embed = discord.Embed(
                title="エラー",
                description="❌ ボイスチャンネルに入ってください。",
                color = discord.Colour.red()
            )
            await ctx.send(embed=embed)
            return
        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()
        self.reading_enabled = True
        embed = discord.Embed(
            title="成功",
            description="🎙️ 読み上げモードを開始しました。",
            color = discord.Colour.green()
        )
        await ctx.send(embed=embed)

    @zunda_group.command(name="off")
    # 読み上げモードをオフにするコマンド
    async def off(self, ctx):
        self.reading_enabled = False
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        embed = discord.Embed(
            title="成功",
            description="🔇 読み上げモードを停止しました。",
            color = discord.Colour.green()
        )
        await ctx.send(embed=embed)

    # VOICEVOXで音声合成を行う関数
    def synthesize(self, text, speaker=SPEAKER_ID):
        try:
            query = requests.post(f"{VOICEVOX_URL}/audio_query",
                                  params={"text": text, "speaker": speaker})
            query.raise_for_status()
            synth = requests.post(f"{VOICEVOX_URL}/synthesis",
                                  params={"speaker": speaker},
                                  json=query.json())
            synth.raise_for_status()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(synth.content)
                return f.name
        except Exception as e:
            print(f"[TTS Error] {e}")
            return None

    # メッセージ受信イベントリスナー
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not self.reading_enabled:
            return
        if not message.guild.voice_client or not message.content.strip():
            return

        path = await asyncio.to_thread(self.synthesize, message.content)
        if not path:
            return

        async with self.playing_lock:
            vc = message.guild.voice_client
            if vc and not vc.is_playing():
                source = discord.FFmpegPCMAudio(path, executable=FFMPEG_PATH)
                vc.play(source)
                while vc.is_playing():
                    await asyncio.sleep(0.2)
                os.remove(path)

async def setup(bot):
    await bot.add_cog(ZundaCommands(bot))
