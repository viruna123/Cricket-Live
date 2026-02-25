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
        print("ERROR: STREAM_KEY is not set in GitHub Secrets!")
        exit(1)

    while True:
        try:
            data = get_data()
            v1, v2, audio = data['video1'], data['video2'], data['audio']
            ticker, title = data['ticker_text'], data['overlay_title']

            print("Starting Stream with Ultimate Audio Balance... 🏏")
            
            # volume=3.0 -> මැච් එකේ සද්දේ 300% කින් වැඩි කරා
            # volume=0.02 -> සින්දුවේ සද්දේ 2% දක්වාම අඩු කරා (පසුබිමෙන් හීනියට ඇහෙන්න)
            
            cmd = (
                f'ffmpeg -re -stream_loop -1 -i "{v1}" -stream_loop -1 -i "{v2}" -stream_loop -1 -i "{audio}" '
                f'-filter_complex "[0:v]scale=1280:720,setsar=1[v1_scaled]; '
                f'[1:v]scale=1280:720,setsar=1[v2_scaled]; '
                f'[v1_scaled][v2_scaled]concat=n=2:v=1[v_base]; '
                f'[0:a][1:a]concat=n=2:v=0:a=1,volume=3.0[v_audio]; '
                f'[2:a]volume=0.32[bg_audio]; '
                f'[v_audio][bg_audio]amix=inputs=2:duration=longest:dropout_transition=0[a_final]; '
                f'[v_base]drawtext=text=\'{title}\':x=20:y=20:fontsize=30:fontcolor=yellow:box=1:boxcolor=black@0.6, '
                f'drawtext=text=\'{ticker}\':x=w-mod(t*100\\,w+tw):y=h-50:fontsize=25:fontcolor=white:box=1:boxcolor=black@0.7[v_final]" '
                f'-map "[v_final]" -map "[a_final]" -c:v libx264 -preset ultrafast -tune zerolatency '
                f'-b:v 2500k -maxrate 2500k -bufsize 5000k -g 60 '
                f'-c:a aac -b:a 128k -f flv {YOUTUBE_URL}/{STREAM_KEY}'
            )
            os.system(cmd)
        except Exception as e:
            print(f"Stream encountered an error: {e}")
        
        print("Restarting stream in 5 seconds...")
        time.sleep(5)

# ---------------------------------------------------------
# මෙන්න මේ පේළිය වෙනස් කරලා Commit කරන්න (උදා: 1 වෙනුවට 2 දාන්න)
# එතකොට කිසිම Risk එකක් නැතුව Stream එක Auto Restart වෙනවා.
# Restart count: 1
# ---------------------------------------------------------
