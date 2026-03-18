import os
import tempfile
from pathlib import Path

import yaml
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
    os.makedirs(output_dir, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(temp_dir, "%(id)s.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
            }],
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            base = ydl.prepare_filename(info)
            wav_path = base.rsplit(".", 1)[0] + ".wav"

        final_path = os.path.join(output_dir, "downloaded_audio.wav")
        os.rename(wav_path, final_path)

    return final_path


def split_audio(input_audio, timestamps, output_folder):
    """
    Splits an audio file based on timestamps and names.
    Saves both WAV and MP3 versions of each segment.
    """
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
        base_filename = f"{i + 1:02d}_{safe_name}"

        # Extract segment
        segment = audio[start_ms:end_ms]

        # Save as WAV
        wav_path = os.path.join(output_folder, f"{base_filename}.wav")
        segment.export(wav_path, format="wav")
        print(f"Saved: {wav_path} ({start_time} - {end_time})")

        # Save as MP3 with 192k bitrate (good quality)
        mp3_path = os.path.join(output_folder, f"{base_filename}.mp3")
        segment.export(mp3_path, format="mp3", bitrate="192k")
        print(f"Saved: {mp3_path} ({start_time} - {end_time})")

    print("\nAll segments have been saved in both WAV and MP3 formats!")


def load_config(config_path):
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


def save_config(config, output_dir):
    file_path = Path(output_dir) / "config.yaml"

    with open(file_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f)

    return file_path
