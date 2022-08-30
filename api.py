import requests
from api_secrets import API_KEY_ASSEMBLY
from time import sleep
import json 
import youtube_dl

transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
assemblyai_headers = {'authorization': API_KEY_ASSEMBLY}


def get_video_info(url):
    ytd = youtube_dl.YoutubeDL()
    with ytd:
        result = ytd.extract_info(url, download=False)
    
    if 'entries' in result:
        return result['entries'][0]
    return result

def get_audio_url(video_url):
    video_info = get_video_info(video_url)
    for f in video_info['formats']:
        if f['ext']=='m4a':
            audio_url = f['url']
            break
    video_id = video_info['id']
    video_title = video_info['title']
    video_thumbnail = video_info['thumbnail']
    return audio_url,video_id,video_title,video_thumbnail


#transcription
def transcribe(audio_url,auto_chapters):
    transcript_request = {
        "audio_url": audio_url,
        "auto_chapters":auto_chapters
        }
    
    transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=assemblyai_headers)
    job_id = transcript_response.json()['id']
    return job_id


#poll
def poll(transcript_id):
    polling_endpoint = transcript_endpoint + '/' + transcript_id
    polling_response = requests.get(polling_endpoint, headers=assemblyai_headers)
    return polling_response.json()

def get_transcript_result(audio_url,auto_chapters):
    transcript_id = transcribe(audio_url,auto_chapters)

    while True:
        data = poll(transcript_id)
        if data['status'] == 'completed':
            return data, None
        elif data['status'] == 'error':
            return  None, data['error']
        print(' > Transcription is still processing! Sleeping 60 seconds...')
        sleep(60)

#save
def save_transcript(video_url):
    chapters_filename = 'data/' + video_url.split('?v=')[1] + '_chapters.json'
    transcript_filename = 'data/' + video_url.split('?v=')[1] + '_transcript.txt'

    audio_url,video_id,video_title,video_thumbnail = get_audio_url(video_url)
   
    data, error = get_transcript_result(audio_url,auto_chapters=True)

    if data is not None:
        with open(transcript_filename, 'w') as f:
            f.write(data['text'])
        
        with open(chapters_filename, 'w') as f:
            chapters = data['chapters']
            video_data = {'chapters':chapters}
            video_data['video_thumbnail'] = video_thumbnail
            video_data['video_title'] = video_title
            video_data['video_id'] = video_id

            json.dump(video_data, f, indent=4)
            
            print('Results saved! check',chapters_filename)
            return True
    elif error:
        print('Error!!', error)
        return False


def get_clean_time(start_ms):
    seconds = int((start_ms / 1000) % 60)
    minutes = int((start_ms / (1000*60) ) % 60)
    hours = int((start_ms / (1000*60*60) ) % 24)
    if hours>0:
        return f'{hours:02d}:{minutes:02d}:{seconds:02d}'
    else:
        return f'{minutes:02d}:{seconds:02d}'