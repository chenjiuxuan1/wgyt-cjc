import axios from 'axios';

class TTSService {
  constructor() {
    this.isSpeaking = false;
    this.audioContext = null;
  }

  async speak(text, onStart, onEnd, onError) {
    if (this.isSpeaking) {
      console.log('等待当前语音播放完成...');
      return;
    }

    try {
      console.log('开始播放语音:', text);
      this.isSpeaking = true;
      onStart && onStart();

      const response = await axios.post('http://localhost:5000/tts', { text });
      const { audio: audioBase64 } = response.data;

      // 将 base64 转换为 ArrayBuffer
      const binaryString = window.atob(audioBase64);
      const len = binaryString.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      const audioData = bytes.buffer;

      if (!this.audioContext) {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      }

      const audioBuffer = await this.audioContext.decodeAudioData(audioData);
      const source = this.audioContext.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(this.audioContext.destination);

      source.onended = () => {
        console.log('语音播放结束');
        this.isSpeaking = false;
        onEnd && onEnd();
      };

      source.start(0);
    } catch (error) {
      console.error('语音播报失败:', error);
      this.isSpeaking = false;
      onError && onError(error);
    }
  }

  cleanup() {
    if (this.audioContext) {
      this.audioContext.close();
    }
  }
}

export default new TTSService(); 