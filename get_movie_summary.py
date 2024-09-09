import requests
import os
from bs4 import BeautifulSoup


def get_movie_plot_summary(movie_title):
    # Format the movie title to match Wikipedia URL format
    formatted_title = movie_title.replace(' ', '_').replace("'", "%27")
    url = f'https://imsdb.com/scripts/{formatted_title}_(film).html'

    # Fetch the Wikipedia page
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve Wikipedia page for {movie_title}... trying a different url")
        response = requests.get(url.replace("_(film)", ""))
        if response.status_code != 200:
            response = requests.get(url.replace("_", "%20"))
            if response.status_code != 200:
                response = requests.get(url + "%20Script")

    # Parse the page content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the first <pre> tag
    pre_tag = soup.find('pre')

    if not pre_tag:
        print(f"Script section not found for {movie_title}")
        return

    # Extract the text and remove HTML tags
    script_text = pre_tag.get_text()

    file_path = f'scripts/srt_files/{movie_title}_summary.txt'
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Save the script text to a file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(script_text)

    print(f"Script for {movie_title} saved to {file_path}")
get_movie_plot_summary("Eyes Wide Shut")