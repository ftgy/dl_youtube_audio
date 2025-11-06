import os

from utils import (
    download_youtube_audio,
    split_audio,
    load_config
)


def main():
    try:
        # Load configuration
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, 'config.yaml')
        config = load_config(config_path)

        # Get values from config
        youtube_url = config['youtube_url']
        timestamps = config['timestamps']
        output_dir = os.path.join(base_dir, config.get('output_dir', 'data/output'))

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        print(f"Downloading audio from: {youtube_url}")
        audio_file = download_youtube_audio(youtube_url, output_dir)

        print("\nSplitting audio into segments...")
        split_audio(audio_file, timestamps, output_dir)

        return 0

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    import sys

    sys.exit(main())
