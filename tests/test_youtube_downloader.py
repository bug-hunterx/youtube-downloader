import os
import pytest
from downloader.downloader import download_video_yt_dlp, split_file  # Replace with your module name

# Example YouTube video URL (short and accessible for testing)
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Replace with a public video link


def test_download_video():
    """
    Test the download_video function.
    Ensure the video is downloaded and exists in the specified directory.
    """
    # Act
    current_path = os.path.dirname(os.path.abspath(__file__))
    video_path = download_video_yt_dlp(TEST_VIDEO_URL, current_path)

    # Assert
    assert os.path.exists(video_path), "The video file was not downloaded."
    assert os.path.getsize(video_path) > 0, "The downloaded video file is empty."

    # Cleanup
    # os.remove(video_path)


def test_split_file():
    """
    Test the split_file function.
    Ensure the file is correctly split into chunks of 5 MB or less.

    Using file downloaded by previous test, given the os.remove(video_path) line is commented
    """
    current_path = os.path.dirname(os.path.abspath(__file__))

    test_file = os.path.join(current_path, "Rick Astley - Never Gonna Give You Up (Official Music Video).mp4")
    max_size_mb = 5
    # Act
    chunks = split_file(test_file, max_size_mb)

    # Assert
    assert len(chunks) == 3, "The file should be split into 3 chunks"
    for chunk in chunks:
        assert os.path.getsize(chunk) <= max_size_mb * 1024 * 1024, "A chunk exceeds the 50 MB limit."
        # os.remove(chunk)  # Cleanup chunk files

    # Cleanup
    # os.remove(dummy_file_path)
