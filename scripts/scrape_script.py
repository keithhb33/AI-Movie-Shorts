import requests
from bs4 import BeautifulSoup
import os
import argparse

def get_movie_script(title):
    # Format the title to create the URL
    formatted_title = title.replace(' ', '-')
    url = f"https://imsdb.com/scripts/{formatted_title}.html"

    # Send a GET request to the URL
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to retrieve the script. Status code: {response.status_code}")
        formatted_title = formatted_title.replace("(", "").replace(")", "")
        url = f"https://imsdb.com/scripts/{formatted_title}.html"
        response = requests.get(url)
        if response.status_code != 200:
            return None

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the script content
    script_content = soup.find('pre')
    
    if script_content:
        # Extract the text from the <pre> tag
        script_text = script_content.get_text(separator='\n')
        return script_text
    else:
        print("Script content not found.")
        return None

def save_script(script, path):
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # Save the script to the specified location
    with open(path, "w", encoding="utf-8") as file:
        file.write(script)
    
    print(f"Script saved to {path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape movie script from IMSDb")
    parser.add_argument("script_path", help="Path to save the script")
    parser.add_argument("movie_title", help="Title of the movie")
     
    args = parser.parse_args()
    
    script = get_movie_script(args.movie_title)
    
    if script:
        save_script(script.replace("\t", "").replace("  ", ""), args.script_path)
    else:
        print("No script found or there was an error retrieving the script.")
