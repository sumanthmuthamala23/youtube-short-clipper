import os
import subprocess
import streamlit as st
from yt_dlp import YoutubeDL
import imageio_ffmpeg

st.set_page_config(
    page_title="The DAAN Kids - Shorts Clipper", page_icon="🎬", layout="centered"
)

if os.path.exists("logo.png"):
  st.image("logo.png", width=120)

st.title("The DAAN Kids - Shorts Clipper")
st.markdown(
    "Transform long children's videos into multiple 9:16 vertical Shorts!"
)

input_mode = st.radio(
    "Select Input Source:", ("YouTube Video URL", "Upload/Attach Video File")
)

video_path = "source_video.mp4"

if input_mode == "YouTube Video URL":
  url = st.text_input("Paste YouTube Video URL:")
  if st.button("Download & Process Video"):
    if not url:
      st.warning("Please enter a valid YouTube video URL.")
    else:
      with st.spinner("Downloading video with robust client bypass..."):
        ydl_opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": video_path,
            "cookiefile": "cookies.txt" if os.path.exists("cookies.txt") else None,
            "extractor_args": {"youtube": {"player_client": ["ios", "android"]}},
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "noplaylist": True,
        }
        try:
          with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
          st.success("Video downloaded successfully!")
        except Exception as e:
          st.error(
              f"Download failed due to YouTube restriction (403): {e}. Please"
              " use 'Upload/Attach Video File' instead!"
          )

else:
  uploaded_file = st.file_uploader(
      "Upload Video File (MP4, MOV)", type=["mp4", "mov", "avi"]
  )
  if uploaded_file is not None:
    with open(video_path, "wb") as f:
      f.write(uploaded_file.getbuffer())
    st.success("Video uploaded successfully!")

if os.path.exists(video_path):
  st.subheader("🎬 Generate Multiple Vertical Shorts (9:16)")

  clip_duration = st.slider(
      "Duration per Short (seconds):", min_value=15, max_value=60, value=30, step=5
  )

  if st.button("Split into Multiple Shorts"):
    with st.spinner(
        "Slicing video into vertical 9:16 shorts... Please wait."
    ):
      output_pattern = "short_%03d.mp4"
      for f in os.listdir("."):
        if f.startswith("short_") and f.endswith(".mp4"):
          os.remove(f)

      ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
      cmd = [
          ffmpeg_exe,
          "-y",
          "-i",
          video_path,
          "-vf",
          (
              "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2"
          ),
          "-f",
          "segment",
          "-segment_time",
          str(clip_duration),
          "-c:v",
          "libx264",
          "-c:a",
          "aac",
          output_pattern,
      ]

      try:
        subprocess.run(cmd, check=True, stderr=subprocess.PIPE)
        st.success("Successfully generated multiple shorts!")
      except subprocess.CalledProcessError as e:
        st.error(
            "Error generating shorts:"
            f" {e.stderr.decode('utf-8', errors='ignore')}"
        )

  shorts = sorted(
      [f for f in os.listdir(".") if f.startswith("short_") and f.endswith(".mp4")]
  )
  if shorts:
    st.markdown("### 📥 Download Your Shorts")
    for idx, short_file in enumerate(shorts, 1):
      col1, col2 = st.columns([2, 1])
      with col1:
        st.text(f"Short #{idx} ({short_file})")
        st.video(short_file)
      with col2:
        with open(short_file, "rb") as sf:
          st.download_button(
              label=f"Download #{idx}",
              data=sf,
              file_name=f"daan_kids_short_{idx}.mp4",
              mime="video/mp4",
              key=f"dl_{idx}",
          )
