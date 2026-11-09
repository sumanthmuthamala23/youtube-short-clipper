import os
import streamlit as st
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip

# Page Configuration
st.set_page_config(
    page_title="The DAAN Kids - Shorts Clipper", page_icon="🎬", layout="centered"
)

# App Header
if os.path.exists("logo.png"):
  st.image("logo.png", width=120)

st.title("The DAAN Kids - Shorts Clipper")
st.markdown(
    "Transform children's videos into engaging vertical YouTube Shorts & Reels"
    " instantly!"
)

# Input Mode Selection: YouTube Link or File Upload
input_mode = st.radio(
    "Select Input Source:", ("YouTube Video URL", "Upload/Attach Video File")
)

video_path = "processed_video.mp4"

# Clean up previous temp video
if os.path.exists(video_path):
  try:
    os.remove(video_path)
  except:
    pass

target_file = None

if input_mode == "YouTube Video URL":
  url = st.text_input("Paste YouTube Video URL:")
  num_shorts = st.slider("Select number of shorts to generate:", 1, 10, 5)
  clip_duration = st.slider("Duration of each short (seconds):", 10, 60, 30)

  if st.button("Generate Shorts from YouTube"):
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
        except Exception as e:
          st.error(f"Error downloading video: {e}")

else:
  uploaded_file = st.file_uploader(
      "Attach/Upload Video File (MP4, MOV, AVI)",
      type=["mp4", "mov", "avi"],
      key="video_upload",
  )
  num_shorts = st.slider(
      "Select number of shorts to generate:", 1, 10, 5, key="up_num"
  )
  clip_duration = st.slider(
      "Duration of each short (seconds):", 10, 60, 30, key="up_dur"
  )

  if uploaded_file is not None:
    with open(video_path, "wb") as f:
      f.write(uploaded_file.getbuffer())
    target_file = video_path

  if st.button("Generate Shorts from Attached File"):
    if uploaded_file is None:
      st.warning("Please attach or upload a video file first.")
    else:
      target_file = video_path

# Process Video and Slice Shorts
if target_file and os.path.exists(target_file):
  with st.spinner("Processing and slicing video clips... Please wait."):
    try:
      clip = VideoFileClip(target_file)
      total_duration = clip.duration

      st.success(
          f"Video loaded successfully! Total duration: {int(total_duration)}s"
      )

      interval = max(1, (total_duration - clip_duration) / max(1, num_shorts))

      for i in range(num_shorts):
        start_time = i * interval
        end_time = min(start_time + clip_duration, total_duration)

        if start_time >= total_duration:
          break

        subclip = clip.subclip(start_time, end_time)

        # Crop to vertical 9:16 aspect ratio
        w, h = subclip.size
        target_w = int(h * (9 / 16))
        if target_w < w:
          x1 = (w - target_w) / 2
          subclip = subclip.crop(x1=x1, x2=x1 + target_w)

        output_filename = f"short_{i+1}.mp4"
        subclip.write_videofile(
            output_filename,
            codec="libx264",
            audio_codec="aac",
            preset="fast",
            logger=None,
        )

        st.subheader(f"Short {i+1} ({int(start_time)}s - {int(end_time)}s)")
        st.video(output_filename)

        with open(output_filename, "rb") as file:
          st.download_button(
              label=f"Download Short {i+1}",
              data=file,
              file_name=f"the_daan_kids_short_{i+1}.mp4",
              mime="video/mp4",
              key=f"download_{i}",
          )

      clip.close()
    except Exception as e:
      st.error(f"Error processing video clips: {e}")
