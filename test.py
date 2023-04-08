import streamlit as st
import pandas as pd
from pytube import YouTube
import requests
import pprint
from configure import auth_key
from time import sleep

if "status" not in st.session_state:
    st.session_state["status"] = "submitted"

transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
upload_endpoint = "https://api.assemblyai.com/v2/upload"
headers_auth_only = {"authorization": auth_key}
headers = {"authorization": auth_key, "content-type": "application/json"}
CHUNK_SIZE = 5242880


@st.cache
def transcribe_from_link(link, categories):
    if link == "":
        return 
    
    _id = link.strip()

    def get_vid(_id):
        video = YouTube(_id)
        video = video.streams.get_highest_resolution()

        try:
            print("Downloading")
            video.download("./download.mp4")
        except:
            print("Failed to download video")
    get_vid(_id)
    save_location = "./download.mp4"

    def read_file(filename):
        with open(filename, "r") as _file:
            while True:
                data = _file.read(CHUNK_SIZE)
                if not data:
                    break
                yield data

    upload_response = requests.post(
        upload_endpoint, headers=headers_auth_only, data=read_file(save_location)
    )
    audio_url = upload_response.json()["upload_url"]

    transcript_request = {
        "audio_url": audio_url,
        "iab_categories": "True" if categories else "False",
    }

    transcript_response = requests.post(
        transcript_endpoint, json=transcript_request, headers=headers
    )

    transcript_id = transcript_response.json()["id"]
    polling_endpoint = transcript_endpoint + "/" + transcript_id
    return polling_endpoint


st.title("An easy way to transcribe videos")
link = st.text_input("Enter your youtube link below", "")
transcribe_from_link(link, False)


option = st.selectbox(
    "Live today", ("Manchester United vs Brighton", "Chelsea vs Brentford")
)

st.write("You selected:", option)
