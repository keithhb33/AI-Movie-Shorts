import requests
from bs4 import BeautifulSoup
import zipfile
import io
import sys
import os

def parse_movie_title(movie_title):
    parsed_movie_title = movie_title.replace("'", '').replace(' ', '-').replace(' ', '-').replace('(', '').replace(')', '').lower()
    if parsed_movie_title.endswith("ii"):
        parsed_movie_title += "-2"
    if parsed_movie_title.endswith("iii"):
        parsed_movie_title += "-3"
    if parsed_movie_title.endswith("iv"):
        parsed_movie_title += "-4"
    return parsed_movie_title

def download_subtitle(parsed_movie_title, movie_title):
    url = f"https://subf2m.co/subtitles/{parsed_movie_title}/english"
    print(f"Accessing URL: {url}")
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to access URL: {url}, Status code: {response.status_code}")
        end_index = parsed_movie_title.rfind('-')
        if "ii" in parsed_movie_title[end_index:]:
            ending = url[end_index+1:]  # Extract the part after the last '-'
            parsed_movie_title = parsed_movie_title.replace(ending, "ii-2")
            url = f"https://subf2m.co/subtitles/{parsed_movie_title}/english"
            response = requests.get(url)
            if response.status_code != 200:
                return
        else:
            return

    soup = BeautifulSoup(response.text, 'html.parser')
    first_subtitle_link = None

    for link in soup.find_all('a', href=True):
        if link['href'].startswith(f"/subtitles/{parsed_movie_title}/english") and link['href'] != f"/subtitles/{parsed_movie_title}/english" and link['href'] != f"/subtitles/{parsed_movie_title}/english-german":
            first_subtitle_link = f"https://subf2m.co{link['href']}"
            break

    if not first_subtitle_link:
        print(f"No subtitle link found for {parsed_movie_title}")
        return

    print(f"Accessing subtitle page: {first_subtitle_link}")
    subtitle_page_response = requests.get(first_subtitle_link)
    if subtitle_page_response.status_code != 200:
        print(f"Failed to access subtitle page: {first_subtitle_link}, Status code: {subtitle_page_response.status_code}")
        return

    subtitle_soup = BeautifulSoup(subtitle_page_response.text, 'html.parser')
    download_link = None

    for link in subtitle_soup.find_all('a', href=True):
        if link['href'].endswith("download"):
            download_link = f"https://subf2m.co{link['href']}"
            break

    if not download_link:
        print("No download link found")
        return

    print(f"Downloading from: {download_link}")
    zip_response = requests.get(download_link)
    if zip_response.status_code != 200:
        print(f"Failed to download zip file from: {download_link}, Status code: {zip_response.status_code}")
        return

    with zipfile.ZipFile(io.BytesIO(zip_response.content)) as z:
        srt_files = [f for f in z.namelist() if f.endswith('.srt') or f.endswith('.SRT')]
        if len(srt_files) != 1:
            print("Error: Multiple or no SRT files found in the zip")
            return

        srt_filename = srt_files[0]
        with z.open(srt_filename) as srt_file:
            with open(f"scripts/srt_files/{movie_title}.srt", "wb") as out_file:
                out_file.write(srt_file.read())
        print(f"Subtitle downloaded and saved as {movie_title}.srt")

if len(sys.argv) > 1:
    movie_title = sys.argv[1]
else:
    print("Pass a movie title as an argument")
    os._exit(0)

parsed_movie_title = parse_movie_title(movie_title)
download_subtitle(parsed_movie_title, movie_title)
