import os
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
import speech_recognition as sr

class Timestamps:

    @staticmethod
    def extract_audio(movie_path, audio_output_path):
        clip = VideoFileClip(movie_path)
        clip.audio.write_audiofile(audio_output_path)
    
    @staticmethod
    def convert_audio_to_wav(mp3_path, wav_path):
        audio = AudioSegment.from_file(mp3_path, format="mp3")
        audio.export(wav_path, format="wav")
        os.remove(mp3_path)

    @staticmethod
    def transcribe_audio(audio_path):
        print("Starting audio transcription")
        recognizer = sr.Recognizer()
        audio_file = sr.AudioFile(audio_path)
        transcript = []
        timestamps = []

        with audio_file as source:
            duration = source.DURATION

        interval = 30  # Segment duration in seconds
        overlap = 5    # Overlapping duration in seconds
        current_offset = 0

        while current_offset < duration:
            with audio_file as source:
                audio = recognizer.record(source, offset=current_offset, duration=interval)
                try:
                    text = recognizer.recognize_google(audio)
                    #if text.strip() != "" and text.strip() != "\n":
                    transcript.append(text)
                    timestamps.append(current_offset)
                    print(text)
                    print(f'{current_offset}/{duration}')
                except sr.UnknownValueError:
                    continue
            current_offset += (interval - overlap)

        print("Finished audio transcription")
        return transcript, timestamps

    @staticmethod
    def assign_timestamps_to_transcript(transcript, timestamps):
        output_lines = []
        transcript_index = 0

        for i, line in enumerate(transcript):
            if (i + 1) % 5 == 0 and transcript_index < len(transcript):
                timestamp = timestamps[transcript_index]
                output_lines.append(f"{line} [{timestamp // 60}:{timestamp % 60}]\n")
                transcript_index += 1
            else:
                output_lines.append(f"{line}\n")

        print("Finished assigning timestamps")
        return output_lines

    @staticmethod
    def save_output_script(output_path, output_lines):
        with open(output_path, 'w') as file:
            file.writelines(output_lines)
            
    @staticmethod
    def main(movie_path, audio_output_path, wav_output_path, output_path):
        # Extract audio from movie
        Timestamps.extract_audio(movie_path, audio_output_path)

        # Convert MP3 to WAV
        Timestamps.convert_audio_to_wav(audio_output_path, wav_output_path)

        # Transcribe audio to text
        transcript, timestamps = Timestamps.transcribe_audio(wav_output_path)

        # Assign timestamps to every 5th line of the transcript
        output_lines = Timestamps.assign_timestamps_to_transcript(transcript, timestamps)

        # Save the output script
        Timestamps.save_output_script(output_path, output_lines)
        os.remove(wav_output_path)
        print("Transcription Process Complete.")

if __name__ == "__main__":
    movie_title = "American Psycho"
    movie_path = f'movies/{movie_title}.mp4'
    audio_output_path = f'scripts/audio_extractions/{movie_title}.mp3'
    wav_output_path = f'scripts/audio_extractions/{movie_title}.wav'
    output_path = f'scripts/parsed_scripts/{movie_title} Script.txt'
    Timestamps.main(movie_path, audio_output_path, wav_output_path, output_path)
