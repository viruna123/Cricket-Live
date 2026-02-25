import os
import json
import time

def get_data():
    with open('index.json', 'r') as f:
        return json.load(f)

if __name__ == "__main__":
    YOUTUBE_URL = "rtmp://a.rtmp.youtube.com/live2"
    STREAM_KEY = os.getenv("STREAM_KEY")
    
    if not STREAM_KEY:
        print("ERROR: STREAM_KEY is not set!")
        exit(1)

    while True:
        try:
            data = get_data()
            v1, v2, audio = data['video1'], data['video2'], data['audio']
            ticker, title = data['ticker_text'], data['overlay_title']

            print("Starting Stream with Aspect Ratio Fix... 🛠️🏏")
            
            # setsar=1:1 සහ scale පාවිච්චි කරලා වීඩියෝ දෙකම එකම මට්ටමට ගත්තා
            # force_original_aspect_ratio=decrease: වීඩියෝ එක ඇද නොවී තියාගන්නවා
            
            cmd = (
                f'ffmpeg -re -stream_loop -1 -i "{v1}" -stream_loop -1 -i "{v2}" -stream_loop -1 -i "{audio}" '
                f'-filter_complex "[0:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p[v1s]; '
                f'[1:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p[v2s]; '
                f'[v1s][v2s]concat=n=2:v=1:a=0[v_base]; '
                f'[v_base]drawtext=text=\'{title}\':x=20:y=20:fontsize=30:fontcolor=yellow:box=1:boxcolor=black@0.6, '
                f'drawtext=text=\'{ticker}\':x=w-mod(t*100\\,w+tw):y=h-50:fontsize=25:fontcolor=white:box=1:boxcolor=black@0.7[vf]; '
                f'[0:a][1:a]concat=n=2:v=0:a=1,volume=3.0[a_match]; '
                f'[2:a]volume=0.02[a_bg]; '
                f'[a_match][a_bg]amix=inputs=2:duration=longest[af]" '
                f'-map "[vf]" -map "[af]" -c:v libx264 -preset ultrafast -tune zerolatency -threads 0 '
                f'-b:v 1200k -maxrate 1200k -bufsize 2400k -g 60 '
                f'-c:a aac -b:a 128k -f flv {YOUTUBE_URL}/{STREAM_KEY}'
            )
            os.system(cmd)
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(5)

# Restart count: 10
