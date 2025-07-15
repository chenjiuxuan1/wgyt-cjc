<template>
  <div class="job-recommendation" v-if="visible">
    <div class="job-recommendation-content">
      <div class="header">
        <h3>岗位推荐</h3>
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
          <el-select v-model="params.salary" placeholder="请选择薪资范围" teleported>
            <el-option v-for="item in salaryOptions" :key="item.value" :label="item.label" :value="item.value"></el-option>
          </el-select>
          <div class="weight-slider">
            <span class="weight-label">权重: {{weights.salary}}</span>
            <el-slider v-model="weights.salary" :min="0" :max="100" :step="1"></el-slider>
          </div>
        </div>
        
        <div class="parameter-item">
          <label>学历要求</label>
          <el-select v-model="params.education" placeholder="请选择学历" teleported>
            <el-option v-for="item in educationOptions" :key="item.value" :label="item.label" :value="item.value"></el-option>
          </el-select>
          <div class="weight-slider">
            <span class="weight-label">权重: {{weights.education}}</span>
            <el-slider v-model="weights.education" :min="0" :max="100" :step="1"></el-slider>
          </div>
        </div>
        
        <div class="parameter-item">
          <label>经验要求</label>
          <el-select v-model="params.experience" placeholder="请选择工作经验" teleported>
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
          <el-select v-model="params.scale" placeholder="请选择公司规模" teleported>
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
      </div>

      <div class="actions">
        <el-button type="primary" @click="searchJobs" class="search-btn">开始匹配</el-button>
      </div>

      <div class="results" v-if="recommendedJobs.length > 0">
        <h4>推荐岗位</h4>
        <div class="job-list">
          <div v-for="(job, index) in recommendedJobs" :key="index" class="job-item">
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
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Close } from '@element-plus/icons-vue'
import axios from 'axios'

const visible = ref(false)
const params = reactive({
  city: '',
  salary: '',
  education: '',
  experience: '',
  position: '',
  scale: '',
  companyType: ''
})

const weights = reactive({
  city: 50,
  salary: 50,
  education: 50,
  experience: 50,
  position: 50,
  scale: 50,
  companyType: 50
})

const recommendedJobs = ref([])

// 添加选项数据
const salaryOptions = [
  { label: '3k以下', value: '0-3k' },
  { label: '3-5k', value: '3-5k' },
  { label: '5-8k', value: '5-8k' },
  { label: '8-12k', value: '8-12k' },
  { label: '12-15k', value: '12-15k' },
  { label: '15k以上', value: '15k+' }
]

const educationOptions = [
  { label: '不限', value: '不限' },
  { label: '大专', value: '大专' },
  { label: '本科', value: '本科' },
  { label: '硕士', value: '硕士' }
]

const experienceOptions = [
  { label: '经验不限', value: '经验不限' },
  { label: '1-3年', value: '1-3年' },
  { label: '3-5年', value: '3-5年' },
  { label: '5-10年', value: '5-10年' }
]

const scaleOptions = [
  { label: '1-49人', value: '1-49人' },
  { label: '50-199人', value: '50-199人' },
  { label: '200-499人', value: '200-499人' },
  { label: '500人以上', value: '500+' }
]

const show = () => {
  console.log('Show method called')
  visible.value = true
}

const close = () => {
  visible.value = false
  recommendedJobs.value = []
}

const searchJobs = async () => {
  try {
    const response = await axios.post('/api/jobs/recommend', {
      params,
      weights
    })

    if (!response.data) {
      throw new Error('No data received')
    }

    const data = response.data

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
    console.error('Job recommendation error:', error)
    ElMessage.error('查询失败，请检查后端服务是否启动')
  }
}

defineExpose({
  show,
  close
})
</script>

<style lang="scss" scoped>
.job-recommendation {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;

  .job-recommendation-content {
    position: relative;
    width: 800px;
    max-height: 80vh;
    background: rgba(0, 16, 36, 0.95);
    border: 1px solid rgba(0, 225, 255, 0.2);
    border-radius: 8px;
    padding: 20px;
    color: #fff;
    overflow-y: auto;
    box-shadow: 0 0 20px rgba(0, 225, 255, 0.1);
    backdrop-filter: blur(10px);

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 10px;
      border-bottom: 1px solid rgba(0, 225, 255, 0.2);

      h3 {
        color: #00e1ff;
        margin: 0;
        font-size: 20px;
        text-shadow: 0 0 10px rgba(0, 225, 255, 0.5);
      }

      .close-icon {
        cursor: pointer;
        color: #00e1ff;
        font-size: 20px;
        transition: all 0.3s ease;

        &:hover {
          transform: scale(1.1);
          text-shadow: 0 0 10px rgba(0, 225, 255, 0.8);
        }
      }
    }

    .parameters {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 20px;
      margin-bottom: 20px;

      .parameter-item {
        label {
          display: block;
          margin-bottom: 8px;
          color: #00e1ff;
        }

        .weight-slider {
          margin-top: 8px;
          
          .weight-label {
            display: block;
            margin-bottom: 4px;
            color: rgba(255, 255, 255, 0.7);
            font-size: 12px;
          }
        }

        .full-width {
          width: 100%;
        }
      }
    }

    .actions {
      text-align: center;
      margin: 20px 0;

      .search-btn {
        background: rgba(0, 225, 255, 0.2);
        border: 1px solid rgba(0, 225, 255, 0.4);
        color: #00e1ff;
        padding: 12px 30px;
        font-size: 16px;
        transition: all 0.3s ease;

        &:hover {
          background: rgba(0, 225, 255, 0.3);
          transform: translateY(-2px);
          box-shadow: 0 0 15px rgba(0, 225, 255, 0.3);
        }
      }
    }

    .results {
      margin-top: 20px;
      
      h4 {
        color: #00e1ff;
        margin-bottom: 15px;
      }

      .job-list {
        display: grid;
        gap: 15px;

        .job-item {
          background: rgba(0, 225, 255, 0.1);
          border: 1px solid rgba(0, 225, 255, 0.2);
          border-radius: 6px;
          padding: 15px;
          transition: all 0.3s ease;

          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 15px rgba(0, 225, 255, 0.2);
          }

          h5 {
            color: #00e1ff;
            margin: 0 0 10px 0;
            font-size: 16px;
          }

          .job-info,
          .job-requirements {
            display: flex;
            justify-content: space-between;
            margin-top: 8px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 14px;
          }

          .match-score {
            margin-top: 10px;
            color: #00e1ff;
            font-weight: bold;
            text-align: right;
          }
        }
      }
    }
  }
}

:deep(.el-select) {
  width: 100%;
  
  .el-input {
    width: 100%;
    
    .el-input__wrapper {
      background: rgba(0, 16, 36, 0.8);
      border: 1px solid rgba(0, 225, 255, 0.2);
      box-shadow: none;
      
      &.is-focus {
        border-color: #00e1ff;
      }
      
      .el-input__inner {
        color: #fff;
        
        &::placeholder {
          color: rgba(255, 255, 255, 0.5);
        }
      }
    }
  }
}

:deep(.el-select-dropdown) {
  background: rgba(0, 16, 36, 0.95);
  border: 1px solid rgba(0, 225, 255, 0.2);
  backdrop-filter: blur(10px);
  
  .el-select-dropdown__item {
    color: #fff;
    
    &:hover {
      background: rgba(0, 225, 255, 0.1);
    }
    
    &.selected {
      background: rgba(0, 225, 255, 0.2);
      color: #00e1ff;
      font-weight: bold;
    }
  }
}

:deep(.el-input__inner),
:deep(.el-select .el-input__inner) {
  background: rgba(0, 16, 36, 0.8);
  border: 1px solid rgba(0, 225, 255, 0.2);
  color: #fff;

  &:focus {
    border-color: rgba(0, 225, 255, 0.5);
  }
}

:deep(.el-slider__runway) {
  background-color: rgba(255, 255, 255, 0.1);
}

:deep(.el-slider__bar) {
  background-color: rgba(0, 225, 255, 0.5);
}

:deep(.el-slider__button) {
  border: 2px solid #00e1ff;
  background-color: #00e1ff;
}
</style> 