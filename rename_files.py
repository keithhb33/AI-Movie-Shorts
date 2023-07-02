import os
import sys
import re

def rename_again(directory, channel_name):
    for file in os.listdir(directory):
        if str(channel_name) not in file:
            os.rename(directory + "/" + str(file), directory + "/" + str(file) + " — " + channel_name)        


def rename_files(directory, channel_name):
    if len(os.listdir(directory)) > 0:
        for filename in os.listdir(directory):
            if filename.endswith(".mp4") and channel_name not in filename:
                base = os.path.splitext(filename)[0]
                new_filename = f"{base} — {channel_name}.mp4"
                if os.path.exists(os.path.join(directory, new_filename)):
                    os.replace(os.path.join(directory, filename), os.path.join(directory, new_filename))
                else:
                    os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))


def add_space():
    strings = os.listdir("output")
    # For each string in the list
    for i in range(len(strings)):
        filename, file_extension = os.path.splitext(strings[i])
        title, _, channel = filename.partition(" — ")
        # If the string has an uppercase letter immediately following a lowercase letter or a digit
        if re.search(r'([a-z]([A-Z0-9])|[A-Z]{2,})', title):
            # Add a space between the lowercase and uppercase letter or digit
            new_title = re.sub(r'([a-z])([A-Z0-9])', r'\1 \2', title)
            # Add a space between consecutive uppercase letters
            new_title = re.sub(r'([A-Z])([A-Z])', r'\1 \2', new_title)
            new_filename = new_title + " — " + channel
            # Append the file extension back onto the string
            new_filename_with_ext = new_filename + file_extension
            os.rename(f"output/{strings[i]}", f"output/{new_filename_with_ext}")





