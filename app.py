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
    "Paste any children's YouTube video link below to slice it into multiple"
    " vertical YouTube Shorts instantly!"
)

# User Inputs
url = st.text_input("Paste YouTube Video URL:")
num_shorts = st.slider("Select number of shorts to generate:", 1, 10, 5)
clip_duration = st.slider(
    "Duration of each short (seconds):", 10, 60, 30
)  # standard 30s for kids shorts

if st.button("Generate Shorts"):
  if not url:
    st.warning("Please enter a valid YouTube video URL.")
  else:
    with st.spinner("Downloading and processing video... Please wait."):
      output_template = "downloaded_video.mp4"

      # Clean up previous downloads if any
      if os.path.exists(output_template):
        os.remove(output_template)

      # yt-dlp configuration with cookies support
      ydl_opts = {
          "format": "bv*+ba/b",
          "outtmpl": output_template,
          "cookiefile": "cookies.txt" if os.path.exists("cookies.txt") else None,
          "noplaylist": True,
      }

      try:
        with YoutubeDL(ydl_opts) as ydl:
          ydl.download([url])

        if not os.path.exists(output_template):
          st.error(
              "Download failed. Please check the URL or your cookies file."
          )
        else:
          # Process video clipping using moviepy
          clip = VideoFileClip(output_template)
          total_duration = clip.duration

          st.success(
              f"Video downloaded successfully! Total duration:"
              f" {int(total_duration)}s"
          )

          # Calculate start times evenly spaced
          interval = max(
              1, (total_duration - clip_duration) / max(1, num_shorts)
          )

          for i in range(num_shorts):
            start_time = i * interval
            end_time = min(start_time + clip_duration, total_duration)

            if start_time >= total_duration:
              break

            subclip = clip.subclip(start_time, end_time)

            # Crop to vertical 9:16 aspect ratio for Shorts/Reels
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
        st.error(f"Error processing video: {e}")
