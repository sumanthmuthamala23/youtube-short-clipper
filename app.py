import os
import streamlit as st
import yt_dlp
from moviepy.editor import VideoFileClip
import zipfile
import glob

st.set_page_config(page_title="The DAAN Kids - Shorts Clipper", page_icon="🎬", layout="centered")

if os.path.exists("logo.png"):
    st.image("logo.png", width=220)

st.title("🎬 The DAAN Kids - YouTube Shorts Clipper")
st.write("Paste any children's trending YouTube video link below to slice it into multiple vertical YouTube Shorts instantly for free!")

youtube_url = st.text_input("Paste YouTube Video URL:")
num_shorts = st.slider("Select number of shorts to generate:", min_value=3, max_value=10, value=5)
duration_sec = st.slider("Duration of each short (seconds):", min_value=15, max_value=60, value=30)

if st.button("Generate Shorts"):
    if not youtube_url:
        st.error("Please enter a valid YouTube URL.")
    else:
        with st.spinner("Downloading and processing video... Please wait."):
            for f in glob.glob("output_*.mp4") + glob.glob("downloaded_video.mp4") + glob.glob("shorts.zip"):
                if os.path.exists(f):
                    os.remove(f)

            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': 'downloaded_video.mp4',
                'noplaylist': True,
                'merge_output_format': 'mp4',
                'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
            }
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([youtube_url])
            except Exception as e:
                st.error(f"Error downloading video: {e}")
                st.stop()

            downloaded_file = "downloaded_video.mp4"
            if not os.path.exists(downloaded_file):
                possible_files = glob.glob("downloaded_video.*")
                if possible_files:
                    downloaded_file = possible_files[0]

            if os.path.exists(downloaded_file):
                clip = VideoFileClip(downloaded_file)
                total_duration = int(clip.duration)
                
                generated_files = []
                step = max(1, (total_duration - duration_sec) // max(1, num_shorts))
                
                for i in range(num_shorts):
                    start_time = i * step
                    if start_time + duration_sec > total_duration:
                        start_time = max(0, total_duration - duration_sec)
                    
                    end_time = start_time + duration_sec
                    subclip = clip.subclip(start_time, end_time)
                    
                    w, h = subclip.size
                    if w > h:
                        new_w = int(h * (9 / 16))
                        x1 = (w - new_w) // 2
                        subclip = subclip.crop(x1=x1, y1=0, x2=x1 + new_w, y2=h)
                    
                    output_filename = f"output_short_{i+1}.mp4"
                    subclip.write_videofile(output_filename, codec="libx264", audio_codec="aac", fps=24, logger=None)
                    generated_files.append(output_filename)
                
                clip.close()

                with zipfile.ZipFile("shorts.zip", "w") as zipf:
                    for file in generated_files:
                        zipf.write(file)

                st.success("🎉 Shorts generated successfully!")
                
                with open("shorts.zip", "rb") as fp:
                    st.download_button(
                        label="📦 Download All Shorts (.zip)",
                        data=fp,
                        file_name="the_daan_kids_shorts.zip",
                        mime="application/zip"
                    )
            else:
                st.error("Failed to download video file. Please check the URL.")
