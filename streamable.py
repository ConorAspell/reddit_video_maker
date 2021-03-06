from moviepy.editor import *
import moviepy.video.fx.all as vfx
from datetime import datetime
import requests
import json
import os
import praw 
import time
from pystreamable import StreamableApi


def get_videos():
    number_of_videos = os.environ.get("number_of_videos")
    game = os.environ.get("game")
    twitch_id = os.environ.get("twitch_id")
    url="https://api.twitch.tv/kraken/clips/top?limit="+str(number_of_videos)+"&game="+game+"&period=week"
    referrer = "google.ie"
    client_id = twitch_id
    headers = {
        'Client-ID' : client_id,    
        'Accept': 'application/vnd.twitchtv.v5+json'
    }
    response = requests.get(url, headers=headers, timeout=10)
    clips=[]    
    places=[]   
    titles=[]
    test = json.loads(response.content)
    print(test)
    today = datetime.now().strftime("%d_%m_%Y")
    save_location = "top_clips_" + today
    duration = 0
    for item in test['clips']:
        duration += item['duration']
        if duration > 125:
            break
        temp = item['thumbnails']['medium']
        temp2='-'.join(temp.split('-')[:-2])+".mp4"
        clips.append(temp2)
        titles.append(item['title'])
    for clip in clips:
        r=requests.get(clip)
        key=clip.split('/')[-1]
        place=key
        with open(place, 'wb') as f:
            f.write(r.content)
        places.append(place)
    return places, titles

def transform(intro, paths, titles):
    clips=[]
    final = VideoFileClip(intro)
    for i in range(0, len(paths)):

        clip = VideoFileClip(paths[i])

        clips.append(clip)
    for clip in clips:
        clip.resize((460, 720))
        final = concatenate_videoclips([final, clip])
        clip.close()
    today = datetime.now().strftime("%d_%m_%Y")
    save_location = "top_clips_" + today + ".mp4"
    final.write_videofile(save_location, temp_audiofile='temp-audio.m4a', remove_temp=True, codec="libx264", audio_codec="aac") 
    if os.path.getsize(save_location) > 1000000000:
        del paths[-1]
        edit_video(paths)
    return save_location


def edit_video(paths, titles):
    clips=[VideoFileClip("intro.mp4")]
    for i in range(0, len(paths)):
        clip = VideoFileClip(paths[i])
        clip.resize((460, 720))
        
        clips.append(clip)
    final = concatenate_videoclips(clips, method='compose')
        
    today = datetime.now().strftime("%M_%H_%d_%m_%Y")
    save_location = "top_clips_" + today + ".mp4"
    final.write_videofile(save_location, temp_audiofile='temp-audio.m4a', remove_temp=True, codec="libx264", audio_codec="aac", fps=24,logger=None, threads=4)
    if os.path.getsize(save_location) > 1000000000:
        del paths[-1]
        edit_video(paths)
    print('complete')
    print(save_location)
    return save_location

def upload_to_streamable(path):
    username = os.environ.get("username")
    password = os.environ.get("password")
    api = StreamableApi(username, password)
    deets = api.upload_video(path, path.split('/')[-1])
    count = 0
    while True:
        count+=1
        test = api.get_info(deets['shortcode'])
        if test['percent'] == 100:
            break
        elif count == 6:
            exit()
        else:
            time.sleep(10)
    return "https://streamable.com/" +deets['shortcode']

def upload_to_reddit(url='https://streamable.com/6ws17r'):
    username = os.environ.get("username")
    password = os.environ.get("password")
    reddit_id = os.environ.get("reddit_id")
    reddit_secret = os.environ.get("reddit_secret")
    subreddit = os.environ.get("subreddit")
    reddit = praw.Reddit(client_secret = reddit_secret,
    client_id = reddit_id,
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
    username=username,
    password=password
    )
    reddit.subreddit(subreddit).submit(title='Top Twitch Clips for This Week', url=url)

# export number_of_videos=1
# export game=League%20of%20Legends
# export twitch_id=022i90v7stu8i3u71otlf5xxa6w8si
# export username=concueta
# export password=4562433Ss
# export subreddit=leagueoflegends
# export reddit_id=ps2XmeHmNwaP2g
# export reddit_secret=OSxpjcizyXRovExi9VZ_y2n6Ihc
# export subreddit=leagueoflegends

# number_of_videos=3
# game="League%20of%20Legends"
# twitch_id="022i90v7stu8i3u71otlf5xxa6w8si"
# username="concueta"
# password="4562433Ss"
# subreddit="leagueoflegends"
# reddit_id="ps2XmeHmNwaP2g"
# reddit_secret="OSxpjcizyXRovExi9VZ_y2n6Ihc"
# subreddit="leagueoflegends"
if '__name__' == '__main__':
    places, titles=get_videos()
    filename=edit_video(places, titles)

    url = upload_to_streamable(filename)
    upload_to_reddit(url)