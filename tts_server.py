from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import base64
import io
from yycs import call_tts_stream, audio_play

app = Flask(__name__)
CORS(app)

@app.route('/tts', methods=['POST'])
def text_to_speech():
    try:
        data = request.json
        text = data.get('text', '')
        
        # 调用 yycs.py 的函数生成语音
        audio_chunk_iterator = call_tts_stream(text)
        audio = audio_play(audio_chunk_iterator)
        
        # 将音频数据转换为 base64
        audio_base64 = base64.b64encode(audio).decode('utf-8')
        
        return jsonify({
            'success': True,
            'audio': audio_base64
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(port=5000) 