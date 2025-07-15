// MiniMax TTS 服务
class MiniMaxTTS {
  constructor() {
    this.isSpeaking = false;
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

      // 调用 Python 服务
      const response = await fetch('http://localhost:5000/tts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text })
      });

      if (!response.ok) {
        throw new Error('语音生成失败');
      }

      // 播放完成的处理
      this.isSpeaking = false;
      onEnd && onEnd();

    } catch (error) {
      console.error('语音播报失败:', error);
      this.isSpeaking = false;
      onError && onError(error);
    }
  }

  cleanup() {
    this.isSpeaking = false;
  }
}

export default new MiniMaxTTS(); 