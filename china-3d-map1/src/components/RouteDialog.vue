<template>
  <div class="route-dialog" v-if="visible">
    <div class="dialog-content">
      <div class="dialog-header">
        <span class="title">智能路线规划助手</span>
        <span class="close-btn" @click="handleClose">×</span>
      </div>
      <div class="dialog-body">
        <div class="input-area">
          <textarea 
            v-model="userInput" 
            placeholder="请输入您的问题，例如：我想从北京到上海，有什么好的路线建议？"
            rows="4"
          ></textarea>
        </div>
        <div class="result-area" v-if="result || processingSteps.length > 0">
          <div class="processing-steps" v-if="processingSteps.length > 0">
            <div v-for="(step, index) in processingSteps" 
                 :key="index" 
                 class="step-item"
                 :class="{ 'completed': step.completed, 'error': step.error }">
              <span class="step-icon">{{ step.completed ? '✓' : '•' }}</span>
              <span class="step-text">{{ step.text }}</span>
            </div>
          </div>
          <div class="result-content" :class="{ 'error': isError }" v-if="result">
            <pre>{{ result }}</pre>
          </div>
        </div>
        <div class="log-area" v-if="logs.length > 0">
          <div class="log-header">处理日志</div>
          <div class="log-content">
            <div v-for="(log, index) in logs" 
                 :key="index" 
                 class="log-item"
                 :class="{ 'info': log.type === 'info', 'error': log.type === 'error' }">
              <span class="log-time">{{ log.time }}</span>
              <span class="log-type">{{ log.type.toUpperCase() }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
          </div>
        </div>
        <div class="loading" v-if="loading">
          <div class="loading-text">{{ loadingText }}</div>
          <div class="loading-spinner"></div>
        </div>
      </div>
      <div class="dialog-footer">
        <button class="submit-btn" @click="handleSubmit" :disabled="loading || !userInput.trim()">
          {{ loading ? '处理中...' : '提交问题' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RouteDialog',
  data() {
    return {
      visible: false,
      userInput: '',
      result: '',
      loading: false,
      loadingText: '正在连接服务器...',
      isError: false,
      processingSteps: [],
      logs: []
    }
  },
  methods: {
    handleClose() {
      this.visible = false
      this.resetState()
    },
    resetState() {
      this.userInput = ''
      this.result = ''
      this.isError = false
      this.processingSteps = []
      this.logs = []
      this.loading = false
      this.loadingText = '正在连接服务器...'
    },
    async handleSubmit() {
      if (!this.userInput.trim()) {
        alert('请输入问题')
        return
      }

      this.loading = true
      this.isError = false
      this.result = ''
      this.processingSteps = []
      this.logs = []
      
      this.addProcessingStep('正在发送路线规划请求...')
      this.addLog('info', '收到新的路线规划请求: ' + this.userInput)
      
      try {
        const response = await fetch('http://localhost:5123/api/route-planning', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            question: this.userInput
          })
        })

        this.addProcessingStep('正在等待服务器响应...')
        const data = await response.json()
        
        // 添加服务器返回的日志
        if (data.logs && Array.isArray(data.logs)) {
          data.logs.forEach(log => {
            this.addLog('info', log)
          })
        }

        if (response.ok) {
          if (data.error) {
            this.isError = true
            this.result = data.error
            this.addLog('error', data.error)
            this.markLastStepAsCompleted(false)
          } else {
            this.addProcessingStep('正在解析路线规划结果...')
            this.result = data.result
            this.isError = false
            this.addLog('info', '路线规划完成')
            this.markLastStepAsCompleted(true)
          }
        } else {
          this.isError = true
          this.result = `服务器响应错误: ${response.status}`
          this.addLog('error', `服务器响应错误: ${response.status}`)
          this.markLastStepAsCompleted(false)
        }
      } catch (error) {
        console.error('Error:', error)
        this.isError = true
        this.result = '请求失败: ' + error.message
        this.addLog('error', '请求失败: ' + error.message)
        this.markLastStepAsCompleted(false)
      } finally {
        this.loading = false
      }
    },
    addProcessingStep(text) {
      this.processingSteps.push({
        text,
        completed: false,
        error: false
      })
    },
    markLastStepAsCompleted(success) {
      if (this.processingSteps.length > 0) {
        const lastStep = this.processingSteps[this.processingSteps.length - 1]
        lastStep.completed = true
        lastStep.error = !success
      }
    },
    addLog(type, message) {
      const now = new Date()
      const time = now.toLocaleTimeString('zh-CN', { 
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
      this.logs.push({
        time,
        type,
        message
      })
    },
    show() {
      this.visible = true
      this.resetState()
    }
  }
}
</script>

<style scoped>
.route-dialog {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog-content {
  background: rgba(4, 19, 36, 0.95);
  border: 1px solid #0e4b80;
  border-radius: 4px;
  width: 900px;
  max-width: 95%;
  max-height: 95vh;
  color: #fff;
  display: flex;
  flex-direction: column;
}

.dialog-header {
  padding: 15px;
  border-bottom: 1px solid #0e4b80;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  color: #00a0e9;
}

.close-btn {
  cursor: pointer;
  font-size: 24px;
  color: #666;
}

.close-btn:hover {
  color: #00a0e9;
}

.dialog-body {
  padding: 20px;
  flex: 1;
  overflow-y: auto;
  min-height: 600px;
}

.input-area textarea {
  width: 100%;
  background: rgba(14, 75, 128, 0.2);
  border: 1px solid #0e4b80;
  color: #fff;
  padding: 10px;
  border-radius: 4px;
  resize: vertical;
  min-height: 100px;
}

.result-area {
  margin-top: 20px;
  padding: 15px;
  background: rgba(14, 75, 128, 0.2);
  border: 1px solid #0e4b80;
  border-radius: 4px;
  max-height: 600px;
  overflow-y: auto;
}

.result-content {
  white-space: pre-wrap;
  word-break: break-word;
  font-family: monospace;
  line-height: 1.5;
}

.result-content.error {
  color: #ff4d4f;
}

.processing-steps {
  margin-bottom: 15px;
}

.step-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  color: #00a0e9;
  font-size: 14px;
}

.step-item.completed {
  color: #52c41a;
}

.step-item.completed.error {
  color: #ff4d4f;
}

.step-icon {
  margin-right: 8px;
  font-size: 16px;
}

.step-text {
  flex: 1;
}

.loading {
  text-align: center;
  margin: 20px 0;
  color: #00a0e9;
}

.loading-text {
  margin-bottom: 10px;
}

.loading-spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid #00a0e9;
  border-radius: 50%;
  border-top-color: transparent;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.dialog-footer {
  padding: 15px;
  text-align: right;
  border-top: 1px solid #0e4b80;
}

.submit-btn {
  background: #00a0e9;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 4px;
  cursor: pointer;
  min-width: 100px;
}

.submit-btn:disabled {
  background: #666;
  cursor: not-allowed;
}

.log-area {
  margin-top: 20px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid #0e4b80;
  border-radius: 4px;
}

.log-header {
  padding: 8px 12px;
  background: rgba(14, 75, 128, 0.3);
  border-bottom: 1px solid #0e4b80;
  font-size: 14px;
  color: #00a0e9;
}

.log-content {
  padding: 12px;
  max-height: 200px;
  overflow-y: auto;
  font-family: monospace;
}

.log-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 6px;
  font-size: 13px;
  line-height: 1.5;
  color: #b0b0b0;
  padding: 4px 0;
}

.log-time {
  flex-shrink: 0;
  margin-right: 8px;
  color: #666;
  min-width: 80px;
}

.log-type {
  flex-shrink: 0;
  margin-right: 8px;
  padding: 0 4px;
  border-radius: 2px;
  min-width: 50px;
  text-align: center;
}

.log-item.info .log-type {
  color: #00a0e9;
  background: rgba(0, 160, 233, 0.1);
}

.log-item.error .log-type {
  color: #ff4d4f;
  background: rgba(255, 77, 79, 0.1);
}

.log-message {
  flex: 1;
  word-break: break-word;
  white-space: pre-wrap;
}

pre {
  margin: 0;
  white-space: pre-wrap;
  font-family: monospace;
}
</style> 