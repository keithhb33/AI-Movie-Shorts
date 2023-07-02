import os
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from ffmpeg import *
import ffmpeg
from pydub import AudioSegment

def adjust_volume(directory):
    max_dbfs = -float('inf')
    files_dbfs = {}

    # Iterate over all .mp3 files in the specified directory
    for filename in os.listdir(directory):
        if filename.endswith('.mp3'):
            # Load audio file
            audio = AudioSegment.from_mp3(os.path.join(directory, filename))

            # Calculate loudness of the file
            dbfs = audio.dBFS

            # Store the dBFS value and audio segment for later processing
            files_dbfs[filename] = (dbfs, audio)

            # Update max_dbfs if this file is louder
            if dbfs > max_dbfs:
                max_dbfs = dbfs

    # Adjust volume of all files to the maximum dBFS value
    for filename, (dbfs, audio) in files_dbfs.items():
        if dbfs < max_dbfs:
            # Calculate the difference in dBFS from the loudest file
            dbfs_diff = max_dbfs - dbfs
            
            if dbfs_diff == 0:
                continue

            # Increase the volume
            louder_audio = audio.apply_gain(dbfs_diff)

            # Export the result
            louder_audio.export(os.path.join(directory, filename), format="mp3")


