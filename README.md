# Discord Voice Channel Transcription Bot

A Discord bot that records voice channel audio in real-time, processes it to remove silence, and saves the audio chunks for each user separately.

## Features

- Real-time voice recording
- Automatic silence removal
- Separate audio files for each user
- Configurable chunk duration and silence detection parameters

## Prerequisites

- Python 3.8 or higher
- Discord Bot Token
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Create a `.env` file and add your Discord bot token:
```
DISCORD_BOT_TOKEN=your_token_here
```

## Usage

1. Start the bot:
```bash
python main.py
```

2. Bot Commands:
- `/record` - Start recording in the current voice channel
- `/stop_recording` - Stop the current recording session

## Configuration

You can modify the following settings in `config.py`:
- Chunk duration
- Sample rate and audio channels
- Silence detection parameters
- Recording directory path

## File Structure

```
VCTranscript/
├── main.py
├── config.py
├── requirements.txt
├── .env
└── recordings/
    └── user_id/
        └── chunk_timestamp.wav
```

## Notes

- Audio files are saved in WAV format
- Each user's audio is stored in a separate directory
- Files are automatically chunked every 5 seconds (configurable)
- Silent portions are automatically removed

---
*This README was generated using AI assistance.*
