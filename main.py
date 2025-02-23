import discord
import os
from datetime import datetime
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import time
from config import Config
import signal
import sys
import asyncio

config = Config()

# Create recordings directory if it doesn't exist
os.makedirs(config.RECORDINGS_DIR, exist_ok=True)

bot = discord.Bot()

# Modify the connections dictionary to store both VC and sink
connections = {} # Format: {guild_id: (vc, sink)}

class RealtimeAudioSink(discord.sinks.WaveSink):
    def __init__(self, vc, channel):
        super().__init__()
        self.vc = vc
        self.channel = channel
        self.buffers = {}
        self.chunk_duration = config.CHUNK_DURATION
        self.last_save = {}
        
    def write(self, data, user_id):
        # Initialize user buffer if doesn't exist
        if user_id not in self.buffers:
            self.buffers[user_id] = []
            self.last_save[user_id] = time.time()
            
        self.buffers[user_id].append(data)
        
        # Process buffer if we have 5 seconds of audio
        current_time = time.time()
        if current_time - self.last_save[user_id] >= self.chunk_duration:
            self._process_buffer(user_id)
            
    def _process_buffer(self, user_id):
        if not self.buffers[user_id]:
            return
            
        # Combine buffer data
        audio_data = b''.join(self.buffers[user_id])
        
        # Convert to AudioSegment
        audio_segment = AudioSegment(
            data=audio_data,
            sample_width=config.SAMPLE_WIDTH,
            frame_rate=config.SAMPLE_RATE,
            channels=config.CHANNELS
        )
        
        # Detect non-silent parts
        nonsilent = detect_nonsilent(
            audio_segment,
            min_silence_len=config.MIN_SILENCE_LEN,
            silence_thresh=config.SILENCE_THRESH
        )
        
        if nonsilent:
            # Keep only non-silent parts
            non_silent_audio = AudioSegment.empty()
            for start, end in nonsilent:
                non_silent_audio += audio_segment[start:end]
            
            # Save if there's non-silent audio
            if len(non_silent_audio) > 0:
                timestamp = datetime.now().strftime(config.TIMESTAMP_FORMAT)
                filepath = os.path.join(
                    config.RECORDINGS_DIR,
                    str(user_id),
                    f"chunk_{timestamp}.wav"
                )
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                non_silent_audio.export(filepath, format="wav")
        
        # Clear buffer
        self.buffers[user_id] = []
        self.last_save[user_id] = time.time()

@bot.command()
async def record(ctx):
    voice = ctx.author.voice
    if not voice:
        await ctx.respond("You aren't in a voice channel!")
        return

    vc = await voice.channel.connect()
    sink = RealtimeAudioSink(vc, ctx.channel)
    connections[ctx.guild.id] = (vc, sink)

    vc.start_recording(
        sink,
        once_done,
        ctx.channel
    )
    await ctx.respond("Started recording!")

async def once_done(sink: RealtimeAudioSink, channel: discord.TextChannel, *args):
    await sink.vc.disconnect()
    await channel.send("Recording stopped!")

@bot.command()
async def stop_recording(ctx):
    if ctx.guild.id in connections:
        vc, sink = connections[ctx.guild.id]
        
        # Process any remaining audio buffers before stopping
        if isinstance(sink, RealtimeAudioSink):
            for user_id in list(sink.buffers.keys()):
                sink._process_buffer(user_id)
        
        vc.stop_recording()
        del connections[ctx.guild.id]
    else:
        await ctx.respond("I am currently not recording here.")

async def cleanup():
    # Process remaining audio and disconnect from all voice channels
    for guild_id, (vc, sink) in connections.items():
        if isinstance(sink, RealtimeAudioSink):
            for user_id in list(sink.buffers.keys()):
                sink._process_buffer(user_id)
        try:
            vc.stop_recording()
            await vc.disconnect(force=True)
        except:
            pass
    
    # Close the bot
    await bot.close()

def signal_handler(sig, frame):
    print("\nForce stopping...")
    os._exit(0)  # Force exit without cleanup

signal.signal(signal.SIGINT, signal_handler)

bot.run(config.BOT_TOKEN)