<template>
  <div class="job-alert" v-if="visible">
    <div class="job-alert-content">
      <div class="header">
        <h3>岗位预警</h3>
        <el-icon class="close-icon" @click="close">
          <Close />
        </el-icon>
      </div>
      
      <div class="parameters">
        <div class="parameter-item">
          <label>工作城市</label>
          <el-input v-model="params.city" placeholder="请输入城市"></el-input>
          <div class="weight-slider">
            <span class="weight-label">权重: {{weights.city}}</span>
            <el-slider v-model="weights.city" :min="0" :max="100" :step="1"></el-slider>
          </div>
        </div>
        
        <div class="parameter-item">
          <label>工作薪资</label>
          <el-select v-model="params.salary" placeholder="请选择薪资范围">
            <el-option v-for="item in salaryOptions" :key="item.value" :label="item.label" :value="item.value"></el-option>
          </el-select>
          <div class="weight-slider">
            <span class="weight-label">权重: {{weights.salary}}</span>
            <el-slider v-model="weights.salary" :min="0" :max="100" :step="1"></el-slider>
          </div>
        </div>
        
        <div class="parameter-item">
          <label>学历要求</label>
          <el-select v-model="params.education" placeholder="请选择学历">
            <el-option v-for="item in educationOptions" :key="item.value" :label="item.label" :value="item.value"></el-option>
          </el-select>
          <div class="weight-slider">
            <span class="weight-label">权重: {{weights.education}}</span>
            <el-slider v-model="weights.education" :min="0" :max="100" :step="1"></el-slider>
          </div>
        </div>
        
        <div class="parameter-item">
          <label>经验要求</label>
          <el-select v-model="params.experience" placeholder="请选择工作经验">
            <el-option v-for="item in experienceOptions" :key="item.value" :label="item.label" :value="item.value"></el-option>
          </el-select>
          <div class="weight-slider">
            <span class="weight-label">权重: {{weights.experience}}</span>
            <el-slider v-model="weights.experience" :min="0" :max="100" :step="1"></el-slider>
          </div>
        </div>
        
        <div class="parameter-item">
          <label>工作岗位</label>
          <el-input v-model="params.position" placeholder="请输入岗位"></el-input>
          <div class="weight-slider">
            <span class="weight-label">权重: {{weights.position}}</span>
            <el-slider v-model="weights.position" :min="0" :max="100" :step="1"></el-slider>
          </div>
        </div>
        
        <div class="parameter-item">
          <label>公司规模</label>
          <el-select v-model="params.scale" placeholder="请选择公司规模">
            <el-option v-for="item in scaleOptions" :key="item.value" :label="item.label" :value="item.value"></el-option>
          </el-select>
          <div class="weight-slider">
            <span class="weight-label">权重: {{weights.scale}}</span>
            <el-slider v-model="weights.scale" :min="0" :max="100" :step="1"></el-slider>
          </div>
        </div>
        
        <div class="parameter-item">
          <label>企业类型</label>
          <el-input v-model="params.companyType" placeholder="请输入企业类型"></el-input>
          <div class="weight-slider">
            <span class="weight-label">权重: {{weights.companyType}}</span>
            <el-slider v-model="weights.companyType" :min="0" :max="100" :step="1"></el-slider>
          </div>
        </div>

        <div class="parameter-item">
          <label>掌握技能</label>
          <el-input 
            v-model="params.skills" 
            type="textarea" 
            :rows="2"
            placeholder="请输入您掌握的技能，多个技能用逗号分隔"
          ></el-input>
        </div>
      </div>

      <div class="actions">
        <el-button type="primary" @click="searchJobs" class="search-btn">查找岗位</el-button>
      </div>

      <div class="results" v-if="recommendedJobs.length > 0">
        <h4>匹配岗位</h4>
        <div class="job-list">
          <div 
            v-for="(job, index) in recommendedJobs" 
            :key="index" 
            class="job-item"
            :class="{ 'selected': selectedJob && selectedJob.position === job.position }"
            @click="viewJobDetail(job)"
          >
            <h5>{{ job.position }}</h5>
            <div class="job-info">
              <span>{{ job.company }}</span>
              <span>{{ job.city }} | {{ job.salary }}</span>
            </div>
            <div class="job-requirements">
              <span>{{ job.education }} | {{ job.experience }}</span>
              <span>{{ job.companyType }} | {{ job.scale }}</span>
            </div>
            <div class="match-score">
              匹配度: {{ Math.round(job.matchScore) }}%
            </div>
          </div>
        </div>

        <el-dialog
          v-model="showDetail"
          title="岗位详情"
          width="50%"
          :close-on-click-modal="false"
          class="job-detail-dialog"
        >
          <template v-if="selectedJob">
            <div class="job-detail">
              <div class="detail-header">
                <h3>{{ selectedJob.position }}</h3>
                <div class="company-info">{{ selectedJob.company }}</div>
              </div>
              
              <div class="detail-content">
                <div class="detail-item">
                  <label>工作地点</label>
                  <span>{{ selectedJob.city }}</span>
                </div>
                <div class="detail-item">
                  <label>薪资范围</label>
                  <span>{{ selectedJob.salary }}</span>
                </div>
                <div class="detail-item">
                  <label>学历要求</label>
                  <span>{{ selectedJob.education }}</span>
                </div>
                <div class="detail-item">
                  <label>经验要求</label>
                  <span>{{ selectedJob.experience }}</span>
                </div>
                <div class="detail-item">
                  <label>公司类型</label>
                  <span>{{ selectedJob.companyType }}</span>
                </div>
                <div class="detail-item">
                  <label>公司规模</label>
                  <span>{{ selectedJob.scale }}</span>
                </div>
                <div class="detail-item">
                  <label>匹配度</label>
                  <span class="match-score">{{ Math.round(selectedJob.matchScore) }}%</span>
                </div>
              </div>

              <div class="detail-actions">
                <el-button type="warning" @click="getJobAlert" :loading="loading">
                  获取岗位预警
                </el-button>
              </div>

              <div class="alert-result" v-if="alertResult">
                <h4>预警分析</h4>
                <div class="result-content">{{ alertResult }}</div>
              </div>
            </div>
          </template>
        </el-dialog>

        <div class="alert-result" v-if="alertResult && !showDetail">
          <h4>预警分析</h4>
          <div class="result-content">{{ alertResult }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Close } from '@element-plus/icons-vue'
import axios, { AxiosError } from 'axios'

interface Job {
  position: string
  company: string
  city: string
  salary: string
  education: string
  experience: string
  companyType: string
  scale: string
  matchScore: number
}

interface Option {
  label: string
  value: string
}

interface JobParams {
  city: string
  salary: string
  education: string
  experience: string
  position: string
  scale: string
  companyType: string
  skills: string
}

interface JobWeights {
  city: number
  salary: number
  education: number
  experience: number
  position: number
  scale: number
  companyType: number
}

interface JobResponse {
  code: number
  message?: string
  data: Job[]
}

const visible = ref<boolean>(false)
const params = reactive<JobParams>({
  city: '',
  salary: '',
  education: '',
  experience: '',
  position: '',
  scale: '',
  companyType: '',
  skills: ''
})

const weights = reactive<JobWeights>({
  city: 50,
  salary: 50,
  education: 50,
  experience: 50,
  position: 50,
  scale: 50,
  companyType: 50
})

const recommendedJobs = ref<Job[]>([])
const selectedJob = ref<Job | null>(null)
const alertResult = ref<string>('')
const showDetail = ref<boolean>(false)
const loading = ref<boolean>(false)

const salaryOptions: Option[] = [
  { label: '3k以下', value: '0-3k' },
  { label: '3-5k', value: '3-5k' },
  { label: '5-8k', value: '5-8k' },
  { label: '8-12k', value: '8-12k' },
  { label: '12-15k', value: '12-15k' },
  { label: '15k以上', value: '15k+' }
]

const educationOptions: Option[] = [
  { label: '不限', value: '不限' },
  { label: '大专', value: '大专' },
  { label: '本科', value: '本科' },
  { label: '硕士', value: '硕士' }
]

const experienceOptions: Option[] = [
  { label: '经验不限', value: '经验不限' },
  { label: '1-3年', value: '1-3年' },
  { label: '3-5年', value: '3-5年' },
  { label: '5-10年', value: '5-10年' }
]

const scaleOptions: Option[] = [
  { label: '1-49人', value: '1-49人' },
  { label: '50-199人', value: '50-199人' },
  { label: '200-499人', value: '200-499人' },
  { label: '500人以上', value: '500+' }
]

const show = () => {
  visible.value = true
}

const close = () => {
  visible.value = false
  recommendedJobs.value = []
  selectedJob.value = null
  alertResult.value = ''
}

const searchJobs = async () => {
  try {
    const response = await axios.post('/api/jobs/recommend', {
      params,
      weights
    });

    if (!response.data) {
      throw new Error('No data received');
    }

    const data = response.data as JobResponse;

    if (data.code === 200) {
      if (data.data.length === 0) {
        ElMessage({
          message: '未找到匹配的岗位',
          type: 'warning'
        })
      } else {
        ElMessage({
          message: `找到 ${data.data.length} 个匹配的岗位`,
          type: 'success'
        })
      }
      recommendedJobs.value = data.data
    } else {
      ElMessage.error(data.message || '查询失败')
    }
  } catch (error) {
    console.error('Job alert error:', error)
    if (error instanceof Error) {
      ElMessage.error(error.message)
    } else {
      ElMessage.error('查询失败，请检查后端服务是否启动')
    }
  }
}

const getJobAlert = async () => {
  if (!selectedJob.value) {
    ElMessage.warning('请先选择一个岗位')
    return
  }

  loading.value = true
  try {
    const workspace = '87c53d43-4fba-4ec0-b275-b7370dba0752'
    const url = `/api/v1/workspace/${workspace}/chat`
    
    const prompt = `
      我是一名求职者，以下是我的情况：
      - 期望城市：${params.city}
      - 期望薪资：${params.salary}
      - 学历：${params.education}
      - 工作经验：${params.experience}
      - 掌握技能：${params.skills}

      我想应聘这个职位：
      - 职位名称：${selectedJob.value.position}
      - 公司名称：${selectedJob.value.company}
      - 公司规模：${selectedJob.value.scale}
      - 公司类型：${selectedJob.value.companyType}
      - 要求学历：${selectedJob.value.education}
      - 要求经验：${selectedJob.value.experience}
      - 薪资范围：${selectedJob.value.salary}

      请分析我是否适合这个职位，有什么优势和不足，以及如何提高竞争力？
    `

    const response = await axios.post(url, {
      message: prompt,
      mode: 'chat',
      max_token: 512
    }, {
      headers: {
        'Authorization': 'Bearer GG41P0D-JDW4N05-PTH2RHS-BJQK8HB',
        'Content-Type': 'application/json',
        'accept': 'application/json'
      },
      timeout: 30000
    })

    alertResult.value = response.data.textResponse
    ElMessage.success('岗位预警分析完成')
  } catch (error) {
    console.error('Job alert analysis error:', error)
    if (error instanceof AxiosError) {
      ElMessage.error(error.response?.data?.message || '岗位预警分析失败')
    } else if (error instanceof Error) {
      ElMessage.error(error.message)
    } else {
      ElMessage.error('岗位预警分析失败')
    }
  } finally {
    loading.value = false
  }
}

const viewJobDetail = (job: Job) => {
  selectedJob.value = job
  showDetail.value = true
}

const closeDetail = () => {
  showDetail.value = false
}

defineExpose({
  show,
  close
})
</script>

<style lang="scss" scoped>
.job-alert {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.job-alert-content {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  padding: 20px;
  width: 80%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h3 {
  margin: 0;
  color: #333;
}

.close-icon {
  cursor: pointer;
  font-size: 20px;
  color: #666;
}

.close-icon:hover {
  color: #333;
}

.parameters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.parameter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.parameter-item label {
  font-weight: 500;
  color: #333;
}

.weight-slider {
  margin-top: 8px;
}

.weight-label {
  display: block;
  margin-bottom: 4px;
  color: #666;
  font-size: 14px;
}

.actions {
  margin-top: 20px;
  text-align: center;
}

.search-btn {
  min-width: 120px;
}

.results {
  margin-top: 30px;
}

.results h4 {
  margin-bottom: 15px;
  color: #333;
}

.job-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.job-item {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.job-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.job-item.selected {
  border-color: #409EFF;
  background: rgba(64, 158, 255, 0.1);
}

.job-item h5 {
  margin: 0 0 10px 0;
  color: #333;
}

.job-info, .job-requirements {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.match-score {
  margin-top: 10px;
  text-align: right;
  color: #409EFF;
  font-weight: 500;
}

.alert-action {
  margin-top: 20px;
  text-align: center;
}

.alert-btn {
  min-width: 120px;
}

.alert-result {
  margin-top: 30px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 6px;
}

.alert-result h4 {
  margin-bottom: 15px;
}

.result-content {
  white-space: pre-line;
  line-height: 1.6;
  color: #333;
}

.job-detail-dialog {
  :deep(.el-dialog) {
    z-index: 2001;
  }
  
  :deep(.el-dialog__body) {
    padding: 20px;
  }
}

.job-detail {
  .detail-header {
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #eee;

    h3 {
      margin: 0 0 10px 0;
      color: #333;
      font-size: 20px;
    }

    .company-info {
      color: #666;
      font-size: 16px;
    }
  }

  .detail-content {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 20px;

    .detail-item {
      display: flex;
      flex-direction: column;
      gap: 5px;

      label {
        color: #666;
        font-size: 14px;
      }

      span {
        color: #333;
        font-size: 16px;
        font-weight: 500;

        &.match-score {
          color: #409EFF;
        }
      }
    }
  }

  .detail-actions {
    text-align: center;
    margin: 20px 0;
  }
}
</style> 