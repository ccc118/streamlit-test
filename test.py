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


@st.cache_data
def transcribe_from_link(link, categories):
    if link == "":
        return

    _id = link.strip()

    def get_vid(_id):
        video = YouTube(_id)
        video = video.streams.get_highest_resolution()

        try:
            print("Downloading")
            path = video.download()
        except:
            path = None
            print("Failed to download video")
        return path

    save_location = get_vid(_id)

    def read_file(filename):
        with open(filename, "rb") as _file:
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

def get_status(polling_endpoint):
    polling_response = requests.get(polling_endpoint, headers=headers)
    st.session_state['status'] = polling_response.json()['status']

def refresh_state():
    st.session_state['status']='submitted'
    

st.title("Tester")
link = st.text_inpsut("Enter your youtube link below", "", on_change=refresh_state)
polling_endpoint = transcribe_from_link(link, False)
st.video(link) 
st.text('The transcription is ' +  st.session_state["status"])

st.button('check_status', on_click=get_status, args=(polling_endpoint,))
transcript=''
if st.session_state['status'] =='completed':
    polling_response = requests.get(polling_endpoint, headers=headers)
    transcript = polling_response.json()['text']
st.markdown(transcript)

option = st.selectbox(
    "Live today", ("Manchester United vs Brighton", "Chelsea vs Brentford")
)

st.write("You selected:", option)
