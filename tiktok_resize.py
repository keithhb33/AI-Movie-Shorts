from moviepy.editor import *
import os

def tiktok_version(video_path, output_path):
    # Load the video
    clip = VideoFileClip(video_path)
        
    # Calculate the crop dimensions (20% off the left and right)
    original_width, original_height = clip.size
    crop_width = int(original_width * 0.6)  # Keep 60% of the width
    crop_x1 = int(original_width * 0.2)  # Crop 20% from the left
    crop_x2 = crop_x1 + crop_width  # Set the right boundary of the crop

    # Crop the video
    cropped_clip = clip.crop(x1=crop_x1, x2=crop_x2)
        
    # Calculate the new dimensions for the vertical video
    new_height = original_height
    new_width = int(new_height * (9 / 16))
        
    # Resize the cropped video to fit 60% of the vertical real estate, stretched by 20%
    target_height = int(new_height * 0.6 * 1.2)  # Stretch by 20%
    resized_clip = cropped_clip.resize(height=target_height)
        
    # Create a black background with the same size as the original using a black background video
    background = VideoFileClip("black_background.mp4", has_mask=True).set_duration(clip.duration).resize((new_width, new_height))
        
    # Position the resized video in the center of the background
    final_clip = CompositeVideoClip([background, resized_clip.set_position(('center', 'center'))])
        
    # Save the edited video
    final_clip.write_videofile(output_path, codec='libx264')
    
tiktok_version("output/The Truman Show.mp4", "tiktok_output/The Truman Show_vertical.mp4")