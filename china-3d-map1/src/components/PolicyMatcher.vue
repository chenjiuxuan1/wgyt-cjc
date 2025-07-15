<template>
  <div class="policy-matcher-container">
    <div class="policy-matcher-header">
      <div class="title">政策推荐</div>
      <div class="close-btn" @click="close">×</div>
    </div>
    
    <div v-if="!showResults" class="user-profile-form">
      <div class="form-title">填写您的个人信息，获取个性化政策推荐</div>
      
      <div class="form-group">
        <label>学历</label>
        <div class="select-wrapper">
          <select v-model="userProfile.education">
            <option value="">请选择</option>
            <option value="高中及以下">高中及以下</option>
            <option value="专科">专科</option>
            <option value="本科">本科</option>
            <option value="硕士">硕士</option>
            <option value="博士">博士</option>
          </select>
        </div>
      </div>
      
      <div class="form-group">
        <label>专业</label>
        <input type="text" v-model="userProfile.major" placeholder="请输入您的专业">
      </div>
      
      <div class="form-group">
        <label>当前状态</label>
        <div class="select-wrapper">
          <select v-model="userProfile.currentStatus">
            <option value="">请选择</option>
            <option value="学生">学生</option>
            <option value="应届毕业生">应届毕业生</option>
            <option value="在职">在职</option>
            <option value="待业">待业</option>
            <option value="创业中">创业中</option>
          </select>
        </div>
      </div>
      
      <div class="form-group">
        <label>工作年限</label>
        <div class="select-wrapper">
          <select v-model="userProfile.workYears">
            <option value="">请选择</option>
            <option value="无工作经验">无工作经验</option>
            <option value="1-3年">1-3年</option>
            <option value="3-5年">3-5年</option>
            <option value="5-10年">5-10年</option>
            <option value="10年以上">10年以上</option>
          </select>
        </div>
      </div>
      
      <div class="form-group">
        <label>是否有创业计划</label>
        <div class="radio-group">
          <label class="radio-label">
            <input type="radio" v-model="userProfile.hasStartupPlan" :value="true">
            <span>是</span>
          </label>
          <label class="radio-label">
            <input type="radio" v-model="userProfile.hasStartupPlan" :value="false">
            <span>否</span>
          </label>
        </div>
      </div>
      
      <div class="form-group">
        <label>期望工作地区</label>
        <div class="select-wrapper">
          <select v-model="userProfile.location">
            <option value="">请选择</option>
            <option v-for="(_, province) in provincePolicies" :key="province" :value="province">
              {{ province }}
            </option>
          </select>
        </div>
      </div>
      
      <div class="form-group">
        <label>行业</label>
        <div class="select-wrapper">
          <select v-model="userProfile.industry">
            <option value="">请选择</option>
            <option value="互联网/IT">互联网/IT</option>
            <option value="金融">金融</option>
            <option value="教育">教育</option>
            <option value="医疗健康">医疗健康</option>
            <option value="制造业">制造业</option>
            <option value="农业">农业</option>
            <option value="服务业">服务业</option>
            <option value="其他">其他</option>
          </select>
        </div>
      </div>
      
      <div class="form-actions">
        <button class="submit-btn" @click="matchPolicies">获取政策推荐</button>
      </div>
    </div>
    
    <div v-if="showResults" class="policy-results">
      <div class="results-header">
        <div class="back-btn" @click="showResults = false">
          <span class="back-icon">←</span> 返回
        </div>
        <div class="results-title">为您匹配到的政策 ({{ matchedPolicies.length }})</div>
      </div>
      
      <div v-if="matchedPolicies.length === 0" class="no-results">
        <div class="no-results-icon">😔</div>
        <div class="no-results-text">暂未找到匹配的政策，请尝试调整您的个人信息</div>
      </div>
      
      <div v-else class="results-list">
        <div v-for="(policy, index) in matchedPolicies" :key="index" class="policy-card" @click="showPolicyDetail(policy)">
          <div class="policy-card-header">
            <div class="policy-card-title">{{ policy.title }}</div>
            <div class="policy-card-region">{{ policy.region }}</div>
          </div>
          <div class="policy-card-content">{{ policy.content }}</div>
          <div class="policy-card-tags">
            <span v-for="(tag, tagIndex) in policy.tags" :key="tagIndex" class="policy-tag">
              {{ tag }}
            </span>
          </div>
          <div class="policy-card-match">
            匹配度: <span class="match-score">{{ policy.matchScore }}%</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 添加政策详情模态框 -->
    <div v-if="showDetailModal" class="policy-detail-modal">
      <div class="policy-detail-content">
        <div class="policy-detail-header">
          <div class="policy-detail-title">{{ selectedPolicy.title }}</div>
          <div class="policy-detail-close" @click="showDetailModal = false">×</div>
        </div>
        <div class="policy-detail-body">
          <div class="policy-detail-info">
            <div class="policy-detail-region">
              <span class="info-label">地区:</span> {{ selectedPolicy.region }}
            </div>
            <div class="policy-detail-type">
              <span class="info-label">类型:</span> {{ selectedPolicy.type }}
            </div>
            <div class="policy-detail-match">
              <span class="info-label">匹配度:</span> <span class="match-score">{{ selectedPolicy.matchScore }}%</span>
            </div>
          </div>
          <div class="policy-detail-tags">
            <span v-for="(tag, tagIndex) in selectedPolicy.tags" :key="tagIndex" class="policy-tag">
              {{ tag }}
            </span>
          </div>
          <div class="policy-detail-content-text">
            {{ selectedPolicy.content }}
          </div>
          <div class="policy-detail-match-reason">
            <div class="match-reason-title">匹配原因</div>
            <ul class="match-reason-list">
              <li v-if="userProfile.location && selectedPolicy.region.includes(userProfile.location)">
                您选择的期望工作地区 <b>{{ userProfile.location }}</b> 与该政策地区相符
              </li>
              <li v-if="userProfile.education && selectedPolicy.tags.includes(userProfile.education)">
                您的学历 <b>{{ userProfile.education }}</b> 符合该政策要求
              </li>
              <li v-if="userProfile.hasStartupPlan && selectedPolicy.tags.includes('创业')">
                您有创业计划，该政策提供创业相关支持
              </li>
              <li v-if="userProfile.currentStatus && selectedPolicy.tags.includes(userProfile.currentStatus)">
                您当前的状态 <b>{{ userProfile.currentStatus }}</b> 符合该政策目标人群
              </li>
              <li v-if="userProfile.industry && selectedPolicy.tags.includes(userProfile.industry)">
                您选择的行业 <b>{{ userProfile.industry }}</b> 与该政策支持的行业相符
              </li>
              <li v-if="userProfile.workYears && selectedPolicy.tags.includes(userProfile.workYears)">
                您的工作年限 <b>{{ userProfile.workYears }}</b> 符合该政策要求
              </li>
              <li v-if="userProfile.major && selectedPolicy.content && selectedPolicy.content.includes(userProfile.major)">
                您的专业 <b>{{ userProfile.major }}</b> 在政策内容中被提及
              </li>
            </ul>
          </div>
        </div>
        <div class="policy-detail-footer">
          <button class="btn-back" @click="showDetailModal = false">返回列表</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import provincePoliciesData from '@/assets/data/provincePolicies.js';
import { provinceSubsidiesData } from '@/assets/data/province_rcbt_data.js';
import { entrepreneurPolicy } from '@/assets/data/province_cyzc_data.js';

const emit = defineEmits(['close']);

// 用户画像数据
const userProfile = reactive({
  education: '',
  major: '',
  currentStatus: '',
  workYears: '',
  hasStartupPlan: false,
  location: '',
  industry: ''
});

// 匹配到的政策列表
const matchedPolicies = ref([]);
// 是否显示结果页面
const showResults = ref(false);

// 添加政策详情模态框状态和选中的政策
const showDetailModal = ref(false);
const selectedPolicy = reactive({
  title: '',
  content: '',
  region: '',
  type: '',
  tags: [],
  matchScore: 0
});

// 合并所有省份政策数据
const provincePolicies = computed(() => {
  return provincePoliciesData;
});

// 政策标签映射
const policyTags = {
  // 学历相关标签
  '博士': ['博士', '博士研究生', '博士学位', '高层次人才'],
  '硕士': ['硕士', '研究生', '硕士研究生', '硕士学位', '高层次人才'],
  '本科': ['本科', '大学本科', '学士', '学士学位'],
  '专科': ['专科', '大专', '高职', '职业院校'],
  '高中及以下': ['高中', '职高', '中专', '技校'],
  
  // 当前状态相关标签
  '学生': ['学生', '在校生', '在读'],
  '应届毕业生': ['应届生', '应届毕业生', '毕业生', '毕业'],
  '在职': ['在职', '就业', '就职', '工作'],
  '待业': ['待业', '失业', '无业'],
  '创业中': ['创业', '自主创业', '创办企业'],
  
  // 工作年限相关标签
  '无工作经验': ['应届', '实习', '无经验'],
  '1-3年': ['1年', '2年', '3年', '初级'],
  '3-5年': ['3年', '4年', '5年', '中级'],
  '5-10年': ['5年', '6年', '7年', '8年', '9年', '10年', '高级'],
  '10年以上': ['10年以上', '资深', '专家', '高级'],
  
  // 创业计划相关标签
  '创业': ['创业', '创业补贴', '创业扶持', '创业资助', '初创', '自主创业', '首次创业'],
  
  // 行业相关标签
  '互联网/IT': ['IT', '互联网', '软件', '人工智能', '大数据', '编程', '信息技术'],
  '金融': ['金融', '银行', '证券', '保险', '投资'],
  '教育': ['教育', '培训', '教师', '学校', '教学'],
  '医疗健康': ['医疗', '健康', '医生', '医师', '医院', '护理'],
  '制造业': ['制造', '生产', '工厂', '加工', '组装'],
  '农业': ['农业', '种植', '养殖', '农村', '农产品'],
  '服务业': ['服务', '餐饮', '酒店', '旅游', '零售']
};

// 政策匹配算法
const matchPolicies = () => {
  console.log('匹配政策...');
  console.log('用户画像:', userProfile);
  
  const allPolicies = [];
  
  // 处理落户政策数据
  Object.entries(provincePoliciesData).forEach(([province, data]) => {
    if (data.conditions) {
      data.conditions.forEach(condition => {
        allPolicies.push({
          title: condition.title,
          content: condition.content,
          region: province,
          type: '落户政策',
          tags: extractTags(condition.content),
          matchScore: 0
        });
      });
    }
    
    if (data.benefits) {
      data.benefits.forEach(benefit => {
        allPolicies.push({
          title: benefit.title,
          content: benefit.content,
          region: province,
          type: '落户福利',
          tags: extractTags(benefit.content),
          matchScore: 0
        });
      });
    }
  });
  
  // 处理人才补贴数据
  Object.entries(provinceSubsidiesData).forEach(([province, data]) => {
    if (data.subsidies) {
      data.subsidies.forEach(subsidy => {
        allPolicies.push({
          title: subsidy.title,
          content: subsidy.content,
          region: province,
          type: '人才补贴',
          tags: extractTags(subsidy.content),
          matchScore: 0
        });
      });
    }
  });
  
  // 处理创业政策数据
  Object.entries(entrepreneurPolicy).forEach(([province, policies]) => {
    if (Array.isArray(policies)) {
      policies.forEach(policy => {
        allPolicies.push({
          title: policy.title,
          content: policy.content,
          region: province,
          type: '创业政策',
          tags: extractTags(policy.content),
          matchScore: 0
        });
      });
    }
  });
  
  console.log(`总共收集了 ${allPolicies.length} 条政策`);
  
  // 计算每条政策的匹配分数
  allPolicies.forEach(policy => {
    policy.matchScore = calculateMatchScore(policy);
  });
  
  // 过滤有效匹配的政策并按匹配分数排序
  matchedPolicies.value = allPolicies
    .filter(policy => policy.matchScore > 0)
    .sort((a, b) => b.matchScore - a.matchScore)
    .slice(0, 20); // 最多展示前20条
  
  console.log(`匹配到 ${matchedPolicies.value.length} 条政策`);
  showResults.value = true;
};

// 从政策内容中提取标签
const extractTags = (content) => {
  const tags = [];
  
  // 确保content是字符串
  if (!content || typeof content !== 'string') {
    return tags;
  }
  
  // 用所有标签关键词搜索内容
  Object.entries(policyTags).forEach(([category, keywords]) => {
    keywords.forEach(keyword => {
      if (keyword && content.includes(keyword)) {
        tags.push(category);
      }
    });
  });
  
  // 去重
  return [...new Set(tags)];
};

// 计算政策与用户画像的匹配分数
const calculateMatchScore = (policy) => {
  let score = 0;
  const maxScore = 100;
  
  // 确保policy和policy.region存在且是字符串
  if (!policy || !policy.region || typeof policy.region !== 'string') {
    return 0;
  }

  // 确保policy.tags存在且是数组
  if (!policy.tags || !Array.isArray(policy.tags)) {
    return 0;
  }
  
  // 1. 地区匹配 (权重25%)
  if (userProfile.location && (policy.region.includes(userProfile.location) || userProfile.location.includes(policy.region))) {
    score += 25;
  }
  
  // 2. 学历匹配 (权重20%)
  if (userProfile.education && policy.tags.includes(userProfile.education)) {
    score += 20;
  }
  
  // 3. 创业意向匹配 (权重20%)
  if (userProfile.hasStartupPlan && policy.tags.includes('创业')) {
    score += 20;
  }
  
  // 4. 当前状态匹配 (权重15%)
  if (userProfile.currentStatus && policy.tags.includes(userProfile.currentStatus)) {
    score += 15;
  }
  
  // 5. 行业匹配 (权重10%)
  if (userProfile.industry && policy.tags.includes(userProfile.industry)) {
    score += 10;
  }
  
  // 6. 工作年限匹配 (权重10%)
  if (userProfile.workYears && policy.tags.includes(userProfile.workYears)) {
    score += 10;
  }
  
  // 内容关键词匹配 (额外加分)
  // 检查专业是否在内容中提到
  if (userProfile.major && policy.content && typeof policy.content === 'string' && policy.content.includes(userProfile.major)) {
    score += 10;
  }
  
  return Math.min(score, maxScore);
};

// 关闭组件
const close = () => {
  emit('close');
};

// 显示政策详情
const showPolicyDetail = (policy) => {
  // 复制政策数据到选中的政策对象
  Object.assign(selectedPolicy, policy);
  // 显示详情模态框
  showDetailModal.value = true;
};

onMounted(() => {
  console.log('PolicyMatcher组件已挂载');
});
</script>

<style scoped>
.policy-matcher-container {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  width: 650px;
  max-width: 90vw;
  max-height: 85vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  position: relative;
  font-family: 'Microsoft YaHei', Arial, sans-serif;
}

.policy-matcher-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eaeaea;
  background: linear-gradient(135deg, #1a6fc0, #2a9d8f);
}

.policy-matcher-header .title {
  color: white;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  font-size: 20px;
  background-color: rgba(255, 255, 255, 0.2);
  transition: background-color 0.2s;
}

.close-btn:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

.user-profile-form {
  padding: 20px;
}

.form-title {
  font-size: 16px;
  color: #333;
  margin-bottom: 20px;
  text-align: center;
  font-weight: 500;
}

.form-group {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-size: 14px;
  color: #333;
  margin-bottom: 6px;
  font-weight: 500;
}

.select-wrapper {
  position: relative;
  width: 100%;
}

.select-wrapper::after {
  content: '';
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 0;
  height: 0;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-top: 5px solid #666;
  pointer-events: none;
}

.select-wrapper select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #fff;
  font-size: 14px;
  color: #333;
  appearance: none;
  cursor: pointer;
}

input[type="text"] {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
}

.radio-group {
  display: flex;
  gap: 20px;
}

.radio-label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.radio-label input {
  margin-right: 6px;
}

.form-actions {
  margin-top: 25px;
  text-align: center;
}

.submit-btn {
  background: linear-gradient(135deg, #1a6fc0, #2a9d8f);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-btn:hover {
  background: linear-gradient(135deg, #166ab8, #258c80);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.policy-results {
  padding: 0;
}

.results-header {
  padding: 15px 20px;
  border-bottom: 1px solid #eaeaea;
  display: flex;
  align-items: center;
}

.back-btn {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #1a6fc0;
  font-size: 14px;
  margin-right: 15px;
}

.back-icon {
  margin-right: 5px;
  font-size: 18px;
}

.results-title {
  font-size: 16px;
  color: #333;
  font-weight: 500;
}

.no-results {
  padding: 40px 20px;
  text-align: center;
}

.no-results-icon {
  font-size: 40px;
  margin-bottom: 15px;
}

.no-results-text {
  color: #666;
  font-size: 15px;
}

.results-list {
  padding: 15px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 15px;
}

.policy-card {
  border: 1px solid #eaeaea;
  border-radius: 8px;
  padding: 15px;
  background-color: #f9f9f9;
  transition: transform 0.2s, box-shadow 0.2s;
  height: 100%;
  display: flex;
  flex-direction: column;
  cursor: pointer; /* 添加指针样式表明可点击 */
}

.policy-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.policy-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.policy-card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a6fc0;
}

.policy-card-region {
  font-size: 13px;
  color: #666;
  padding: 3px 8px;
  background-color: #f0f0f0;
  border-radius: 4px;
}

.policy-card-content {
  font-size: 14px;
  color: #333;
  flex-grow: 1;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.policy-card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 12px;
}

.policy-tag {
  font-size: 12px;
  color: #555;
  background-color: #e8f4fc;
  padding: 3px 8px;
  border-radius: 4px;
}

.policy-card-match {
  font-size: 13px;
  color: #666;
  display: flex;
  justify-content: flex-end;
}

.match-score {
  color: #1a6fc0;
  font-weight: 600;
  margin-left: 5px;
}

/* 政策详情模态框样式 */
.policy-detail-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.policy-detail-content {
  background-color: #fff;
  border-radius: 8px;
  width: 700px;
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  animation: modal-in 0.3s ease-out;
}

@keyframes modal-in {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.policy-detail-header {
  padding: 16px 20px;
  border-bottom: 1px solid #eaeaea;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #1a6fc0, #2a9d8f);
  border-radius: 8px 8px 0 0;
}

.policy-detail-title {
  color: white;
  font-size: 18px;
  font-weight: 600;
}

.policy-detail-close {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  font-size: 20px;
  background-color: rgba(255, 255, 255, 0.2);
  transition: background-color 0.2s;
}

.policy-detail-close:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

.policy-detail-body {
  padding: 20px;
  overflow-y: auto;
  max-height: calc(90vh - 140px);
}

.policy-detail-info {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px dashed #eaeaea;
}

.policy-detail-region,
.policy-detail-type,
.policy-detail-match {
  font-size: 14px;
  color: #555;
}

.info-label {
  color: #888;
  margin-right: 5px;
}

.policy-detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}

.policy-detail-content-text {
  font-size: 15px;
  line-height: 1.6;
  color: #333;
  margin-bottom: 25px;
  white-space: pre-line;
}

.policy-detail-match-reason {
  background-color: #f5f9ff;
  border: 1px solid #e0ebf8;
  border-radius: 6px;
  padding: 15px;
}

.match-reason-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a6fc0;
  margin-bottom: 10px;
}

.match-reason-list {
  margin: 0;
  padding-left: 20px;
}

.match-reason-list li {
  margin-bottom: 8px;
  font-size: 14px;
  color: #555;
}

.policy-detail-footer {
  padding: 15px 20px;
  border-top: 1px solid #eaeaea;
  display: flex;
  justify-content: flex-end;
}

.btn-back {
  background-color: #f0f0f0;
  color: #555;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-back:hover {
  background-color: #e0e0e0;
}
</style> 