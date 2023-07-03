# AI-Movie-Shorts
Turn Full Movies or .MP4 Files into AI-Generated Movie Trailers/Summaries Using AI.

<h3>Basic Installation Steps:</h3>

```python
#Clone the Git repository:
git clone https://github.com/keithhb33/AI-Movie-Shorts.git

#Install modules and dependencies within cloned directory:
python3 -m pip install -r requirements.txt
```

<h3>OpenAI API Setup & Configuration</h3>
Due to OpenAI's API usage rate costs, users must configure their own GPT 3.5 API Key.
<br />
Key acquisition guide <a href="https://www.howtogeek.com/885918/how-to-get-an-openai-api-key/#:~:text=Go%20to%20OpenAI's%20Platform%20website,generate%20a%20new%20API%20key">here.</a>
<br />
<br />
Once acquired, edit line 37 in "main.py":
```python
#Replace string with your API key
open_api_key = "OPEN_AI_API_KEY HERE"
```
