import streamlit as st
import pandas as pd
import youtube_dl
import requests
import pprint
from configure import auth_key
from time import sleep

if "status" not in st.session_state:
    st.session_state["status"] = "submitted"

ydl_opts = {
    "format": "bestaudio/best",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "prefferedquality": "192",
        }
    ],
    "ffmpeg-location": "./",
    "outtmpl": "./%(id)s.%(ext)s",
}

transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
upload_endpoint = "https://api.assemblyai.com/v2/upload"
headers_auth_only = {"authorization": auth_key}
headers = {"authorization": auth_key, "content-type": "application/json"}
CHUNK_SIZE = 5242880


@st.cache
def transcribe_from_link(link, categories):
    _id = link.strip()

    def get_vid(_id):
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(_id)

    meta = get_vid(_id)
    save_location = meta["id"] + ".mp3"

    def read_file(filename):
        with open(filename, "r") as _file:
            while True:
                data = _file.read(CHUNK_SIZE)
                if not data:
                    break
                yield data


option = st.selectbox(
    "Live today", ("Manchester United vs Brighton", "Chelsea vs Brentford")
)

st.write("You selected:", option)
