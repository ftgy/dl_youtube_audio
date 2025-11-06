import os
import tempfile

from pydub import AudioSegment
from yt_dlp import YoutubeDL


def time_to_milliseconds(time_str):
    """Convert a time string (MM:SS or H:MM:SS) to milliseconds."""
    parts = time_str.split(":")
    if len(parts) == 3:  # HH:MM:SS format
        hours, minutes, seconds = map(int, parts)
        return (hours * 3600 + minutes * 60 + seconds) * 1000
    else:  # MM:SS format
        minutes, seconds = map(int, parts)
        return (minutes * 60 + seconds) * 1000


def download_youtube_audio(youtube_url, output_dir):
    """Download audio from YouTube using yt-dlp and convert to WAV."""
    print(f"Downloading audio from {youtube_url}...")

    os.makedirs(output_dir, exist_ok=True)
    temp_dir = tempfile.mkdtemp()

    # Download best audio to a temporary file
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(temp_dir, "download.%(ext)s"),
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        downloaded_file = ydl.prepare_filename(info)

    # Convert to WAV
    audio = AudioSegment.from_file(downloaded_file)
    wav_path = os.path.join(output_dir, "downloaded_audio.wav")
    audio.export(wav_path, format="wav")

    # Cleanup temp input file
    if os.path.exists(downloaded_file):
        os.remove(downloaded_file)

    print(f"✅ Audio downloaded and saved as WAV:\n   {wav_path}")
    return wav_path


def split_audio(input_audio, timestamps, output_folder):
    """Splits an audio file based on timestamps and names."""
    # Load audio file
    audio = AudioSegment.from_file(input_audio)
    os.makedirs(output_folder, exist_ok=True)

    for i in range(len(timestamps) - 1):
        start_time, name = timestamps[i]
        end_time, _ = timestamps[i + 1]  # Next timestamp as end time

        start_ms = time_to_milliseconds(start_time)
        end_ms = time_to_milliseconds(end_time)

        # Clean up the name to be a valid filename
        safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in name).strip()
        output_path = os.path.join(output_folder, f"{i + 1:02d}_{safe_name}.wav")

        # Extract and save segment
        segment = audio[start_ms:end_ms]
        segment.export(output_path, format="wav")
        print(f"Saved: {output_path} ({start_time} - {end_time})")

    print("\nAll segments have been saved successfully!")


def load_config(config_path):
    """Load configuration from YAML file."""
    import yaml
    import sys
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Validate required fields
        required_fields = ['youtube_url', 'timestamps']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field in config: {field}")

        # Convert timestamps to list of tuples if it's a list of lists
        if config['timestamps'] and isinstance(config['timestamps'][0], list):
            config['timestamps'] = [tuple(item) for item in config['timestamps']]

        return config
    except FileNotFoundError:
        print(f"Error: Config file not found at {config_path}")
        print("Please create a config.yaml file in the project root.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML config: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)
