import os
import subprocess
import shlex

def upload_to_youtube(movietitle):
    # Set the command
    command = f'python3 youtube_upload.py --file="output/{movietitle}.mp4" --title="{movietitle}" --description="Like, comment, and subscribe for more top tier movie content." --category="22" --privacyStatus="public"'
    
    # Use shlex to split the command string into a list
    args = shlex.split(command)
    
    # Run the command
    subprocess.run(args)
    

# Use the function
movies = os.listdir("output")
for movie in movies:
    temp = movie
    temp = temp[0:len(temp)-4]
    upload_to_youtube(str(temp))
