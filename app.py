import os
import streamlit as st
from yt_dlp import YoutubeDL

st.set_page_config(
    page_title="The DAAN Kids - Shorts Clipper", page_icon="🎬", layout="centered"
)

if os.path.exists("logo.png"):
  st.image("logo.png", width=120)

st.title("The DAAN Kids - Shorts Clipper")
st.markdown("Transform children's videos into YouTube Shorts & Reels instantly!")

input_mode = st.radio(
    "Select Input Source:", ("YouTube Video URL", "Upload/Attach Video File")
)

video_path = "processed_video.mp4"

if os.path.exists(video_path):
  try:
    os.remove(video_path)
  except:
    pass

target_file = None

if input_mode == "YouTube Video URL":
  url = st.text_input("Paste YouTube Video URL:")

  if st.button("Download Video"):
    if not url:
      st.warning("Please enter a valid YouTube video URL.")
    else:
      with st.spinner("Downloading video with yt-dlp... Please wait."):
        ydl_opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": video_path,
            "cookiefile": "cookies.txt" if os.path.exists("cookies.txt") else None,
            "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
            "noplaylist": True,
        }
        try:
          with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
          target_file = video_path
          st.success("Video downloaded successfully!")
        except Exception as e:
          st.error(f"Error downloading video: {e}")

else:
  uploaded_file = st.file_uploader(
      "Attach/Upload Video File (MP4, MOV, AVI)", type=["mp4", "mov", "avi"]
  )
  if uploaded_file is not None:
    with open(video_path, "wb") as f:
      f.write(uploaded_file.getbuffer())
    target_file = video_path
    st.success("Video uploaded successfully!")

if target_file and os.path.exists(target_file):
  st.subheader("Preview Video")
  st.video(target_file)

  with open(target_file, "rb") as file:
    st.download_button(
        label="Download Video File",
        data=file,
        file_name="the_daan_kids_video.mp4",
        mime="video/mp4",
    )
