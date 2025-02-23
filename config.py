import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Bot settings
    BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    
    # Audio settings
    CHUNK_DURATION = 5
    SAMPLE_RATE = 48000
    CHANNELS = 2
    SAMPLE_WIDTH = 2
    
    # Silence detection settings
    MIN_SILENCE_LEN = 500  # ms
    SILENCE_THRESH = -40  # dB
    
    # File storage settings
    RECORDINGS_DIR = "recordings"
    TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
