# This Python file uses the following encoding: utf-8

import json
import subprocess
import time
from typing import Iterator

import requests

group_id = '1911946946881265729'    #请输入您的group_id
api_key = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiLpmYjmsZ_lt50iLCJVc2VyTmFtZSI6IumZiOaxn-W3nSIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxOTExOTQ2OTQ2ODg5NjU0MzM3IiwiUGhvbmUiOiIxNTMzMDQ3MDE3NSIsIkdyb3VwSUQiOiIxOTExOTQ2OTQ2ODgxMjY1NzI5IiwiUGFnZU5hbWUiOiIiLCJNYWlsIjoiIiwiQ3JlYXRlVGltZSI6IjIwMjUtMDQtMTUgMTY6NDQ6MDciLCJUb2tlblR5cGUiOjEsImlzcyI6Im1pbmltYXgifQ.oGOP1sP4pvYUFNqWYao04AXGq4HBhE4r4xbF72GYF-qTVZ4ep1yTFolmHykQTrMG7rOPMaQEiz3Kn-9JopMq2ucAqzYM3rEp37Y18zu_QI2J4iy0W7YQc5AnD8JwE7bI3FHbosUELxvndJlrP3LaBZZ5wH8adUhXPL9ALVeNdBl2j5oIts4pv06zAk-b5WP_I5KMYE1pqKlsWquATu-u5ON-fOIDJ_7AJsawV0xEM-xdNiJERv3lldG0mkErOEdhjL14r0T3WEA29Eay37eTeg6MdT5HQGuqr642XTQvkSiRyZeNNPbYH-sojRjTI_cijkWIvYHfooOYOn-vY34kkw'    #请输入您的api_key

file_format = 'mp3'  # 支持 mp3/pcm/flac

url = "https://api.minimax.chat/v1/t2a_v2?GroupId=" + group_id
headers = {"Content-Type":"application/json", "Authorization":"Bearer " + api_key}


def build_tts_stream_headers() -> dict:
    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'authorization': "Bearer " + api_key,
    }
    return headers


def build_tts_stream_body(text: str) -> dict:
    body = json.dumps({
        "model":"speech-02-turbo",
        "text": text,
        "stream":True,
        "voice_setting":{
            "voice_id":"female-shaonv",
            "speed":1.0,
            "vol":1.0,
            "pitch":0
        },
        "pronunciation_dict":{
            "tone":[
                "处理/(chu3)(li3)", "危险/dangerous"
            ]
        },
        "audio_setting":{
            "sample_rate":32000,
            "bitrate":128000,
            "format":"mp3",
            "channel":1
        }
    })
    return body


mpv_command = ["E:\\mpv\\mpv-x86_64\\mpv.exe", "--no-cache", "--no-terminal", "--", "fd://0"]
mpv_process = subprocess.Popen(
    mpv_command,
    stdin=subprocess.PIPE,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)


def call_tts_stream(text: str) -> Iterator[bytes]:
    tts_url = url
    tts_headers = build_tts_stream_headers()
    tts_body = build_tts_stream_body(text)

    response = requests.request("POST", tts_url, stream=True, headers=tts_headers, data=tts_body)
    for chunk in (response.raw):
        if chunk:
            if chunk[:5] == b'data:':
                data = json.loads(chunk[5:])
                if "data" in data and "extra_info" not in data:
                    if "audio" in data["data"]:
                        audio = data["data"]['audio']
                        yield audio


def audio_play(audio_stream: Iterator[bytes]) -> bytes:
    audio = b""
    for chunk in audio_stream:
        if chunk is not None and chunk != '\n':
            decoded_hex = bytes.fromhex(chunk)
            mpv_process.stdin.write(decoded_hex)  # type: ignore
            mpv_process.stdin.flush()
            audio += decoded_hex

    return audio


audio_chunk_iterator = call_tts_stream('')
audio = audio_play(audio_chunk_iterator)

# 结果保存至文件
timestamp = int(time.time())
file_name = f'output_total_{timestamp}.{file_format}'
with open(file_name, 'wb') as file:
    file.write(audio)