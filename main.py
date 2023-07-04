import os
import tkinter as tk
import sys
import random
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
from moviepy.audio.AudioClip import concatenate_audioclips
import moviepy.editor as mpe
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import ffmpeg
from moviepy.audio.io.AudioFileClip import AudioFileClip
import random
import pyttsx3
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from moviepy.editor import *
from os import path
import speech_recognition as sr
from pydub import *
import re
import sys
import shutil
from make_mp3_same_volume import *
from moviepy.video.fx.all import speedx
from mutagen.mp3 import MP3
from youtube_upload import *
import subprocess
import shlex
import openai
import threading

# Define the ranges
MIN_NUM_CLIPS = 40
MAX_NUM_CLIPS = 53
MIN_TOTAL_DURATION = 2 * 60
MAX_TOTAL_DURATION = 3.5 * 60

open_api_key = "OPEN_AI_API_KEY HERE"

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
        if open_api_key == "OPEN_AI_API_KEY HERE":
            self.upload_button.config(state=tk.DISABLED)
        if open_api_key == "OPEN_AI_API_KEY HERE":
            self.start_button.config(state=tk.DISABLED)
        
        self.uploaded_movies = 0
        

        # Create the 'Exit' button at the top left
        exit_button = tk.Button(root, text="Exit Program", command=self.end_program, font=("Helvetica", 10), height=2, width=10, bg='red', fg='white')
        exit_button.pack(anchor='nw', padx=10, pady=10)
        
        #Create the 'Stop Processing' button at the top right
        self.stop_button = tk.Button(root, text="Stop Processing", command=self.restart_program, font=("Helvetica", 10), height=2, width=15, bg="orange")
        self.stop_button.pack(anchor='ne', pady=12)
        self.stop_button.pack_forget()
        
        self.stop_uploading_button = tk.Button(root, text="Stop Uploading", command=self.restart_program, font=("Helvetica", 10), height=2, width=15, bg="orange")
        self.stop_uploading_button.pack(anchor='ne', pady=12)
        self.stop_uploading_button.pack_forget()
        
        title = tk.Label(root, text="Movie Summary Bot", font=("Helvetica", 24, "bold"))
        title.pack(pady=20)

        #Create the 'Processing...' label and hide it initially
        self.processing_label = tk.Label(root, text="Processing...", font=("Helvetica", 14))
        self.processing_label.pack(pady=10)
        self.processing_label.pack_forget()
        
        self.uploading_label = tk.Label(root, text="Uploading...", font=("Helvetica", 14))
        self.uploading_label.pack(pady=10)
        self.uploading_label.pack_forget()

        movie_button = tk.Button(root, text="Open Movie Directory", command=lambda: self.open_directory("movies"), font=("Helvetica", 14), height=2, width=20, bg='aqua')
        movie_button.pack(pady=10)

        self.start_button = tk.Button(root, text="Start Generation", command=self.start_process, fg="white", font=("Helvetica", 14), height=2, width=20, bg="grey")
        self.start_button.pack(pady=10)

        output_button = tk.Button(root, text="Open Output Directory", command=lambda: self.open_directory("output"), font=("Helvetica", 14), height=2, width=20, bg='aqua')
        output_button.pack(pady=10)

        self.upload_button = tk.Button(root, text="Upload all to YouTube", command=self.upload_to_youtube, font=("Helvetica", 14), height=2, width=20, bg='red', fg='white')
        self.upload_button.pack(pady=10)
        
        dir = "movies"
        
        self.progress_status = tk.StringVar()
        self.progress_status.set(f"0/{str(len(os.listdir(dir)))} Generated")
        
        self.progress_label = tk.Label(root, textvariable=self.progress_status, font=("Helvetica", 14))
        self.progress_label.pack()
        
        # Add a refresh method to keep the GUI responsive.
        self.refresh()
        
    def end_program(self):
        if open_api_key == "OPEN_AI_API_KEY HERE":
            print("Enter a valid openai_api key")
        os._exit(0)

        
    @staticmethod
    def chatGPT_response(message, number_of_words, movie_title):
        try:
            message = f"Ignore previous chats. Act as a narrator providing movie-plot summaries. Provide a summary of approximately {number_of_words} words of the {movie_title} movie? Cover introductary events and middle plot points in high detail. Include key events and details in chronological order. Do not talk about the end in the beginning of the summary, just go through the events as they occur. Mention the end of the movie in the last sentences. Include all spoilers and make subtle/dark comedy jokes if possible, and do not mention actor names."
                
            openai.api_key = open_api_key
                
            response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": message},
                ]
            )
                
            answer = response['choices'][0]['message']['content']
                
            if "here's a summary of" in answer:
                answer = answer.replace("here's a summary of", "")
                
            return "Here we go (spoilers ahead)" + (response['choices'][0]['message']['content'])
        except Exception as e:
            time.sleep(3)
            Gui.chatGPT_response(message, number_of_words, movie_title)
    
    @staticmethod
    def is_within_word_limit(response, number_of_words, tolerance=50):
        # Remove leading/trailing whitespaces and split the response into words
        words = re.findall(r'\w+', response.strip())
            
        # Calculate the word count of the response
        response_word_count = len(words)
            
        # Calculate the lower and upper limits based on the tolerance
        lower_limit = number_of_words - tolerance
        upper_limit = number_of_words + tolerance
            
        # Check if the response word count is within the limits
        return lower_limit <= response_word_count <= upper_limit
    
    
    
    @staticmethod
    def restart_program():
        os.execl(sys.executable, '"{}"'.format(sys.executable), *sys.argv)
        
    def refresh(self):
        self.root.update()
        self.root.after(1000,self.refresh)
        
    def start_process(self):
        dir = "movies"
        
        num_of_movies = len(os.listdir(dir))
        if num_of_movies == 0:
            return ""

        self.start_button.config(state=tk.DISABLED)
        self.upload_button.config(state=tk.DISABLED)
        self.stop_button.pack()
        # Show the processing label
        self.processing_label.pack()

        self.refresh()
        self.process_thread = threading.Thread(target=self.process_movies, args=(num_of_movies,))
        self.process_thread.start()
        
        
    def select_random_song(self):
        songs_dir = "backgroundmusic"
        songs = os.listdir(songs_dir)
        song_path = None

        while not song_path:
            song_name = random.choice(songs)
            songs.remove(song_name)
            song_path = os.path.join(songs_dir, song_name)

            audio_clip = AudioFileClip(song_path)
            if audio_clip.duration <= 60:
                song_path = None

            # Set the start time for the song as 1 minute
        song = AudioFileClip(song_path).subclip(40)
        return song

    def process_movies(self, num_of_movies):
        i = 0
        dir_name = "movies"
        movie_array = [f for f in os.listdir(dir_name) if os.path.isfile(os.path.join(dir_name, f))]
        movies_finished = os.listdir("output")
        
        processed_movies = 0
        
        if num_of_movies == 0:
            return
        
        non_matching_elements = []
        
        while i < num_of_movies:
            new_num_of_movies = len([f for f in os.listdir("movies") if os.path.isfile(os.path.join("movies", f))])
            num_of_movies = new_num_of_movies
            
            
            
            dir_name = "movies"
            if new_num_of_movies != num_of_movies:
                #figure out one that is different, append it to movie_array
                non_matching_elements = [x for x in os.listdir("movies") if x not in movie_array]
                num_of_movies = new_num_of_movies

            for non_matching_element in non_matching_elements:
                movie_array.append(non_matching_element)

            try:
                movie_title = (movie_array[i])[0:len(movie_array[i])-4]
            except Exception as e:
                if num_of_movies > len(os.listdir("movies")):
                    num_of_movies = len(os.listdir("movies"))
            # Get list of all files only from the given directory
            


            clips = Gui.split_video_randomly("movies/" + str(movie_array[i]), "clips")

            # Combine the clips into a single video in chronological order
            if len(clips) > 1:
                final_clip = concatenate_videoclips(clips, method="compose")
            else:
                final_clip = clips[0]

            # Calculate the duration of the final_clip in seconds
            final_clip_duration = final_clip.duration


            # Define the output file path
            output_file = "output/" + str(movie_title) + ".mp4"

            # Write the final video to the output file
            Gui.delete_clips(self, "clips")
            if len(clips) == 1:
                number_of_words = int(1.5 * final_clip_duration)
            else:
                number_of_words = int(3 * final_clip_duration)
            message = f"Ignore previous chats. You are a YouTuber providing movie summaries over clips of the movie. Provide a summary of {number_of_words} words of the {movie_title} movie? Go through every key plot event in detail from start to finish and quickly explain the movie characters' development in chronological order. Do not provide a conclusion/overall paragraph. The last paragraph you write should be about the end of the movie."

            openai.api_key = open_api_key
                
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": message},
                ]
            )
            video_transcript = Gui.chatGPT_response(message, number_of_words, movie_title)

            engine = pyttsx3.init()
            voices = engine.getProperty("voices")
            engine.setProperty("voice", voices[0].id)
            engine.setProperty("rate", 175)
            engine.save_to_file(video_transcript, 'output_audio/output' + str(i+1) + '.mp3')
            engine.runAndWait()
                
            audio_output_dir = 'output_audio/output' + str(i+1) + '.mp3'

            print("OUTPUT" + str(i+1) + "TRANSCRIPT: " + str(video_transcript))
                 
            narration = AudioFileClip(audio_output_dir)
                

            narration = narration.volumex(3.0)
            print(final_clip.duration)
            print(narration.duration)
                

            slowdown_factor = narration.duration / final_clip.duration
            
            if (int(final_clip_duration) - int(narration.duration)) > 4:
                final_clip = final_clip.fl_time(lambda t: t/slowdown_factor, apply_to=['mask', 'audio'])
                final_clip.duration = int(narration.duration)
                
            elif (int(narration.duration) - int(final_clip.duration)) > 4:
                final_clip = final_clip.fl_time(lambda t: t/slowdown_factor, apply_to=['mask', 'audio'])
                final_clip.duration = int(narration.duration)
                
            final_clip_duration = final_clip.duration
            # Create an empty list to store the audio clips
            audio_clips = []

            # Calculate the total duration covered by the background music
            total_duration_covered = 0

            while total_duration_covered < final_clip_duration:
                # Select a random song from the "backgroundmusic" directory
                song = Gui.select_random_song(self)

                # Calculate the remaining duration to be covered by the song
                remaining_duration = final_clip_duration - total_duration_covered

                if song.duration <= remaining_duration:
                    # If the song's duration is less than or equal to the remaining duration,
                    # add the entire song to the audio_clips list
                    audio_clips.append(song)
                    total_duration_covered += song.duration
                else:
                    # If the song's duration is greater than the remaining duration,
                    # trim the song to match the remaining duration and add it to the audio_clips list
                    song = song.subclip(0, remaining_duration)
                    audio_clips.append(song)
                    total_duration_covered += remaining_duration

            # Concatenate the audio clips into a single audio file
            background_music = concatenate_audioclips(audio_clips)

            # Set the audio of the final_clip to the background music
            final_clip = final_clip.set_audio(background_music)
                
                        # Calculate the total duration covered by the background music

                
            if background_music.duration >= final_clip.duration:
                background_music = background_music.subclip(0, int(final_clip.duration))
            else:
                song_to_append = Gui.select_random_song(self)
                difference = final_clip.duration - background_music.duration
                random_point = random.randint(30, 55)
                song_to_append = song_to_append.subclip(random_point, difference + random_point)
                audio_clips = [background_music, song_to_append]
                background_music = concatenate_audioclips(audio_clips)
                
                #add difference seconds of music to the end of background_music
            
            background_music = background_music.volumex(0.1)

            combined_audio = CompositeAudioClip([narration, background_music])
            final_clip = final_clip.set_audio(combined_audio)
            final_clip.write_videofile(output_file, codec='libx264')
            
            processed_movies += 1
            dirrrr = "movies"
            self.progress_status.set(f"{processed_movies}/{len(os.listdir(dirrrr))} Generated")
            self.refresh()
            
            i += 1
        
        self.processing_label.config(text="Process Complete")
        self.stop_uploading_button.destroy()
        self.stop_button.destroy()
        if open_api_key != "OPEN_AI_API_KEY HERE":
            self.start_button.config(state=tk.NORMAL)
        self.start_button.destroy()
        if open_api_key != "OPEN_AI_API_KEY HERE":
            self.upload_button.config(state=tk.NORMAL)
        Gui.rename_files("output", "")
        Gui.rename_again("output", "")
        #Gui.remove_processed_movies()
        Gui.fix_titles("output")
    
    
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
    
    def delete_clips(self, output_dir):
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
            # If the file is a .mp4 file
            if filename.endswith(".mp4"):
                # Construct full file path
                source = os.path.join(source_directory, filename)
                destination = os.path.join(target_directory, filename)
                # Move the file to the new directory
                shutil.move(source, destination)
    
    @staticmethod
    def split_video_randomly(input_file, output_dir):
        try:
            # Load the video
            video = VideoFileClip(input_file)

            print("VIDEO DURATION:", video.duration)
            if video.duration < 59 * 4:
                clips = [video]
                return clips
                
            # Calculate the total duration and the number of clips
            total_duration = random.randint(MIN_TOTAL_DURATION, MAX_TOTAL_DURATION)
            num_clips = random.randint(MIN_NUM_CLIPS, MAX_NUM_CLIPS)

            # Calculate the duration of each clip
            clip_duration = total_duration / num_clips

            # Make sure the output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Calculate the time multiple for evenly distributed start times
            time_multiple = (video.duration - clip_duration) / (num_clips - 1)

            # Create the list of start times for clips in chronological order without overlap
            start_times = [int(i * time_multiple) for i in range(num_clips)]
            
            #Removes focus on credit scene
            for time in start_times:
                if time > 40 and time + 10 < total_duration:
                    start_times.remove(time)
                    start_times.append(time+7)
            start_times = sorted(start_times)

            # Create and save the clips
            clips = []
            for i, start in enumerate(start_times):
                # Calculate the end of the clip
                end = start + clip_duration
                    
                # Clip the video
                clip = video.subclip(start, end)

                # Write the clip to a file
                output_file = os.path.join(output_dir, f"clip_{i+1}.mp4")
                clip.write_videofile(output_file, codec='libx264')

                # Append the clip to the list
                clips.append(clip)

            return clips
        except Exception as e:
            Gui.split_video_randomly(input_file, output_dir)
    
    
    def upload_individual(self, movietitle):
            # Set the command
        command = f'python3 youtube_upload.py --file="output/{movietitle}.mp4" --title="{movietitle}" --description="Like, comment, and subscribe for more top tier movie content." --category="22" --privacyStatus="public"'
    
        # Use shlex to split the command string into a list
        args = shlex.split(command)
    
        # Run the command
        subprocess.run(args)
        
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

            
        # Make upload button active again
        if open_api_key != "OPEN_AI_API_KEY HERE":
            self.upload_button.config(state=tk.NORMAL)
        self.uploading_label.config(text="Uploading...")
        
    def upload_to_youtube(self):
        # Make uploading label visible
        self.uploading_label.pack()
        self.stop_uploading_button.pack(pady=12)
        self.upload_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.DISABLED)

        # Start the upload process in a new thread
        threading.Thread(target=self.upload_thread).start()


    @staticmethod
    def open_directory(path):
        path = os.path.realpath(path)
        os.startfile(path)
        
def start(self):
    self.refresh()
    threading.Thread(target=self.start_process).start()
    self.progress_label.pack()

#Remove placeholder clips

for file in os.listdir("movies"):
    if "-" in file:
        temp = file.replace("-", "")
        os.rename(f"movies/{file}", f"movies/{temp}")

clips_dir = os.listdir("clips")
for clip in clips_dir:
    os.remove("clips/" + clip)
    
out_aud = os.listdir("output_audio")
for audio in out_aud:
    os.remove("output_audio/" + audio)
    
    
def delete_files(starting_directory, file_name):
    for root, dirs, files in os.walk(starting_directory):
        for file in files:
            if file == file_name:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Deleted file: {file_path}")

main_directory = ""
file_name = ".placeholder"
delete_files(main_directory, file_name)
    
    

root = tk.Tk()
GUI = Gui(root)
root.mainloop()
