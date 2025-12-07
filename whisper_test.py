import subprocess
import argparse
import os
from openai import OpenAI

def convert_to_mp3(input_file, output_mp3):
    """
    Converts MP4 to MP3 using FFmpeg.
    Only called if input is not already MP3.
    """
    print(f"Converting {input_file} → {output_mp3} ...")
    command = [
        "ffmpeg",
        "-i", input_file,
        "-vn",
        "-acodec", "mp3",
        output_mp3,
        "-y"
    ]

    subprocess.run(command, check=True)
    return output_mp3

def transcribe(mp3_file):
    """
    Send MP3 file to OpenAI Whisper (gpt-4o-transcribe).
    """
    print(f"Transcribing {mp3_file} ...")
    client = OpenAI()

    with open(mp3_file, "rb") as audio:
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=audio
        )
    return transcript.text

def main():
    parser = argparse.ArgumentParser(description="Transcribe audio or video using Whisper.")
    parser.add_argument("input_file", help="Input .mp3 or .mp4 file")
    parser.add_argument("-o", "--output", default="transcript.txt", help="Output transcript file")

    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output
    file_ext = os.path.splitext(input_file)[1].lower()

    # Determine MP3 path
    if file_ext == ".mp3":
        mp3_file = input_file
    elif file_ext == ".mp4":
        mp3_file = os.path.splitext(input_file)[0] + ".mp3"
        mp3_file = convert_to_mp3(input_file, mp3_file)
    else:
        raise ValueError("Unsupported file. Use .mp4 or .mp3")

    # Transcribe
    text = transcribe(mp3_file)

    # Save transcript
    with open(output_file, "w") as f:
        f.write(text)

    print(f"\nTranscription saved → {output_file}")
    print("\n--- Transcript Preview ---")
    print(text[:500] + ("..." if len(text) > 500 else ""))

if __name__ == "__main__":
    main()

