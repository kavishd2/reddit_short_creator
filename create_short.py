import praw
from random import randrange
from playwright.sync_api import sync_playwright, ViewportSize
from gtts import gTTS
from mutagen.mp3 import MP3
from moviepy import *

# Logs in and navigates to AITAH subreddit
reddit = praw.Reddit(client_id = "YvIRoDbwvCahJJtlHFpQ7Q", client_secret = "yszDIeGArTEBQ_goqN32fi40u8qMuQ", user_agent = "redditshorts", check_for_async=  False)
target_sub = "AskReddit"
subreddit = reddit.subreddit(target_sub)

# Gets one of the top 10 hot posts
randnum = randrange(10)
i = 0
for submission in subreddit.hot(limit = 10) :
    if i == randnum :
        text = [[submission.title, submission.id, submission.url]]
    i += 1
submission = reddit.submission(text[0][1])

# Grabs enough comments for the video
i = 0
size = len(text[0][0])
while (size < 350 and len(text) < 5) :
        text.append([submission.comments[i].body, submission.comments[i].id, "http://www.reddit.com" + submission.comments[i].permalink])
        i += 1
        size += len(text[i][0])
print(text)

# Screenshot capture
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(text[0][2])
    page.wait_for_load_state()
    page.locator("#t3_" + text[0][1]).screenshot(path="screenshot0.png")
    for i in range(1,len(text)):
        page.goto(text[i][2])
        page.wait_for_load_state()
        page.locator("#t1_" + text[i][1] + "-comment-rtjson-content").screenshot(path="screenshot"+str(i)+".png")

# Generate speech from text
length = []
time = 0
contentmp3 = []
for i in range(len(text)):
    gTTS(text = text[i][0], lang='en').save("content"+str(i)+".mp3")
    contentmp3.append(MP3("content" + str(i) + ".mp3"))
    length.append(contentmp3[i].info.length)
    time += length[i] + 1

# creates the audioclips and imageclips
audiofileclips = []
imageclips = []
current = 0
for i in range(len(text)) :
    audiofileclips.append(AudioFileClip("content" + str(i) + ".mp3").with_start(current))
    imageclips.append(ImageClip("screenshot" + str(i) + ".png").with_start(current).with_position("center").resized(width = 980).with_duration(length[i]))
    current += length[i] + 1

# Get background and combine audioclips and videoclips
finalaudio = audiofileclips[0]
for i in range(len(text) - 1) :
    finalaudio = CompositeAudioClip([finalaudio, audiofileclips[i + 1]])
start_time = randrange(0, 450)
final = VideoFileClip('parkour.mp4')
final = final.subclipped(start_time, start_time + time)
for i in range(len(text)) :
   final = CompositeVideoClip([final, imageclips[i]])
final.audio=finalaudio
final.write_videofile("final.mp4")
print("Video finished!")
