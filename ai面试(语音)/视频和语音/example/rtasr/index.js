(function () {
  // 初始化变量
  let mediaRecorder;
  let recordedChunks = [];
  let stream;
  let iatWS;
  let resultText = "";
  let audioContext;
  let processor;

  // 获取DOM元素
  const startButton = document.getElementById('startButton');
  const endButton = document.getElementById('endButton');
  const userVideo = document.getElementById('userVideo');
  const resultDiv = document.getElementById('result');

  /**
   * 获取websocket url
   */
  function getWebSocketUrl() {
    var url = "wss://rtasr.xfyun.cn/v1/ws";
    var appId = '9d7eafb5';
    var secretKey = '07d0a7de3ccb3116c22b8de9c374b1b2';
    var ts = Math.floor(new Date().getTime() / 1000);
    var signa = hex_md5(appId + ts);
    var signatureSha = CryptoJSNew.HmacSHA1(signa, secretKey);
    var signature = CryptoJS.enc.Base64.stringify(signatureSha);
    signature = encodeURIComponent(signature);
    return `${url}?appid=${appId}&ts=${ts}&signa=${signature}`;
  }

  function renderResult(resultData) {
    try {
      let jsonData = JSON.parse(resultData);
      console.log("收到识别结果:", jsonData);
      
      if (jsonData.action == "started") {
        console.log("语音识别连接成功");
      } else if (jsonData.action == "result") {
        const data = JSON.parse(jsonData.data);
        console.log("解析后的识别数据:", data);
        
        if (data.cn && data.cn.st) {
          let tempResult = "";
          // 确保rt存在
          if (data.cn.st.rt) {
            data.cn.st.rt.forEach((j) => {
              if (j.ws) {
                j.ws.forEach((k) => {
                  if (k.cw) {
                    k.cw.forEach((l) => {
                      if (l.w) {
                        tempResult += l.w;
                      }
                    });
                  }
                });
              }
            });
          }
          
          console.log("当前识别文本:", tempResult);
          console.log("识别类型:", data.cn.st.type);
          
          // type为0表示最终结果
          if (data.cn.st.type == 0) {
            resultText += tempResult;
            console.log("累积的识别结果:", resultText);
          }
          
          // 更新显示，同时显示最终结果和临时结果
          resultDiv.innerHTML = resultText + '<span style="color: #666;">' + tempResult + '</span>';
        } else {
          console.log("数据格式不完整:", data);
        }
      } else if (jsonData.action == "error") {
        console.error("语音识别错误:", jsonData);
        alert("语音识别出错：" + (jsonData.desc || "未知错误"));
      }
    } catch (err) {
      console.error("处理识别结果出错:", err, "原始数据:", resultData);
    }
  }

  function connectWebSocket() {
    const websocketUrl = getWebSocketUrl();
    if ("WebSocket" in window) {
      iatWS = new WebSocket(websocketUrl);
    } else {
      alert("浏览器不支持WebSocket，请使用现代浏览器");
      return;
    }

    iatWS.onopen = () => {
      console.log("语音识别WebSocket连接已建立");
      // 发送开始帧
      const startFrame = {
        "common": {
          "app_id": "9d7eafb5"
        },
        "business": {
          "language": "zh_cn",
          "domain": "iat",
          "accent": "mandarin",
          "vad_eos": 5000,
          "dwa": "wpgs"
        },
        "data": {
          "status": 0,
          "format": "audio/L16;rate=16000",
          "encoding": "raw"
        }
      };
      console.log("发送开始帧:", startFrame);
      iatWS.send(JSON.stringify(startFrame));
    };

    iatWS.onmessage = (e) => {
      renderResult(e.data);
    };

    iatWS.onerror = (e) => {
      console.error("WebSocket错误:", e);
    };

    iatWS.onclose = () => {
      console.log("WebSocket连接已关闭");
    };
  }

  // 开始面试
  startButton.addEventListener('click', async () => {
    try {
      // 重置状态
      resultText = "";
      resultDiv.innerText = "";
      recordedChunks = [];

      // 获取摄像头和麦克风权限
      stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        }
      });

      // 显示视频流
      userVideo.srcObject = stream;
      await userVideo.play();
      userVideo.muted = true;

      // 初始化视频录制
      mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'video/webm;codecs=vp8,opus'
      });

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          recordedChunks.push(event.data);
        }
      };

      // 开始录制
      mediaRecorder.start(1000);

      // 初始化语音识别
      connectWebSocket();

      // 创建音频处理器
      audioContext = new AudioContext({
        sampleRate: 16000
      });
      const mediaStreamSource = audioContext.createMediaStreamSource(stream);
      processor = audioContext.createScriptProcessor(2048, 1, 1);

      mediaStreamSource.connect(processor);

      // 处理音频数据
      processor.onaudioprocess = (e) => {
        if (iatWS && iatWS.readyState === WebSocket.OPEN) {
          const inputData = e.inputBuffer.getChannelData(0);
          // 将音频数据转换为16位整数
          const output = new Int16Array(inputData.length);
          for (let i = 0; i < inputData.length; i++) {
            output[i] = Math.max(-1, Math.min(1, inputData[i])) * 0x7FFF;
          }
          // 发送音频数据
          if (iatWS.bufferedAmount === 0) {
            iatWS.send(output.buffer);
          }
        }
      };

      // 更新按钮状态
      startButton.disabled = true;
      endButton.disabled = false;

    } catch (err) {
      console.error('获取媒体设备失败:', err);
      alert('无法访问摄像头或麦克风，请确保已授予权限。');
    }
  });

  // 结束面试
  endButton.addEventListener('click', () => {
    // 停止视频录制
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    }

    // 关闭WebSocket连接
    if (iatWS && iatWS.readyState === WebSocket.OPEN) {
      // 发送结束帧
      iatWS.send(JSON.stringify({
        "data": {
          "status": 2,
          "format": "audio/L16;rate=16000",
          "encoding": "raw"
        }
      }));
      iatWS.close();
    }

    // 清理音频处理器
    if (processor && audioContext) {
      processor.disconnect();
      audioContext.close();
    }

    // 停止所有媒体轨道
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
    }

    // 保存视频文件
    mediaRecorder.onstop = () => {
      const blob = new Blob(recordedChunks, {
        type: 'video/webm'
      });
      const videoUrl = URL.createObjectURL(blob);
      
      // 创建下载链接
      const a = document.createElement('a');
      a.href = videoUrl;
      a.download = `interview-${new Date().toISOString()}.webm`;
      a.click();

      // 保存文字记录
      const textContent = resultDiv.textContent;
      const textBlob = new Blob([textContent], { type: 'text/plain' });
      const textUrl = URL.createObjectURL(textBlob);
      
      const textLink = document.createElement('a');
      textLink.href = textUrl;
      textLink.download = `interview-transcript-${new Date().toISOString()}.txt`;
      textLink.click();
    };

    // 更新按钮状态
    startButton.disabled = false;
    endButton.disabled = true;
  });
})();
