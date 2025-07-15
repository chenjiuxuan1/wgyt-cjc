(function () {
  // 初始化变量
  let mediaRecorder;
  let recordedChunks = [];
  let stream;
  let iatWS;
  let resultText = "";
  let audioContext;
  let processor;
  let currentSessionId = null;
  let interviewData = null;
  let currentQuestionId = null;
  let currentQuestion = "";
  let userAnswers = {};
  let currentEditingQaPair = null;

  // 获取DOM元素
  const setupContainer = document.getElementById('setupContainer');
  const interviewContainer = document.getElementById('interviewContainer');
  const reportContainer = document.getElementById('reportContainer');
  const startButton = document.getElementById('startButton');
  const endButton = document.getElementById('endButton');
  const setupButton = document.getElementById('setupButton');
  const submitButton = document.getElementById('submitButton');
  const finishButton = document.getElementById('finishButton');
  const newInterviewButton = document.getElementById('newInterviewButton');
  const userVideo = document.getElementById('userVideo');
  const resultDiv = document.getElementById('result');
  const positionInput = document.getElementById('positionInput');
  const questionsListDiv = document.getElementById('questionsList');
  const reportContentDiv = document.getElementById('reportContent');
  const qaPairsListDiv = document.getElementById('qaPairsList');
  const editQaPairModal = document.getElementById('editQaPairModal');
  const editQuestionText = document.getElementById('editQuestionText');
  const editAnswerText = document.getElementById('editAnswerText');
  const saveQaPairBtn = document.getElementById('saveQaPairBtn');
  const cancelEditButton = document.getElementById('cancelEditButton');
  const closeModalButton = document.querySelector('.close-modal');

  // 检查API配置
  console.log("API配置检查:");
  console.log("APPID:", APPID);
  console.log("API_KEY是否存在:", !!API_KEY);

  /**
   * 获取websocket url
   */
  function getWebSocketUrl() {
    try {
      if (!APPID || !API_KEY) {
        throw new Error("APPID或API_KEY未配置");
      }
      var url = "wss://rtasr.xfyun.cn/v1/ws";
      var appId = APPID;
      var secretKey = API_KEY;
      var ts = Math.floor(new Date().getTime() / 1000);
      var signa = hex_md5(appId + ts);
      var signatureSha = CryptoJSNew.HmacSHA1(signa, secretKey);
      var signature = CryptoJS.enc.Base64.stringify(signatureSha);
      signature = encodeURIComponent(signature);
      console.log("WebSocket URL生成成功");
      return `${url}?appid=${appId}&ts=${ts}&signa=${signature}`;
    } catch (error) {
      console.error("生成WebSocket URL失败:", error);
      alert("配置错误：" + error.message);
      throw error;
    }
  }

  function renderResult(resultData) {
    try {
      let jsonData = JSON.parse(resultData);
      console.log("收到识别结果:", jsonData);
      
      if (jsonData.action == "started") {
        console.log("语音识别连接成功");
        resultDiv.innerHTML = "<p style='color: green;'>语音识别已连接</p>";
      } else if (jsonData.action == "result") {
        const data = JSON.parse(jsonData.data);
        console.log("解析后的识别数据:", data);
        
        if (data.cn && data.cn.st) {
          let tempResult = "";
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
          
          if (data.cn.st.type == 0) {
            resultText += tempResult;
            console.log("累积的识别结果:", resultText);
          }
          
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
    try {
      const websocketUrl = getWebSocketUrl();
      if ("WebSocket" in window) {
        console.log("正在连接WebSocket...");
        iatWS = new WebSocket(websocketUrl);
      } else {
        alert("浏览器不支持WebSocket，请使用现代浏览器");
        return;
      }

      iatWS.onopen = () => {
        console.log("语音识别WebSocket连接已建立");
        const startFrame = {
          "common": {
            "app_id": APPID
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
        resultDiv.innerHTML += "<p style='color: red;'>WebSocket连接错误</p>";
      };

      iatWS.onclose = () => {
        console.log("WebSocket连接已关闭");
        resultDiv.innerHTML += "<p style='color: orange;'>WebSocket连接已关闭</p>";
      };
    } catch (error) {
      console.error("连接WebSocket失败:", error);
      alert("连接失败：" + error.message);
    }
  }

  // 开始录音
  startButton.addEventListener('click', async () => {
    try {
      console.log("开始获取媒体设备...");
      resultText = "";
      resultDiv.innerText = "";
      recordedChunks = [];

      // 检查是否有面试会话
      if (!currentSessionId || !interviewData || !interviewData.questions || interviewData.questions.length === 0) {
        alert("请先生成面试问题");
        return;
      }

      // 提示用户将在一次录制中回答所有问题
      const allQuestionsText = interviewData.questions.map(q => `问题${q.id}：${q.question}`).join('\n\n');
      const confirmMessage = `您将在一次录制中回答所有问题。请在录制时清晰地表明每个问题的答案，例如"对于第一个问题，我的回答是..."。\n\n${allQuestionsText}`;
      
      const confirmed = confirm(confirmMessage);
      if (!confirmed) {
        return;
      }

      // 始终使用第一个问题作为主问题ID，因为用户会一次性回答所有问题
      if (interviewData.questions.length > 0) {
        currentQuestionId = interviewData.questions[0].id;
        console.log("已将当前问题ID设置为第一个问题:", currentQuestionId);
      }

      // 显示所有问题提示
      resultDiv.innerHTML = '<p style="color: blue;">提示：请在录制中依次回答所有问题，并明确表明每个问题的答案</p>';
      interviewData.questions.forEach(question => {
        resultDiv.innerHTML += `<p><strong>问题${question.id}：</strong>${question.question}</p>`;
      });

      stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        }
      });

      console.log("成功获取媒体流:", stream);
      console.log("音频轨道:", stream.getAudioTracks());
      console.log("视频轨道:", stream.getVideoTracks());

      userVideo.srcObject = stream;
      await userVideo.play();
      userVideo.muted = true;

      // 视频显示后，确保问题容器高度与视频容器一致
      setTimeout(() => {
        const videoBox = document.querySelector('.video-box');
        const questionsContainer = document.getElementById('questionsContainer');
        
        if (videoBox && questionsContainer) {
          const videoBoxHeight = videoBox.offsetHeight;
          console.log("调整问题容器高度与视频容器一致:", videoBoxHeight + "px");
          questionsContainer.style.height = videoBoxHeight + "px";
          
          // 调整问题列表的最大高度，考虑问题容器上的内边距和标题高度
          const questionsTitle = questionsContainer.querySelector('h3');
          const titleHeight = questionsTitle ? questionsTitle.offsetHeight : 0;
          const containerPadding = 30; // 1.5rem * 16px + 上下内边距
          
          const questionsList = document.getElementById('questionsList');
          if (questionsList) {
            const newMaxHeight = videoBoxHeight - titleHeight - containerPadding;
            console.log("调整问题列表最大高度:", newMaxHeight + "px");
            questionsList.style.maxHeight = newMaxHeight + "px";
          }
        }
      }, 300); // 稍微延迟以确保视频已经完全加载

      mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'video/webm;codecs=vp8,opus'
      });

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          recordedChunks.push(event.data);
        }
      };

      mediaRecorder.start(1000);
      console.log("MediaRecorder已启动");

      try {
        connectWebSocket();
      } catch (wsError) {
        console.error("WebSocket连接失败:", wsError);
        alert("语音识别服务连接失败，请检查网络连接和API配置");
        return;
      }

      audioContext = new AudioContext({
        sampleRate: 16000
      });
      const mediaStreamSource = audioContext.createMediaStreamSource(stream);
      processor = audioContext.createScriptProcessor(2048, 1, 1);

      mediaStreamSource.connect(processor);
      processor.connect(audioContext.destination);

      processor.onaudioprocess = (e) => {
        if (iatWS && iatWS.readyState === WebSocket.OPEN) {
          const inputData = e.inputBuffer.getChannelData(0);
          const output = new Int16Array(inputData.length);
          for (let i = 0; i < inputData.length; i++) {
            output[i] = Math.max(-1, Math.min(1, inputData[i])) * 0x7FFF;
          }
          if (iatWS.bufferedAmount === 0) {
            iatWS.send(output.buffer);
          }
        }
      };

      startButton.disabled = true;
      endButton.disabled = false;

    } catch (err) {
      console.error('获取媒体设备失败:', err);
      alert('无法访问摄像头或麦克风，请确保已授予权限并且设备可用。\n错误信息: ' + err.message);
    }
  });

  // 停止录音
  endButton.addEventListener('click', () => {
    try {
      if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        
        // 添加录制完成事件处理
        mediaRecorder.onstop = async () => {
          console.log("视频录制完成，准备保存");
          
          // 重置问题容器高度为自动
          const questionsContainer = document.getElementById('questionsContainer');
          if (questionsContainer) {
            questionsContainer.style.height = '';
          }
          
          // 重置问题列表最大高度为原始值
          const questionsList = document.getElementById('questionsList');
          if (questionsList) {
            questionsList.style.maxHeight = '';
          }
          
          // 检查是否有问题ID和会话ID
          if (!currentQuestionId || !currentSessionId) {
            console.error("缺少问题ID或会话ID，无法保存录制");
            return;
          }
          
          try {
            // 创建一个Blob对象
            const videoBlob = new Blob(recordedChunks, { type: 'video/webm' });
            console.log(`创建视频Blob成功，大小: ${videoBlob.size} 字节`);
            
            // 确保resultDiv已经初始化
            const resultDisplayDiv = document.getElementById('result');
            if (!resultDisplayDiv) {
              console.error("未找到resultDiv元素");
              alert("页面元素加载错误，请刷新页面后重试");
              return;
            }
            
            // 显示保存状态
            resultDisplayDiv.innerHTML = `<p>正在保存视频和文本，请稍候...</p>
                                 <p>视频大小: ${(videoBlob.size / (1024 * 1024)).toFixed(2)} MB</p>`;
            
            // 检查视频大小
            if (videoBlob.size > 50 * 1024 * 1024) {
              const confirmLarge = confirm(`视频较大(${(videoBlob.size / (1024 * 1024)).toFixed(2)} MB)，可能导致上传失败。是否跳过面部表情分析以提高成功率？`);
              if (confirmLarge) {
                resultDisplayDiv.innerHTML += '<p>已选择跳过面部表情分析</p>';
              }
            }
            
            // 转换为Base64
            const reader = new FileReader();
            reader.readAsDataURL(videoBlob);
            reader.onloadend = async () => {
              const base64data = reader.result;
              console.log("视频转换为Base64成功");
              
              // 保存前输出会话和问题ID
              console.log("正在保存视频和文本...");
              console.log("会话ID:", currentSessionId);
              console.log("问题ID:", currentQuestionId);
              console.log("识别文本:", resultText);
              
              // 显示保存中状态
              resultDisplayDiv.innerHTML += '<p>正在上传到服务器...</p>';
              
              // 设置最大重试次数
              const MAX_RETRIES = 2;
              let retryCount = 0;
              let saveError = null;
              let skipEmotionAnalysis = videoBlob.size > 50 * 1024 * 1024;
              
              // 重试逻辑
              while (retryCount <= MAX_RETRIES) {
                try {
                  // 将录制的视频和识别的文本发送到服务器
                const saveResponse = await fetch('/save_video', {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json'
                  },
                  body: JSON.stringify({
                    session_id: currentSessionId,
                    question_id: currentQuestionId,
                    video_data: base64data,
                      answer_text: resultText,
                      skip_emotion_analysis: skipEmotionAnalysis
                  })
                });
                
                if (!saveResponse.ok) {
                    const errorText = await saveResponse.text();
                    let errorMessage;
                    try {
                      const errorJson = JSON.parse(errorText);
                      errorMessage = errorJson.error || `HTTP error ${saveResponse.status}`;
                    } catch {
                      errorMessage = `HTTP error ${saveResponse.status}: ${errorText}`;
                    }
                    throw new Error(errorMessage);
                }
                
                const saveData = await saveResponse.json();
                  console.log("保存视频和文本成功:", saveData);
                  
                  if (saveData.error) {
                    console.error("保存视频和文本失败:", saveData.error);
                    resultDisplayDiv.innerHTML += `<p style="color: red;">保存失败: ${saveData.error}</p>`;
                    return;
                  }
                  
                  // 成功保存，清除错误状态
                  saveError = null;
                  
                  // 保存后清理界面状态
                  resultDisplayDiv.innerHTML = '<p style="color: green;">✓ 视频和文本已成功保存</p>';
                  
                  // 添加一次性回答所有问题的提示
                  resultDisplayDiv.innerHTML += '<p style="color: blue; font-weight: bold;">您已经一次性回答了所有问题，系统会自动解析每个问题的回答。不需要重复录制！</p>';
                  
                  // 显示视频和文本保存成功消息
                  const qaResultDiv = document.createElement('div');
                  qaResultDiv.className = 'qa-pair';
                  qaResultDiv.setAttribute('data-question-id', currentQuestionId);
                  qaResultDiv.setAttribute('data-timestamp', saveData.timestamp);
                  
                  // 如果成功提取多个问题的回答，显示特殊提示
                  if (saveData.all_answers && Object.keys(saveData.all_answers).length > 1) {
                    const multipleAnswersAlert = document.createElement('div');
                    multipleAnswersAlert.className = 'multiple-answers-alert';
                    multipleAnswersAlert.innerHTML = `
                      <p><strong>🎉 检测到多个问题的回答!</strong></p>
                      <p>系统成功提取了${Object.keys(saveData.all_answers).length}个问题的回答，这些回答已分别保存。</p>
                    `;
                    qaResultDiv.appendChild(multipleAnswersAlert);
                  }
                  
                  // 显示回答内容
                  const answerContent = document.createElement('div');
                  answerContent.className = 'answer-content';
                  
                  // 添加问题内容
                  const questionText = document.createElement('div');
                  questionText.className = 'question-text';
                  questionText.innerHTML = `<strong>问题 ${currentQuestionId}:</strong> ${currentQuestion}`;
                  answerContent.appendChild(questionText);
                  
                  // 添加回答内容
                  const answerText = document.createElement('div');
                  answerText.className = 'answer-text';
                  answerText.innerHTML = `<strong>回答:</strong> ${saveData.parsed_answer}`;
                  answerContent.appendChild(answerText);
                  
                  // 添加编辑按钮
                  const editButton = document.createElement('button');
                  editButton.className = 'edit-button';
                  editButton.innerHTML = '<span class="material-symbols-rounded">edit</span> 编辑';
                  editButton.onclick = function() {
                    openEditModal(currentQuestionId, saveData.timestamp, currentQuestion, saveData.parsed_answer);
                  };
                  answerContent.appendChild(editButton);
                  
                  qaResultDiv.appendChild(answerContent);
                  
                  // 显示面部表情分析结果
                  if (saveData.emotion_analysis && saveData.emotion_analysis.length > 0) {
                    const emotionMsg = document.createElement('div');
                    emotionMsg.className = 'emotion-analysis';
                    
                    // 创建表情分析标题
                    const emotionTitle = document.createElement('h4');
                    emotionTitle.innerHTML = `<span style="color: purple;">🎭</span> 面部表情分析`;
                    emotionMsg.appendChild(emotionTitle);
                    
                    // 先显示整体情绪分析（如果有）
                    if (saveData.overall_emotion) {
                      const overallEmotionDiv = document.createElement('div');
                      overallEmotionDiv.className = 'overall-emotion';
                      
                      // 中文表情名称映射
                      const emotionNames = {
                        'angry': '生气',
                        'disgust': '厌恶',
                        'fear': '恐惧',
                        'happy': '开心',
                        'neutral': '中性',
                        'sad': '悲伤',
                        'surprise': '惊讶',
                        'unknown': '未知'
                      };
                      
                      // 使用中文表情名称
                      const dominantEmotionCn = saveData.overall_emotion.dominant_emotion_cn || 
                                              emotionNames[saveData.overall_emotion.dominant_emotion] || 
                                              '未知表情';
                      
                      // 创建整体情绪分析信息
                      const overallEmotionInfo = document.createElement('div');
                      overallEmotionInfo.className = 'emotion-info';
                      
                      // 添加主要表情
                      const mainEmotionLabel = document.createElement('span');
                      mainEmotionLabel.className = 'emotion-label';
                      mainEmotionLabel.textContent = '整体主要表情: ';
                      
                      const mainEmotionValue = document.createElement('span');
                      mainEmotionValue.className = 'emotion-value highlight';
                      mainEmotionValue.textContent = dominantEmotionCn;
                      
                      overallEmotionInfo.appendChild(mainEmotionLabel);
                      overallEmotionInfo.appendChild(mainEmotionValue);
                      
                      // 添加人脸检测信息
                      if (saveData.overall_emotion.frames_with_face !== undefined) {
                        const faceInfoDiv = document.createElement('div');
                        faceInfoDiv.className = 'face-info';
                        faceInfoDiv.innerHTML = `<small>视频中检测到人脸的帧数: ${saveData.overall_emotion.frames_with_face}</small>`;
                        overallEmotionInfo.appendChild(faceInfoDiv);
                      }
                      
                      overallEmotionDiv.appendChild(overallEmotionInfo);
                      
                      // 如果有详细情绪分布数据，添加条形图显示
                      if (saveData.overall_emotion.emotions) {
                        const emotionsData = saveData.overall_emotion.emotions;
                        const emotionBarChart = document.createElement('div');
                        emotionBarChart.className = 'emotion-chart';
                        
                        // 创建详情展开元素
                        const emotionDistDetails = document.createElement('details');
                        const emotionDistSummary = document.createElement('summary');
                        emotionDistSummary.textContent = '情绪分布详情';
                        emotionDistDetails.appendChild(emotionDistSummary);
                        
                        // 排序情绪数据
                        const sortedEmotions = Object.entries(emotionsData)
                            .filter(([_, value]) => value > 0)  // 只显示有值的情绪
                            .sort((a, b) => b[1] - a[1]);       // 按值从大到小排序
                        
                        // 创建条形图容器
                        const barChartContainer = document.createElement('div');
                        barChartContainer.className = 'bar-chart-container';
                        
                        // 为每种情绪创建条形图
                        sortedEmotions.forEach(([emotion, value]) => {
                          const emotionName = emotionNames[emotion] || emotion;
                          const percentage = (value * 100).toFixed(1);
                          
                          // 创建条形图行
                          const barRow = document.createElement('div');
                          barRow.className = 'bar-row';
                          
                          // 情绪名称标签
                          const emotionLabel = document.createElement('div');
                          emotionLabel.className = 'bar-label';
                          emotionLabel.textContent = emotionName;
                          
                          // 条形图条
                          const barContainer = document.createElement('div');
                          barContainer.className = 'bar-container';
                          
                          const bar = document.createElement('div');
                          bar.className = 'bar';
                          bar.style.width = `${Math.min(percentage, 100)}%`;
                          bar.style.backgroundColor = getEmotionColor(emotion);
                          
                          // 百分比值
                          const valueLabel = document.createElement('div');
                          valueLabel.className = 'bar-value';
                          valueLabel.textContent = `${percentage}%`;
                          
                          // 组装条形图
                          barContainer.appendChild(bar);
                          barRow.appendChild(emotionLabel);
                          barRow.appendChild(barContainer);
                          barRow.appendChild(valueLabel);
                          
                          barChartContainer.appendChild(barRow);
                        });
                        
                        // 将条形图添加到详情中
                        emotionDistDetails.appendChild(barChartContainer);
                        emotionBarChart.appendChild(emotionDistDetails);
                        overallEmotionDiv.appendChild(emotionBarChart);
                      }
                      
                      emotionMsg.appendChild(overallEmotionDiv);
                    }
                    
                    // 创建三阶段表情分析详情
                    const emotionDetails = document.createElement('details');
                    emotionDetails.open = false; // 默认不展开，因为已经有了整体分析
                    const emotionSummary = document.createElement('summary');
                    emotionSummary.textContent = '视频三阶段表情分析结果';
                    emotionDetails.appendChild(emotionSummary);
                    
                    // 创建表格显示三阶段分析
                    const emotionTable = document.createElement('table');
                    emotionTable.className = 'emotion-table';
                    
                    // 创建表头
                    const tableHeader = document.createElement('tr');
                    tableHeader.innerHTML = `
                      <th>阶段</th>
                      <th>时间点</th>
                      <th>主要表情</th>
                      <th>表情置信度</th>
                    `;
                    emotionTable.appendChild(tableHeader);
                    
                    // 创建表格内容
                    const tableBody = document.createElement('tbody');
                    
                    saveData.emotion_analysis.forEach(result => {
                      const row = document.createElement('tr');
                      
                      // 获取主要表情的置信度
                      const dominantEmotion = result.dominant_emotion;
                      const confidenceScore = result.emotions[dominantEmotion].toFixed(2);
                      
                      // 中文表情名称映射
                      const emotionNames = {
                        'angry': '生气',
                        'disgust': '厌恶',
                        'fear': '恐惧',
                        'happy': '开心',
                        'neutral': '中性',
                        'sad': '悲伤',
                        'surprise': '惊讶',
                        'unknown': '未知'
                      };
                      
                      // 使用中文表情名称，优先使用已转换的值
                      const emotionName = result.dominant_emotion_cn || emotionNames[dominantEmotion] || dominantEmotion;
                      
                      row.innerHTML = `
                        <td>${result.segment}</td>
                        <td>${result.time_seconds.toFixed(1)}秒</td>
                        <td>${emotionName}</td>
                        <td>${confidenceScore}</td>
                      `;
                      
                      tableBody.appendChild(row);
                    });
                    
                    emotionTable.appendChild(tableBody);
                    emotionDetails.appendChild(emotionTable);
                    
                    // 添加保存路径信息
                    if (saveData.emotion_path) {
                      const pathInfo = document.createElement('div');
                      pathInfo.className = 'emotion-path';
                      pathInfo.innerHTML = `<small>详细结果已保存至: ${saveData.emotion_path}</small>`;
                      emotionDetails.appendChild(pathInfo);
                    }
                    
                    emotionMsg.appendChild(emotionDetails);
                    qaResultDiv.appendChild(emotionMsg);
                  } else if (skipEmotionAnalysis) {
                    // 如果跳过了表情分析，显示提示
                    const emotionSkipMsg = document.createElement('div');
                    emotionSkipMsg.className = 'emotion-analysis';
                    emotionSkipMsg.innerHTML = `<p>已跳过面部表情分析以提高保存成功率</p>`;
                    qaResultDiv.appendChild(emotionSkipMsg);
                  }
                  
                  // 添加到回答列表
                  const qaPairsListElement = document.getElementById('qaPairsList');
                  if (qaPairsListElement) {
                    qaPairsListElement.appendChild(qaResultDiv);
                  } else {
                    console.error("未找到qaPairsList元素");
                  }
                  
                  // 刷新问答对列表
                  setTimeout(() => {
                    fetchQaPairs();
                  }, 1000);
                  
                  // 成功保存，退出重试循环
                  break;
                  
                } catch (error) {
                  retryCount++;
                  saveError = error;
                  console.error(`保存视频失败 (尝试 ${retryCount}/${MAX_RETRIES}):`, error);
                  
                  // 显示重试消息
                  resultDisplayDiv.innerHTML += `<p>保存失败，正在重试 (${retryCount}/${MAX_RETRIES})...</p>`;
                  
                  if (retryCount <= MAX_RETRIES) {
                    // 如果不是最后一次重试，等待一会再重试
                    await new Promise(resolve => setTimeout(resolve, 2000));
                    
                    // 如果视频较大，尝试跳过面部表情分析
                    if (retryCount === MAX_RETRIES - 1) {
                      resultDisplayDiv.innerHTML += '<p>尝试跳过面部表情分析...</p>';
                      skipEmotionAnalysis = true;
                    }
                  }
                }
              }
              
              // 如果所有重试都失败，显示最终错误
              if (saveError) {
                console.error("所有保存尝试均失败:", saveError);
                resultDisplayDiv.innerHTML = `
                  <p style="color: red;">保存视频和文本失败: ${saveError.message}</p>
                  <p>可能的原因:</p>
                  <ul>
                    <li>视频文件过大，服务器无法处理</li>
                    <li>网络连接问题</li>
                    <li>服务器存储空间不足</li>
                  </ul>
                  <p>建议:</p>
                  <ul>
                    <li>尝试录制更短的视频</li>
                    <li>刷新页面后重试</li>
                    <li>检查网络连接</li>
                  </ul>
                `;
                alert("保存视频和文本失败: " + saveError.message);
              }
            };
          } catch (blobError) {
            console.error("创建视频Blob失败:", blobError);
            const resultDisplayDiv = document.getElementById('result');
            if (resultDisplayDiv) {
              resultDisplayDiv.innerHTML = `<p style="color: red;">创建视频文件失败: ${blobError.message}</p>`;
            }
            alert("创建视频文件失败: " + blobError.message);
          }
        };
      }

      if (iatWS && iatWS.readyState === WebSocket.OPEN) {
        iatWS.send(JSON.stringify({
          "data": {
            "status": 2,
            "format": "audio/L16;rate=16000",
            "encoding": "raw"
          }
        }));
        iatWS.close();
      }

      if (processor && audioContext) {
        processor.disconnect();
        audioContext.close();
      }

      if (stream) {
        stream.getTracks().forEach(track => {
          track.stop();
          console.log(`${track.kind} 轨道已停止`);
        });
      }

      startButton.disabled = false;
      endButton.disabled = true;
    } catch (error) {
      console.error("结束录音时发生错误:", error);
      alert("结束录音时发生错误: " + error.message);
    }
  });

  // 生成面试问题
  setupButton.addEventListener('click', async () => {
    try {
      const position = positionInput.value.trim() || '软件工程师';
      
      // 显示加载状态
      setupButton.disabled = true;
      setupButton.textContent = '正在生成问题...';
      
      // 调用API生成问题
      const response = await fetch('/start_interview', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ position })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || '请求失败');
      }
      
      const data = await response.json();
      console.log("面试数据:", data);
      
      currentSessionId = data.session_id;
      
      try {
        interviewData = JSON.parse(data.interview_data);
        console.log("解析后的面试数据:", interviewData);
      } catch (parseError) {
        console.error("解析面试数据失败:", parseError);
        interviewData = { questions: [] };
        alert("解析面试数据失败，请重试");
        setupButton.disabled = false;
        setupButton.textContent = '生成面试问题';
        return;
      }
      
      // 渲染问题
      renderQuestions(interviewData.questions);
      
      // 切换界面
      setupContainer.style.display = 'none';
      interviewContainer.style.display = 'block';
      
    } catch (error) {
      console.error("生成面试问题失败:", error);
      alert("生成面试问题失败: " + error.message);
      setupButton.disabled = false;
      setupButton.textContent = '生成面试问题';
    }
  });

  // 渲染问题列表
  function renderQuestions(questions) {
    if (!questions || !Array.isArray(questions)) {
      console.error("无效的问题数据:", questions);
      return;
    }
    
    questionsListDiv.innerHTML = '';
    
    questions.forEach(question => {
      const questionCard = document.createElement('div');
      questionCard.className = 'question-card';
      questionCard.dataset.id = question.id;
      
      // 设置难度样式
      let difficultyClass = 'easy';
      if (question.difficulty === '中等') {
        difficultyClass = 'medium';
      } else if (question.difficulty === '困难') {
        difficultyClass = 'hard';
      }
      
      questionCard.innerHTML = `
        <div class="question-header">
          <div class="question-title">问题 ${question.id}</div>
          <div class="question-difficulty ${difficultyClass}">${question.difficulty}</div>
        </div>
        <div class="question-content">${question.question}</div>
      `;
      
      // 点击问题卡片时激活
      questionCard.addEventListener('click', () => {
        // 移除其他问题的active类
        document.querySelectorAll('.question-card').forEach(card => {
          card.classList.remove('active');
        });
        
        // 添加active类到当前问题
        questionCard.classList.add('active');
        currentQuestionId = question.id;
        currentQuestion = question.question;
        
        // 清空结果区域
        resultText = "";
        const resultDisplay = document.getElementById('result');
        if (resultDisplay) {
          resultDisplay.innerText = "";
        }
        
        // 不需要重新获取问答对，因为我们已经显示了所有问题的问答对
        // 但是，如果问答对尚未加载，则获取所有问题的问答对
        if (qaPairsListDiv.childElementCount === 0) {
          fetchQaPairs();
        }
      });
      
      questionsListDiv.appendChild(questionCard);
    });
    
    // 默认激活第一个问题
    if (questions.length > 0) {
      const firstCard = document.querySelector('.question-card');
      if (firstCard) {
        firstCard.classList.add('active');
        currentQuestionId = questions[0].id;
        currentQuestion = questions[0].question;
        
        // 获取所有问题的问答对
        fetchQaPairs();
      }
    }
  }

  // 提交回答
  submitButton.addEventListener('click', async () => {
    if (!currentQuestionId || !currentSessionId) {
      alert("请先选择一个问题");
      return;
    }
    
    try {
      // 使用语音识别结果作为回答
      let answer = resultText.trim();
      
      if (!answer) {
        alert("请先录制您的回答");
        return;
      }
      
      // 显示加载状态
      submitButton.disabled = true;
      submitButton.textContent = '提交中...';
      
      // 提交回答前显示提交信息
      console.log("正在提交回答...");
      console.log("会话ID:", currentSessionId);
      console.log("问题ID:", currentQuestionId);
      console.log("回答内容:", answer);
      
      // 提交回答
      const response = await fetch('/submit_answer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: currentSessionId,
          question_id: currentQuestionId,
          answer: answer
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || '请求失败');
      }
      
      const responseData = await response.json();
      console.log("回答提交成功:", responseData);
      
      // 存储回答
      userAnswers[currentQuestionId] = answer;
      
      // 显示成功提示
      const successMsg = document.createElement('p');
      successMsg.className = 'save-success';
      successMsg.innerHTML = `<span style="color: green;">✓</span> 回答已提交并保存至本地`;
      resultDiv.appendChild(successMsg);
      
      // 如果识别出多个问题的回答，显示提示
      if (responseData.all_answers && Object.keys(responseData.all_answers).length > 1) {
        const multiQuestionMsg = document.createElement('p');
        multiQuestionMsg.className = 'multi-question-notice';
        multiQuestionMsg.innerHTML = `<span style="color: blue;">ℹ</span> 系统从您的回答中识别出了多个问题的回答，已分别保存`;
        resultDiv.appendChild(multiQuestionMsg);
        
        // 添加详细的问题回答列表
        const allAnswersMsg = document.createElement('details');
        allAnswersMsg.className = 'all-answers-details';
        
        let summaryText = `识别出${Object.keys(responseData.all_answers).length}个问题的回答`;
        allAnswersMsg.innerHTML = `<summary>${summaryText}</summary>`;
        
        const answersList = document.createElement('ul');
        for (const [qNum, answer] of Object.entries(responseData.all_answers)) {
          // 获取问题的真实文本，优先使用服务器返回的问题映射
          let questionText = "未知问题";
          if (responseData.question_map && responseData.question_map[qNum]) {
            questionText = responseData.question_map[qNum];
          } else if (interviewData && interviewData.questions) {
            const questionObj = interviewData.questions.find(q => q.id == qNum);
            if (questionObj) {
              questionText = questionObj.question;
            }
          }
          
          const answerItem = document.createElement('li');
          answerItem.innerHTML = `<strong>${questionText}</strong>: ${answer.substring(0, 50)}${answer.length > 50 ? '...' : ''}`;
          answersList.appendChild(answerItem);
        }
        
        allAnswersMsg.appendChild(answersList);
        resultDiv.appendChild(allAnswersMsg);
      }
      
      // 延迟一下再刷新问答对，确保服务器处理完成
      setTimeout(() => {
        // 刷新所有问题的问答对列表
        fetchQaPairs();
      
        // 清空语音识别结果
        resultText = "";
        resultDiv.innerHTML = "";
      
        // 移除自动选择下一个问题的逻辑，因为用户一次回答了所有问题
      
        // 恢复按钮状态
        submitButton.disabled = false;
        submitButton.textContent = '提交回答';
      }, 1000);
      
    } catch (error) {
      console.error("提交回答失败:", error);
      alert("提交回答失败: " + error.message);
      submitButton.disabled = false;
      submitButton.textContent = '提交回答';
    }
  });

  // 结束面试
  finishButton.addEventListener('click', async () => {
    if (!currentSessionId) {
      alert("面试会话不存在");
      return;
    }
    
    try {
      // 先获取所有问答对，确保系统已经解析出的所有问题答案都被考虑
      await fetchQaPairs();
      
      // 检查是否所有问题都已回答
      const questions = interviewData.questions;
      
      // 使用一个集合来记录已回答的问题ID
      const answeredQuestionIds = new Set();
      
      // 检查userAnswers对象中的回答
      Object.entries(userAnswers).forEach(([qId, answer]) => {
        if (answer && answer.trim()) {
          answeredQuestionIds.add(String(qId));
          console.log(`问题 ${qId} 已回答`);
        } else {
          console.log(`问题 ${qId} 的回答为空`);
        }
      });
      
      // 找出未回答的问题
      const unansweredQuestions = questions.filter(q => !answeredQuestionIds.has(String(q.id)));
      
      // 如果回答了全部问题或只有一个未回答（可能是汇总问题），则不再显示警告
      if (unansweredQuestions.length > 0) {
        console.log("未回答问题列表:", unansweredQuestions);
        
        // 尝试从服务器获取一次性回答所有问题的记录
        let showWarning = true;
        
        try {
          // 检查是否存在all_questions_*.txt文件
          const checkResponse = await fetch('/get_qa_pairs', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              session_id: currentSessionId,
              check_all_questions_file: true
            })
          });
          
          if (checkResponse.ok) {
            const checkData = await checkResponse.json();
            
            if (checkData.has_all_questions_file) {
              console.log("检测到all_questions文件");
              
              // 检查所有问题的回答是否有效
              if (checkData.all_answers_valid && Object.keys(checkData.all_answers_valid).length > 0) {
                console.log("all_questions文件中的回答有效性:", checkData.all_answers_valid);
                
                // 检查是否所有必要问题都有有效回答
                const allRequiredQuestionsAnswered = unansweredQuestions.every(q => {
                  const qId = String(q.id);
                  // 如果问题在all_answers_valid中且标记为有效，则认为已回答
                  const isAnswered = checkData.all_answers_valid[qId] === true;
                  if (isAnswered) {
                    console.log(`问题 ${qId} 在all_questions文件中有有效回答`);
                  } else {
                    console.log(`问题 ${qId} 在all_questions文件中没有有效回答`);
                  }
                  return isAnswered;
                });
                
                if (allRequiredQuestionsAnswered) {
                  console.log("all_questions文件中所有必要问题都已回答，不显示警告");
                  showWarning = false;
                }
              }
            }
          }
        } catch (checkError) {
          console.error("检查all_questions文件失败:", checkError);
        }
        
        // 如果需要显示警告，则弹出确认对话框
        if (showWarning) {
          const confirm = window.confirm(`还有 ${unansweredQuestions.length} 个问题未回答，确定要结束面试吗？`);
          if (!confirm) {
            return;
          }
        } else {
          console.log("检测到一次性回答了所有问题，不显示未回答警告");
        }
      }
      
      // 显示加载状态
      finishButton.disabled = true;
      finishButton.textContent = '生成报告中...';
      
      // 生成报告
      const response = await fetch('/generate_report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: currentSessionId
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || '请求失败');
      }
      
      const data = await response.json();
      console.log("面试报告:", data);
      
      // 渲染报告
      renderReport(data.report);
      
      // 切换界面
      interviewContainer.style.display = 'none';
      reportContainer.style.display = 'block';
      
    } catch (error) {
      console.error("生成报告失败:", error);
      alert("生成报告失败: " + error.message);
      finishButton.disabled = false;
      finishButton.textContent = '结束面试';
    }
  });

  // 渲染报告
  function renderReport(reportData) {
    try {
      if (!reportData || reportData.trim() === '') {
        reportContentDiv.innerHTML = '<p class="error-message">未能获取到报告数据</p>';
        return;
      }
      
      // 添加marked.js库用于渲染Markdown（如果尚未添加）
      if (typeof marked === 'undefined') {
        console.log("添加marked.js库用于渲染Markdown");
        
        // 创建script元素
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
        script.onload = function() {
          // 加载完成后渲染Markdown
          renderMarkdownReport(reportData);
        };
        
        // 添加到文档
        document.head.appendChild(script);
      } else {
        // 如果marked已经加载，直接渲染
        renderMarkdownReport(reportData);
      }
    } catch (error) {
      console.error("渲染报告失败:", error);
      reportContentDiv.innerHTML = `<p style="color: red;">渲染报告失败: ${error.message}</p>`;
    }
  }
  
  // 使用marked库渲染Markdown报告
  function renderMarkdownReport(markdown) {
    try {
      // 尝试将内容解析为JSON
      let jsonReport = null;
      try {
        jsonReport = JSON.parse(markdown);
      } catch (e) {
        // 如果不是JSON格式，认为是Markdown格式
        console.log("报告不是JSON格式，按Markdown处理");
      }
      
      // 如果成功解析为JSON，则按旧格式处理
      if (jsonReport) {
        console.log("按旧JSON格式渲染报告");
        let reportContent = '';
        
        // 问题评估
        if (jsonReport.question_evaluations && Array.isArray(jsonReport.question_evaluations)) {
          reportContent += `<div class="report-section">
            <h4>问题评估</h4>
          `;
          
          jsonReport.question_evaluations.forEach(eval => {
            reportContent += `
              <div class="report-question">
                <div class="report-score">得分: ${eval.score}/10</div>
                <div class="report-analysis">${eval.analysis}</div>
              </div>
            `;
          });
          
          reportContent += `</div>`;
        }
        
        // 总体评价
        if (jsonReport.overall_evaluation) {
          reportContent += `
            <div class="report-section">
              <h4>总体评价</h4>
              <p>${jsonReport.overall_evaluation}</p>
            </div>
          `;
        }
        
        // 建议
        if (jsonReport.suggestions) {
          reportContent += `
            <div class="report-section">
              <h4>建议</h4>
              <p>${jsonReport.suggestions}</p>
            </div>
          `;
        }
        
        // 最终得分
        if (jsonReport.final_score) {
          reportContent += `
            <div class="report-final-score">
              最终得分: ${jsonReport.final_score}/100
            </div>
          `;
        }
        
        reportContentDiv.innerHTML = reportContent;
      } else {
        // 使用marked库渲染Markdown
        if (typeof marked === 'undefined') {
          console.error("marked库未加载");
          reportContentDiv.innerHTML = `<pre>${markdown}</pre>`;
          return;
        }
        
        // 设置marked选项
        marked.setOptions({
          breaks: true,        // 支持GitHub风格的换行
          gfm: true,           // 支持GitHub风格的Markdown
          headerIds: true,     // 为标题生成ID
          mangle: false,       // 不转义标题中的HTML
          sanitize: false,     // 不清理HTML标签
        });
        
        // 渲染Markdown
        const htmlContent = marked.parse(markdown);
        
        // 添加CSS类以便样式设置
        reportContentDiv.innerHTML = `<div class="markdown-body">${htmlContent}</div>`;
        
        // 添加必要的样式
        addMarkdownStyles();
      }
    } catch (error) {
      console.error("渲染Markdown报告失败:", error);
      reportContentDiv.innerHTML = `<pre>${markdown}</pre>`;
    }
  }
  
  // 添加Markdown样式
  function addMarkdownStyles() {
    // 检查是否已存在样式
    if (document.getElementById('markdown-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'markdown-styles';
    style.textContent = `
      .markdown-body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        line-height: 1.6;
        color: #24292e;
        padding: 1rem;
      }
      .markdown-body h1 {
        font-size: 2em;
        border-bottom: 1px solid #eaecef;
        padding-bottom: 0.3em;
        margin-top: 1.5em;
        margin-bottom: 1em;
      }
      .markdown-body h2 {
        font-size: 1.5em;
        border-bottom: 1px solid #eaecef;
        padding-bottom: 0.3em;
        margin-top: 1.5em;
        margin-bottom: 1em;
      }
      .markdown-body h3 {
        font-size: 1.25em;
        margin-top: 1.5em;
        margin-bottom: 0.5em;
      }
      .markdown-body ul, .markdown-body ol {
        padding-left: 2em;
      }
      .markdown-body li {
        margin: 0.25em 0;
      }
      .markdown-body blockquote {
        margin: 1em 0;
        padding: 0 1em;
        color: #6a737d;
        border-left: 0.25em solid #dfe2e5;
      }
      .markdown-body code {
        padding: 0.2em 0.4em;
        background-color: rgba(27,31,35,0.05);
        border-radius: 3px;
        font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
        font-size: 85%;
      }
      .markdown-body pre {
        padding: 16px;
        overflow: auto;
        font-size: 85%;
        line-height: 1.45;
        background-color: #f6f8fa;
        border-radius: 3px;
      }
      .markdown-body pre code {
        background-color: transparent;
        padding: 0;
      }
      .markdown-body table {
        border-collapse: collapse;
        width: 100%;
        margin: 1em 0;
      }
      .markdown-body table th, .markdown-body table td {
        border: 1px solid #dfe2e5;
        padding: 6px 13px;
      }
      .markdown-body table tr:nth-child(2n) {
        background-color: #f6f8fa;
      }
    `;
    
    document.head.appendChild(style);
  }

  // 开始新面试
  newInterviewButton.addEventListener('click', () => {
    // 重置状态
    currentSessionId = null;
    interviewData = null;
    currentQuestionId = null;
    userAnswers = {};
    resultText = "";
    
    // 切换界面
    reportContainer.style.display = 'none';
    setupContainer.style.display = 'block';
    
    // 重置按钮状态
    setupButton.disabled = false;
    setupButton.textContent = '生成面试问题';
    finishButton.disabled = false;
    finishButton.textContent = '结束面试';
  });

  // 添加获取问答对的方法
  async function fetchQaPairs() {
    if (!currentSessionId) {
      console.error("缺少会话ID，无法获取问答对");
      qaPairsListDiv.innerHTML = '<p class="error-message">缺少会话ID，无法获取问答对</p>';
      return;
    }
    
    console.log(`获取问答对: currentSessionId=${currentSessionId}`);
    
    // 显示加载状态
    qaPairsListDiv.innerHTML = '<p class="loading-message">正在加载问答对...</p>';
    
    try {
      // 调试：获取all_questions文件内容
      let allQuestionsData = null;
      try {
        const allQuestionsResponse = await fetch('/get_all_questions_content', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            session_id: currentSessionId
          })
        });
        
        if (allQuestionsResponse.ok) {
          allQuestionsData = await allQuestionsResponse.json();
          console.log("all_questions文件内容:", allQuestionsData);
          
          // 如果存在qa_pairs，将其答案添加到userAnswers中
          if (allQuestionsData.qa_pairs && allQuestionsData.qa_pairs.length > 0) {
            console.log(`从all_questions文件中获取到${allQuestionsData.qa_pairs.length}个问答对`);
            
            // 这里需要做一些处理，将问题文本匹配到对应的问题ID
            if (interviewData && interviewData.questions) {
              // 初始化一个问题文本到ID的映射
              const questionTextToId = {};
              interviewData.questions.forEach(q => {
                questionTextToId[q.question.trim()] = String(q.id);
              });
              
              // 遍历所有问答对
              allQuestionsData.qa_pairs.forEach(pair => {
                // 尝试通过问题内容找到对应ID
                if (pair.question && pair.question.trim()) {
                  const questionText = pair.question.trim();
                  const matchedId = questionTextToId[questionText];
                  
                  if (matchedId && pair.answer && pair.answer.trim()) {
                    console.log(`从all_questions文件匹配到问题ID ${matchedId}`);
                    
                    // 只有当userAnswers中没有该问题的答案或答案为空时，才更新
                    if (!userAnswers[matchedId] || !userAnswers[matchedId].trim()) {
                      userAnswers[matchedId] = pair.answer;
                      console.log(`从all_questions文件更新问题 ${matchedId} 的答案 (${pair.answer.length} 字符)`);
                    }
                  } else {
                    // 如果通过问题内容找不到ID，尝试从问题内容中提取数字
                    const numMatch = questionText.match(/问题\s*(\d+)/);
                    if (numMatch && numMatch[1]) {
                      const possibleId = numMatch[1];
                      if (interviewData.questions.some(q => String(q.id) === possibleId)) {
                        if (pair.answer && pair.answer.trim()) {
                          userAnswers[possibleId] = pair.answer;
                          console.log(`通过问题编号匹配到问题ID ${possibleId}`);
                        }
                      }
                    }
                  }
                }
              });
            }
          }
        } else {
          console.warn("获取all_questions文件失败:", await allQuestionsResponse.text());
        }
      } catch (allQuestionsError) {
        console.warn("获取all_questions文件内容失败:", allQuestionsError);
        // 这里不需要阻止主流程，所以只是记录警告
      }
      
      const requestData = {
        session_id: currentSessionId
      };
      
      console.log("发送获取问答对请求:", requestData);
      
      const response = await fetch('/get_qa_pairs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      });
      
      // 尝试获取响应数据
      let responseData;
      try {
        responseData = await response.json();
      } catch (parseError) {
        console.error("解析响应失败:", parseError);
        throw new Error("无法解析服务器响应");
      }
      
      if (!response.ok) {
        throw new Error(responseData.error || `请求失败，状态码: ${response.status}`);
      }
      
      console.log("获取问答对成功:", responseData);
      
      // 验证响应数据格式
      if (!responseData.hasOwnProperty('qa_pairs')) {
        console.error("响应数据格式错误，缺少qa_pairs字段:", responseData);
        throw new Error("服务器返回的数据格式不正确");
      }
      
      // 检查qa_pairs是否为对象
      if (!responseData.qa_pairs || typeof responseData.qa_pairs !== 'object') {
        console.warn("服务器返回的qa_pairs不是有效对象:", responseData.qa_pairs);
        
        // 如果有all_questions数据，尝试从中创建qa_pairs
        if (allQuestionsData && allQuestionsData.qa_pairs && allQuestionsData.qa_pairs.length > 0) {
          console.log("尝试从all_questions数据创建问答对");
          
          const qa_pairs = {};
          
          if (interviewData && interviewData.questions) {
            // 初始化一个问题文本到ID的映射
            const questionTextToId = {};
            interviewData.questions.forEach(q => {
              questionTextToId[q.question.trim()] = String(q.id);
            });
            
            // 遍历所有问答对
            allQuestionsData.qa_pairs.forEach(pair => {
              if (pair.question && pair.answer) {
                const questionText = pair.question.trim();
                const matchedId = questionTextToId[questionText];
                
                if (matchedId) {
                  // 创建一个问答对条目
                  const timestamp = Math.floor(Date.now() / 1000);
                  if (!qa_pairs[matchedId]) {
                    qa_pairs[matchedId] = [];
                  }
                  
                  qa_pairs[matchedId].push({
                    timestamp: timestamp,
                    parsed_answer: pair.answer,
                    original_text: pair.answer
                  });
                  
                  console.log(`从all_questions创建问题 ${matchedId} 的问答对`);
                }
              }
            });
          }
          
          // 如果成功创建了问答对，使用它们
          if (Object.keys(qa_pairs).length > 0) {
            responseData.qa_pairs = qa_pairs;
          } else {
            qaPairsListDiv.innerHTML = '<p class="no-qa-pairs">暂无问答记录</p>';
            return;
          }
        } else {
          qaPairsListDiv.innerHTML = '<p class="no-qa-pairs">暂无问答记录</p>';
          return;
        }
      }
      
      // 检查是否有问答对
      if (Object.keys(responseData.qa_pairs).length === 0) {
        console.warn("未获取到任何问答对");
        
        // 如果有all_questions数据，但没有qa_pairs，尝试创建
        if (allQuestionsData && allQuestionsData.qa_pairs && allQuestionsData.qa_pairs.length > 0 &&
            interviewData && interviewData.questions) {
          console.log("尝试从all_questions数据创建问答对");
          
          const qa_pairs = {};
          
          // 初始化一个问题文本到ID的映射
          const questionTextToId = {};
          interviewData.questions.forEach(q => {
            questionTextToId[q.question.trim()] = String(q.id);
          });
          
          // 遍历所有问答对
          allQuestionsData.qa_pairs.forEach(pair => {
            if (pair.question && pair.answer) {
              const questionText = pair.question.trim();
              const matchedId = questionTextToId[questionText];
              
              if (matchedId) {
                // 创建一个问答对条目
                const timestamp = Math.floor(Date.now() / 1000);
                if (!qa_pairs[matchedId]) {
                  qa_pairs[matchedId] = [];
                }
                
                qa_pairs[matchedId].push({
                  timestamp: timestamp,
                  parsed_answer: pair.answer,
                  original_text: pair.answer
                });
                
                console.log(`从all_questions创建问题 ${matchedId} 的问答对`);
              }
            }
          });
          
          // 如果成功创建了问答对，使用它们
          if (Object.keys(qa_pairs).length > 0) {
            responseData.qa_pairs = qa_pairs;
          } else {
            qaPairsListDiv.innerHTML = '<p class="no-qa-pairs">暂无问答记录</p>';
            return;
          }
        } else {
          qaPairsListDiv.innerHTML = '<p class="no-qa-pairs">暂无问答记录</p>';
          return;
        }
      }
      
      // 更新userAnswers对象，从获取的问答对中提取答案
      Object.entries(responseData.qa_pairs).forEach(([questionId, pairs]) => {
        // 确保pairs是数组且有内容
        if (Array.isArray(pairs) && pairs.length > 0) {
          // 按时间戳排序，获取最新的回答
          const validPairs = pairs.filter(pair => pair && pair.timestamp);
          if (validPairs.length > 0) {
            const sortedPairs = [...validPairs].sort((a, b) => {
              return parseInt(b.timestamp) - parseInt(a.timestamp);
            });
            
            // 获取最新的回答
            const latestPair = sortedPairs[0];
            const answer = latestPair.parsed_answer || latestPair.original_text || "";
            
            // 如果回答不为空，则更新userAnswers
            if (answer.trim()) {
              userAnswers[questionId] = answer;
              console.log(`从问答对更新答案: 问题ID=${questionId}, 答案长度=${answer.length}`);
            }
          }
        }
      });
      
      // 渲染问答对
      renderQaPairs(responseData.qa_pairs);
      
    } catch (error) {
      console.error("获取问答对失败:", error);
      
      // 显示错误提示
      qaPairsListDiv.innerHTML = `<p class="error-message">获取问答对失败: ${error.message}</p>`;
      
      // 如果是类型错误或者比较错误，可能是ID类型不匹配
      if (error.message.includes("supported between instances of") || 
          error.message.includes("TypeError")) {
        console.error("可能是ID类型不匹配，尝试刷新页面解决");
        qaPairsListDiv.innerHTML += '<p class="error-help">提示：这可能是数据类型不匹配问题，请尝试刷新页面或重新开始面试</p>';
      }
    }
  }
  
  // 渲染问答对列表
  function renderQaPairs(qaPairs) {
    // 清空列表
    qaPairsListDiv.innerHTML = '';
    
    // 检查问答对数据
    if (!qaPairs || typeof qaPairs !== 'object' || Object.keys(qaPairs).length === 0) {
      qaPairsListDiv.innerHTML = '<p class="no-qa-pairs">暂无问答记录</p>';
      return;
    }
    
    // 输出调试信息
    console.log("渲染问答对列表:", qaPairs);
    console.log("问答对键类型:", Object.keys(qaPairs).map(k => typeof k));
    
    try {
      // 添加"编辑所有问题"按钮
      const editAllButton = document.createElement('button');
      editAllButton.className = 'primary-button edit-all-button';
      editAllButton.innerHTML = '<span class="material-symbols-rounded">edit_note</span> 编辑所有问题';
      editAllButton.style.marginBottom = '1rem';
      editAllButton.style.width = '100%';
      editAllButton.addEventListener('click', () => {
        // 使用第一个问题的数据打开编辑模态框
        if (interviewData && interviewData.questions && interviewData.questions.length > 0) {
          const firstQuestion = interviewData.questions[0];
          const firstQuestionId = String(firstQuestion.id);
          const pairs = qaPairs[firstQuestionId];
          
          if (pairs && pairs.length > 0) {
            // 使用最新的问答对
            const latestPair = [...pairs].sort((a, b) => parseInt(b.timestamp) - parseInt(a.timestamp))[0];
            openEditModal(latestPair, firstQuestion.question, firstQuestionId);
          } else {
            // 如果没有问答对，传递一个空对象
            openEditModal({}, firstQuestion.question, firstQuestionId);
          }
        } else {
          alert("无法加载问题数据");
        }
      });
      qaPairsListDiv.appendChild(editAllButton);
      
      // 遍历所有问题的问答对
      Object.entries(qaPairs).forEach(([questionId, pairs]) => {
        // 确保pairs是数组
        if (!Array.isArray(pairs) || pairs.length === 0) {
          console.warn(`问题${questionId}没有有效的问答对数组`);
          return;
        }
        
        // 获取问题内容
        let questionText = "未知问题";
        if (interviewData && interviewData.questions) {
          const questionObj = interviewData.questions.find(q => 
            String(q.id) === String(questionId)
          );
          if (questionObj) {
            questionText = questionObj.question;
          }
        }
        
        // 确保所有回答都有有效的时间戳
        const validPairs = pairs.filter(pair => pair && pair.timestamp);
        
        if (validPairs.length === 0) {
          console.warn(`问题${questionId}没有有效的回答`);
          return;
        }
        
        // 按时间戳排序，最新的在前面
        const sortedPairs = [...validPairs].sort((a, b) => {
          const timestampA = parseInt(a.timestamp);
          const timestampB = parseInt(b.timestamp);
          if (isNaN(timestampA) || isNaN(timestampB)) {
            console.warn(`问题${questionId}的时间戳格式无效`);
            return 0;
          }
          return timestampB - timestampA;
        });
        
        // 只显示每个问题的最新回答
        const latestPair = sortedPairs[0];
        
        const qaPairCard = document.createElement('div');
        qaPairCard.className = 'qa-pair-card';
        qaPairCard.dataset.questionId = questionId; // 在DOM元素上存储问题ID
        
        // 格式化时间
        let formattedDate = "未知时间";
        try {
          const timestamp = parseInt(latestPair.timestamp);
          if (!isNaN(timestamp)) {
            const date = new Date(timestamp * 1000);
            formattedDate = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}:${String(date.getSeconds()).padStart(2, '0')}`;
          }
        } catch (e) {
          console.error("时间格式化错误:", e);
        }
        
        // 确保有回答内容
        const answerText = latestPair.parsed_answer || latestPair.original_text || "无回答内容";
        
        // 检查回答内容是否为空白，如果是，显示特殊提示
        const displayAnswerText = answerText.trim() ? answerText : "<em>（该问题尚未回答）</em>";
        
        qaPairCard.innerHTML = `
          <div class="qa-pair-question">${questionText}</div>
          <div class="qa-pair-answer">${displayAnswerText}</div>
          <div class="qa-pair-meta">
            <span class="qa-pair-time">${formattedDate}</span>
            <div class="qa-pair-actions">
              <button class="edit-qa-pair secondary-button" data-question-id="${questionId}" data-timestamp="${latestPair.timestamp}">编辑</button>
            </div>
          </div>
        `;
        
        // 添加编辑事件
        const editButton = qaPairCard.querySelector('.edit-qa-pair');
        editButton.addEventListener('click', () => {
          console.log(`编辑按钮点击: questionId=${questionId}, timestamp=${latestPair.timestamp}`);
          openEditModal(latestPair, questionText, questionId);
        });
        
        qaPairsListDiv.appendChild(qaPairCard);
      });
      
      // 如果除了"编辑所有问题"按钮外没有添加任何卡片
      if (qaPairsListDiv.children.length <= 1) {
        // 保留"编辑所有问题"按钮，添加"暂无问答记录"提示
        const noQaPairsMsg = document.createElement('p');
        noQaPairsMsg.className = 'no-qa-pairs';
        noQaPairsMsg.textContent = '暂无问答记录';
        qaPairsListDiv.appendChild(noQaPairsMsg);
      }
    } catch (error) {
      console.error("渲染问答对列表失败:", error);
      qaPairsListDiv.innerHTML = `<p class="error-message">渲染问答对失败: ${error.message}</p>`;
    }
  }
  
  // 打开编辑模态框
  function openEditModal(qaPair, questionText, questionId) {
    console.log("打开编辑模态框:", {
      qaPair,
      questionText,
      questionId,
      questionIdType: typeof questionId
    });
    
    // 更新当前编辑的问题ID和对应的问答对
    currentEditingQaPair = qaPair;
    currentQuestionId = questionId;
    
    // 获取allQuestionsAnswers容器
    const allQuestionsAnswersDiv = document.getElementById('allQuestionsAnswers');
    allQuestionsAnswersDiv.innerHTML = ''; // 清空容器
    
    // 获取所有问题
    if (interviewData && interviewData.questions && interviewData.questions.length > 0) {
      // 首先尝试获取所有问题的回答
      fetchQaPairs().then(() => {
        // 检查获取的用户回答
        console.log("openEditModal - 用户回答:", userAnswers);
        
        // 为每个问题创建编辑项
        interviewData.questions.forEach(question => {
          const q_id = String(question.id);
          const q_text = question.question;
          
          // 创建问题-回答编辑项
          const questionAnswerItem = document.createElement('div');
          questionAnswerItem.className = 'question-answer-item';
          questionAnswerItem.dataset.questionId = q_id;
          
          // 添加问题标签
          const questionLabel = document.createElement('div');
          questionLabel.className = 'question-label';
          questionLabel.textContent = `问题 ${q_id}：${q_text}`;
          questionAnswerItem.appendChild(questionLabel);
          
          // 添加回答文本框
          const answerTextarea = document.createElement('textarea');
          answerTextarea.className = 'answer-textarea';
          answerTextarea.rows = 5;
          answerTextarea.id = `answer-${q_id}`;
          answerTextarea.placeholder = '请输入回答...';
          
          // 设置回答内容，先检查userAnswers，再检查qaPair
          let answerText = '';
          
          // 第一优先级：从userAnswers中获取回答
          if (userAnswers[q_id] && userAnswers[q_id].trim()) {
            console.log(`问题${q_id}从userAnswers获取回答`);
            answerText = userAnswers[q_id];
          } 
          // 第二优先级：如果是当前编辑的问题，从qaPair获取回答
          else if (q_id === questionId && qaPair && (qaPair.parsed_answer || qaPair.original_text)) {
            console.log(`问题${q_id}从qaPair获取回答`);
            answerText = qaPair.parsed_answer || qaPair.original_text || '';
          }
          // 第三优先级：尝试从页面上已存在的问答卡片中获取回答
          else {
            const existingCard = qaPairsListDiv.querySelector(`.qa-pair-card[data-question-id="${q_id}"]`);
            if (existingCard) {
              const answerDiv = existingCard.querySelector('.qa-pair-answer');
              if (answerDiv && !answerDiv.innerHTML.includes('（该问题尚未回答）')) {
                console.log(`问题${q_id}从DOM获取回答`);
                answerText = answerDiv.innerHTML;
              }
            }
          }
          
          // 清理可能的HTML标签
          if (answerText.includes('<') && answerText.includes('>')) {
            try {
              // 使用临时元素解析HTML，然后获取纯文本
              const tempDiv = document.createElement('div');
              tempDiv.innerHTML = answerText;
              answerText = tempDiv.textContent || tempDiv.innerText || answerText;
            } catch (e) {
              console.warn(`清理问题${q_id}的HTML标签失败:`, e);
            }
          }
          
          answerTextarea.value = answerText;
          questionAnswerItem.appendChild(answerTextarea);
          
          // 添加到容器
          allQuestionsAnswersDiv.appendChild(questionAnswerItem);
          
          // 输出调试日志
          console.log(`问题${q_id}的回答长度: ${answerText.length}`);
        });
        
        // 显示模态框
        editQaPairModal.style.display = 'block';
        
        // 如果有当前问题ID，滚动到对应位置
        if (currentQuestionId) {
          const currentQuestionItem = allQuestionsAnswersDiv.querySelector(`.question-answer-item[data-question-id="${currentQuestionId}"]`);
          if (currentQuestionItem) {
            currentQuestionItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
            // 聚焦到当前问题的文本框
            const currentTextarea = currentQuestionItem.querySelector('textarea');
            if (currentTextarea) {
              currentTextarea.focus();
            }
          }
        }
      });
    } else {
      // 如果没有问题数据，显示错误信息
      allQuestionsAnswersDiv.innerHTML = '<p class="error-message">无法加载问题数据</p>';
      editQaPairModal.style.display = 'block';
    }
  }
  
  // 关闭编辑模态框
  function closeEditModal() {
    editQaPairModal.style.display = 'none';
    document.getElementById('allQuestionsAnswers').innerHTML = '';
    currentEditingQaPair = null;
  }
  
  // 保存编辑后的问答对
  async function saveQaPair() {
    if (!currentSessionId) {
      alert("面试会话不存在");
      return;
    }
    
    try {
      // 显示加载状态
      saveQaPairBtn.disabled = true;
      saveQaPairBtn.textContent = '保存中...';
      
      // 获取所有问题回答
      const allQuestionItems = document.querySelectorAll('.question-answer-item');
      const updatedAnswers = {};
      let hasChanges = false;
      
      // 检查每个问题的回答
      for (const item of allQuestionItems) {
        const questionId = item.dataset.questionId;
        const textarea = item.querySelector('textarea');
        if (textarea && textarea.value.trim()) {
          updatedAnswers[questionId] = textarea.value.trim();
          
          // 检查回答是否有变化
          const originalAnswer = userAnswers[questionId] || '';
          if (originalAnswer !== textarea.value.trim()) {
            hasChanges = true;
            console.log(`问题${questionId}的回答已修改，原长度: ${originalAnswer.length}, 新长度: ${textarea.value.trim().length}`);
          }
        }
      }
      
      if (!hasChanges) {
        alert("未检测到任何修改");
        saveQaPairBtn.disabled = false;
        saveQaPairBtn.textContent = '保存';
        return;
      }
      
      // 保存所有已修改的回答
      const savePromises = [];
      let successCount = 0;
      let errorCount = 0;
      
      for (const [qId, answer] of Object.entries(updatedAnswers)) {
        // 只保存有变化的回答
        const originalAnswer = userAnswers[qId] || '';
        if (originalAnswer !== answer) {
          console.log(`问题 ${qId} 的回答已修改，准备保存`);
          
          // 查找该问题的最新问答对记录
          let timestamp = null;
          
          // 从qaPairsList获取最新的时间戳
          const qaPairCard = qaPairsListDiv.querySelector(`.qa-pair-card[data-question-id="${qId}"]`);
          if (qaPairCard) {
            const editButton = qaPairCard.querySelector('.edit-qa-pair');
            if (editButton) {
              timestamp = editButton.dataset.timestamp;
              console.log(`从DOM中获取问题${qId}的时间戳:`, timestamp);
            }
          }
          
          // 如果没有找到时间戳，使用当前时间
          if (!timestamp) {
            timestamp = Math.floor(Date.now() / 1000);
            console.log(`问题 ${qId} 没有现有记录，使用当前时间戳: ${timestamp}`);
          }
          
          // 创建保存请求
          const savePromise = fetch('/update_qa_pair', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              session_id: currentSessionId,
              question_id: qId,
              timestamp: parseInt(timestamp),
              updated_answer: answer
            })
          }).then(response => {
            if (!response.ok) {
              return response.json().then(data => {
                throw new Error(data.error || `保存问题 ${qId} 失败: HTTP ${response.status}`);
              });
            }
            return response.json();
          }).then(data => {
            console.log(`问题 ${qId} 保存成功:`, data);
            // 更新userAnswers
            userAnswers[qId] = answer;
            successCount++;
          }).catch(error => {
            console.error(`保存问题 ${qId} 失败:`, error);
            errorCount++;
            throw error; // 重新抛出错误，以便Promise.all能够捕获
          });
          
          savePromises.push(savePromise);
        }
      }
      
      // 等待所有保存请求完成
      if (savePromises.length > 0) {
        try {
          await Promise.all(savePromises);
          console.log(`所有问题回答保存成功，共${successCount}个问题`);
          
          // 如果有成功的保存，显示成功消息
          if (successCount > 0) {
            alert(`已成功保存${successCount}个问题的回答`);
          }
        } catch (error) {
          console.error("保存部分问题回答失败:", error);
          alert(`保存部分问题回答失败: ${error.message}\n成功: ${successCount}个, 失败: ${errorCount}个`);
        }
        
        // 无论成功与否，都关闭模态框并刷新问答对列表
        closeEditModal();
        fetchQaPairs();
      } else {
        console.log("没有需要保存的修改");
      }
      
      // 恢复按钮状态
      saveQaPairBtn.disabled = false;
      saveQaPairBtn.textContent = '保存';
      
    } catch (error) {
      console.error("保存问答对失败:", error);
      alert("保存问答对失败: " + error.message);
      saveQaPairBtn.disabled = false;
      saveQaPairBtn.textContent = '保存';
    }
  }
  
  // 绑定模态框事件
  saveQaPairBtn.addEventListener('click', saveQaPair);
  cancelEditButton.addEventListener('click', closeEditModal);
  closeModalButton.addEventListener('click', closeEditModal);
  
  // 点击模态框外部关闭
  window.addEventListener('click', (event) => {
    if (event.target === editQaPairModal) {
      closeEditModal();
    }
  });

  // 获取情绪对应的颜色
  function getEmotionColor(emotion) {
    const colorMap = {
        'angry': '#FF5252',    // 红色
        'disgust': '#AA00FF',  // 紫色
        'fear': '#651FFF',     // 深紫色
        'happy': '#FFEB3B',    // 黄色
        'neutral': '#4CAF50',  // 绿色
        'sad': '#2196F3',      // 蓝色
        'surprise': '#FF9800'  // 橙色
    };
    
    return colorMap[emotion] || '#9E9E9E'; // 默认灰色
  }
})();