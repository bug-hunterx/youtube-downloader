# your_lambda_module/lambda_function.py

import os
import math
from yt_dlp import YoutubeDL
import platform

CHUNK_SIZE_DEFAULT = 50 * 1024 * 1024  # 50 MB


def download_video_yt_dlp(url, output_dir):
    """
    Download a YouTube video using yt_dlp to the specified output directory.
    Returns the path of the downloaded video file.
    """
    ffmpeg_path = get_ffmpeg_path()

    options = {
        "format": "best[ext=mp4]",  # Best quality video and audio
        "outtmpl": f"{output_dir}/%(title)s.%(ext)s",  # Output filename format
        "merge_output_format": "mp4",  # Merge video and audio into MP4
        "ffmpeg_location": ffmpeg_path,  # Path to FFmpeg binary
    }

    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        video_path = ydl.prepare_filename(info)

        # Ensure the correct extension for merged files
        if "requested_formats" in info:
            video_path = video_path.replace(".webm", ".mp4").replace(".mkv", ".mp4")

    return video_path


import os
import math
import subprocess


def split_file(file_path, max_size_mb=50):
    """
    Splits a large video file into smaller video chunks, each less than max_size_mb.
    Each chunk is a valid video file.

    Args:
        file_path (str): The path to the input video file.
        max_size_mb (int): Maximum size of each chunk in MB (default: 50 MB).

    Returns:
        list: List of paths to the split video chunks.
    """
    # Get the FFmpeg path
    ffmpeg_path = get_ffmpeg_path()

    # Get file size in bytes
    file_size_bytes = os.path.getsize(file_path)
    file_size_mb = file_size_bytes / (1024 * 1024)

    if file_size_mb <= max_size_mb:
        return [file_path]  # No need to split if file is already smaller than max size

    # Get video duration using FFmpeg
    try:
        result = subprocess.run(
            [ffmpeg_path, "-i", file_path],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )
        output = result.stderr
        duration_line = [line for line in output.splitlines() if "Duration" in line][0]
        duration_str = duration_line.split("Duration:")[1].strip().split(",")[0]
        h, m, s, millisec = map(float, duration_str.replace(".", ":").split(":"))
        total_duration_seconds = int(h * 3600 + m * 60 + s)
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve video duration: {e}")

    # Calculate chunk duration (in seconds) based on file size and target size -
    # as size of frames are not guaranteed to be the same over the duration of the video,
    # we are splitting video in (file_size_mb / max_size_mb + 1) chunks
    number_of_chunks = file_size_mb / max_size_mb + 1
    chunk_duration = math.ceil(total_duration_seconds / number_of_chunks)

    # Split the video into chunks
    base_name, ext = os.path.splitext(os.path.basename(file_path))
    output_dir = os.path.dirname(file_path)
    output_files = []

    try:
        start_time = 0
        chunk_index = 1

        while start_time < total_duration_seconds:
            output_file = os.path.join(
                output_dir, f"{base_name}_part{chunk_index}{ext}"
            )
            command = [
                ffmpeg_path,
                "-i",
                file_path,
                "-ss",
                str(start_time),
                "-t",
                str(chunk_duration),
                "-c",
                "copy",  # Use stream copy to avoid re-encoding
                output_file,
            ]
            subprocess.run(command, check=True)
            output_files.append(output_file)
            start_time += chunk_duration
            chunk_index += 1

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg splitting failed: {e}")

    return output_files


def get_ffmpeg_path():
    """
    Determine the correct FFmpeg path based on the operating system
    and the script's location.
    """
    # Get the absolute path to the current file's directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_dir = os.path.join(base_dir, "../ffmpeg")

    if platform.system() == "Windows":
        return os.path.join(ffmpeg_dir, "ffmpeg.exe")  # Windows version
    else:
        return os.path.join(ffmpeg_dir, "ffmpeg")  # Linux/Mac version
