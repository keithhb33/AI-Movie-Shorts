# AI-Movie-Shorts
Turn Full Movies or .MP4 Files into AI-Generated Movie Trailers/Summaries Using AI.

#Movie Example:

![American Psycho Movie Cover](https://cdn.shopify.com/s/files/1/0057/3728/3618/products/f85ee5ef68c6266f73cf11f6c599cffd_9c1132bb-9c5f-41c8-bd6f-f35db9a6a1a6_480x.progressive.jpg?v=1573653978)



#Video has been heavily compressed to be viewable in README.md

https://github.com/keithhb33/AI-Movie-Shorts/assets/51885619/c1971560-79d5-4037-bd8b-40e0fa8521dc



<h3>Basic Installation Steps</h3>

```python
#This repository works only on Windows PCs
#Clone the Git repository:
git clone https://github.com/keithhb33/AI-Movie-Shorts.git

#Navigate to the cloned repo:
cd AI-Movie-Shorts

#Install modules and dependencies within the cloned directory:
python3 -m pip install -r requirements.txt

#Remove .placeholder files (Windows PowerShell Terminal Command):
Get-ChildItem -Recurse -Filter ".placeholder" | Remove-Item


```

<h3>OpenAI API Setup & Configuration</h3>
Due to OpenAI's API usage rate costs, users must configure their own GPT 3.5 API Key.
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


<h3>Usage</h3>

Place .MP4 files into the "movies" directory. <br />
Ensure all filenames are the titles of their respective movies (Ex: "Pulp Fiction.mp4")
