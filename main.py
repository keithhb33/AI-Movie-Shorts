import os
import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import random
import re
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
from moviepy.audio.AudioClip import concatenate_audioclips
import moviepy.editor as mpe
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import AudioArrayClip
from bs4 import BeautifulSoup
import requests
from moviepy.editor import *
import shutil
import ast
from moviepy.video.fx.all import speedx
from youtube_upload import upload_video
from scripts.scrape_subtitles import parse_movie_title, download_subtitle
from scripts.scrape_script import get_movie_script, save_script
from combine_srt_script import combine_for_title
import webbrowser
import time
from openai import OpenAI
import threading
import numpy as np
import elevenlabs
import moviepy.video.fx.all as vfx
from PyBetterFileIO import *
import json

MIN_NUM_CLIPS = 20
MAX_NUM_CLIPS = 30
MIN_TOTAL_DURATION = 2.5 * 60
MAX_TOTAL_DURATION = 4.5 * 60

def load_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

config = load_config('config.json')
open_api_key = config.get('open_api_key')
elevenlabs_api_key = config.get('elevenlabs_api_key')
if open_api_key:
    os.environ['OPENAI_API_KEY'] = open_api_key
client = OpenAI()

class Gui:
    def __init__(self, root):
        self.root = root
        self.processing_label = None
        self.uploading_label = None
        self.upload_button = None
        self.start_button = None
        self.process_thread = None
        root.title("Movie Summary Bot")
        root.geometry("500x700")
        root.iconbitmap("images/icon.ico")
        self.progress_label = None
        
        self.uploaded_movies = 0
        

        exit_button = tk.Button(root, text="Exit Program", command=self.end_program, font=("Helvetica", 10), height=2, width=10, bg='red', fg='white')
        exit_button.pack(anchor='nw', padx=10, pady=10)

        self.stop_button = tk.Button(root, text="Stop Processing", command=self.restart_program, font=("Helvetica", 10), height=2, width=15, bg="orange")
        self.stop_button.pack(anchor='ne', pady=12)
        self.stop_button.pack_forget()
        
        self.stop_uploading_button = tk.Button(root, text="Stop Uploading", command=self.restart_program, font=("Helvetica", 10), height=2, width=15, bg="orange")
        self.stop_uploading_button.pack(anchor='ne', pady=12)
        self.stop_uploading_button.pack_forget()
        
        title = tk.Label(root, text="Movie Summary Bot", font=("Helvetica", 24, "bold"))
        title.pack(pady=20)

        self.processing_label = tk.Label(root, text="Processing...", font=("Helvetica", 14))
        self.processing_label.pack(pady=10)
        self.processing_label.pack_forget()
        
        self.uploading_label = tk.Label(root, text="Uploading...", font=("Helvetica", 14))
        self.uploading_label.pack(pady=10)
        self.uploading_label.pack_forget()

        movies_dir = "movies"
        output_dir = "output"

        movie_button = tk.Button(root, text="Open Movie Directory", command=lambda: self.open_directory(movies_dir), font=("Helvetica", 14), height=2, width=20, bg='aqua')
        movie_button.pack(pady=10)

        # Checkbox to optionally use a user-provided SRT file
        self.use_own_srt_var = tk.BooleanVar(value=False)
        self.use_own_srt_checkbox = tk.Checkbutton(root, text="Use your own SRT file", variable=self.use_own_srt_var)
        self.use_own_srt_checkbox.pack(pady=5)

        self.start_button = tk.Button(root, text="Start Generation", command=lambda: self.start_process(movies_dir, output_dir), fg="white", font=("Helvetica", 14), height=2, width=20, bg="grey")
        self.start_button.pack(pady=10)

        output_button = tk.Button(root, text="Open Output Directory", command=lambda: self.open_directory(output_dir), font=("Helvetica", 14), height=2, width=20, bg='aqua')
        output_button.pack(pady=10)

        self.upload_button = tk.Button(root, text="Upload all to YouTube", command=self.upload_to_youtube, font=("Helvetica", 14), height=2, width=20, bg='red', fg='white')
        self.upload_button.pack(pady=10)
        if open_api_key == "OPENAPIKEY" or open_api_key == "":
            self.upload_button.config(state=tk.DISABLED)
            self.start_button.config(state=tk.DISABLED)
        
        
        self.progress_status = tk.StringVar()
        movie_count = Gui.get_number_of_movies(movies_dir, output_dir, 0)
        self.progress_status.set(f"0/{movie_count} Generated")
        
        self.progress_label = tk.Label(root, textvariable=self.progress_status, font=("Helvetica", 14))
        self.progress_label.pack()
        
        self.refresh()
        
    @staticmethod
    def get_movie_plot_summary(movie_title):
        formatted_title = movie_title.replace(' ', '_').replace("'", "%27")
        url = f'https://imsdb.com/scripts/{formatted_title}_(film)'

        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve Wikipedia page for {movie_title}... trying a different url")
            response = requests.get(url.replace("_(film)", ""))

        # Parse the page content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the first <pre> tag
        pre_tag = soup.find('pre')

        if not pre_tag:
            print(f"Script section not found for {movie_title}")
            return

        script_text = pre_tag.get_text()

        file_path = f'scripts/srt_files/{movie_title}_summary.txt'
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(script_text)

        print(f"Script for {movie_title} saved to {file_path}")
        

        
    def end_program(self):
        if open_api_key == "OPENAPIKEY":
            print("Enter a valid openai_api key")
        os._exit(0)
        
    @staticmethod
    def get_number_of_movies(movies_dir, output_dir, _unused=None):
        """Return the number of pending .mp4 movies to process.
        - Only counts files in movies_dir that end with .mp4 (case-insensitive)
        - Excludes movies that already have a processed output .mp4 (non-vertical) in output_dir
        - Ignores hidden/system files such as .DS_Store or .placeholder
        """
        try:
            movies = [
                f for f in os.listdir(movies_dir)
                if os.path.isfile(os.path.join(movies_dir, f)) and f.lower().endswith('.mp4')
            ]
        except FileNotFoundError:
            movies = []
        try:
            processed_titles = {
                os.path.splitext(f)[0]
                for f in os.listdir(output_dir)
                if os.path.isfile(os.path.join(output_dir, f)) and f.lower().endswith('.mp4') and '_vertical' not in f
            }
        except FileNotFoundError:
            processed_titles = set()
        pending = [m for m in movies if os.path.splitext(m)[0] not in processed_titles]
        return len(pending)

    def prompt_for_srt(self, expected_path, movie_title):
        messagebox.showinfo("SRT required", f"No subtitles found for '{movie_title}'. Please select the SRT file to continue.")
        srt_file = filedialog.askopenfilename(title=f"Select SRT for {movie_title}", filetypes=[("SRT files", "*.srt *.SRT")])
        if srt_file and os.path.isfile(srt_file):
            os.makedirs(os.path.dirname(expected_path), exist_ok=True)
            shutil.copyfile(srt_file, expected_path)
            return True
        return False
    
    @staticmethod
    def is_within_word_limit(response, number_of_words, tolerance=50):
        words = re.findall(r'\w+', response.strip())
            
        response_word_count = len(words)
        lower_limit = number_of_words - tolerance
        upper_limit = number_of_words + tolerance
            
        return lower_limit <= response_word_count <= upper_limit
    
    @staticmethod
    def convert_timestamp_to_seconds(timestamp):
        hours, minutes, seconds = map(float, re.split('[:,]', timestamp)[:3])
        total_seconds = int(hours * 3600 + minutes * 60 + seconds)
        return total_seconds

    def convert_srt_timestamps(input_file, output_file):
        try:
            with open(input_file, 'r', encoding="utf-8-sig") as infile, open(output_file, 'w') as outfile:
                for line in infile:
                    timestamp_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', line)
                    if timestamp_match:
                        start_time, end_time = timestamp_match.groups()
                        start_seconds = Gui.convert_timestamp_to_seconds(start_time)
                        end_seconds = Gui.convert_timestamp_to_seconds(end_time)
                        outfile.write(f'{start_seconds} --> {end_seconds}\n')
                    else:
                        outfile.write(line)
        except Exception as e:
            try:
                with open(input_file, 'r', encoding="utf-8") as infile, open(output_file, 'w') as outfile:
                    for line in infile:
                        timestamp_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', line)
                        if timestamp_match:
                            start_time, end_time = timestamp_match.groups()
                            start_seconds = Gui.convert_timestamp_to_seconds(start_time)
                            end_seconds = Gui.convert_timestamp_to_seconds(end_time)
                            outfile.write(f'{start_seconds} --> {end_seconds}\n')
                        else:
                            outfile.write(line)
            except:
                with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
                    for line in infile:
                        timestamp_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', line)
                        if timestamp_match:
                            start_time, end_time = timestamp_match.groups()
                            start_seconds = Gui.convert_timestamp_to_seconds(start_time)
                            end_seconds = Gui.convert_timestamp_to_seconds(end_time)
                            outfile.write(f'{start_seconds} --> {end_seconds}\n')
                        else:
                            outfile.write(line)

    
    @staticmethod
    def restart_program():
        os.execl(sys.executable, '"{}"'.format(sys.executable), *sys.argv)
        
    def refresh(self):
        self.root.update()
        self.root.after(1000,self.refresh)
        
    def start_process(self, movies_dir, output_dir):
        
        num_of_movies = Gui.get_number_of_movies(movies_dir, output_dir, 0)
        
        if num_of_movies == 0:
            return ""

        self.start_button.config(state=tk.DISABLED)
        self.upload_button.config(state=tk.DISABLED)
        self.stop_button.pack()
        # Show the processing label
        self.processing_label.pack()

        self.refresh()
        self.process_thread = threading.Thread(target=self.process_movies, args=(num_of_movies, movies_dir, output_dir))
        self.process_thread.start()
        
    @staticmethod
    def select_random_song():
        songs_dir = "backgroundmusic"
        songs = os.listdir(songs_dir)
        song_path = None
        song_name = None

        while not song_path:
            song_name = random.choice(songs)
            songs.remove(song_name)
            song_path = os.path.join(songs_dir, song_name)

            audio_clip = AudioFileClip(song_path)
            if audio_clip.duration <= 60:
                song_path = None

        song = AudioFileClip(song_path).subclip(40)
        return song
    
    @staticmethod
    def tiktok_version(video_path, output_path):
        clip = VideoFileClip(video_path)
        
        original_width, original_height = clip.size
        crop_width = int(original_width * 0.6)  # Keep 60% of the width
        crop_x1 = int(original_width * 0.2)  # Crop 20% from the left
        crop_x2 = crop_x1 + crop_width  # Set the right boundary of the crop

        cropped_clip = clip.crop(x1=crop_x1, x2=crop_x2)
        
        new_height = original_height
        new_width = int(new_height * (9 / 16))
        
        target_height = int(new_height * 0.6 * 1.2)  # Stretch by 20%
        resized_clip = cropped_clip.resize(height=target_height)
        
        background = VideoFileClip("black_background.mp4", has_mask=True).set_duration(clip.duration).resize((new_width, new_height))
        
        final_clip = CompositeVideoClip([background, resized_clip.set_position(('center', 'center'))])
        
        final_clip.write_videofile(output_path, codec='libx264')

    def process_movies(self, num_of_movies, movies_dir, output_dir):

        movie_array = [
            f for f in os.listdir(movies_dir)
            if os.path.isfile(os.path.join(movies_dir, f)) and f.endswith(".mp4")
        ]
        print(movie_array)
        
        processed_movies = 0
        
        if num_of_movies == 0:
            return

        i = 0
        while i < num_of_movies:
            if len(os.listdir(output_dir)) > 0:
                processed_titles = {os.path.splitext(f)[0] for f in os.listdir(output_dir) if f.endswith('.mp4') and '_vertical' not in f}
                movie_array = [m for m in movie_array if os.path.splitext(m)[0] not in processed_titles]
                num_of_movies = len(movie_array)
            
            movie_title = str(movie_array[i])[:-4]
            video = VideoFileClip(os.path.join(movies_dir, str(movie_array[i])))
            duration_in_seconds = video.duration
            
            input_dir_srt = f"scripts/srt_files/{movie_title}.srt"
            output_dir_srt = f"scripts/srt_files/{movie_title}_modified.srt"

            subtitles_path = 'scripts/scrape_subtitles.py'
            script_path = 'scripts/scrape_script.py'
            
            output_dir_script = f'scripts/srt_files/{movie_title}_summary.txt'
            try:
                if self.use_own_srt_var.get():
                    # Prompt the user to upload an SRT file and place it at the expected path
                    if not self.prompt_for_srt(input_dir_srt, movie_title):
                        print(f"SRT file for {movie_title} not provided. Skipping this movie.")
                        continue
                else:
                    parsed_title = parse_movie_title(movie_title)
                    download_subtitle(parsed_title, movie_title)

                    if not os.path.isfile(input_dir_srt):
                        if not self.prompt_for_srt(input_dir_srt, movie_title):
                            print(f"SRT file for {movie_title} not provided. Skipping this movie.")
                            continue

                if not os.path.isfile(output_dir_srt):
                    Gui.convert_srt_timestamps(input_dir_srt, output_dir_srt)
                    os.remove(input_dir_srt)

                if not self.use_own_srt_var.get():
                    script = get_movie_script(movie_title)
                    if script:
                        save_script(script.replace("\t", "").replace("  ", ""), output_dir_script)
                    if not os.path.isfile(output_dir_script):
                        print(f"Script for {movie_title} not found. Proceeding without script summary.")

                if os.path.isfile(output_dir_srt) and os.path.isfile(output_dir_script):
                    try:
                        combine_for_title(movie_title)
                    except Exception as e:
                        print(f"Problem analyzing SRT and Script files for {movie_title}: {e}")

            except Exception as e:
                print(e)
                continue
            
            script_dir = os.path.dirname(subtitles_path)

            try:
                File(output_dir_srt).replace("<i>", "")
            except Exception as e:
                print("FAILED")
            
            with open(output_dir_srt, 'r') as output_file_replace:
                data = output_file_replace.read()
                data = data.replace("<i>", "").replace("</i>", "")
                with open(output_dir_srt, 'w') as output_file_replace:
                    output_file_replace.write(data)
            with open(output_dir_srt, "r") as srt_file:
                data = srt_file.read()
            print(data)
            print("DURATION OF MOVIE: " + str(duration_in_seconds))
            combined_path = f"scripts/srt_files/{movie_title}_combined.txt"
            if os.path.isfile(combined_path):
                with open(combined_path, 'r') as file:
                    combined_script = file.read()
            else:
                with open(output_dir_srt, 'r') as file:
                    combined_script = file.read()
            
            
            script = f'''Read and understand this script of the movie {movie_title}, which includes timestamps (indicating number of seconds into the movie): "{combined_script}"
            From this, choose {num_clips} time ranges that are most essential to the plot and development of the movie's story. Each chosen range should be in between 10 seconds and 30 seconds. Choose ranges from the script provided or combinations of such.
            Only output the time ranges, formatted in a Python dictionary in the format of: {{"120-145": "PLOT SUMMARY OF WHAT OCCURS DURING THAT TIME RANGE", "280-300": ...}}
            Don't overlap time ranges.
            Each value in this dictionary should be a commentary describing what is happening in the scene. This should be a description of each event within the time duration. Consult the SRT script. Use full sentences like you're a commentator speaking to an audience going scene-by-scene for each dict value.
            For the first dict value start it with: "Here we go, let's go over the movie {movie_title}." Write at least 3 sentences for each value.
            Make sure the whole movie's plot arc is covered, up until the final scene. Output the time ranges in numerical order. Ignore the very first time range, which starts at 0.
            '''
            
        
            response = Gui.get_SRT_response(script)
            if response == "error":
                break
            
            response = response.replace("```", "").replace("python", "").replace("    ", "").replace(r"\n\n", "")
            response = ast.literal_eval(response)
            if not isinstance(response, dict):
                try:
                    Gui.delete_clips("clips")
                    continue
                except Exception as e:
                    continue
                
            for key, value in response.items():
                print(str(key) + ": " + str(value))
            

            try:
                clips, audio_outputs = Gui.split_video_importance("movies/" + str(movie_array[i]), "clips", response)
            except Exception as e:
                clips, audio_outputs = Gui.split_video_importance("movies/" + str(movie_array[i]), "clips", response)     
        
            
            adjusted_clips = []
            for j in range(len(audio_outputs)):
                clip = clips[j]
                narration = audio_outputs[j]

                # Remove any existing audio from the video segment to avoid layering
                try:
                    clip = clip.without_audio()
                except Exception:
                    clip = clip.set_audio(None)

                target_dur = clip.duration
                narr_dur = narration.duration
                tol = 0.02  # 20 ms tolerance for floating point safety

                # If narration is longer, stretch the video (not the audio) to match the narration length
                if narr_dur > target_dur + tol:
                    factor = max(0.01, narr_dur / target_dur)
                    clip = clip.fl_time(lambda t: t / factor, apply_to=['mask'])
                    # Set the clip duration slightly under narration to avoid boundary read errors
                    eps = 0.005
                    clip = clip.set_duration(max(0, narr_dur - eps))
                    target_dur = clip.duration
                    # Ensure narration matches final clip duration exactly (safe to trim by eps if needed)
                    if narration.duration > target_dur + 1e-3:
                        narration = narration.subclip(0, target_dur)

                # If narration is shorter, pad with a tiny silence tail to match clip duration
                elif narr_dur < target_dur - tol:
                    sr = 44100
                    pad = max(0, target_dur - narr_dur)
                    pad_len = int(np.ceil(pad * sr))
                    silence = np.zeros((pad_len, 2), dtype=np.float32)
                    silence_clip = AudioArrayClip(silence, fps=sr)
                    narration = concatenate_audioclips([narration, silence_clip]).set_duration(target_dur)

                # Set the narration as the clip's audio
                clip = clip.set_audio(narration.volumex(4.0))
                adjusted_clips.append(clip)

            final_clip = concatenate_videoclips(adjusted_clips)
            final_clip_duration = final_clip.duration
            final_output_path = os.path.join("output", f"{movie_title}.mp4")

            audio_clips = []
            total_duration_covered = 0

            while total_duration_covered < final_clip_duration:
                song = Gui.select_random_song()
                remaining_duration = final_clip_duration - total_duration_covered

                if song.duration <= remaining_duration + 5:
                    audio_clips.append(song)
                    total_duration_covered += song.duration
                else:
                    song = song.subclip(0, remaining_duration)
                    audio_clips.append(song)
                    total_duration_covered += remaining_duration

            background_music = concatenate_audioclips(audio_clips)

            if background_music.duration < final_clip.duration:
                difference = final_clip.duration - background_music.duration
                song_to_append = Gui.select_random_song().subclip(0, difference)
                background_music = concatenate_audioclips([background_music, song_to_append])

            background_music = background_music.volumex(0.1)

            # Align background music to exactly match the final video duration
            background_music = background_music.set_duration(final_clip.duration)

            combined_audio = CompositeAudioClip([final_clip.audio, background_music])
            final_clip = final_clip.set_audio(combined_audio)

            final_clip.write_videofile(final_output_path, codec='libx264')
            
            processed_movies += 1

            self.progress_status.set(f"{processed_movies}/{num_of_movies} Generated")
            self.refresh()
            Gui.tiktok_version(final_output_path, final_output_path[:-4].replace("output", "tiktok_output") + "_vertical.mp4")

            i += 1
            time.sleep(5)
        
        self.processing_label.config(text="Process Complete")
        self.stop_uploading_button.destroy()
        self.stop_button.destroy()
        if open_api_key != "OPENAPIKEY" and open_api_key != "":
            self.start_button.config(state=tk.NORMAL)
            self.start_button.destroy()
            self.upload_button.config(state=tk.NORMAL)
        else:
            print("Please enter an OpenAPI API Key")

        for vid in os.listdir(output_dir):
            if "_vertical" in vid and vid.endswith(".mp4"):
                File(str(vid)).move_to(os.path.join("tiktok_output", vid))
                
        for movie in os.listdir(movies_dir):
            if movie.endswith(".mp4"):
                File(str(movie)).move_to(movies_dir + "_retired")
        try:
            Gui.rename_files(output_dir, "")
            Gui.rename_again(output_dir, "")
            Gui.fix_titles(output_dir)
        except Exception as e:
            pass
        

            
    @staticmethod
    def parse_narration_script(response):
        narration_script = ""

        for value in response.values():
            narration_script += str(value) + "\n"
    
    @staticmethod
    def fix_titles(output):
        outputted = os.listdir(output)
        for finished in outputted:
            new_finished = finished
            if "-" in finished:
                new_finished = new_finished.replace("-", " ")
            os.rename(f"{output}/{finished}", f"{output}/{new_finished}")
                
    
    
    @staticmethod
    def rename_again(directory, channel_name):
        for file in os.listdir(directory):
            if str(channel_name) not in file:
                os.rename(directory + "/" + str(file), directory + "/" + str(file) + "" + channel_name)
    
    @staticmethod
    def delete_clips(output_dir):
        for f in os.listdir(output_dir):
            os.remove(os.path.join(output_dir, f))
    
    @staticmethod
    def rename_files(directory, channel_name):
        if len(os.listdir(directory)) > 0:
            for filename in os.listdir(directory):
                if filename.endswith(".mp4") and channel_name not in filename:
                    base = os.path.splitext(filename)[0]
                    new_filename = f"{base}.mp4"
                    if os.path.exists(os.path.join(directory, new_filename)):
                        os.replace(os.path.join(directory, filename), os.path.join(directory, new_filename))
                    else:
                        os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
    
    
    @staticmethod
    def remove_processed_movies():
        source_directory = "movies"
        target_directory = "retiredmovies"

        if not os.path.exists(target_directory):
            os.makedirs(target_directory)
                
        if not os.path.exists(source_directory):
            os.makedirs(source_directory)

        # Loop through all the files in the source directory
        for filename in os.listdir(source_directory):
            if filename.endswith(".mp4"):
                source = os.path.join(source_directory, filename)
                destination = os.path.join(target_directory, filename)
                shutil.move(source, destination)
    
    @staticmethod
    def split_video_importance(input_file, output_dir, response_list):
        try:
            # Load the video
            video = VideoFileClip(input_file)

            if video.duration < 59 * 4:
                clips = [video]
                return clips

            # Make sure the output directory exists
            os.makedirs(output_dir, exist_ok=True)
            audio_output_dir = os.path.join(output_dir, "audio")
            os.makedirs(audio_output_dir, exist_ok=True)

            clips = []
            audio_clips = []
            for i, time_range in enumerate(response_list.keys()):
                start_str, end_str = time_range.split('-')
                start = int(start_str)
                end = int(end_str)

                if end > video.duration:
                    end = video.duration

                clip = video.subclip(start, end)

                output_file = os.path.join(output_dir, f"clip_{i+1}.mp4")
                clip.write_videofile(output_file, codec='libx264')

                clips.append(clip)

                narration_script = response_list[time_range]
                elevenlabs.set_api_key(elevenlabs_api_key)
                audio = elevenlabs.generate(
                    text=narration_script,
                    voice="Liam",
                    model="eleven_multilingual_v2"
                )
                audio_file_path = os.path.join(audio_output_dir, f"audio_{i+1}.mp3")
                elevenlabs.save(audio, audio_file_path)

                audio_clip = AudioFileClip(audio_file_path)

                audio_clips.append(audio_clip)

            return clips, audio_clips

        except Exception as e:
            print(f"An error occurred: {e}")
            return []
    
    @staticmethod
    def split_video_randomly(input_file, output_dir):
        try:
            # Load the video
            video = VideoFileClip(input_file)

            if video.duration < 59 * 4:
                clips = [video]
                return clips

            clip_duration = total_duration / num_clips

            os.makedirs(output_dir, exist_ok=True)
            time_multiple = (video.duration - clip_duration) / (num_clips - 1)

            start_times = [int(i * time_multiple) for i in range(num_clips)]
            
            for time in start_times:
                if time > 40 and time + 10 < total_duration:
                    start_times.remove(time)
                    start_times.append(time+7)
            start_times = sorted(start_times)

            clips = []
            for i, start in enumerate(start_times):
                end = start + clip_duration
                    
                clip = video.subclip(start, end)
                output_file = os.path.join(output_dir, f"clip_{i+1}.mp4")
                clip.write_videofile(output_file, codec='libx264')
                clips.append(clip)

            return clips
        except Exception as e:
            Gui.split_video_randomly(input_file, output_dir)
    
    
    def upload_individual(self, movietitle):
        upload_video(
            file=f'output/{movietitle}.mp4',
            title=movietitle,
            description="Like, comment, and subscribe for more top tier movie content.",
            category="22",
            privacyStatus="public"
        )
        self.uploading_label.config(text="Upload Attempt Complete")


    
    def upload_thread(self):
        movies = os.listdir("output")
        if len(movies) > 0:
            for i in range(len(movies)):
                temp = movies[i]
                temp = temp[0:len(temp) - 4]
                Gui.upload_individual(self, str(temp))
            if len(movies) == 1:
                self.uploading_label.config(text = "Upload Complete")
            else:
                self.uploading_label.config(text = "Uploads Complete")

            
        if open_api_key != "OPENAPIKEY":
            self.upload_button.config(state=tk.NORMAL)
        self.uploading_label.config(text="Uploading...")
        
    def upload_to_youtube(self):
        # Make uploading label visible
        self.uploading_label.pack()
        self.stop_uploading_button.pack(pady=12)
        self.upload_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.DISABLED)

        threading.Thread(target=self.upload_thread).start()

    def open_directory(self, path):
        path = os.path.realpath(path)
        if sys.platform == "win32":
            os.startfile(path)
        else:
            webbrowser.open(f'file://{path}')

    @staticmethod            
    def get_SRT_response(script):
        try:
            prompt = script
            response = client.responses.create(
                model="gpt-5-mini",
                reasoning={"effort": "high"},
                input=[{"role": "user", "content": prompt}]
            )
            return response.output_text
        except Exception as e:
            print("GPT Failed... retrying... " + str(e))
            if "too large" in str(e).lower():
                return "error", "error"
            time.sleep(37)
            return Gui.get_SRT_response(script)
        
def start(self, movies_dir="movies", output_dir="output"):
    self.refresh()
    threading.Thread(target=self.start_process, args=(movies_dir, output_dir)).start()
    self.progress_label.pack()

def delete_files(starting_directory, file_name):
    for root, dirs, files in os.walk(starting_directory):
        for file in files:
            if file == file_name:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
                
def create_folders(folders):
    for folder in folders:
        if not os.path.isdir(folder):
            os.makedirs(folder)

            

if __name__ == "__main__":
    
    total_duration = random.randint(MIN_TOTAL_DURATION, MAX_TOTAL_DURATION)
    num_clips = random.randint(MIN_NUM_CLIPS, MAX_NUM_CLIPS)

    
    folders = [
        "clips",
        "movies",
        "output",
        "backgroundmusic",
        "scripts",
        "output_audio",
        "tiktok_output",
        os.path.join("scripts", "audio_extractions"),
        os.path.join("scripts", "parsed_scripts"),
        os.path.join("scripts", "srt_files"),
    ]
    create_folders(folders)
    
    for file in os.listdir("movies"):
        if "-" in file:
            temp = file.replace("-", "")
            os.rename(f"movies/{file}", f"movies/{temp}")

    clips_dir = os.listdir("clips")
    for clip in clips_dir:
        if os.path.isfile(clip):
            os.remove("clips/" + clip)
            
    audio_clips_dir_temp = os.listdir("clips/audio")
    for audio in audio_clips_dir_temp:
        if os.path.isfile(audio):
            os.remove("clips/audio/" + audio)
        
    out_aud = os.listdir("output_audio")
    for audio in out_aud:
        os.remove("output_audio/" + audio)
        
    main_directory = ""
    file_name = ".placeholder"
    delete_files(main_directory, file_name)

    root = tk.Tk()
    GUI = Gui(root)

    root.mainloop()
