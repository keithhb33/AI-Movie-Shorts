# AI-Movie-Shorts
Turn full movies or .MP4 Files into AI-generated movie trailers and summaries using OpenAI.

Example Video: [Citizen Kane (1941)](https://www.youtube.com/watch?v=ej8c0NwKW00&t=5s)

<h3>Basic Installation Steps</h3>

```python
#This repository only works on Windows PCs
#Clone the Git repository:
git clone https://github.com/keithhb33/AI-Movie-Shorts.git

#Navigate to the cloned repo:
cd AI-Movie-Shorts

#Install modules and dependencies within the cloned "AI-Movie-Shorts" directory:
python3 -m pip install -r requirements.txt

#Remove .placeholder files (Windows PowerShell Terminal Command):
Get-ChildItem -Recurse -Filter ".placeholder" | Remove-Item

```

<h3>OpenAI API Setup & Configuration</h3>
Due to OpenAI's API usage rate costs, users must configure their own GPT 4o API keys.
<br />
Key acquisition guide <a href="https://www.howtogeek.com/885918/how-to-get-an-openai-api-key/#:~:text=Go%20to%20OpenAI's%20Platform%20website,generate%20a%20new%20API%20key">here.</a>
<br />
<br />
Once acquired, edit the config.json file:
<br />

```python
# Replace with OpenAI and ElevenLabs API keys ('legacy' user OpenAI API keys are utilized here).
# IMPORTANT: OpenAI TIER 2 API ACCOUNT IS REQUIRED DUE TO CHARACTER LIMITS ON LEVEL 1.
config.json
```

<h3>Usage</h3>
After configuration:

```python
#Run the terminal command in the "AI-Movie-Shorts" directory:
python3 main.py
```

An application GUI should appear.

<p align="center">
  <img src="https://github.com/keithhb33/AI-Movie-Shorts/assets/51885619/0c136488-f3d7-4b94-a49e-32af9a861ef8" alt="GUI Image"/>
</p>

Place .MP4 (movie) files into the "movies" directory.
Ensure all filenames are the titles of their respective movies (Ex: "American Psycho.mp4")

Click "Start Generation"

If the algorithm cannot find a particular movie script, it will ask for you to place it in scripts/srt_files/{movie_title}_summary.txt.
Find the movie script online and paste it into this file. Then rerun "Start Generation."

For non-public movies, the algorithm may have trouble finding an SRT file for the movie. If this error occurs, find an SRT file
for your movie/video and place it in scripts/srt_files/{movie_title}.srt

After all narrations are complete, the GUI will indicate such. Processed movie shorts can be viewed in the "output" directory.
Here is an example movie short: [Watch Short](https://youtu.be/TBBme4gQ9G8)


<h3>(Optional) YouTube API Setup & Configuration</h3>

Users must configure the YouTube API to access their particular YouTube channel. This configuration is optional if users only wish to generate MP4 files.

Follow the steps <a href="https://developers.google.com/youtube/v3/guides/uploading_a_video">here</a> only under the "Requirements" heading. Configure your YouTube API <a href="https://console.cloud.google.com/apis/dashboard">here</a>. Once the YouTube Data API web application has been configured, paste the correct "client_id" and "client_secret" into 
a client_secrets.json file.

After clicking "Upload All to Youtube" on the GUI, users should be asked to sign in to the Google account associated with their YouTube channel, and all of the outputted .MP4 files in the "output" directory will upload to YouTube.

Unfortunately, as of 2020 July, only audited and approved user-created YouTube APIs can be used to upload public videos to the platform. Using non-audited APIs to upload videos to YouTube results in the videos being locked as private. The audit application can be found <a href="https://support.google.com/youtube/contact/yt_api_form?hl=en">here</a>. The process usually only takes a few days.
