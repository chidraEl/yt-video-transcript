from api import *
import streamlit as st
import json


st.title('Summarize Youtube Videos')
video_url = st.sidebar.text_input('Please enter video url')



button = st.sidebar.button('Summarize', on_click=save_transcript,args=(video_url,))


if button:
    chapters_filename = 'data/' + video_url.split('?v=')[1] + '_chapters.json'
    transcript_filename = 'data/' + video_url.split('?v=')[1] + '_transcript.txt'
    with open(chapters_filename, 'r') as f:
        data = json.load(f)

        chapters = data['chapters']
        video_title=data['video_title']
        thumbnail=data['video_thumbnail']
    
    with open(transcript_filename, 'r') as f:
        transcript_text = f.read()


    st.header(f'{video_title} ')
    st.image(thumbnail)

    st.header('Video Chapters')
    for chap in chapters:
        with st.expander(chap['gist']+ ' | '+get_clean_time(chap['start'])+ ' - '+get_clean_time(chap['end'])):
            chap['summary']
    

    st.header('Video Transcription')
    st.text(transcript_text)
        

# RUN : streamlit run main.py
