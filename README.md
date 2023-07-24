# AI-Movie-Shorts
Turn full movies or .MP4 Files into AI-generated movie trailers and summaries using OpenAI.

Example:

[![American Psycho Short](http://img.youtube.com/watch?v=B0jX8zkZuYM.JPG)][(https://www.youtube.com/watch?v=B0jX8zkZuYM)]
<img src="https://cdn.shopify.com/s/files/1/0057/3728/3618/products/f85ee5ef68c6266f73cf11f6c599cffd_9c1132bb-9c5f-41c8-bd6f-f35db9a6a1a6_480x.progressive.jpg?v=1573653978" alt="American Psycho Movie Cover" width="29.25%"/>



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
Due to OpenAI's API usage rate costs, users must configure their own GPT 3.5 API keys.
<br />
Key acquisition guide <a href="https://www.howtogeek.com/885918/how-to-get-an-openai-api-key/#:~:text=Go%20to%20OpenAI's%20Platform%20website,generate%20a%20new%20API%20key">here.</a>
<br />
<br />
Once acquired, edit line 37 in "main.py":
<br />

```python
#Replace string with your API key
open_api_key = "OPEN_AI_API_KEY HERE"
```

<h3>(Optional) YouTube API Setup & Configuration</h3>

Users must configure the YouTube API to access their particular YouTube channel. This configuration is optional if users only wish to generate MP4 files.

Follow the steps <a href="https://developers.google.com/youtube/v3/guides/uploading_a_video">here</a> only under the "Requirements" heading. Configure your YouTube API <a href="https://console.cloud.google.com/apis/dashboard">here</a>. Once the YouTube Data API web application has been configured, paste the correct "client_id" and "client_secret" into the 
existing client_secrets.json or replace the file.

After clicking "Upload All to Youtube" on the GUI, users should be asked to sign in to the Google account associated with their YouTube channel, and all of the outputted .MP4 files in the "output" directory will upload to YouTube.

Unfortunately, as of 2020 July, only audited and approved user-created YouTube APIs can be used to upload public videos to the platform. Using non-audited APIs to upload videos to YouTube results in the videos being locked as private. The audit application can be found <a href="https://support.google.com/youtube/contact/yt_api_form?hl=en">here</a>. The process usually only takes a few days.



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

After all narrations are complete, the GUI will indicate such. Processed trailers can be viewed in the "output" directory.

If properly configured, all of the .MP4 files in the directory "output" will be uploaded to YouTube, each upload sharing the name of the original file placed in "movies" along with a preloaded description.

*Changes to the preloaded description and titles can be configured in "upload_action.py" under the "upload_to_youtube" method.


