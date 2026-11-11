import os
import subprocess
import streamlit as st
from yt_dlp import YoutubeDL
import imageio_ffmpeg

st.set_page_config(
    page_title="The DAAN Kids - Shorts Clipper", page_icon="🎬", layout="wide"
)

if os.path.exists("logo.png"):
  st.image("logo.png", width=120)

st.title("The DAAN Kids - Shorts Clipper")
st.markdown(
    "Transform long children's videos into multiple 9:16 vertical Shorts"
    " seamlessly!"
)
st.markdown("---")

video_path = "source_video.mp4"
active_source = None

# Side-by-side layout for YouTube URL and File Upload
col_url, col_upload = st.columns(2, gap="large")

with col_url:
  st.subheader("🔗 Option A: YouTube Video URL")
  st.markdown(
      "Paste a YouTube link to analyze and download for shorts creation."
  )
  url = st.text_input("YouTube Video URL:", key="yt_url_input")
  if st.button("Download & Process URL", key="dl_btn"):
    if not url:
      st.warning("Please enter a valid YouTube video URL.")
    else:
      with st.spinner(
          "Downloading video with robust client bypass... Please wait."
      ):
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
          st.success("YouTube video downloaded successfully!")
          active_source = video_path
        except Exception as e:
          st.error(
              f"Download restricted by YouTube (403): {e}. Please use Option B"
              " (Upload File) below!"
          )

with col_upload:
  st.subheader("📁 Option B: Upload Video File")
  st.markdown(
      "Attach a local video file directly from your device storage."
  )
  uploaded_file = st.file_uploader(
      "Choose video file (MP4, MOV, AVI)",
      type=["mp4", "mov", "avi"],
      key="file_up",
  )
  if uploaded_file is not None:
    with open(video_path, "wb") as f:
      f.write(uploaded_file.getbuffer())
    st.success("Video uploaded successfully!")
    active_source = video_path

# Check if video is loaded and available
if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
  st.markdown("---")
  st.subheader("🎬 Smart Timeline & Shorts Studio")

  # Calculate video duration for intelligent suggestions
  try:
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    probe_cmd = [
        ffmpeg_exe,
        "-i",
        video_path,
    ]
    result = subprocess.run(
        probe_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True
    )
    # Parse duration from ffmpeg output
    duration_sec = 60  # default fallback
    for line in result.stderr.split("\n"):
      if "Duration:" in line:
        parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
        duration_sec = (
            int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        )

    est_shorts = int(duration_sec // 30)
    st.success(
        f"💡 **Timeline Analysis:** Total video length is"
        f" **{int(duration_sec)} seconds**. Recommended strategy: Split into"
        f" **{est_shorts if est_shorts > 0 else 1} shorts** of **30 seconds"
        " each** for optimal viewer retention on YouTube Shorts & Instagram"
        " Reels."
    )
  except Exception:
    st.info(
        "💡 **Suggestion:** 30-second clips are the sweet spot for children's"
        " shorts and reels."
    )

  clip_duration = st.slider(
      "Select Duration per Short (seconds):",
      min_value=15,
      max_value=60,
      value=30,
      step=5,
  )

  if st.button("🚀 Split into Multiple Shorts", key="split_btn"):
    with st.spinner(
        "Slicing video into vertical 9:16 shorts with optimal timing..."
    ):
      output_pattern = "short_%03d.mp4"
      for f in os.listdir("."):
        if f.startswith("short_") and f.endswith(".mp4"):
          os.remove(f)

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
    st.markdown("---")
    st.markdown("### 📥 Download Your Generated Shorts & Social Kit")

    for idx, short_file in enumerate(shorts, 1):
      col_prev, col_dl = st.columns([2, 1])
      with col_prev:
        st.text(f"Short #{idx} ({short_file})")
        st.video(short_file)
      with col_dl:
        with open(short_file, "rb") as sf:
          st.download_button(
              label=f"Download Short #{idx}",
              data=sf,
              file_name=f"daan_kids_short_{idx}.mp4",
              mime="video/mp4",
              key=f"dl_{idx}",
          )

    st.markdown("---")
    st.markdown("### 📋 Ready-to-Post Social Media Kit")
    st.markdown(
        "Copy and paste these suggested captions and tags for your YouTube"
        " Shorts and Instagram Reels:"
    )

    st.text_area(
        "YouTube Shorts Title & Description:",
        value=(
            "Magical Adventures & Fun Learning with The DAAN Kids! #shorts\n\nWelcome"
            " to The DAAN Kids! 🌟 Dive into delightful stories, joyful"
            " animations, and exciting learning adventures made specially for"
            " children. Subscribe for daily wholesome content! 🚀\n\nTags:"
            " #TheDAANKids #KidsShorts #ChildrenStories #FunLearning"
            " #KidsEntertainment"
        ),
        height=130,
    )

    st.text_area(
        "Instagram Reels Caption & Hashtags:",
        value=(
            "Bringing smiles, curiosity, and wholesome adventures to your little"
            " ones! ✨ Drop a ❤️ if your child enjoys stories like this!\n\n#TheDAANKids"
            " #KidsReels #ParentingLife #ToddlerFun #KidsActivities"
            " #WholesomeContent #KidsStories"
        ),
        height=110,
    )
