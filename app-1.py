import streamlit as st
import moviepy.editor as mp
import speech_recognition as sr
from moviepy.editor import VideoFileClip, concatenate_videoclips, clips_array
import os
import tempfile


page_bg_img = """
<style>
[data-testid="stAppViewContainer"]{
background-image: url("https://img.freepik.com/free-vector/network-mesh-wire-digital-technology-background_1017-27428.jpg?w=2000&t=st=1693327404~exp=1693328004~hmac=2639e33069cd4fc4e89a7753e1e51ec4a4839b997781994650ae5b46dacc8797");
background-size:cover;

}



</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)


def merge_letter_videos(word, assets_folder):
    letter_clips = []

    for letter in word:
        letter_lower = letter.lower()
        letter_video_path = os.path.join(assets_folder, f'{letter_lower}.mp4')

        if os.path.isfile(letter_video_path):
            letter_clip = VideoFileClip(letter_video_path)
            letter_clips.append(letter_clip)
        else:
            st.warning(f"No video found for letter: {letter_lower}")

    if not letter_clips:
        st.warning("No valid videos found for the word.")
        return None

    final_clip = concatenate_videoclips(letter_clips)
    return final_clip


def merge_word_videos(words, assets_folder):
    video_clips = []

    for word in words:
        word_lower = word.lower()
        word_video_path = os.path.join(assets_folder, f'{word_lower}.mp4')

        if os.path.isfile(word_video_path):
            video_clip = VideoFileClip(word_video_path)
            video_clips.append(video_clip)
        else:
            st.warning(f"No video found for word: {word_lower}")
            st.info(f"Splitting '{word}' into letters...")
            letter_video = merge_letter_videos(word, assets_folder)
            if letter_video is not None:
                video_clips.append(letter_video)

    if not video_clips:
        st.warning("No valid videos found.")
        return None

    final_clip = concatenate_videoclips(video_clips)
    return final_clip


def extract_audio_as_text(video_path):
    video = mp.VideoFileClip(video_path)
    audio = video.audio

    temp_audio_path = "temp_audio.wav"
    audio.write_audiofile(temp_audio_path)

    r = sr.Recognizer()

    with sr.AudioFile(temp_audio_path) as source:
        audio_data = r.record(source)
        audio_text = r.recognize_google(audio_data)

    return audio_text


def generate_combined_video(extracted_text, uploaded_file, video_path):
    words = extracted_text.split()

    assets_folder = '/Users/vamsikeshwaran/Desktop/assets'

    if st.button("Generate Combined Video"):
        if not words:
            st.warning("Please enter a sentence.")
        else:
            st.info(f"Generating combined video for text: {extracted_text}...")
            video = merge_word_videos(words, assets_folder)

            if video is not None:
                st.success("Combined video generated successfully!")

                continuous_video_path = "output_continuous_video.mp4"
                video.write_videofile(continuous_video_path, codec="libx264")

                uploaded_video = VideoFileClip(video_path)
                uploaded_video = uploaded_video.resize(height=video.h)

                final_video = clips_array([[uploaded_video, video]])

                final_video_path = "final_combined_video.mp4"
                final_video.write_videofile(final_video_path, codec="libx264")

                st.subheader("Generated Combined Video")
                st.video(final_video_path)

                os.remove(continuous_video_path)
                os.remove(video_path)


def main():
    st.title("Sign language generator from a Video")

    uploaded_file = st.file_uploader("Upload a video file", type=["mp4"])

    if uploaded_file is not None:
        st.info("Video uploaded successfully!")

        temp_dir = tempfile.mkdtemp()
        video_path = os.path.join(temp_dir, "temp_video.mp4")

        with open(video_path, "wb") as temp_video_file:
            temp_video_file.write(uploaded_file.read())

        extracted_text = extract_audio_as_text(video_path)

        st.subheader("Extracted Text from Uploaded Video:")
        st.text(extracted_text)

        generate_combined_video(extracted_text, uploaded_file, video_path)


if __name__ == '__main__':
    main()
