import os
from tiktok_uploader.src.tiktok_uploader.upload import upload_video, upload_videos
from tiktok_uploader.src.tiktok_uploader.auth import AuthBackend
from selenium.webdriver.chrome.options import Options
import time

directory = "tiktok_output"

options = Options()
options.add_argument('start-maximized')

auth = AuthBackend(cookies="cookies.txt")

videos_upload = []

while True:

    if len(os.listdir(directory)) in [0]:
        print("Waiting for TikTok videos...")
        time.sleep(5)
        continue
    
    success = False
    for video in os.listdir("tiktok_output"):
        if video.endswith(".mp4"):
            if video.endswith("_vertical.mp4"):
                vid_replace = video.replace("_vertical", "")
                while not success:
                    try:
                        os.rename("tiktok_output/" + video, "tiktok_output/" + vid_replace)
                        success = True
                    except Exception as e:
                        print("Waiting for Movie Summary Bot to finish.")
                        time.sleep(10)
    
    videos = os.listdir(directory)

    for video in videos:
        title = video[0:len(video)-4]
        description = f"{title}. Like, comment, and follow for more top tier movie content. #fyp #film #movies #tiktok #asian #jynxzi #summaries #movieshort #xiaoling"
    
        videos_upload.append({'video': f"{directory}/{title}.mp4", 'description': description})
        
    failed_videos = upload_videos(videos=videos_upload, auth=auth, headless=False)
    
    failed_vids = [video['video'] for video in failed_videos]

    for upload in videos_upload:
        
        print("upload['video']", upload['video'])
        if upload['video'] not in failed_vids:
            if os.listdir(directory) != videos:
                
                set_a = set(os.listdir(directory))
                set_b = set(videos)
                
                not_in_b = set_a.difference(set_b)
                odd_one_out = list(not_in_b)
                if upload['video'] != odd_one_out:
                    os.remove(upload['video'])
            else:
                os.remove(upload['video'])

    videos_upload.clear()
