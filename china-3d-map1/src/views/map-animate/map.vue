<template>
  <div class="map-level">
    <!-- 科技感标题 -->
    <div class="data-title">
      <div class="title-box">
        <div class="title-bg">
          <div class="bg-line"></div>
        </div>
        <div class="title-content">
          <div class="tech-line left">
            <div class="line-dot"></div>
            <div class="line-segment"></div>
            <div class="line-arrow"></div>
            <div class="tech-dots">
              <span></span><span></span><span></span>
            </div>
          </div>
          <div class="title-text">维谷云途   基于大模型可视化驱动的智能择业决策助手</div>
          <div class="tech-line right">
            <div class="line-dot"></div>
            <div class="line-segment"></div>
            <div class="line-arrow"></div>
            <div class="tech-dots">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
        <div class="tech-border">
          <div class="border-corner tl"></div>
          <div class="border-corner tr"></div>
          <div class="border-corner bl"></div>
          <div class="border-corner br"></div>
          <div class="border-line top"></div>
          <div class="border-line right"></div>
          <div class="border-line bottom"></div>
          <div class="border-line left"></div>
        </div>
      </div>
    </div>

    <div class="canvas-container" :style="{ display: is3DMap ? 'none' : 'block' }">
      <canvas id="canvas"></canvas>
      
      <!-- 添加岗位推荐按钮 -->
      <div class="job-recommend-btn-container" v-show="false">
        <div class="job-recommend-btn" @click="handleJobRecommend">
          <el-icon>
            <Location />
          </el-icon>
          <span>岗位推荐</span>
        </div>
      </div>

      <!-- 添加岗位预警按钮 -->
      <div class="job-alert-btn-container" v-show="false">
        <div class="job-alert-btn" @click="handleJobAlert">
          <el-icon>
            <Bell />
          </el-icon>
          <span>岗位预警</span>
        </div>
      </div>
    </div>
   
    <!-- 政策匹配器弹窗 -->
    <div v-if="showPolicyMatcherModal" class="modal-overlay" @click.self="closePolicyMatcher12">
      <policy-matcher @close="closePolicyMatcher12" />
    </div>
    
    <!-- 添加岗位推荐组件 -->
    <job-recommendation ref="jobRecommendationRef" @close="closeJobRecommendation"></job-recommendation>
    
    <!-- 添加岗位预警组件 -->
    <job-alert ref="jobAlertRef" @close="closeJobAlert"></job-alert>
    
    <div id="amap-container" :style="{ display: is3DMap ? 'block' : 'none' }" class="amap-container"></div>

    <!-- 3D地图返回按钮 -->
    <div class="map3d-return-btn-container" v-show="is3DMap">
      <div class="map3d-return-btn" @click="handleReturn">
        <div class="btn-frame">
          <div class="frame-line top"></div>
          <div class="frame-line right"></div>
          <div class="frame-line bottom"></div>
          <div class="frame-line left"></div>
        </div>
        <i class="el-icon-back"></i>
        <span>返回上一级</span>
        <div class="btn-glow"></div>
      </div>
    </div>

    <!-- 2D地图返回按钮 -->
    <div class="map2d-return-btn-container" v-show="!is3DMap && app && app.currentScene === 'childScene'">
      <div class="map2d-return-btn" @click="goBack">
        <div class="btn-frame">
          <div class="frame-line top"></div>
          <div class="frame-line right"></div>
          <div class="frame-line bottom"></div>
          <div class="frame-line left"></div>
        </div>
        <i class="el-icon-back"></i>
        <span>返回上一级</span>
        <div class="btn-glow"></div>
      </div>
    </div>

    <!-- 左上词云图 -->
    <div class="table left-table top" v-show="chartVisible.wordCloud && !is3DMap">
      <div class="chart-header">
        <span>地区分布</span>
      </div>
      <div id="wordCloudChart" class="chart-container"></div>
    </div>

    <!-- 左下趋势图 -->
    <div class="table left-table bottom" v-show="chartVisible.pie && !is3DMap">
      <div class="chart-header">
        <span>职位发布数量趋势</span>
      </div>
      <div id="pieChart" class="chart-container"></div>
    </div>

    <!-- 右上河流图 -->
    <div class="table right-table top" v-show="chartVisible.calendar && !is3DMap">
      <div class="chart-header">
        <span>职位发布趋势</span>
      </div>
      <div id="calendarChart" class="chart-container"></div>
    </div>

    <!-- Live2D容器 -->
    <div class="live2d-container" v-show="true">
      <canvas ref="liveCanvas" />
      <!-- 添加消息气泡容器 -->
      <div class="message-bubble" v-if="chatHistory.length > 0">
        {{ chatHistory[chatHistory.length - 1].text }}
      </div>
        <!-- 添加AI面试按钮 -->
      <div class="ai-interview-btn" @click="openAiInterview">
        <i class="ai-icon"></i>
        <span>ai面试</span>
      </div>
      <!-- 添加视频按钮 -->
      <div class="video-btn" @click="showVideoModal = true">
        <i class="video-icon"></i>
        <span>学习推荐</span>
      </div>

    </div>
    <!-- 添加视频弹窗 -->
    <div class="video-modal" v-if="showVideoModal">
      <div class="modal-content">
        <div class="modal-header">
          <span>视频</span>
          <button class="close-btn" @click="showVideoModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <iframe 
            :src="'http://10.9.3.130:5000/video'"
            frameborder="0"
            allowfullscreen
          ></iframe>
        </div>
      </div>
    </div>


    <!-- 独立的聊天输入框 -->
    <div class="fixed-chat-input">
      <input 
        v-model="userInput" 
        @keyup.enter="sendMessage" 
        placeholder="输入问题..." 
        type="text"
        ref="chatInput"
        id="chatInput"
        name="chatInput"
        autocomplete="off"
      >
      <button @click.prevent="sendMessage" type="button">发送</button>
      <button @click.prevent="toggleRecording" type="button" :disabled="isButtonDisabled" class="voice-btn">{{ buttonText }}</button>
      <div v-if="errorMessage" class="record-error">{{ errorMessage }}</div>
    </div>

    <div class="return-btn" @click="goBack">返回上一级</div>
    
    <!-- 添加半圆轮播组件 -->
    <div class="carousel-container" v-show="app && app.currentScene === 'mainScene' && showArcCarousel">
      <div class="pagination">
        <span class="dot active" data-target-group="0"></span>
        <span class="dot" data-target-group="1"></span>
        <span class="dot" data-target-group="2"></span>
        <span class="dot" data-target-group="3"></span>
      </div>

      <div class="segmented-arc-container">
        <div class="segmented-arc">
        </div>
        <div class="arc-labels">
          <span id="label-0"></span>
          <span id="label-1"></span>
          <span id="label-2"></span>
          <span id="label-3"></span>
        </div>
      </div>
    </div>
    <!-- 添加控制按钮 -->
    <div class="arc-toggle-btn">
        <div class="checkbox-wrapper">
          <input
              name="arc_toggle"
              id="arcToggle"
              type="checkbox"
              :checked="showArcCarousel"
              @change="toggleArcCarousel"
          />
          <label for="arcToggle">
            <div class="tick_mark">
              <div class="cross"></div>
            </div>
          </label>
        </div>
      </div>
    <!-- 原始按钮组但设置为隐藏 -->
    <div class="map-btn-group" v-show="app && app.currentScene === 'mainScene'">
      <div class="btn" :class="{ active: showPolicyMatcherModal }" @click="openPolicyMatcher" id="btn-policy">政策推荐</div>
      <div class="btn" :class="{ active: showCareerTestModal }" @click="openCareerTest" id="btn-career">职业测试</div>
      <div class="btn" :class="{ active: is3DMap }" @click="toggleMapMode" id="btn-3dmap">3D地图户</div>
      <div class="btn" :class="{ active: state.bar }" @click="setEffectToggle('bar')" id="btn-bar">柱状图</div>
      <div class="btn" :class="{ active: state.flyLine }" @click="setEffectToggle('flyLine')" id="btn-flyline">飞线</div>
      <div class="btn" :class="{ active: state.scatter }" @click="setEffectToggle('scatter')" id="btn-scatter">散点图</div>
      <div class="btn" :class="{ active: state.card }" @click="setEffectToggle('card')" id="btn-card">标签</div>
      <div class="btn" :class="{ active: state.particle }" @click="setEffectToggle('particle')" id="btn-particle">粒子效果</div>
      <div class="btn" :class="{ active: state.mirror }" @click="setEffectToggle('mirror')" id="btn-mirror">镜面反射</div>
      <div class="btn" :class="{ active: state.path }" @click="setEffectToggle('path')" id="btn-path">路径</div>
      <!-- 添加控制图表显示的按钮 -->
      <div class="btn" :class="{ active: chartVisible.pie }" @click="toggleChart('pie')" id="btn-pie">职位数量图</div>
      <div class="btn" :class="{ active: chartVisible.wordCloud }" @click="toggleChart('wordCloud')" id="btn-wordcloud">学历经验图</div>
      <div class="btn" :class="{ active: chartVisible.calendar }" @click="toggleChart('calendar')" id="btn-calendar">趋势图</div>
      <!-- 新增按钮 -->
      <div class="btn" :class="{ active: showJobRecommendation }" @click="openJobRecommendation" id="btn-job" v-show="false">岗位推荐</div>
      <div class="btn" :class="{ active: showJobAlert }" @click="openJobAlert" id="btn-alert" v-show="false">岗位预警</div>
      <div class="btn" :class="{ active: showPathPlanning }" @click="openPathPlanning" id="btn-planning" v-show="false">路径规划</div>
    </div>

    <!-- 左上角信息面板 - 落户政策 -->
    <div class="hologram-panel left-top" 
         v-show="app && app.currentScene === 'childScene'"
         :class="{ 'panel-enter': app && app.currentScene === 'childScene' }"
         @mouseenter="isHoveringLeft = true"
         @mouseleave="isHoveringLeft = false">
      <div class="holo-frame">
        <div class="frame-line top"></div>
        <div class="frame-line right"></div>
        <div class="frame-line bottom"></div>
        <div class="frame-line left"></div>
        <div class="corner-box tl"></div>
        <div class="corner-box tr"></div>
        <div class="corner-box bl"></div>
        <div class="corner-box br"></div>
      </div>
      
      <div class="holo-header">
        <div class="header-grid"></div>
        <div class="header-content">
          <div class="tech-dots">
            <span></span><span></span><span></span>
          </div>
          <h2>落户条件及好处</h2>
          <div class="tech-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <div class="holo-content" ref="leftPanelContent">
        <div class="policy-content" v-if="currentPolicy">
          <div class="holo-section" @click="showSourceLink(currentPolicy)">
            <div class="section-header">
              <div class="tech-line"></div>
              <h3>落户条件</h3>
              <div class="tech-line"></div>
            </div>
            <div v-for="(condition, index) in currentPolicy.conditions" 
                 :key="'condition-' + index" 
                 class="holo-item">
              <div class="item-header">
                <span class="tech-icon"></span>
                {{ condition.title }}
              </div>
              <div class="item-body">{{ condition.content }}</div>
            </div>
          </div>

          <div class="holo-section">
            <div class="section-header">
              <div class="tech-line"></div>
              <h3>落户好处</h3>
              <div class="tech-line"></div>
            </div>
            <div v-for="(benefit, index) in currentPolicy.benefits" 
                 :key="'benefit-' + index" 
                 class="holo-item">
              <div class="item-header">
                <span class="tech-icon"></span>
                {{ benefit.title }}
              </div>
              <div class="item-body">{{ benefit.content }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="scan-line"></div>
      <div class="holo-overlay"></div>
    </div>

    <!-- 右上角信息面板 - 人才补贴政策 -->
    <div class="hologram-panel right-top" 
         v-show="app && app.currentScene === 'childScene'"
         :class="{ 'panel-enter': app && app.currentScene === 'childScene' }"
         @mouseenter="isHoveringRight = true"
         @mouseleave="isHoveringRight = false">
      <div class="holo-frame">
        <div class="frame-line top"></div>
        <div class="frame-line right"></div>
        <div class="frame-line bottom"></div>
        <div class="frame-line left"></div>
        <div class="corner-box tl"></div>
        <div class="corner-box tr"></div>
        <div class="corner-box bl"></div>
        <div class="corner-box br"></div>
      </div>
      
      <div class="holo-header">
        <div class="header-grid"></div>
        <div class="header-content">
          <div class="tech-dots">
            <span></span><span></span><span></span>
          </div>
          <h2>人才补贴政策</h2>
          <div class="tech-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <div class="holo-content" ref="rightPanelContent">
        <div v-if="currentSubsidy && currentSubsidy.subsidies">
          <div class="holo-section" @click="showSourceLink(currentSubsidy)">
            <div v-for="(subsidy, index) in currentSubsidy.subsidies" 
                 :key="'subsidy-' + index" 
                 class="holo-item">
              <div class="item-header">
                <span class="tech-icon"></span>
                {{ subsidy.title }}
              </div>
              <div class="item-body">{{ subsidy.content }}</div>
            </div>
          </div>
        </div>
        <div v-else class="no-data">
          <div class="tech-icon"></div>
          <span>该地区补贴政策信息正在完善中...</span>
        </div>
      </div>
      
      <div class="scan-line"></div>
      <div class="holo-overlay"></div>
    </div>

      <!-- 子地图三个模块 -->
  <!-- 模块1: 职位数量动态 -->
  <div class="hologram-panel region-box region-box-1" 
       v-show="app && app.currentScene === 'childScene' && panelVisibility.panel1"
       :class="{ 'panel-enter': app && app.currentScene === 'childScene' }">
    <div class="holo-frame">
      <div class="frame-line top"></div>
      <div class="frame-line right"></div>
      <div class="frame-line bottom"></div>
      <div class="frame-line left"></div>
      <div class="corner-box tl"></div>
      <div class="corner-box tr"></div>
      <div class="corner-box bl"></div>
      <div class="corner-box br"></div>
    </div>
    
    <div class="holo-header">
      <div class="header-grid"></div>
      <div class="header-content">
        <div class="tech-dots">
          <span></span><span></span><span></span>
        </div>
        <h2>{{ currentArea.name }}职位数量动态</h2>
        <div class="tech-dots">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>

    <div class="holo-content" style="height: 400px;">
      <div class="tech-border">
        <div class="border-line top"></div>
        <div class="border-line right"></div>
        <div class="border-line bottom"></div>
        <div class="border-line left"></div>
        <div class="border-corner tl"></div>
        <div class="border-corner tr"></div>
        <div class="border-corner bl"></div>
        <div class="border-corner br"></div>
      </div>
      <!-- 添加echarts图表 -->
      <div id="jobTimelineChart" ref="jobTimelineChart" style="width: 100%; height: 380px;"></div>
    </div>
    
    <div class="scan-line"></div>
    <div class="holo-overlay"></div>
  </div>

  <!-- 模块2: 人才补贴政策 -->
  <div class="hologram-panel region-box region-box-2" 
       v-show="app && app.currentScene === 'childScene' && panelVisibility.panel2"
       :class="{ 'panel-enter': app && app.currentScene === 'childScene' }">
    <div class="holo-frame">
      <div class="frame-line top"></div>
      <div class="frame-line right"></div>
      <div class="frame-line bottom"></div>
      <div class="frame-line left"></div>
      <div class="corner-box tl"></div>
      <div class="corner-box tr"></div>
      <div class="corner-box bl"></div>
      <div class="corner-box br"></div>
    </div>
    
    <div class="holo-header">
      <div class="header-grid"></div>
      <div class="header-content">
        <div class="tech-dots">
          <span></span><span></span><span></span>
        </div>
        <h2>{{ currentArea.name }}就业分析</h2>
        <div class="tech-dots">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>

    <div class="holo-content">
      <div class="tech-border">
        <div class="border-line top"></div>
        <div class="border-line right"></div>
        <div class="border-line bottom"></div>
        <div class="border-line left"></div>
        <div class="border-corner tl"></div>
        <div class="border-corner tr"></div>
        <div class="border-corner bl"></div>
        <div class="border-corner br"></div>
      </div>
      <!-- 薪资范围与工作年限散点图 -->
      <div class="holo-section">
        <div class="section-header">
          <div class="tech-line"></div>
          <h3>薪资范围与工作年限关系</h3>
          <div class="tech-line"></div>
        </div>
        <div class="holo-item">
          <div class="item-body chart-container">
            <div ref="salaryExperienceChart" style="width: 100%; height: 380px;"></div>
          </div>
        </div>
      </div>
      <!-- 原有的就业见习补贴内容 -->
    </div>
    
    <div class="scan-line"></div>
    <div class="holo-overlay"></div>
  </div>

  <!-- 新增: 红框区域3 - 左下角模块框 -->
  <div class="hologram-panel region-box region-box-3" 
       v-show="app && app.currentScene === 'childScene' && panelVisibility.panel3"
       :class="{ 'panel-enter': app && app.currentScene === 'childScene' }">
    <div class="holo-frame">
      <div class="frame-line top"></div>
      <div class="frame-line right"></div>
      <div class="frame-line bottom"></div>
      <div class="frame-line left"></div>
      <div class="corner-box tl"></div>
      <div class="corner-box tr"></div>
      <div class="corner-box bl"></div>
      <div class="corner-box br"></div>
    </div>
    
    <div class="holo-header">
      <div class="header-grid"></div>
      <div class="header-content">
        <div class="tech-dots">
          <span></span><span></span><span></span>
        </div>
        <h2>薪资范围分布的职位数量</h2>
        <div class="tech-dots">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>

    <div class="holo-content">
      <div class="tech-border">
        <div class="border-line top"></div>
        <div class="border-line right"></div>
        <div class="border-line bottom"></div>
        <div class="border-line left"></div>
        <div class="border-corner tl"></div>
        <div class="border-corner tr"></div>
        <div class="border-corner bl"></div>
        <div class="border-corner br"></div>
      </div>
      <!-- 添加薪资范围分布图表 -->
      <div id="salaryCounts" ref="salaryCountsChart" style="width: 100%; height: 380px;"></div>
    </div>
    
    <div class="scan-line"></div>
    <div class="holo-overlay"></div>
  </div>

  <!-- 控制面板按钮 -->
  <div class="control-panels" v-show="app && app.currentScene === 'childScene'">
    <div class="control-panel-btn" 
         :class="{ active: panelVisibility.panel1 }" 
         @click="togglePanel('panel1')" 
         title="职位数量动态">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
      </svg>
    </div>
    <div class="control-panel-btn" 
         :class="{ active: panelVisibility.panel2 }" 
         @click="togglePanel('panel2')" 
         title="人才补贴政策">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
        <circle cx="9" cy="7" r="4"></circle>
        <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
        <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
      </svg>
    </div>
    <div class="control-panel-btn" 
         :class="{ active: panelVisibility.panel3 }" 
         @click="togglePanel('panel3')" 
         title="薪资范围分布的职位数量">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
        <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
      </svg>
    </div>
  </div>

    <!-- 左中角信息面板 - 创业补贴 -->
    <div class="hologram-panel left-middle" 
         v-show="app && app.currentScene === 'childScene'"
         :class="{ 'panel-enter': app && app.currentScene === 'childScene' }"
         @mouseenter="isHoveringLeftMiddle = true"
         @mouseleave="isHoveringLeftMiddle = false">
      <div class="holo-frame">
        <div class="frame-line top"></div>
        <div class="frame-line right"></div>
        <div class="frame-line bottom"></div>
        <div class="frame-line left"></div>
        <div class="corner-box tl"></div>
        <div class="corner-box tr"></div>
        <div class="corner-box bl"></div>
        <div class="corner-box br"></div>
      </div>
      
      <div class="holo-header">
        <div class="header-grid"></div>
        <div class="header-content">
          <div class="tech-dots">
            <span></span><span></span><span></span>
          </div>
          <h2>创业补贴</h2>
          <div class="tech-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <div class="holo-content" ref="leftMiddlePanelContent">
        <div v-if="currentEntrepreneurPolicy && currentEntrepreneurPolicy.length">
          <div class="holo-section" @click="showSourceLink(currentEntrepreneurPolicy[currentEntrepreneurPolicy.length-1])">
            <div v-for="(policy, index) in currentEntrepreneurPolicy" 
                 :key="'entrepreneur-' + index" 
                 class="holo-item">
              <div class="item-header">
                <span class="tech-icon"></span>
                {{ policy.title }}
              </div>
              <div class="item-body">{{ policy.content }}</div>
            </div>
          </div>
        </div>
        <div v-else class="no-data">
          <div class="tech-icon"></div>
          <span>该地区创业补贴政策信息正在完善中...</span>
        </div>
      </div>
      
      <div class="scan-line"></div>
      <div class="holo-overlay"></div>
    </div>

    <!-- 新增: 红框区域1 - 左上角模块框 -->
    <div class="hologram-panel region-box region-box-1" 
        v-show="app && app.currentScene === 'childScene' && panelVisibility.panel1"
        :class="{ 'panel-enter': app && app.currentScene === 'childScene' }">
      <div class="holo-frame">
        <div class="frame-line top"></div>
        <div class="frame-line right"></div>
        <div class="frame-line bottom"></div>
        <div class="frame-line left"></div>
        <div class="corner-box tl"></div>
        <div class="corner-box tr"></div>
        <div class="corner-box bl"></div>
        <div class="corner-box br"></div>
      </div>
      
      <div class="holo-header">
        <div class="header-grid"></div>
        <div class="header-content">
          <div class="tech-dots">
            <span></span><span></span><span></span>
          </div>
          <h2>{{ currentArea.name }}职位数量动态</h2>
          <div class="tech-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <div class="holo-content" style="height: 400px;">
        <div class="tech-border">
          <div class="border-line top"></div>
          <div class="border-line right"></div>
          <div class="border-line bottom"></div>
          <div class="border-line left"></div>
          <div class="border-corner tl"></div>
          <div class="border-corner tr"></div>
          <div class="border-corner bl"></div>
          <div class="border-corner br"></div>
        </div>
        <!-- 添加echarts图表 -->
        <div id="jobTimelineChart" ref="jobTimelineChart" style="width: 100%; height: 380px;"></div>
      </div>
      
      <div class="scan-line"></div>
      <div class="holo-overlay"></div>
    </div>

    <!-- 新增: 红框区域2 - 右上角模块框 -->
    <div class="hologram-panel region-box region-box-2" 
        v-show="app && app.currentScene === 'childScene' && panelVisibility.panel2"
        :class="{ 'panel-enter': app && app.currentScene === 'childScene' }">
      <div class="holo-frame">
        <div class="frame-line top"></div>
        <div class="frame-line right"></div>
        <div class="frame-line bottom"></div>
        <div class="frame-line left"></div>
        <div class="corner-box tl"></div>
        <div class="corner-box tr"></div>
        <div class="corner-box bl"></div>
        <div class="corner-box br"></div>
      </div>
      
      <div class="holo-header">
        <div class="header-grid"></div>
        <div class="header-content">
          <div class="tech-dots">
            <span></span><span></span><span></span>
          </div>
          <h2>薪资与经验关系</h2>
          <div class="tech-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <div class="holo-content">
        <div class="tech-border">
          <div class="border-line top"></div>
          <div class="border-line right"></div>
          <div class="border-line bottom"></div>
          <div class="border-line left"></div>
          <div class="border-corner tl"></div>
          <div class="border-corner tr"></div>
          <div class="border-corner bl"></div>
          <div class="border-corner br"></div>
        </div>
        <!-- 添加薪资与工作年限散点图 -->
        <div id="salaryExperienceChart" ref="salaryExperienceChart" style="width: 100%; height: 380px;"></div>
      </div>
      
      <div class="scan-line"></div>
      <div class="holo-overlay"></div>
    </div>

    <!-- 新增: 红框区域3 - 左下角模块框 -->
    <div class="hologram-panel region-box region-box-3" 
        v-show="app && app.currentScene === 'childScene' && panelVisibility.panel3"
        :class="{ 'panel-enter': app && app.currentScene === 'childScene' }">
      <div class="holo-frame">
        <div class="frame-line top"></div>
        <div class="frame-line right"></div>
        <div class="frame-line bottom"></div>
        <div class="frame-line left"></div>
        <div class="corner-box tl"></div>
        <div class="corner-box tr"></div>
        <div class="corner-box bl"></div>
        <div class="corner-box br"></div>
      </div>
      
      <div class="holo-header">
        <div class="header-grid"></div>
        <div class="header-content">
          <div class="tech-dots">
            <span></span><span></span><span></span>
          </div>
          <h2>{{ salaryCountsTitle }}</h2>
          <div class="tech-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <div class="holo-content">
        <div class="tech-border">
          <div class="border-line top"></div>
          <div class="border-line right"></div>
          <div class="border-line bottom"></div>
          <div class="border-line left"></div>
          <div class="border-corner tl"></div>
          <div class="border-corner tr"></div>
          <div class="border-corner bl"></div>
          <div class="border-corner br"></div>
        </div>
        <!-- 添加薪资范围分布图表 -->
        <div id="salaryCounts" ref="salaryCountsChart" style="width: 100%; height: 380px;"></div>
      </div>
      
      <div class="scan-line"></div>
      <div class="holo-overlay"></div>
    </div>
    
    <!-- 添加右侧控制面板按钮 -->
    <div class="control-panels" v-show="app && app.currentScene === 'childScene'">
      <div class="control-panel-btn" 
          :class="{ active: panelVisibility.panel1 }" 
          @click="togglePanel('panel1')" 
          title="职位数量动态">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
        </svg>
      </div>
      <div class="control-panel-btn" 
          :class="{ active: panelVisibility.panel2 }" 
          @click="togglePanel('panel2')" 
          title="薪资与经验关系">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
          <circle cx="9" cy="7" r="4"></circle>
          <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
          <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
        </svg>
      </div>
      <div class="control-panel-btn" 
          :class="{ active: panelVisibility.panel3 }" 
          @click="togglePanel('panel3')" 
          title="薪资范围分布的职位数量">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
          <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
        </svg>
      </div>
    </div>
    <!-- 修改搜索框组件 -->
    <div class="search-container" v-show="is3DMap">
      <div class="search-box">
        <div class="input-wrapper">
          <input 
            type="text" 
            v-model="searchKeyword" 
            @keyup.enter="handleSearch"
            placeholder="请输入公司名称..."
            ref="searchInput"
          >
          <span class="clear-btn" v-if="searchKeyword" @click="clearSearch">×</span>
          <button class="search-btn" @click="handleSearch">
            <i class="search-icon">🔍</i>
          </button>
        </div>
      </div>
      <!-- 搜索结果列表 -->
      <div class="search-results" v-if="searchResults.length > 0">
        <div 
          v-for="(item, index) in searchResults" 
          :key="index" 
          class="result-item"
          :class="{ active: index === activeIndex }"
          @click="locateCompany(item)"
          @mouseover="activeIndex = index"
        >
          <div class="company-name">{{ item.name }}</div>
          <div class="company-address">{{ item.C13 || '暂无描述' }}</div>
        </div>
      </div>
    </div>

    <!-- 添加路线规划按钮 -->
    <div class="route-planning-btn" @click="showRoutePlanning" v-show="false">
      <el-icon><Location /></el-icon>
      <span>路线规划</span>
    </div>
    <!-- 路线规划对话框组件 -->
    <route-dialog ref="routeDialogRef" />
  </div>

  <!-- 添加职业测试弹窗 -->
  <div class="career-test-modal" v-if="showCareerTestModal">
    <div class="modal-content">
      <div class="modal-header">
        <span>{{ currentTest ? getTestName(currentTest) : '职业测试中心' }}</span>
        <div class="header-buttons">
          <button v-if="currentTest" class="back-btn" @click="currentTest = null">返回</button>
          <button class="close-btn" @click="showCareerTestModal = false">&times;</button>
        </div>
      </div>
      <div class="modal-body">
        <!-- 测试选项列表 -->
        <transition name="fade">
          <div v-if="!currentTest">
            <div class="test-options">
              <div class="test-item" @click="startTest('valueTest')">
                <h3>职业价值观测评</h3>
                <p>了解您的职业价值取向和追求</p>
              </div>
              <div class="test-item" @click="startTest('careerAnchor')">
                <h3>职业锚测评</h3>
                <p>发现您的职业发展定位</p>
              </div>
              <div class="test-item" @click="startTest('bigFive')">
                <h3>大五人格测验</h3>
                <p>评估您的性格特征</p>
              </div>
              <div class="test-item" @click="startTest('holland')">
                <h3>霍兰德职业兴趣测评</h3>
                <p>探索您的职业兴趣类型</p>
              </div>
              <div class="test-item" @click="startTest('strong')">
                <h3>斯特朗职业兴趣量表</h3>
                <p>深入分析您的职业兴趣</p>
              </div>
              <div class="test-item" @click="startTest('mbti')">
                <h3>MBTI性格类型测试</h3>
                <p>了解您的性格类型</p>
              </div>
            </div>
          </div>
        </transition>
        
        <!-- 测试内容 -->
        <transition name="slide-fade">
          <div class="test-content" v-if="currentTest">
            <iframe 
              :src="getTestUrl(currentTest)"
              frameborder="0"
              allowfullscreen
            ></iframe>
          </div>
        </transition>
      </div>
    </div>
  </div>

  <!-- 添加源链接弹窗 -->
  <el-dialog
    v-model="sourceLinkDialogVisible"
    title="政策来源"
    width="80%" 
    class="source-link-dialog"
  >
    <div v-if="currentSourceLink" class="source-link-content">
      <iframe 
        :src="currentSourceLink"
        frameborder="0"
        width="100%"
        height="600px"  
        style="border: none;"
      ></iframe>
    </div>
    <div v-else>
      暂无来源链接
    </div>
  </el-dialog>


</template>

<script setup>
import { onMounted, reactive, onBeforeUnmount, ref, watch, nextTick, computed, onUnmounted } from "vue"
import { World } from "./map"
import * as echarts from 'echarts';
import axios from 'axios';
// 引入词云图扩展
import 'echarts-wordcloud';
import provincePoliciesData from '@/assets/data/provincePolicies.js';
import { provinceSubsidiesData } from '@/assets/data/province_rcbt_data.js';
import { entrepreneurPolicy } from '@/assets/data/province_cyzc_data.js';
// 添加Live2D相关导入
import * as PIXI from "pixi.js";
// @ts-ignore
import { Live2DModel } from "pixi-live2d-display/cubism4";
// 添加语音播报相关导入
import Speech from 'speak-tts';
import miniMaxTTS from '@/services/miniMaxTTS';
import JobRecommendation from '@/components/JobRecommendation.vue'
import JobAlert from '@/components/JobAlert.vue'
import { Location, Bell } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PolicyMatcher from '@/components/PolicyMatcher.vue'
import RouteDialog from '@/components/RouteDialog.vue'

// 声明全局PIXI
window.PIXI = PIXI;

let app = null;
let pieChart = null;
let calendarChart = null;
let wordCloudChart = null;

// 添加Live2D相关变量
let pixiApp = null;
let model = null;
const liveCanvas = ref(null);
const isLive2DInitialized = ref(false);
const animationFrameId = ref(null);

// 添加折线图初始化标志，确保只初始化一次
let jobTimelineInitialized = false;

// 添加立即初始化默认折线图的函数
const initDefaultJobTimeline = () => {
  if (!jobTimelineChart.value) {
    console.warn('职位时间线图表容器不存在，无法初始化默认图表');
    return;
  }
  
  console.log('初始化默认职位时间线图表');
  
  // 确保容器尺寸正确
  const container = jobTimelineChart.value;
  container.style.width = '100%';
  container.style.height = '380px';
  
  // 使用延迟初始化
  setTimeout(() => {
    try {
      // 销毁旧的实例
      if (jobChartInstance) {
        jobChartInstance.dispose();
      }
      
      // 创建新实例
      jobChartInstance = echarts.init(container);
      
      // 使用简单的默认数据
      const defaultData = {
        months: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月'],
        counts: [500, 600, 800, 1200, 900, 700, 1000, 1100]
      };
      
      const option = {
        backgroundColor: 'transparent',
        grid: {
          left: '5%',
          right: '5%',
          top: '10%',
          bottom: '15%',
          containLabel: true
        },
        tooltip: {
          trigger: 'axis',
          formatter: '{b}: {c} 个职位'
        },
        xAxis: {
          type: 'category',
          data: defaultData.months,
          axisLine: {
            lineStyle: {
              color: '#fff'
            }
          },
          axisLabel: {
            color: '#fff',
            fontSize: 12
          }
        },
        yAxis: {
          type: 'value',
          name: '职位数量',
          nameTextStyle: {
            color: '#fff'
          },
          axisLine: {
            lineStyle: {
              color: '#fff'
            }
          },
          splitLine: {
            show: false
          },
          axisLabel: {
            color: '#fff',
            fontSize: 12
          }
        },
        series: [{
          name: '职位数量',
          type: 'line',
          data: defaultData.counts,
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          lineStyle: {
            width: 3,
            color: '#00c6ff'
          },
          itemStyle: {
            color: '#00c6ff'
          }
        }]
      };
      
      // 设置选项
      jobChartInstance.setOption(option);
      jobTimelineInitialized = true;
      console.log('默认职位时间线图表绘制完成');
      
      // 强制刷新
      setTimeout(() => {
        if (jobChartInstance) {
          jobChartInstance.resize();
        }
      }, 200);
    } catch (error) {
      console.error('绘制默认职位时间线图表失败:', error);
    }
  }, 500);
};

// 添加响应式数据 - 移动到这里，确保在使用前定义
const currentArea = ref({
  name: '',
  jobCount: 0,
  avgSalary: 0,
  maxSalary: 0,
  hotJobs: [
    { name: 'Java开发工程师', count: 2500 },
    { name: '前端开发工程师', count: 2000 },
    { name: '算法工程师', count: 1800 },
    { name: '产品经理', count: 1500 },
    { name: '运维工程师', count: 1200 }
  ],
  policyContent: '上海引进人才落户政策旨在吸引各类优秀人才...'
});

// 当前省份的政策信息
const currentPolicy = ref(null);
// 当前省份的补贴政策信息
const currentSubsidy = ref(null);
// 添加创业政策相关的响应式变量
const currentEntrepreneurPolicy = ref(null);

// 在 script setup 中添加
const sourceLinkDialogVisible = ref(false);
const currentSourceLink = ref('');

// 政策匹配器显示状态
const showPolicyMatcherModal = ref(false)
// 打开政策匹配器
const openPolicyMatcher = () => {
  showPolicyMatcherModal.value = true;
};

// 关闭政策匹配器
const closePolicyMatcher12 = () => {
  showPolicyMatcherModal.value = false;
};
// 从职业测试跳转到政策匹配器
const openPolicyMatcherFromTest12 = () => {
  showCareerTestModal.value = false;
  showPolicyMatcherModal.value = true;
};
// 图表显示状态控制
const chartVisible = reactive({
  pie: false,
  wordCloud: false,
  calendar: false
});

// 在script部分添加面板可见性控制
const panelVisibility = reactive({
  panel1: true,
  panel2: true,
  panel3: true
});

// 切换面板显示状态
const togglePanel = (panelName) => {
  panelVisibility[panelName] = !panelVisibility[panelName];
};

// 添加职位数量动态时间线图表相关代码
const jobTimelineChart = ref(null);
let jobChartInstance = null;
// 添加薪资范围与工作年限散点图相关代码
const salaryExperienceChart = ref(null);
let salaryChartInstance = null;
// 添加薪资范围分布图表相关代码
const salaryCountsChart = ref(null);
let salaryCountsChartInstance = null; // 添加薪资范围分布图表实例变量
const salaryCountsTitle = ref('薪资范围分布的职位数量');
let salaryCountsInitialized = false; // 添加初始化标记

// 添加省份名称规范化函数
const normalizeProvinceName = (name) => {
  if (!name) return '';
  
  // 省份规范化映射表
  const provinceMap = {
    '新疆维吾尔自治区': '新疆',
    '广西壮族自治区': '广西',
    '宁夏回族自治区': '宁夏',
    '西藏自治区': '西藏',
    '内蒙古自治区': '内蒙古'
  };
  
  // 先检查是否在映射表中
  if (provinceMap[name]) {
    console.log(`使用映射表转换省份名称: "${name}" → "${provinceMap[name]}"`);
    return provinceMap[name];
  }
  
  // 否则应用规则处理
  if (name.endsWith('省')) {
    return name.substring(0, name.length - 1);
  } else if (name.endsWith('市')) {
    return name.substring(0, name.length - 1);
  } else if (name.endsWith('特别行政区')) {
    return name.split('特别行政区')[0];
  } else if (name.includes('自治区')) {
    // 提取自治区名称的前缀部分
    const prefix = name.split('自治区')[0];
    // 提取民族前缀部分
    return prefix.split('族')[0].split('维吾尔')[0].split('壮')[0].split('回')[0].split('藏')[0];
  }
  
  return name;
};

// 修复薪资范围分布图表问题的函数
window.fixSalaryCountsChart = function() {
  // 定义全局变量
  window.salaryCountsChartInstance = null;
  
  // 重定义测试函数
  window.testSalaryCountsChart = function(provinceName) {
    console.log('测试加载' + provinceName + '的薪资范围分布数据');
    
    // 获取图表容器
    const container = document.getElementById('salaryCounts');
    if (!container) {
      console.error('未找到图表容器');
      return;
    }
    
    // 默认数据
    const defaultData = {
      salaryRanges: ['0-5K', '5K-10K', '10K-15K', '15K-20K', '20K-30K', '30K+'],
      counts: [120, 350, 280, 150, 80, 40]
    };
    
    // 销毁旧实例
    if (window.salaryCountsChartInstance) {
      window.salaryCountsChartInstance.dispose();
    }
    
    // 创建新实例
    window.salaryCountsChartInstance = echarts.init(container);
    
    // 配置
    const option = {
      backgroundColor: 'transparent',
      grid: { left: '5%', right: '5%', top: '10%', bottom: '15%', containLabel: true },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: defaultData.salaryRanges },
      yAxis: { type: 'value', name: '职位数量' },
      series: [{
        type: 'bar',
        data: defaultData.counts,
        itemStyle: { color: 'rgba(51, 204, 255, 0.8)' }
      }]
    };
    
    // 设置选项
    window.salaryCountsChartInstance.setOption(option);
    console.log('薪资范围分布图表绘制完成');
    
    // 显示面板
    if (typeof panelVisibility !== 'undefined') {
      panelVisibility.panel3 = true;
    }
  };
  
  console.log('修复完成，请执行 window.testSalaryCountsChart("上海") 测试');
};

// 自动执行修复
window.fixSalaryCountsChart();

// 修改loadJobTimelineData函数的实现
const loadJobTimelineData = async (provinceName) => {
  try {
    console.log(`★★★ 开始加载${provinceName}的职位动态数据 ★★★`);
    
    // 确认省份名称和格式
    if (!provinceName) {
      console.warn('⚠️ 未提供省份名称，使用默认值');
      provinceName = '湖南'; // 默认值
    } else {
      // 输出确切的省份名称，以便检查格式和空格
      console.log(`省份名称: "${provinceName}" (长度: ${provinceName.length})`);
    }
    
    // 确保DOM已经完全渲染
    await nextTick();
    
    // 等待一小段时间确保容器尺寸已经计算完成
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // 使用默认数据
    const defaultData = {
      months: ['1月', '2月', '3月', '4月', '5月', '6月'],
      counts: [500, 600, 800, 1200, 900, 700]
    };
    
    // 确保容器存在且有尺寸
    if (!jobTimelineChart.value) {
      console.error('❌ 职位时间线图表容器未找到');
      return;
    }

    // 强制设置容器尺寸
    const container = jobTimelineChart.value;
    container.style.width = '100%';
    container.style.height = '380px';
    
    try {
      // 使用规范化函数获取标准省份名称
      const fileProvinceName = normalizeProvinceName(provinceName);
      if (fileProvinceName !== provinceName) {
        console.log(`省份名称规范化: "${provinceName}" → "${fileProvinceName}"`);
      }
      
      // 构建准确的CSV文件路径
      const csvPath = `/职业动态时间图/${fileProvinceName}_monthly_stats.csv`;
      console.log(`🔍 尝试加载CSV文件: "${csvPath}"`);
      
      // 使用fetch替代axios，更直接
      const response = await fetch(csvPath);
      console.log(`📊 文件请求状态: ${response.status} ${response.statusText}`);
      
      if (response.ok) {
        const csvText = await response.text();
        console.log('CSV文件内容预览:', csvText.substring(0, 100) + '...');
        
        // 解析CSV数据
        const rows = csvText.trim().split('\n');
        const headers = rows[0].split(',');
        const monthIndex = headers.findIndex(h => h.trim() === '月份');
        const countIndex = headers.findIndex(h => h.trim() === '职位数量');
        
        if (monthIndex === -1 || countIndex === -1) {
          console.warn(`CSV格式不匹配，使用默认数据`);
          drawJobTimelineChart(defaultData.months, defaultData.counts);
          return;
        }
        
        const data = {
          months: [],
          counts: []
        };
        
        // 解析数据行
        for (let i = 1; i < rows.length; i++) {
          const cols = rows[i].split(',');
          if (cols.length > Math.max(monthIndex, countIndex)) {
            const month = cols[monthIndex].trim();
            const count = parseInt(cols[countIndex].trim());
            
            if (month && !isNaN(count)) {
              data.months.push(month);
              data.counts.push(count);
            }
          }
        }
        
        if (data.months.length > 0) {
          console.log(`成功解析${provinceName}的职位动态数据:`, data);
          drawJobTimelineChart(data.months, data.counts);
        } else {
          console.warn(`${provinceName}数据为空，使用默认数据`);
          drawJobTimelineChart(defaultData.months, defaultData.counts);
        }
      } else {
        console.warn(`加载${provinceName}的CSV文件失败，状态码:`, response.status);
        
        // 尝试其他可能的文件名格式 (原始名称)
        console.log(`尝试使用原始省份名称加载: "${provinceName}"`);
        const alternativePath = `/职业动态时间图/${provinceName}_monthly_stats.csv`;
        let csvData = await tryLoadCSVFile(alternativePath, provinceName);
        
        if (csvData) {
          // 如果成功加载，绘制图表
          console.log(`成功加载并解析${provinceName}的职位动态数据(使用原始名称):`, csvData);
          drawJobTimelineChart(csvData.months, csvData.counts);
          return;
        }
          
        // 尝试第三种可能的文件名格式 - 使用前两个字符
        if (provinceName.length > 2) {
          const shortName = provinceName.substring(0, 2);
          console.log(`尝试使用简化名称加载: "${shortName}"`);
          const shortPath = `/职业动态时间图/${shortName}_monthly_stats.csv`;
          
          csvData = await tryLoadCSVFile(shortPath, provinceName);
          
          if (csvData) {
            // 如果成功加载，绘制图表
            console.log(`成功加载并解析${provinceName}的职位动态数据(使用简化名称):`, csvData);
            drawJobTimelineChart(csvData.months, csvData.counts);
            return;
          } else {
            // 所有文件加载尝试都失败，输出有用的调试信息
            console.warn(`三种路径加载尝试全部失败，使用默认数据`);
            console.warn(`期望的CSV文件格式有以下几种可能:`);
            console.warn(`1. /职业动态时间图/${fileProvinceName}_monthly_stats.csv`);
            console.warn(`2. /职业动态时间图/${provinceName}_monthly_stats.csv`);
            console.warn(`3. /职业动态时间图/${shortName}_monthly_stats.csv`);
          }
        }
        
        // 如果所有尝试都失败，使用默认数据
        drawJobTimelineChart(defaultData.months, defaultData.counts);
      }
    } catch (error) {
      console.warn(`加载${provinceName}的职位动态数据失败:`, error);
      // 使用默认数据作为后备方案
      drawJobTimelineChart(defaultData.months, defaultData.counts);
    }
  } catch (error) {
    console.error('初始化职位时间线图表失败:', error);
  }
};

// 辅助函数：尝试加载CSV文件并解析
const tryLoadCSVFile = async (filePath, provinceName) => {
  try {
    const response = await fetch(filePath);
    
    if (response.ok) {
      console.log(`成功加载CSV文件: "${filePath}"`);
      const csvText = await response.text();
      
      // 解析CSV数据
      const rows = csvText.trim().split('\n');
      const headers = rows[0].split(',');
      const monthIndex = headers.findIndex(h => h.trim() === '月份');
      const countIndex = headers.findIndex(h => h.trim() === '职位数量');
      
      if (monthIndex === -1 || countIndex === -1) {
        console.warn(`CSV格式不匹配: ${filePath}`);
        return null;
      }
      
      const data = {
        months: [],
        counts: []
      };
      
      // 解析数据行
      for (let i = 1; i < rows.length; i++) {
        const cols = rows[i].split(',');
        if (cols.length > Math.max(monthIndex, countIndex)) {
          const month = cols[monthIndex].trim();
          const count = parseInt(cols[countIndex].trim());
          
          if (month && !isNaN(count)) {
            data.months.push(month);
            data.counts.push(count);
          }
        }
      }
      
      if (data.months.length > 0) {
        return data;
      }
    }
    
    return null;
  } catch (error) {
    console.warn(`尝试加载 ${filePath} 时出错:`, error);
    return null;
  }
};

// 优化drawJobTimelineChart函数
const drawJobTimelineChart = (months, counts) => {
  if (!jobTimelineChart.value) {
    console.error('职位时间线图表容器未找到');
    return;
  }
  
  // 确保容器尺寸正确
  const container = jobTimelineChart.value;
  if (container.clientWidth === 0 || container.clientHeight === 0) {
    console.warn('图表容器尺寸为零，强制设置尺寸');
    container.style.width = '100%';
    container.style.height = '380px';
  }
  
  console.log('图表容器尺寸:', {
    width: container.clientWidth,
    height: container.clientHeight,
    offsetWidth: container.offsetWidth,
    offsetHeight: container.offsetHeight
  });
  
  // 销毁旧的实例
  if (jobChartInstance) {
    jobChartInstance.dispose();
  }
  
  // 使用setTimeout延迟创建实例，确保DOM已经完全渲染
  setTimeout(() => {
    try {
      // 创建新的实例
      jobChartInstance = echarts.init(container);
      
      const option = {
        backgroundColor: 'transparent',
        grid: {
          left: '5%',
          right: '5%',
          top: '10%',
          bottom: '10%',
          containLabel: true
        },
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(6, 23, 46, 0.8)',
          borderColor: 'rgba(0, 198, 255, 0.3)',
          textStyle: {
            color: '#fff'
          },
          formatter: '{b}: {c} 个职位'
        },
        xAxis: {
          type: 'category',
          data: months,
          axisLine: {
            lineStyle: {
              color: 'rgba(0, 198, 255, 0.5)'
            }
          },
          axisLabel: {
            color: 'rgba(255, 255, 255, 0.7)',
            rotate: 45
          }
        },
        yAxis: {
          type: 'value',
          name: '职位数量',
          nameTextStyle: {
            color: 'rgba(255, 255, 255, 0.7)'
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(0, 198, 255, 0.5)'
            }
          },
          splitLine: {
            lineStyle: {
              color: 'rgba(0, 198, 255, 0.15)'
            }
          },
          axisLabel: {
            color: 'rgba(255, 255, 255, 0.7)'
          }
        },
        series: [{
          name: '职位数量',
          type: 'line',
          data: counts,
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          itemStyle: {
            color: '#00c6ff'
          },
          lineStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [{
                offset: 0,
                color: 'rgba(0, 255, 255, 1)'
              }, {
                offset: 1,
                color: 'rgba(51, 102, 255, 1)'
              }]
            },
            width: 3
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [{
                offset: 0,
                color: 'rgba(0, 255, 255, 0.4)'
              }, {
                offset: 1,
                color: 'rgba(51, 102, 255, 0.1)'
              }]
            }
          }
        }]
      };
      
      // 设置图表选项
      jobChartInstance.setOption(option);
      console.log('职位时间线图表绘制完成');
      
      // 创建ResizeObserver监听容器尺寸变化
      const resizeObserver = new ResizeObserver(() => {
        if (jobChartInstance) {
          console.log('容器尺寸变化，重新调整图表大小');
          jobChartInstance.resize();
        }
      });
      resizeObserver.observe(container);
      
      // 另外再添加窗口大小变化的监听
      window.addEventListener('resize', () => {
        if (jobChartInstance) {
          jobChartInstance.resize();
        }
      });
      
      // 标记为已初始化
      jobTimelineInitialized = true;
      
      // 强制触发一次resize，解决一些渲染问题
      setTimeout(() => {
        if (jobChartInstance) {
          jobChartInstance.resize();
        }
      }, 200);
    } catch (error) {
      console.error('创建图表实例失败:', error);
    }
  }, 300); // 使用300ms延迟确保DOM已渲染
};

// 在组件卸载时清理图表实例
onBeforeUnmount(() => {
  if (jobChartInstance) {
    jobChartInstance.dispose();
    jobChartInstance = null;
  }
});

// 窗口大小变化时调整图表大小
const resizeJobChart = () => {
  if (jobChartInstance) {
    jobChartInstance.resize();
  }
};

window.addEventListener('resize', resizeJobChart);
onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeJobChart);
});

// 添加监听currentArea.name变化的逻辑 - 移动到这里确保currentArea已定义
watch(() => currentArea.name, (newName) => {
  if (newName && app && app.currentScene === 'childScene') {
    console.log(`当前区域变更为: ${newName}，准备加载时间线数据`);
    // 使用省市名称加载数据
    nextTick(() => {
      loadJobTimelineData(newName);
      
      // 添加额外的延迟加载尝试，确保图表可以显示
      setTimeout(() => {
        if (!jobTimelineInitialized && jobTimelineChart.value) {
          console.log('再次尝试加载图表...');
          loadJobTimelineData(newName);
        }
      }, 1500);
    });
  }
}, { immediate: true });

// 添加监听进入子地图的逻辑
watch(() => app?.currentScene, (newScene, oldScene) => {
  console.log(`场景变更: ${oldScene} -> ${newScene}`);
  if (newScene === 'childScene' && currentArea.name) {
    console.log(`进入子场景，当前区域: ${currentArea.name}`);
    // 确保面板可见
    panelVisibility.panel1 = true;
    panelVisibility.panel3 = true; // 确保薪资范围面板可见
    
    // 使用setTimeout延迟加载，确保DOM已渲染
    setTimeout(() => {
      loadJobTimelineData(currentArea.name);
      loadSalaryCountsData(currentArea.name); // 加载薪资范围分布数据
      
      // 添加额外的延迟加载尝试，确保图表可以显示
      setTimeout(() => {
        if (!jobTimelineInitialized && jobTimelineChart.value) {
          console.log('子场景变更后再次尝试加载图表...');
          loadJobTimelineData(currentArea.name);
        }
        
        // 额外尝试加载薪资范围分布图表
        if (!salaryCountsInitialized && salaryCountsChart.value) {
          console.log('子场景变更后再次尝试加载薪资范围分布图表...');
          loadSalaryCountsData(currentArea.name);
        }
      }, 2000);
    }, 500);
  }
});


const showSourceLink = (data) => {
  // 根据不同数据结构获取 src
  let sourceLink = '';
  if (Array.isArray(data)) {
    // 创业补贴数据结构
    const srcObj = data.find(item => item.src);
    sourceLink = srcObj ? srcObj.src : '';
  } else {
    // 落户政策和人才补贴数据结构
    sourceLink = data.src || '';
  }
  
  if (sourceLink) {
    currentSourceLink.value = sourceLink;
    sourceLinkDialogVisible.value = true;
  } else {
    ElMessage.info('暂无来源链接');
  }
};

// 地图状态控制
const state = reactive({
  bar: true,
  flyLine: false,
  scatter: false,
  card: false,
  particle: false,
  mirror: false,
  path: false,
});

// 添加聊天相关的响应式变量
const chatMessages = ref(null);
const chatHistory = ref([]);
const userInput = ref('');
const chatInput = ref(null);

// 添加城市到模型编号的映射
const cityModelMap = {
  '上海': 'llm3-dot-2',
  '深圳': 'new-workspace',
  '北京': '8cb18b35-5d38-4baa-bb98-05cb6eec3dc9',
  '广州': 'new-workspace'
};

// 添加城市地理数据映射
const cityGeoData = {
  '上海': {
    name: "上海市",
    center: [121.472644, 31.231706],
    centroid: [121.438737, 31.072559],
    adcode: 310000,
    childrenNum: 16
  },
  '北京': {
    name: "北京市",
    center: [116.405285, 39.904989],
    centroid: [116.419889, 40.189911],
    adcode: 110000,
    childrenNum: 16
  },
  '广州': {
    name: "广州市",
    center: [113.280637, 23.125178],
    centroid: [113.264434, 23.129162],
    adcode: 440100,
    childrenNum: 11
  },
  '深圳': {
    name: "深圳市",
    center: [114.085947, 22.547],
    centroid: [114.057868, 22.543099],
    adcode: 440300,
    childrenNum: 10
  }
};

// 获取当前城市的模型工作空间
const getModelWorkspace = (message) => {
  for (const city in cityModelMap) {
    if (message.includes(city)) {
      return cityModelMap[city];
    }
  }
  return 'llm3-dot-2'; // 默认模型
};

// 获取城市名称
const getCityFromMessage = (message) => {
  for (const city in cityGeoData) {
    if (message.includes(city)) {
      return city;
    }
  }
  return null;
};

const setEffectToggle = (type) => {
  // 如果是子场景且是这些按钮，则不执行任何操作
  if (["bar", "flyLine", "scatter", "card", "path"].includes(type) && app && app.currentScene === "childScene") {
    return false;
  }
  // 设置按钮状态
  state[type] = !state[type];

  if (type === "bar") {
    app.barGroup.visible = state[type];
    app.setLabelVisible("labelGroup", state[type]);
  }
  if (type === "particle") {
    app.particles.enable = state[type];
    app.particles.instance.visible = state[type];
  }
  if (type === "flyLine") {
    app.flyLineGroup.visible = state[type];
    app.flyLineFocusGroup.visible = state[type];
  }
  if (type === "scatter") {
    app.scatterGroup.visible = state[type];
  }
  if (type === "card") {
    app.setLabelVisible("badgeGroup", state[type]);
  }
  if (type === "mirror") {
    app.groundMirror.visible = state[type];
  }
  if (type === "path") {
    app.pathLineGroup.visible = state[type];
  }
};

// 修改 setEnable 函数
const setEnable = (bool) => {
  state.bar = bool;
  state.flyLine = bool;
  state.scatter = bool;
  state.card = bool;
  state.path = bool;

  // 当进入子场景时（bool为false），隐藏所有图表
  if (!bool) {
    chartVisible.pie = false;
    chartVisible.wordCloud = false;
    chartVisible.calendar = false;
  } else {
    // 返回主场景时，显示所有图表
    chartVisible.pie = true;
    chartVisible.wordCloud = true;
    chartVisible.calendar = true;
    // 重新渲染所有图表
    setTimeout(() => {
      drawPieChart();
      drawWordCloudChart();
      drawCalendarChart();
    }, 0);
  }
};

// 修改 goBack 函数
const goBack = () => {
  if (!app) return;
  
  app.goBack();
  
  // 只有当返回到主场景时才显示图表
  if (app.currentScene === 'mainScene') {
    chartVisible.pie = true;
    chartVisible.wordCloud = true;
    chartVisible.calendar = true;
    // 重新渲染所有图表
    setTimeout(() => {
      drawPieChart();
      drawWordCloudChart();
      drawCalendarChart();
    }, 0);
  }
};

// 定义表情列表
const expressions = [
  'xin xin',
  'xing xing',
  'tuan shan',
  'lian hong',
  'shuang ma wei',
  'kan jian',
  'hou fa',
  'hua hua',
  'bai yan',
  'hei lian',
  'hong yan'
];

// 定义动作状态
const motionStates = {
  IDLE: 'Idle',
  TALKING: 'Talking',
  THINKING: 'Thinking',
  HAPPY: 'Happy',
  SURPRISED: 'Surprised',
  WAVE: 'Wave',      // 挥手
  NOD: 'Nod',        // 点头
  SHAKE: 'Shake',    // 摇头
  DANCE: 'Dance'     // 舞蹈
};

// 修改可点击切换的动作列表，调整参数使动作更明显
const clickableMotions = [
  { 
    state: motionStates.WAVE, 
    params: { 
      'ParamAngleX': 15, 
      'ParamAngleY': 15, 
      'ParamAngleZ': 10,
      'ParamBodyAngleX': 10,
      'ParamBodyAngleY': 10,
      'ParamBodyAngleZ': 5,
      'ParamArmLA': -30,
      'ParamArmRA': 30
    }
  },
  { 
    state: motionStates.NOD, 
    params: { 
      'ParamAngleX': 0, 
      'ParamAngleY': 30, 
      'ParamAngleZ': 0,
      'ParamBodyAngleX': 0,
      'ParamBodyAngleY': 10,
      'ParamBodyAngleZ': 0
    }
  },
  { 
    state: motionStates.SHAKE, 
    params: { 
      'ParamAngleX': 30, 
      'ParamAngleY': 0, 
      'ParamAngleZ': -15,
      'ParamBodyAngleX': 15,
      'ParamBodyAngleY': 0,
      'ParamBodyAngleZ': -5
    }
  },
  { 
    state: motionStates.DANCE, 
    params: { 
      'ParamAngleX': 15, 
      'ParamAngleY': -15, 
      'ParamAngleZ': 15,
      'ParamBodyAngleX': 10,
      'ParamBodyAngleY': -10,
      'ParamBodyAngleZ': 10,
      'ParamArmLA': 30,
      'ParamArmRA': -30
    }
  }
];

// 当前动作索引
const currentMotionIndex = ref(0);

// 当前状态
const currentMotionState = ref(motionStates.IDLE);
const currentExpression = ref('');
let expressionTimeout = null;
let motionTimeout = null;

// 随机切换表情
const changeRandomExpression = async () => {
  if (!model || !model.internalModel) return;
  
  // 清除之前的定时器
  if (expressionTimeout) {
    clearTimeout(expressionTimeout);
  }

  // 随机选择一个表情
  const randomExp = expressions[Math.floor(Math.random() * expressions.length)];
  
  try {
    // 检查模型是否有setExpression方法
    if (typeof model.internalModel.setExpression === 'function') {
      // 应用表情
      await model.internalModel.setExpression(randomExp);
      currentExpression.value = randomExp;
      
      // 设置表情持续时间
      expressionTimeout = setTimeout(() => {
        if (model && model.internalModel && typeof model.internalModel.setExpression === 'function') {
          model.internalModel.setExpression(''); // 恢复默认表情
        }
        currentExpression.value = '';
      }, 3000);
    } else {
      console.warn('Live2D模型不支持setExpression方法，使用替代方法');
      // 尝试使用替代方法
      if (model.internalModel.coreModel && typeof model.internalModel.coreModel.setParameterValueById === 'function') {
        // 使用参数控制表情
        model.internalModel.coreModel.setParameterValueById('ParamMouthForm', 1); // 微笑
        model.internalModel.coreModel.setParameterValueById('ParamEyeLSmile', 1); // 眯眼
        model.internalModel.coreModel.setParameterValueById('ParamEyeRSmile', 1); // 眯眼
        currentExpression.value = randomExp;
        
        // 设置表情持续时间
        expressionTimeout = setTimeout(() => {
          if (model && model.internalModel && model.internalModel.coreModel) {
            model.internalModel.coreModel.setParameterValueById('ParamMouthForm', 0);
            model.internalModel.coreModel.setParameterValueById('ParamEyeLSmile', 0); 
            model.internalModel.coreModel.setParameterValueById('ParamEyeRSmile', 0);
          }
          currentExpression.value = '';
        }, 3000);
      }
    }
  } catch (error) {
    console.error('Failed to change expression:', error);
  }
};

// 添加点击切换动作的处理函数
const handleModelClick = () => {
  // 只在空闲状态下允许切换动作
  if (currentMotionState.value === motionStates.IDLE) {
    currentMotionIndex.value = (currentMotionIndex.value + 1) % clickableMotions.length;
    const motion = clickableMotions[currentMotionIndex.value];
    updateMotionState(motion.state, motion.params);
  }
};

// 修改updateMotionState函数，增强动作效果和连贯性
const updateMotionState = async (state, customParams = null) => {
  if (!model || !model.internalModel) return;
  
  // 清除之前的定时器
  if (motionTimeout) {
    clearTimeout(motionTimeout);
  }

  currentMotionState.value = state;
  
  try {
    // 如果提供了自定义参数，使用自定义参数
    if (customParams) {
      Object.entries(customParams).forEach(([param, value]) => {
        try {
          // 使用缓动效果使动作更平滑
          const currentValue = model.internalModel.coreModel.getParameterValueById(param);
          const steps = 10;
          const increment = (value - currentValue) / steps;
          
          let step = 0;
          const animate = () => {
            if (step < steps) {
              const newValue = currentValue + (increment * step);
              model.internalModel.coreModel.setParameterValueById(param, newValue);
              step++;
              requestAnimationFrame(animate);
            } else {
              model.internalModel.coreModel.setParameterValueById(param, value);
            }
          };
          animate();
        } catch (error) {
          console.warn(`Failed to set parameter ${param}:`, error);
        }
      });
    } else {
      // 使用预定义的动作参数
      switch (state) {
        case motionStates.TALKING:
          // 说话时的动作更自然
          const talkingAnimation = () => {
            if (currentMotionState.value === motionStates.TALKING) {
              const mouthOpen = Math.sin(Date.now() / 200) * 0.5 + 0.5; // 更自然的嘴部动作
              model.internalModel.coreModel.setParameterValueById('ParamMouthOpenY', mouthOpen);
              model.internalModel.coreModel.setParameterValueById('ParamMouthForm', 0.2);
              requestAnimationFrame(talkingAnimation);
            }
          };
          talkingAnimation();
          break;
        case motionStates.THINKING:
          model.internalModel.coreModel.setParameterValueById('ParamAngleX', -15);
          model.internalModel.coreModel.setParameterValueById('ParamAngleY', 30);
          model.internalModel.coreModel.setParameterValueById('ParamAngleZ', -10);
          model.internalModel.coreModel.setParameterValueById('ParamEyeLOpen', 0.8);
          model.internalModel.coreModel.setParameterValueById('ParamEyeROpen', 0.8);
          break;
        case motionStates.HAPPY:
          changeRandomExpression();
          model.internalModel.coreModel.setParameterValueById('ParamAngleX', 0);
          model.internalModel.coreModel.setParameterValueById('ParamAngleY', 15);
          model.internalModel.coreModel.setParameterValueById('ParamAngleZ', 0);
          model.internalModel.coreModel.setParameterValueById('ParamMouthForm', 1);
          model.internalModel.coreModel.setParameterValueById('ParamEyeRSmile', 1);
          model.internalModel.coreModel.setParameterValueById('ParamEyeLSmile', 1);
          break;
        case motionStates.SURPRISED:
          model.internalModel.coreModel.setParameterValueById('ParamAngleX', 0);
          model.internalModel.coreModel.setParameterValueById('ParamAngleY', -15);
          model.internalModel.coreModel.setParameterValueById('ParamAngleZ', 0);
          model.internalModel.coreModel.setParameterValueById('ParamEyeBallY', -0.5);
          model.internalModel.coreModel.setParameterValueById('ParamMouthOpenY', 0.8);
          model.internalModel.coreModel.setParameterValueById('ParamEyeLOpen', 1.2);
          model.internalModel.coreModel.setParameterValueById('ParamEyeROpen', 1.2);
          break;
        default:
          // 恢复到空闲状态
          model.internalModel.coreModel.setParameterValueById('ParamAngleX', 0);
          model.internalModel.coreModel.setParameterValueById('ParamAngleY', 0);
          model.internalModel.coreModel.setParameterValueById('ParamAngleZ', 0);
          model.internalModel.coreModel.setParameterValueById('ParamBodyAngleX', 0);
          model.internalModel.coreModel.setParameterValueById('ParamBodyAngleY', 0);
          model.internalModel.coreModel.setParameterValueById('ParamBodyAngleZ', 0);
          model.internalModel.coreModel.setParameterValueById('ParamMouthOpenY', 0);
          model.internalModel.coreModel.setParameterValueById('ParamMouthForm', 0);
          model.internalModel.coreModel.setParameterValueById('ParamEyeLOpen', 1);
          model.internalModel.coreModel.setParameterValueById('ParamEyeROpen', 1);
          model.internalModel.coreModel.setParameterValueById('ParamEyeRSmile', 0);
          model.internalModel.coreModel.setParameterValueById('ParamEyeLSmile', 0);
      }
    }
    
    // 设置状态持续时间
    if (state !== motionStates.IDLE && state !== motionStates.TALKING) {
      motionTimeout = setTimeout(() => {
        updateMotionState(motionStates.IDLE);
      }, 3000);
    }
  } catch (error) {
    console.error('Failed to update motion state:', error);
  }
};

// 修改sendMessage函数，添加表情和动作响应
const sendMessage = async () => {
  if (!userInput.value.trim()) return;
  
  const ques = userInput.value.trim();
  console.log('发送消息:', ques);
  userInput.value = '';
  
  // 添加用户消息到聊天历史
  chatHistory.value.push({
    type: 'user',
    text: ques
  });

  // 切换到说话状态并保持直到收到回答
  updateMotionState(motionStates.TALKING);

  // 处理城市地图跳转
  const cityName = getCityFromMessage(ques);
  console.log('检测到城市名称:', cityName);
  
  if (cityName && cityGeoData[cityName]) {
    console.log('准备跳转到城市:', cityName);
    console.log('当前app状态:', app);
    console.log('当前场景:', app?.currentScene);
    console.log('历史记录:', app?.history);
    
    if (app && app.history.length > 0 && app.history[app.history.length - 1].name === cityGeoData[cityName].name) {
      const response = `当前已在${cityName}地区`;
      chatHistory.value.push({
        type: 'ai',
        text: response
      });
      await speak(response);
      return;
    } else if (app && app.mainSceneGroup && app.mainSceneGroup.visible) {
      const response = `正在为您跳转到${cityName}地区...`;
      chatHistory.value.push({
        type: 'ai',
        text: response
      });
      await speak(response);

      const cityData = cityGeoData[cityName];
      console.log('城市数据:', cityData);
      
      // 先隐藏所有图表
      chartVisible.pie = false;
      chartVisible.wordCloud = false;
      chartVisible.calendar = false;
      
      try {
        // 设置场景状态
        app.currentScene = 'childScene';
        console.log('设置场景为:', app.currentScene);
        
        // 添加到历史记录
        app.history.push(cityData);
        console.log('添加历史记录:', app.history);
        
        // 加载子地图
        app.loadChildMap(cityData);
        console.log('加载子地图完成');
        
        // 等待地图加载完成
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // 在地图跳转完成后，继续处理用户的问题
        try {
          // 获取当前城市的模型工作空间
          const modelWorkspace = getModelWorkspace(ques);
          console.log('使用的模型工作空间:', modelWorkspace);
          
          // 构造请求URL
          const url = `/api/v1/workspace/${modelWorkspace}/chat`;
          
          // 构造请求配置
          const config = {
            headers: {
              'Authorization': 'Bearer GG41P0D-JDW4N05-PTH2RHS-BJQK8HB',
              'Content-Type': 'application/json',
              'accept': 'application/json'
            },
            timeout: 30000
          };

          // 构造请求体
          const data = {
            message: ques,
            mode: 'query',
            max_token: 512
          };

          // 发送请求
          const response = await axios.post(url, data, config);
          console.log('收到API响应:', response);

          if (response.data && response.data.textResponse) {
            const mxhd = response.data.textResponse;
            
            // 继续保持说话状态一小段时间
            updateMotionState(motionStates.TALKING);
            
            // 延迟后根据回答内容切换表情
            setTimeout(() => {
              if (mxhd.includes('抱歉') || mxhd.includes('对不起')) {
                updateMotionState(motionStates.THINKING);
              } else if (mxhd.includes('！') || mxhd.includes('!')) {
                updateMotionState(motionStates.SURPRISED);
              } else {
                updateMotionState(motionStates.HAPPY);
              }
            }, 1000);

            chatHistory.value.push({
              type: 'ai',
              text: mxhd
            });
            await speak(mxhd);
          }
        } catch (error) {
          console.error('API调用失败:', error);
          updateMotionState(motionStates.THINKING);
          const response = `已为您跳转到${cityName}地区。您可以继续询问该地区的相关信息。`;
          chatHistory.value.push({
            type: 'ai',
            text: response
          });
          await speak(response);
        }
      } catch (error) {
        console.error('地图跳转失败:', error);
        updateMotionState(motionStates.THINKING);
        const response = `抱歉，跳转到${cityName}地区失败，请稍后重试。`;
        chatHistory.value.push({
          type: 'ai',
          text: response
        });
        await speak(response);
      }
      return;
    }
  }

  // 显示加载状态
  chatHistory.value.push({
    type: 'ai',
    text: '正在思考中...'
  });

  try {
    // 获取当前城市的模型工作空间
    const modelWorkspace = getModelWorkspace(ques);
    console.log('使用的模型工作空间:', modelWorkspace);
    
    // 构造请求URL - 使用正确的端口号
    const url = `/api/v1/workspace/${modelWorkspace}/chat`;
    
    // 构造请求配置
    const config = {
      headers: {
        'Authorization': 'Bearer GG41P0D-JDW4N05-PTH2RHS-BJQK8HB',
        'Content-Type': 'application/json',
        'accept': 'application/json'
      },
      timeout: 30000 // 30秒超时
    };

    // 构造请求体
    const data = {
      message: ques,
      mode: 'query',
      max_token: 512
    };

    console.log('发送请求到:', url);
    console.log('请求配置:', config);
    console.log('请求数据:', data);

    // 使用 axios 发送请求
    const response = await axios.post(url, data, config);
    console.log('收到原始响应:', response);
    
    // 移除加载状态消息
    chatHistory.value.pop();

    // 根据响应内容切换表情和动作
    if (response.data && response.data.textResponse) {
      const mxhd = response.data.textResponse;
      
      // 继续保持说话状态一小段时间
      updateMotionState(motionStates.TALKING);
      
      // 延迟后根据回答内容切换表情
      setTimeout(() => {
        if (mxhd.includes('抱歉') || mxhd.includes('对不起')) {
          updateMotionState(motionStates.THINKING);
        } else if (mxhd.includes('！') || mxhd.includes('!')) {
          updateMotionState(motionStates.SURPRISED);
        } else {
          updateMotionState(motionStates.HAPPY);
        }
      }, 1000);

      chatHistory.value.push({
        type: 'ai',
        text: mxhd
      });
      await speak(mxhd);
    } else {
      console.error('响应数据格式不正确:', response.data);
      throw new Error('未收到有效的模型回答');
    }

  } catch (error) {
    console.error('API调用失败:', error);
    updateMotionState(motionStates.THINKING);
    if (error.response) {
      // 服务器返回了错误状态码
      console.error('服务器错误:', error.response.status, error.response.data);
    } else if (error.request) {
      // 请求发出但没有收到响应
      console.error('未收到响应:', error.request);
    } else {
      // 请求配置出错
      console.error('请求配置错误:', error.message);
    }
    
    // 移除加载状态消息
    chatHistory.value.pop();
    
    // 使用本地简单回复作为fallback
    let localResponse = '抱歉，我暂时无法回答您的问题。';
    
    if (error.response) {
      localResponse += ` (错误码: ${error.response.status})`;
    } else if (error.request) {
      localResponse += ' (无法连接到服务器，请检查服务是否启动)';
    }
    
    // 根据问题类型返回本地回复
    if (ques.includes('你好') || ques.includes('您好')) {
      localResponse = '您好！我是您的智能助手，请问有什么可以帮您？';
    } else if (ques.includes('招聘') || ques.includes('工作')) {
      localResponse = '我可以帮您查看各地区的招聘信息和数据分析。您想了解哪个地区的情况？';
    } else if (ques.includes('数据') || ques.includes('分析')) {
      localResponse = '您可以查看左侧的饼图了解学历需求分布，右上角的热力图了解时间分布，左下角的词云图了解地区分布。';
    } else if (ques.includes('谢谢') || ques.includes('感谢')) {
      localResponse = '不客气！如果还有其他问题，随时问我。';
    }
    
    chatHistory.value.push({
      type: 'ai',
      text: localResponse
    });
    await speak(localResponse);
  }

  // 保持滚动到底部
  setTimeout(() => {
    if (chatMessages.value) {
      chatMessages.value.scrollTop = chatMessages.value.scrollHeight;
    }
  }, 100);

  // 滚动到底部
  await nextTick();
  autoScroll(leftMiddlePanelContent.value);
};

// 修改 toggleChart 函数
const toggleChart = (chartType) => {
  // 只有在主场景时才允许切换图表显示状态
  if (app && app.currentScene !== 'mainScene') {
    return;
  }
  
  chartVisible[chartType] = !chartVisible[chartType];
  
  // 在显示图表时重新渲染
  if (chartVisible[chartType]) {
    setTimeout(() => {
      switch (chartType) {
        case 'pie':
          drawPieChart();
          break;
        case 'wordCloud':
          drawWordCloudChart();
          break;
        case 'calendar':
          drawCalendarChart();
          break;
      }
    }, 0);
  }
};

const drawPieChart = async () => {
  try {
    const chartDom = document.getElementById('pieChart');
    if (!chartDom) {
      console.error('Error: pieChart DOM element not found');
      return;
    }

    // 设置容器尺寸
    chartDom.style.width = '100%';
    chartDom.style.height = '300px';

    // 初始化图表实例
    if (pieChart) {
      pieChart.dispose();
    }
    pieChart = echarts.init(chartDom);

    // 读取CSV数据
    const response = await fetch('/daily_job_stats.csv');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const csvText = await response.text();

    // 解析CSV数据
    const rows = csvText.trim().split('\n').slice(1); // 跳过标题行
    let currentIndex = 0;
    
    // 初始化数据数组
    let dates = [];
    let values = [];
    
    // 更新函数
    const updateChart = () => {
      // 获取10条数据
      const currentData = rows.slice(currentIndex, currentIndex + 10);
      
      // 更新数据数组
      dates = currentData.map(row => {
        const [date] = row.split(',');
        return date;
      });
      
      values = currentData.map(row => {
        const [, count] = row.split(',');
        return parseInt(count);
      });

      // 设置图表配置
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross',
            label: {
              backgroundColor: '#283b56'
            }
          }
        },
        legend: {
          data: ['发布数量', '趋势线'],
          textStyle: {
            color: '#fff'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: [
          {
            type: 'category',
            boundaryGap: true,
            data: dates,
            axisLabel: {
              color: '#fff',
              rotate: 45
            }
          }
        ],
        yAxis: [
            {
              type: 'value',
              scale: true,
              name: '职位数量',
              max: 20,     // 设置最大值为80
              min: 0,      // 最小值保持为0
              interval: 5, // 将刻度间隔改为10，这样会显示0,10,20,...,80
              boundaryGap: [0.2, 0.2],
              axisLabel: {
                color: '#fff',
                formatter: '{value}'
              },
              nameTextStyle: {
                color: '#fff',
                fontSize: 12,
                padding: [0, 0, 0, 30]
              },
              splitLine: {
                show: true,
                lineStyle: {
                  color: 'rgba(255, 255, 255, 0.1)',
                  type: 'dashed'
                }
              }
            }
          ],
        series: [
          {
            name: '发布数量',
            type: 'bar',
            data: values,
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(58, 218, 255, 0.8)' },
                { offset: 1, color: 'rgba(58, 218, 255, 0.1)' }
              ])
            }
          },
          {
            name: '趋势线',
            type: 'line',
            smooth: true,
            data: values,
            symbolSize: 8,
            lineStyle: {
              width: 2,
              color: '#ffce77'
            },
            itemStyle: {
              color: '#ffce77'
            }
          }
        ]
      };

      pieChart.setOption(option);
      
      // 更新索引，循环显示数据
      currentIndex = (currentIndex + 1) % (rows.length - 9);  // -9确保始终有10条数据
    };

    // 首次更新
    updateChart();

    // 设置定时器，每2.1秒更新一次
    const timer = setInterval(updateChart, 5000);

    // 在组件卸载时清除定时器
    onBeforeUnmount(() => {
      clearInterval(timer);
    });

    // 监听窗口大小变化
    window.addEventListener('resize', () => {
      pieChart && pieChart.resize();
    });

  } catch (error) {
    console.error('Error in drawPieChart:', error);
  }
};

// 修改drawCalendarChart函数
const drawCalendarChart = async () => {
  try {
    const chartDom = document.getElementById('calendarChart');
    if (!chartDom) {
      console.error('Error: calendarChart DOM element not found');
      return;
    }

    // 设置容器尺寸
    chartDom.style.width = '100%';
    chartDom.style.height = '300px';

    // 初始化图表实例
    if (calendarChart) {
      calendarChart.dispose();
    }
    calendarChart = echarts.init(chartDom);
    
    // 读取CSV数据
    const response = await fetch('/河流图data.csv');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const csvText = await response.text();
    
    // 解析CSV数据
    const rows = csvText.trim().split('\n').slice(1); // 跳过标题行
    const allData = rows.map(row => {
      const [date, name, value] = row.split(',');
      return {
        date,
        name,
        value: parseInt(value)
      };
    });

    // 获取所有唯一的类别
    const categories = [...new Set(allData.map(item => item.name))];
    
    // 创建更新函数
    const updateChart = () => {
      // 随机选择5个类别
      const selectedCategories = [];
      while (selectedCategories.length < 5 && categories.length > selectedCategories.length) {
        const randomCategory = categories[Math.floor(Math.random() * categories.length)];
        if (!selectedCategories.includes(randomCategory)) {
          selectedCategories.push(randomCategory);
        }
      }

      // 为每个选中的类别准备数据系列
      const series = selectedCategories.map(category => {
        // 获取该类别的所有数据点
        const categoryData = allData
          .filter(item => item.name === category)
          .map(item => [item.date, item.value])
          .sort((a, b) => new Date(a[0]) - new Date(b[0])); // 按日期排序

        return {
          name: category,
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          lineStyle: {
            width: 2
          },
          areaStyle: {
            opacity: 0.3,
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              {
                offset: 0,
                color: 'rgba(58, 218, 255, 0.8)'
              },
              {
                offset: 1,
                color: 'rgba(58, 218, 255, 0.1)'
              }
            ])
          },
          emphasis: {
            focus: 'series'
          },
          data: categoryData
        };
      });

      // 设置图表配置
      const option = {
        title: {
          text: '职位发布趋势',
          textStyle: {
            color: '#fff',
            fontSize: 14
          },
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'line',
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.3)'
            }
          },
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          borderColor: '#2bc4dc',
          borderWidth: 1,
          textStyle: {
            color: '#fff'
          }
        },
        legend: {
          data: selectedCategories,
          textStyle: {
            color: '#fff'
          },
          top: 25
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'time',
          boundaryGap: false,
          axisLine: {
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.3)'
            }
          },
          axisLabel: {
            color: '#fff',
            fontSize: 10,
            formatter: '{MM}-{dd}'
          }
        },
        yAxis: {
          type: 'value',
          name: '职位数量',
          nameTextStyle: {
            color: '#fff'
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.3)'
            }
          },
          splitLine: {
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.1)'
            }
          },
          axisLabel: {
            color: '#fff'
          }
        },
        series: series
      };

      calendarChart.setOption(option);
    };

    // 首次更新
    updateChart();

    // 设置定时器，每10秒更新一次
    const timer = setInterval(updateChart, 10000);

    // 在组件卸载时清除定时器
    onBeforeUnmount(() => {
      clearInterval(timer);
    });

    // 监听窗口大小变化
    window.addEventListener('resize', () => {
      calendarChart && calendarChart.resize();
    });

  } catch (error) {
    console.error('Error in drawCalendarChart:', error);
  }
};

// 添加绘制词云图的函数
const drawWordCloudChart = async () => {
  try {
    // 获取DOM元素
    const chartDom = document.getElementById('wordCloudChart');
    if (!chartDom) {
      console.error('找不到wordCloudChart DOM元素');
      return;
    }
    
    // 更新标题
    const headerSpan = document.querySelector('.table.left-table.top .chart-header span');
    if (headerSpan) {
      headerSpan.textContent = '学历和工作经验分布';
    }
    
    // 初始化图表
    if (wordCloudChart) {
      wordCloudChart.dispose();
    }
    wordCloudChart = echarts.init(chartDom);
    
    // 读取两个CSV文件
    const [expResponse, eduResponse] = await Promise.all([
      fetch('/工作经验统计.csv'),
      fetch('/result_processed1.csv')
    ]);
    
    if (!expResponse.ok || !eduResponse.ok) {
      throw new Error('读取CSV文件失败');
    }
    
    const expCsvText = await expResponse.text();
    const eduCsvText = await eduResponse.text();
    
    // 解析工作经验数据
    const expRows = expCsvText.trim().split('\n').slice(1);
    const expData = expRows.map(row => {
      const [experience, percentage] = row.split(',');
      return {
        name: experience,
        value: parseFloat(percentage.replace('%', ''))
      };
    });
    
    // 解析学历数据
    const eduRows = eduCsvText.trim().split('\n').slice(1);
    const eduData = eduRows.map(row => {
      const [education, count] = row.split(',');
      return {
        name: education,
        value: parseInt(count)
      };
    });
    
    // 数据集
    const datasets = [
      {
        title: '工作经验分布',
        data: expData,
        color: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452']
      },
      {
        title: '学历需求分布',
        data: eduData,
        color: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452']
      }
    ];
    
    let currentIndex = 0;
    
    // 绘制图表函数
    const renderChart = (datasetIndex) => {
      const dataset = datasets[datasetIndex];
      
      const option = {
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c}',
          backgroundColor: 'rgba(0,0,0,0.7)',
          borderWidth: 0,
          textStyle: {
            color: '#fff'
          }
        },
        legend: {
          orient: 'horizontal',
          top: '5%',
          left: 'center',
          itemGap: 20,
          textStyle: {
            color: '#ffffff', // 修改为白色
            fontSize: 12
          },
          itemWidth: 12,
          itemHeight: 12,
          icon: 'rect'
        },
        title: {
          text: dataset.title,
          left: 'center',
          top: '12%',
          textStyle: {
            color: '#fff',
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        grid: {
          top: '25%',
          bottom: '5%',
          containLabel: true
        },
        series: [
          {
            name: dataset.title,
            type: 'pie',
            radius: '60%',
            center: ['50%', '60%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 4,
              borderColor: 'rgba(255, 255, 255, 0.2)',
              borderWidth: 1
            },
            label: {
              show: true,
              position: 'outside',
              formatter: '{b}',
              fontSize: 12,
              lineHeight: 14,
              padding: [0, 0, 0, 0],
              color: '#ffffff' // 修改为白色
            },
            labelLine: {
              show: true,
              length: 15,
              length2: 10,
              smooth: true,
              lineStyle: {
                color: 'rgba(255, 255, 255, 0.7)', // 修改为半透明白色
                width: 1,
                type: 'solid'
              }
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 14,
                fontWeight: 'bold',
                color: '#ffffff' // 修改为白色
              }
            },
            data: dataset.data,
            animationType: 'scale',
            animationEasing: 'elasticOut',
            animationDelay: function(idx) {
              return Math.random() * 200;
            }
          }
        ]
      };
      
      wordCloudChart.setOption(option, true);
    };
    
    // 初始渲染第一个图表
    renderChart(currentIndex);
    
    // 切换图表的定时器
    const changeChartTimer = setInterval(() => {
      currentIndex = (currentIndex + 1) % datasets.length;
      renderChart(currentIndex);
    }, 5000);
    
    // 监听窗口大小变化
    window.addEventListener('resize', () => {
      wordCloudChart && wordCloudChart.resize();
    });
    
    // 组件卸载时清除定时器
    onBeforeUnmount(() => {
      clearInterval(changeChartTimer);
    });
    
  } catch (error) {
    console.error('绘制图表时出错:', error);
  }
};
// 添加调试函数
const debugProvinceName = (name) => {
  console.log('Province name:', name);
  console.log('Available provinces:', Object.keys(provincePoliciesData));
  console.log('Found policy:', provincePoliciesData[name]);
};

// 添加加载省份政策的函数
const loadProvincePolicy = (provinceName) => {
  console.log('Loading policy for province:', provinceName);
  
  // 尝试不同的名称格式
  const policy = provincePoliciesData[provinceName] || 
                provincePoliciesData[provinceName + '市'] ||
                provincePoliciesData[provinceName.replace('市', '')];
  
  return policy || {
    conditions: [
      {
        title: '提示',
        content: `${provinceName}的具体落户政策正在完善中...`
      }
    ],
    benefits: [
      {
        title: '提示',
        content: '详细信息即将更新'
      }
    ]
  };
};

// 添加加载省份补贴政策的函数
const loadProvinceSubsidy = (provinceName) => {
  console.log('Loading subsidy for province:', provinceName);
  
  // 尝试不同的名称格式
  const subsidy = provinceSubsidiesData[provinceName] || 
                 provinceSubsidiesData[provinceName + '市'] ||
                 provinceSubsidiesData[provinceName.replace('市', '')];
  
  console.log('Found subsidy:', subsidy);
  
  return subsidy || {
    subsidies: [
      {
        title: '提示',
        content: `${provinceName}的具体补贴政策正在完善中...`
      }
    ]
  };
};

// 添加加载创业政策的函数
const loadEntrepreneurPolicy = (provinceName) => {
  console.log('Loading entrepreneur policy for province:', provinceName);
  
  // 尝试不同的名称格式
  const policy = entrepreneurPolicy[provinceName] || 
                entrepreneurPolicy[provinceName + '市'] ||
                entrepreneurPolicy[provinceName.replace('市', '')];
  
  console.log('Found entrepreneur policy:', policy);
  
  return policy || [];
};

// 修改 loadChildMap 函数
const loadChildMap = (data) => {
  if (!app) return;
  
  console.log('Loading child map for:', data);
  
  // 更新当前省份的所有政策信息
  if (data && data.name) {
    currentPolicy.value = loadProvincePolicy(data.name);
    currentSubsidy.value = loadProvinceSubsidy(data.name);
    currentEntrepreneurPolicy.value = loadEntrepreneurPolicy(data.name);
  }

  // 确保在调用 app.loadChildMap 之前设置场景
  app.currentScene = 'childScene';
  
  // 调用原始的 loadChildMap 函数
  app.loadChildMap(data);
};

// 修改Live2D初始化函数
const initLive2D = async () => {
  if (isLive2DInitialized.value) return;
  
  console.log('Initializing Live2D...');
  
  try {
    // 等待DOM更新完成
    await nextTick();
    
    // 确保canvas元素存在
    if (!liveCanvas.value) {
      throw new Error('Canvas element not found');
    }

    // 确保之前的实例被清理
    if (pixiApp) {
      pixiApp.destroy(true, { children: true, texture: true, baseTexture: true });
      pixiApp = null;
    }
    if (model) {
      model.destroy({ children: true, texture: true, baseTexture: true });
      model = null;
    }

    // 创建新的PIXI应用
    pixiApp = new PIXI.Application({
      view: liveCanvas.value,
      width: 300,
      height: 400,
      backgroundAlpha: 0,
      antialias: true,
      autoDensity: true,
      resolution: window.devicePixelRatio || 1,
      powerPreference: 'high-performance',
      preserveDrawingBuffer: true,
      clearBeforeRender: true
    });

    // 设置交互选项
    pixiApp.stage.interactive = true;
    pixiApp.stage.interactiveChildren = true;

    console.log('Loading Live2D model...');
    
    // 加载模型
    try {
      model = await Live2DModel.from('./jingying1.0/jingying.model3.json', {
        autoInteract: false,
        autoUpdate: true,
        motionPreload: "ALL",
        idleMotionGroup: "Idle"
      });

      if (!model) {
        throw new Error('Failed to load Live2D model');
      }

      // 添加模型到舞台
      pixiApp.stage.addChild(model);
      
      // 调整模型位置和比例
      model.scale.set(0.085);
      model.x = 120;
      model.y = 160;
      model.anchor.set(0.5, 0.5);
      
      // 启用交互
      model.interactive = true;
      model.buttonMode = true;
      
      // 添加点击事件监听（同时支持鼠标点击和触摸）
      const handleClick = (event) => {
        event.stopPropagation();
        handleModelClick();
      };
      
      model.on('pointerdown', handleClick);
      model.on('touchstart', handleClick);
      
      // 移除悬停效果
      model.on('pointerover', () => {
        // 移除放大效果
      });
      
      model.on('pointerout', () => {
        // 移除缩小效果
      });

      // 初始化表情和动作
      updateMotionState(motionStates.IDLE);
      
      // 添加随机表情变化
      setInterval(() => {
        if (currentMotionState.value === motionStates.IDLE) {
          const shouldChangeExpression = Math.random() < 0.3; // 30%的概率改变表情
          if (shouldChangeExpression) {
            changeRandomExpression();
          }
        }
      }, 5000);

      // 添加鼠标跟踪功能
      const onMouseMove = (event) => {
        if (!model || !model.internalModel) return;

        // 获取鼠标位置相对于视口的坐标
        const mouseX = event.clientX;
        const mouseY = event.clientY;

        // 获取模型容器的位置和尺寸
        const containerRect = liveCanvas.value.getBoundingClientRect();
        const containerCenterX = containerRect.left + containerRect.width / 2;
        const containerCenterY = containerRect.top + containerRect.height / 2;

        // 计算鼠标相对于模型中心的位置（-1 到 1 的范围）
        const xRatio = (mouseX - containerCenterX) / (window.innerWidth / 2);
        const yRatio = (mouseY - containerCenterY) / (window.innerHeight / 2);

        // 将比率转换为角度（限制在合理范围内）
        const angleX = Math.max(Math.min(xRatio, 1), -1) * 30;
        const angleY = Math.max(Math.min(yRatio, 1), -1) * 30;

        // 更新模型的视线参数
        const params = model.internalModel.parameters;
        if (params) {
          // 更新眼球参数
          const eyeParams = [
            'ParamEyeBallX',
            'ParamEyeBallY',
            'ParamAngleX',
            'ParamAngleY',
            'ParamAngleZ'
          ];

          eyeParams.forEach(param => {
            if (param.includes('EyeBallX') || param.includes('AngleX')) {
              model.internalModel.coreModel.setParameterValueById(param, angleX);
            }
            if (param.includes('EyeBallY') || param.includes('AngleY')) {
              model.internalModel.coreModel.setParameterValueById(param, -angleY);
            }
          });

          // 暂停眨眼动画
          if (model.internalModel.eyeBlink) {
            model.internalModel.eyeBlink.pause();
            
            // 一段时间后恢复眨眼
            setTimeout(() => {
              if (model.internalModel.eyeBlink) {
                model.internalModel.eyeBlink.resume();
              }
            }, 100);
          }
        }
      };

      // 添加鼠标移动事件监听器
      window.addEventListener('mousemove', onMouseMove);
      
      // 开始动画循环
      startAnimation();
      
      isLive2DInitialized.value = true;
      console.log('Live2D model initialized successfully');

      // 在组件销毁时移除事件监听器
      onBeforeUnmount(() => {
        window.removeEventListener('mousemove', onMouseMove);
      });

      // 添加点击事件监听
      model.interactive = true;
      model.buttonMode = true;
      model.on('click', handleModelClick);
      model.on('tap', handleModelClick);

    } catch (error) {
      console.error('Failed to load Live2D model:', error);
      throw error;
    }
  } catch (error) {
    console.error('Failed to initialize Live2D:', error);
    isLive2DInitialized.value = false;
    
    if (!window.live2dRetryCount) {
      window.live2dRetryCount = 0;
    }
    
    if (window.live2dRetryCount < 3) {
      window.live2dRetryCount++;
      setTimeout(() => {
        initLive2D();
      }, 3000);
    }
  }
};

// 分离动画循环逻辑
const startAnimation = () => {
  if (!model || !model.internalModel || !pixiApp) return;
  
  const animate = () => {
    try {
      // 更新模型动画
      model.internalModel.motionManager.update();
      model.update(pixiApp.ticker.deltaMS);
      pixiApp.render();
      
      // 继续动画循环
      animationFrameId.value = requestAnimationFrame(animate);
    } catch (error) {
      console.error('Animation error:', error);
    }
  };

  // 启动动画循环
  animate();
};

onMounted(async () => {
  // 初始化语音系统
  try {
    speech.value = new Speech();
    const speechInitResult = await speech.value.init({
      volume: 1,
      lang: 'zh-CN',
      rate: 1,
      pitch: 1,
      voice: 'Microsoft Xiaoxiao - Chinese (Simplified)'
    });
    console.log('语音初始化结果:', speechInitResult);
    
    if (speechInitResult) {
      const testMessage = '语音系统初始化成功';
      await speech.value.speak(testMessage);
    }
  } catch (error) {
    console.error('语音初始化失败:', error);
  }

  app = new World(document.getElementById("canvas"), {
    geoProjectionCenter: [108.55, 34.32],
    setEnable: setEnable,
  });

  // 等待一帧以确保DOM已更新
  await nextTick();
  
  // 等待地图加载完成
  await new Promise(resolve => {
    const checkMapLoaded = () => {
      if (app && app.mainSceneGroup) {
        resolve();
      } else {
        setTimeout(checkMapLoaded, 100);
      }
    };
    checkMapLoaded();
  });

  // 初始化所有图表
  drawPieChart();
  drawCalendarChart();
  drawWordCloudChart();

  // 添加初始聊天消息
  chatHistory.value.push({
    type: 'ai',
    text: '您好！我是您的智能助手，请问有什么可以帮您？'
  });
  
  // 尝试播放欢迎语音
  try {
    await speak('您好！我是您的智能助手，请问有什么可以帮您？');
  } catch (error) {
    console.error('欢迎语音播放失败:', error);
  }

  // 添加模型加载状态监听
  window.addEventListener('live2d-model-load-error', (event) => {
    console.error('Live2D model load error:', event.detail);
    isLive2DInitialized.value = false;
  });

  window.addEventListener('live2d-model-load-success', () => {
    console.log('Live2D model loaded successfully');
    isLive2DInitialized.value = true;
  });
  
  // 延迟初始化Live2D，确保地图完全加载
  setTimeout(async () => {
    try {
      await initLive2D();
    } catch (error) {
      console.error('Failed to initialize Live2D in mounted:', error);
    }
  }, 3000);

  // 监听子地图加载事件
  const originalLoadChildMap = app.loadChildMap.bind(app);
  app.loadChildMap = function(...args) {
    originalLoadChildMap(...args);
    app.currentScene = 'childScene';
    
    // 更新当前省份的政策信息
    if (args[0] && args[0].name) {
      // 输出调试信息，确认名称正确传递
      console.log('加载子地图:', args[0].name);
      
      // 更新currentArea名称，这是关键步骤
      currentArea.value.name = args[0].name;
      
      // 更新其他政策信息
      currentPolicy.value = loadProvincePolicy(args[0].name);
      currentSubsidy.value = loadProvinceSubsidy(args[0].name);
      currentEntrepreneurPolicy.value = loadEntrepreneurPolicy(args[0].name);
      
      // 确保面板可见
      panelVisibility.panel1 = true;
      
      // 直接触发数据加载和图表绘制
      nextTick(() => {
        console.log('子地图加载完成，准备加载时间线数据:', args[0].name);
        // 确保在这里传递正确的省份名称格式
        loadJobTimelineData(args[0].name);
      });
    }
  };

  // 在World类初始化时添加这些方法
  if (app && app.world) {
    app.world.stopAllAnimations = stopAllAnimations;
    app.world.startAllAnimations = startAllAnimations;
  }

  if (is3DMap) {
    setupAMap();
  }

  // 安全地检查和访问组件引用
  try {
    if (app && app.$refs) {
      console.log('App refs available:', Object.keys(app.$refs));
      if (app.$refs.jobRecommendation) {
        console.log('Job recommendation component found:', app.$refs.jobRecommendation);
      } else {
        console.log('Job recommendation component not found in refs');
      }
    } else {
      console.log('App or app.$refs is undefined');
    }
  } catch (error) {
    console.error('Error accessing app.$refs:', error);
  }

  // 首先尝试初始化默认图表，确保图表容器可见
  setTimeout(() => {
    initDefaultJobTimeline();
    
    // 注入修改app.loadChildMap函数的代码，确保在子地图加载时加载薪资与经验散点图
    if (app && app.loadChildMap) {
      const originalLoadChildMap = app.loadChildMap;
      app.loadChildMap = function(data) {
        // 调用原始函数
        originalLoadChildMap.call(app, data);
        
        // 加载薪资与经验数据
        if (data && data.name) {
          console.log('修改后的loadChildMap: 加载薪资与工作年限数据', data.name);
          setTimeout(() => {
            loadSalaryExperienceData(data.name);
            // 确保模块二面板可见
            panelVisibility.panel2 = true;

            // 加载薪资范围分布数据
            console.log('修改后的loadChildMap: 加载薪资范围分布数据', data.name);
            loadSalaryCountsData(data.name);
            // 确保模块三面板可见
            panelVisibility.panel3 = true;
          }, 500);
        }
      };
      console.log('已修改app.loadChildMap函数，支持薪资与工作年限数据加载');
    }
    
    // 然后如果是子场景，再尝试加载真实数据
    if (app && app.currentScene === 'childScene' && currentArea.name) {
      setTimeout(() => {
        console.log('组件挂载完成，尝试加载职位时间线数据');
        loadJobTimelineData(currentArea.name);
        
        // 初始加载薪资与工作年限数据
        console.log('组件挂载完成，尝试加载薪资与工作年限数据');
        loadSalaryExperienceData(currentArea.name);
        
        // 初始加载薪资范围分布数据
        console.log('组件挂载完成，尝试加载薪资范围分布数据');
        loadSalaryCountsData(currentArea.name);
      }, 1000);
    }
  }, 500);

  // 在onMounted函数的最后添加全局调试函数
  // 添加全局调试函数
  window.testJobDataLoad = (provinceName) => {
    console.log(`📊 手动测试加载${provinceName}的职位数据`);
    loadJobTimelineData(provinceName);
  };

  window.testSalaryChart = (provinceName) => {
    console.log(`📊 手动测试加载${provinceName}的薪资与工作年限数据`);
    loadSalaryExperienceData(provinceName);
    panelVisibility.panel2 = true;
  };
  // 在控制台中执行以下代码
  window.testSalaryCountsChart = function(provinceName) {
    console.log(`📊 手动测试加载${provinceName}的薪资范围分布数据`);
    // 检查函数是否存在
    if (typeof loadSalaryCountsData === 'function') {
      loadSalaryCountsData(provinceName);
      // 尝试手动显示面板
      if (window.app && window.app.panelVisibility) {
        window.app.panelVisibility.panel3 = true;
      }
    } else {
      console.error('loadSalaryCountsData函数未找到');
      // 检查全局变量
      console.log('全局变量:', Object.keys(window).filter(k => k.includes('salary') || k.includes('chart')));
    }
  };

  window.checkCurrentArea = () => {
    console.log('当前区域信息:', currentArea.value);
    console.log('app当前场景:', app.currentScene);
    return {
      currentArea: currentArea.value,
      currentScene: app.currentScene,
      panels: panelVisibility
    };
  };
  // 在 mounted 或 onMounted 钩子末尾添加
setTimeout(() => {
  // 圆环按钮初始化
  const arcElement = document.querySelector('.segmented-arc');
  const labelElements = [
    document.getElementById('label-0'),
    document.getElementById('label-1'),
    document.getElementById('label-2'),
    document.getElementById('label-3'),
  ];
  const dots = document.querySelectorAll('.pagination .dot');
  const carouselContainer = document.querySelector('.carousel-container');

  // 获取原始按钮元素
  const originalButtons = {
    '政策推荐': document.getElementById('btn-policy'),
    '职业测试': document.getElementById('btn-career'),
    '3D地图户': document.getElementById('btn-3dmap'),
    '柱状图': document.getElementById('btn-bar'),
    '飞线': document.getElementById('btn-flyline'),
    '散点图': document.getElementById('btn-scatter'),
    '标签': document.getElementById('btn-card'),
    '粒子效果': document.getElementById('btn-particle'),
    '镜面反射': document.getElementById('btn-mirror'),
    '路径': document.getElementById('btn-path'),
    '职位数量图': document.getElementById('btn-pie'),
    '学历经验图': document.getElementById('btn-wordcloud'),
    '趋势图': document.getElementById('btn-calendar'),
    '岗位推荐': document.getElementById('btn-job'),
    '岗位预警': document.getElementById('btn-alert'),
    '路径规划': document.getElementById('btn-planning')
  };

  // --- Data for each group ---
  const groupsData = [
    // Group 0
    [
      { label: '政策推荐', color: '#0f3360' },
      { label: '职业测试', color: '#0e3260' }, 
      { label: '3D地图户', color: '#0e3260' }, 
      { label: '柱状图', color: '#0e3260' }
    ],
    // Group 1
    [
      { label: '飞线', color: '#0e3260' },
      { label: '散点图', color: '#0e3260' },
      { label: '标签', color: '#0e3260' },
      { label: '粒子效果', color: '#0e3260' }
    ],
    // Group 2
    [
      { label: '镜面反射', color: '#0e3260' },
      { label: '路径', color: '#0e3260' },
      { label: '职位数量图', color: '#0e3260' },
      { label: '学历经验图', color: '#0e3260' }
    ],
    // Group 3
    [
      { label: '趋势图', color: '#0e3260' },
      { label: '岗位推荐', color: '#0e3260' },
      { label: '岗位预警', color: '#0e3260' },
      { label: '路径规划', color: '#0e3260' }
    ]
  ];

  // 以下是您提供的圆环逻辑代码
  const itemsPerGroup = 4;
  const totalGroups = groupsData.length;
  const segmentAngle = 180 / itemsPerGroup;
  let currentGroup = 0;
  let currentSegmentIndex = 0;
  let carouselInterval;

  const arcContainer = document.querySelector('.segmented-arc-container');
  let arcRadius = 0;
  let labelRadius = 0;

  function calculateDimensions() {
    arcRadius = arcContainer.offsetWidth / 2;
    labelRadius = arcRadius * 0.65;
  }

  function positionLabels(groupIndex) {
    if (arcRadius === 0) calculateDimensions();

    const groupData = groupsData[groupIndex];
    groupData.forEach((itemData, index) => {
      const startAngle = 90; // Left semi-circle
      const angleOffset = segmentAngle / 2;
      const midAngleDegrees = startAngle + (index * segmentAngle) + angleOffset;
      const midAngleRadians = midAngleDegrees * Math.PI / 180;

      const labelX = arcRadius + labelRadius * Math.cos(midAngleRadians);
      const labelY = arcRadius + labelRadius * Math.sin(midAngleRadians);

      const labelEl = labelElements[index];
      if(labelEl){
        labelEl.style.left = `${labelX}px`;
        labelEl.style.top = `${labelY}px`;
        labelEl.textContent = itemData.label;
        labelEl.classList.add('visible');
        
        // 检查相应原始按钮的状态
        const originalBtn = originalButtons[itemData.label];
        if (originalBtn && originalBtn.classList.contains('active')) {
          labelEl.classList.add('active');
        } else {
          labelEl.classList.remove('active');
        }
        
        // 添加点击事件 - 触发原始按钮的点击
        labelEl.onclick = function() {
          const originalBtn = originalButtons[itemData.label];
          if (originalBtn) {
            // 触发原始按钮点击
            originalBtn.click();
            // 更新激活状态
            if (originalBtn.classList.contains('active')) {
              labelEl.classList.add('active');
            } else {
              labelEl.classList.remove('active');
            }
          }
          
          // 可选：直接输出调试信息
          console.log(`点击了: ${itemData.label}`);
        };
        
        // 添加鼠标悬停事件
        labelEl.addEventListener('mouseenter', stopCarousel);
        labelEl.addEventListener('mouseleave', startCarousel);
      }
    });

    for (let i = groupData.length; i < labelElements.length; i++) {
      if(labelElements[i]) labelElements[i].classList.remove('visible');
    }
  }

  function updateArc(groupIndex, activeIndex) {
  if (groupIndex < 0 || groupIndex >= totalGroups) return;
  if (arcRadius === 0) calculateDimensions();

  const groupData = groupsData[groupIndex];
  let gradientString = 'conic-gradient(transparent 0deg 180deg, ';
  let currentAngle = 180;
  groupData.forEach((itemData, index) => {
    let currentColor = itemData.color;
    
    // 设置默认透明度为0.3，增强可见度
    currentColor = addTransparency(currentColor, 0.3);
    
    // 激活状态处理 - 使用高透明度和更亮的颜色
    if (index === activeIndex) {
      // 增加颜色亮度 - 使青蓝色更突出
      currentColor = lightenColor(currentColor, 0.15);
      // 使用更高的透明度
      currentColor = addTransparency(currentColor, 0.7);
    }
    
    gradientString += `${currentColor} ${currentAngle}deg ${currentAngle + segmentAngle}deg`;
    currentAngle += segmentAngle;
    if (index < groupData.length - 1) { gradientString += ', '; }
  });
  gradientString += ')';
  arcElement.style.background = gradientString;

  labelElements.forEach(lbl => lbl.classList.remove('visible'));
  setTimeout(() => {
    positionLabels(groupIndex);
  }, 50);

  // Update active class for pagination dots
  dots.forEach(d => d.classList.remove('active'));
  if (dots[groupIndex]) {
    dots[groupIndex].classList.add('active');
  }
}
  // 添加一个使颜色变亮的函数
function lightenColor(color, factor) {
  let usePound = false;
  
  // 处理rgba格式
  if (color.startsWith('rgba')) {
    const parts = color.match(/rgba\((\d+),\s*(\d+),\s*(\d+),\s*([0-9.]+)\)/);
    if (parts) {
      const r = Math.min(255, parseInt(parts[1]) + Math.round(factor * 255));
      const g = Math.min(255, parseInt(parts[2]) + Math.round(factor * 255));
      const b = Math.min(255, parseInt(parts[3]) + Math.round(factor * 255));
      return `rgba(${r}, ${g}, ${b}, ${parts[4]})`;
    }
    return color;
  }
  
  // 处理rgb格式
  if (color.startsWith('rgb')) {
    const parts = color.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
    if (parts) {
      const r = Math.min(255, parseInt(parts[1]) + Math.round(factor * 255));
      const g = Math.min(255, parseInt(parts[2]) + Math.round(factor * 255));
      const b = Math.min(255, parseInt(parts[3]) + Math.round(factor * 255));
      return `rgb(${r}, ${g}, ${b})`;
    }
    return color;
  }
  
  // 处理十六进制格式
  if (color[0] === "#") {
    color = color.slice(1);
    usePound = true;
  }

  const num = parseInt(color, 16);
  let r = Math.min(255, (num >> 16) + Math.round(factor * 255));
  let g = Math.min(255, ((num >> 8) & 0x00FF) + Math.round(factor * 255));
  let b = Math.min(255, (num & 0x0000FF) + Math.round(factor * 255));

  return (usePound ? "#" : "") + 
    String("000000" + ((r << 16) | (g << 8) | b).toString(16)).slice(-6);
}

  // 添加颜色透明度的辅助函数
  function addTransparency(color, alpha) {
    // 处理rgba格式
    if (color.startsWith('rgba')) {
      const parts = color.match(/rgba\((\d+),\s*(\d+),\s*(\d+),\s*([0-9.]+)\)/);
      if (parts) {
        return `rgba(${parts[1]}, ${parts[2]}, ${parts[3]}, ${alpha})`;
      }
      return color;
    }
    
    // 处理rgb格式
    if (color.startsWith('rgb')) {
      const parts = color.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
      if (parts) {
        return `rgba(${parts[1]}, ${parts[2]}, ${parts[3]}, ${alpha})`;
      }
      return color;
    }
    
    // 处理十六进制格式
    let r, g, b;
    
    if (color.startsWith('#')) {
      color = color.slice(1);
    }
    
    if (color.length === 3) {
      r = parseInt(color.charAt(0) + color.charAt(0), 16);
      g = parseInt(color.charAt(1) + color.charAt(1), 16);
      b = parseInt(color.charAt(2) + color.charAt(2), 16);
    } else if (color.length === 6) {
      r = parseInt(color.substring(0, 2), 16);
      g = parseInt(color.substring(2, 4), 16);
      b = parseInt(color.substring(4, 6), 16);
    } else {
      return color;
    }
    
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  function darkenColor(color, factor) {
    let usePound = false;
    if (color[0] === "#") {
      color = color.slice(1);
      usePound = true;
    }

    const num = parseInt(color, 16);

    let r = (num >> 16) + Math.round(factor * 255);
    if (r > 255) r = 255;
    else if (r < 0) r = 0;

    let b = ((num >> 8) & 0x00FF) + Math.round(factor * 255);
    if (b > 255) b = 255;
    else if (b < 0) b = 0;

    let g = (num & 0x0000FF) + Math.round(factor * 255);
    if (g > 255) g = 255;
    else if (g < 0) g = 0;

    return (usePound ? "#" : "") + (g | (b << 8) | (r << 16)).toString(16).padStart(6, '0');
  }

  function startCarousel() {
    clearInterval(carouselInterval);
    carouselInterval = setInterval(() => {
      updateArc(currentGroup, currentSegmentIndex);
      currentSegmentIndex++;
      if (currentSegmentIndex >= itemsPerGroup) {
        currentSegmentIndex = 0;
        currentGroup++;
        if (currentGroup >= totalGroups) {
          currentGroup = 0; // Loop back to the first group if needed
        }
        updateArc(currentGroup, currentSegmentIndex); // Update arc for the new group
      }
    }, 1500); // Adjust interval as needed
  }

  function stopCarousel() {
    clearInterval(carouselInterval);
  }

  // Event Listeners for Pagination Dots
  dots.forEach((dot, index) => {
    dot.addEventListener('click', () => {
      currentGroup = index;
      currentSegmentIndex = 0; // Reset segment index when changing group
      updateArc(currentGroup, currentSegmentIndex);
      startCarousel(); // Restart carousel for the new group
    });
  });

  // Event Listeners for Mouse Hover
  carouselContainer.addEventListener('mouseenter', stopCarousel);
  carouselContainer.addEventListener('mouseleave', startCarousel);

  // Initial setup
  calculateDimensions();
  positionLabels(0);
  updateArc(0, 0); // Highlight the first segment initially
  dots[0].classList.add('active'); // Ensure the first dot is active
  setTimeout(startCarousel, 1000); // Start carousel with a delay

  // Recalculate dimensions on resize
  window.addEventListener('resize', () => {
    calculateDimensions();
    positionLabels(currentGroup);
    updateArc(currentGroup, currentSegmentIndex % itemsPerGroup); // Ensure highlighting on resize
  });
}, 2000); // 延迟2秒初始化，确保其他组件已加载
});

// 添加监听以便调试
watch([currentPolicy, currentSubsidy, currentEntrepreneurPolicy], ([newPolicy, newSubsidy, newEntrepreneur]) => {
  console.log('Policy changed:', newPolicy);
  console.log('Subsidy changed:', newSubsidy);
  console.log('Entrepreneur policy changed:', newEntrepreneur);
});

onBeforeUnmount(() => {
  // 停止动画循环
  if (animationFrameId.value) {
    cancelAnimationFrame(animationFrameId.value);
    animationFrameId.value = null;
  }
  
  // 清理Live2D相关资源
  if (model) {
    model.destroy({ children: true, texture: true, baseTexture: true });
    model = null;
  }
  if (pixiApp) {
    pixiApp.destroy(true, { children: true, texture: true, baseTexture: true });
    pixiApp = null;
  }
  isLive2DInitialized.value = false;
  
  // 清理聊天相关的数据
  chatHistory.value = [];
  userInput.value = '';

  // 清理语音资源
  if (speech.value) {
    speech.value.cancel();
  }
});

// 添加自动滚动相关的状态
const leftPanelContent = ref(null);
const rightPanelContent = ref(null);
const isHoveringLeft = ref(false);
const isHoveringRight = ref(false);
const isHoveringLeftMiddle = ref(false);
const leftMiddlePanelContent = ref(null);

// 自动滚动函数
const autoScroll = async (element) => {
  if (!element) return;
  
  // 获取内容高度和可视区域高度
  const scrollHeight = element.scrollHeight;
  const clientHeight = element.clientHeight;
  
  // 如果内容不需要滚动，直接返回
  if (scrollHeight <= clientHeight) return;
  
  while (true) {
    // 检查是否悬停
    if (element === leftPanelContent.value && isHoveringLeft.value) {
      await new Promise(resolve => setTimeout(resolve, 500));
      continue;
    }
    if (element === rightPanelContent.value && isHoveringRight.value) {
      await new Promise(resolve => setTimeout(resolve, 500));
      continue;
    }
    if (element === leftMiddlePanelContent.value && isHoveringLeftMiddle.value) {
      await new Promise(resolve => setTimeout(resolve, 500));
      continue;
    }

    // 滚动到底部
    await smoothScroll(element, element.scrollHeight - element.clientHeight);
    await new Promise(resolve => setTimeout(resolve, 2000)); // 底部停留2秒

    // 滚动回顶部
    await smoothScroll(element, 0);
    await new Promise(resolve => setTimeout(resolve, 2000)); // 顶部停留2秒
  }
};

// 平滑滚动函数
const smoothScroll = async (element, targetScroll) => {
  const startScroll = element.scrollTop;
  const distance = targetScroll - startScroll;
  const duration = 3000; // 滚动持续时间
  const startTime = performance.now();

  return new Promise(resolve => {
    const animateScroll = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // easeInOutQuad 缓动函数
      const easeProgress = progress < 0.5
        ? 2 * progress * progress
        : 1 - Math.pow(-2 * progress + 2, 2) / 2;

      element.scrollTop = startScroll + (distance * easeProgress);

      if (progress < 1) {
        requestAnimationFrame(animateScroll);
      } else {
        resolve();
      }
    };

    requestAnimationFrame(animateScroll);
  });
};

// 监听内容变化，启动自动滚动
watch(() => currentPolicy.value, async () => {
  await nextTick();
  autoScroll(leftPanelContent.value);
}, { deep: true });

watch(() => currentSubsidy.value, async () => {
  await nextTick();
  autoScroll(rightPanelContent.value);
}, { deep: true });

watch(() => currentEntrepreneurPolicy.value, async () => {
  await nextTick();
  autoScroll(leftMiddlePanelContent.value);
}, { deep: true });

// 添加语音相关变量
const speech = ref(null);
const isSpeaking = ref(false);

// 添加语音播报相关函数
const initSpeech = async () => {
  try {
    speech.value = new Speech();
    await speech.value.init({
      volume: 1,
      lang: 'zh-CN',
      rate: 1,
      pitch: 1,
      voice: 'Microsoft Xiaoxiao - Chinese (Simplified)'
    });
    console.log('语音初始化成功');
  } catch (error) {
    console.error('语音初始化失败:', error);
  }
};

const speak = async (text) => {
  try {
    updateMotionState(motionStates.TALKING);
    await miniMaxTTS.speak(
      text,
      () => {
        console.log('语音播放开始');
      },
      () => {
        console.log('语音播放结束');
        updateMotionState(motionStates.IDLE);
      },
      (error) => {
        console.error('语音播放错误:', error);
        updateMotionState(motionStates.IDLE);
      }
    );
  } catch (error) {
    console.error('语音播报失败:', error);
    updateMotionState(motionStates.IDLE);
  }
};

// 在组件卸载时清理语音资源
onBeforeUnmount(() => {
  // ... existing code ...
  if (speech.value) {
    speech.value.cancel();
  }
});

// 添加语音识别相关的响应式变量
const btnStatus = ref("CLOSED"); // "CONNECTING", "OPEN", "CLOSING", "CLOSED"
const resultText = ref('');      // 累加最终结果
const resultTextTemp = ref('');  // 当前处理块，用于显示
const errorMessage = ref('');
const recorderInstance = ref(null);
const websocketInstance = ref(null);

// 按钮是否禁用
const isButtonDisabled = computed(() => {
  return btnStatus.value === "CONNECTING" || btnStatus.value === "CLOSING";
});

// 计算按钮文本
const buttonText = computed(() => {
  switch (btnStatus.value) {
    case "CONNECTING": return "连接中...";
    case "OPEN": return "录音中";
    case "CLOSING": return "关闭中...";
    case "CLOSED": return "语音输入";
    default: return "语音输入";
  }
});

// 获取 WebSocket URL
function getWebSocketUrl() {
  // 检查必要的全局对象/函数是否存在
  if (!window.hex_md5 || !window.CryptoJSNew || !window.CryptoJS) {
    errorMessage.value = "加密库未正确加载。请检查 public/index.html 中的脚本。";
    console.error("Crypto libraries not found on window.");
    return null;
  }
  try {
    const url = "wss://rtasr.xfyun.cn/v1/ws";
    const appId = window.APPID || "YOUR_APPID"; // 使用你的 APPID
    const secretKey = window.API_KEY || "YOUR_APIKEY"; // 使用你的 API Key
    const ts = Math.floor(new Date().getTime() / 1000);
    const signa = window.hex_md5(appId + ts);
    const signatureSha = window.CryptoJSNew.HmacSHA1(signa, secretKey);
    let signature = window.CryptoJS.enc.Base64.stringify(signatureSha);
    signature = encodeURIComponent(signature);
    return `${url}?appid=${appId}&ts=${ts}&signa=${signature}`;
  } catch (error) {
    errorMessage.value = `生成 WebSocket URL 时出错: ${error.message}`;
    console.error("Error generating WebSocket URL:", error);
    return null;
  }
}

// 更新按钮状态
function changeBtnStatus(status) {
  btnStatus.value = status;
  if (status === "CONNECTING") {
    resultText.value = "";
    resultTextTemp.value = "";
    errorMessage.value = "";
  }
}

// 处理 WebSocket 消息
function renderResult(resultData) {
  try {
    const jsonData = JSON.parse(resultData);
    if (jsonData.action == "started") {
      console.log("握手成功");
    } else if (jsonData.action == "result") {
      const data = JSON.parse(jsonData.data);
      
      // 解析当前文本块
      let currentChunkThisMessage = "";
      if (data?.cn?.st?.rt) {
        data.cn.st.rt.forEach((j) => {
          if(j?.ws) {
            j.ws.forEach((k) => {
              if(k?.cw) {
                k.cw.forEach((l) => {
                  currentChunkThisMessage += l.w || '';
                });
              }
            });
          }
        });
      }
      
      // 更新临时结果文本
      resultTextTemp.value = currentChunkThisMessage;
      
      // 如果是最终结果，追加到累积结果中
      if (data?.cn?.st?.type == 0) {
        resultText.value += resultTextTemp.value;
        resultTextTemp.value = "";
        // 将识别结果直接填入输入框
        userInput.value = resultText.value;
      }
    } else if (jsonData.action == "error") {
      console.error("WebSocket 错误:", jsonData);
      errorMessage.value = `识别错误: ${jsonData.code} - ${jsonData.desc || JSON.stringify(jsonData)}`;
      stopRecordingAndWs();
    }
  } catch (error) {
    console.error("处理 WebSocket 消息出错:", error);
    errorMessage.value = `处理消息失败: ${error.message}`;
  }
}

// 停止录音和 WebSocket 连接
function stopRecordingAndWs() {
  console.log("停止录音和连接...");
  if (recorderInstance.value) {
    try {
      recorderInstance.value.stop();
      console.log("录音已停止");
    } catch (e) {
      console.error("停止录音器时出错:", e);
    }
  }
  
  if (websocketInstance.value && 
     (websocketInstance.value.readyState === WebSocket.CONNECTING || 
      websocketInstance.value.readyState === WebSocket.OPEN)) {
    try {
      changeBtnStatus("CLOSING");
      websocketInstance.value.close(1000, "User requested stop");
      console.log("WebSocket连接已关闭");
    } catch (e) {
      console.error("关闭 WebSocket 时出错:", e);
      changeBtnStatus("CLOSED");
      websocketInstance.value = null;
    }
  } else {
    console.log("WebSocket 实例不存在或已关闭");
    changeBtnStatus("CLOSED");
    if (recorderInstance.value) {
      recorderInstance.value = null;
    }
    websocketInstance.value = null;
  }
}

// 连接 WebSocket 并开始录音
function connectWebSocketAndStartRecording() {
  if (!window.RecorderManager) {
    errorMessage.value = "RecorderManager 未加载。请检查 public/index.html 中的脚本。";
    console.error("RecorderManager not found on window.");
    changeBtnStatus("CLOSED");
    return;
  }

  const websocketUrl = getWebSocketUrl();
  if (!websocketUrl) {
    changeBtnStatus("CLOSED");
    return;
  }

  if (websocketInstance.value && websocketInstance.value.readyState !== WebSocket.CLOSED) {
    console.warn("WebSocket 仍在连接状态，请先关闭。");
    return;
  }

  console.log("准备连接 WebSocket...");
  changeBtnStatus("CONNECTING");

  try {
    websocketInstance.value = new WebSocket(websocketUrl);

    websocketInstance.value.onopen = (e) => {
      console.log("WebSocket 连接已打开:", e);
      try {
        recorderInstance.value = new window.RecorderManager('/js/libs');
        console.log("RecorderManager 实例已创建");

        recorderInstance.value.onStart = () => {
          console.log("录音开始");
          changeBtnStatus("OPEN");
        };

        recorderInstance.value.onFrameRecorded = ({ isLastFrame, frameBuffer }) => {
          if (websocketInstance.value && websocketInstance.value.readyState === WebSocket.OPEN) {
            try {
              websocketInstance.value.send(new Int8Array(frameBuffer));
              if (isLastFrame) {
                websocketInstance.value.send('{"end": true}');
                console.log('已发送结束帧');
              }
            } catch (sendError) {
              console.error("发送数据错误:", sendError);
              errorMessage.value = `发送音频数据失败: ${sendError.message}`;
            }
          }
        };

        recorderInstance.value.onStop = () => {
          console.log("录音已停止");
          recorderInstance.value = null;
        };

        console.log("开始录音...");
        recorderInstance.value.start({
          sampleRate: 16000,
          frameSize: 1280
        });
        console.log("录音已开始");

      } catch (recError) {
        console.error("录音初始化失败:", recError);
        errorMessage.value = `录音失败: ${recError.message}`;
        stopRecordingAndWs();
      }
    };

    websocketInstance.value.onmessage = (e) => {
      renderResult(e.data);
    };

    websocketInstance.value.onerror = (e) => {
      console.error("WebSocket错误:", e);
      let errorDetail = "未知连接错误";
      if (e instanceof ErrorEvent) {
        errorDetail = e.message;
      } else if (typeof e === 'object' && e !== null && 'message' in e) {
        errorDetail = e.message;
      } else if (e instanceof Event && e.type === 'error') {
        errorDetail = "连接无法建立或中断";
      }
      errorMessage.value = `连接错误: ${errorDetail}`;
      stopRecordingAndWs();
    };

    websocketInstance.value.onclose = (e) => {
      console.log(`WebSocket连接已关闭: 代码=${e.code}, 原因='${e.reason || '无原因'}', 干净=${e.wasClean}`);

      if (recorderInstance.value) {
        console.warn("WebSocket关闭，停止录音...");
        try {
          recorderInstance.value.stop();
        } catch(recStopError) {
          console.error("停止录音失败:", recStopError);
        }
        recorderInstance.value = null;
      }

      if (!errorMessage.value && !e.wasClean && e.code !== 1000 && e.code !== 1005) {
        errorMessage.value = `连接意外关闭 (代码: ${e.code})`;
      }

      changeBtnStatus("CLOSED");
      websocketInstance.value = null;
    };

  } catch (error) {
    errorMessage.value = `创建WebSocket失败: ${error.message}`;
    console.error("创建WebSocket错误:", error);
    changeBtnStatus("CLOSED");
  }
}

// 按钮点击事件处理
const toggleRecording = () => {
  if (btnStatus.value === "CLOSED") {
    connectWebSocketAndStartRecording();
  } else if (btnStatus.value === "OPEN") {
    console.log("用户停止录音");
    stopRecordingAndWs();
  } else {
    console.log(`当前按钮状态: ${btnStatus.value}, 无效操作`);
  }
};
// 添加视频弹窗控制变量
const showVideoModal = ref(false);

// 添加3D地图相关变量
let map = null;
let markers = [];
let markerCluster = null;
const is3DMap = ref(false);

// 添加3D地图初始化函数
const initAMap = () => {
  if (!window.AMap) {
    const script = document.createElement('script');
    script.src = 'https://webapi.amap.com/maps?v=2.0&key=your_key_here&plugin=AMap.ControlBar,AMap.MarkerClusterer';
    script.async = true;
    document.head.appendChild(script);
    
    script.onload = () => {
      createAMap();
    };
  } else {
    createAMap();
  }
};

// 创建3D地图实例
const createAMap = () => {
  try {
    // 默认中心点，防止NaN
    const defaultCenter = [116.397428, 39.90923]; // 北京市中心
    
    map = new AMap.Map('amap-container', {
      viewMode: '3D',
      pitch: 50,
      rotateEnable: true,
      pitchEnable: true,
      zoom: 17,
      zooms: [2, 20],
      rotation: -15,
      center: defaultCenter, // 使用默认中心点
      buildingAnimation: true,
      expandZoomRange: true,
      showBuildingBlock: true
    });

    const controlBar = new AMap.ControlBar({
      position: { right: '10px', top: '80px' }
    });
    map.addControl(controlBar);

    // 添加工具条控件
    const toolbar = new AMap.ToolBar({
      position: { top: '80px', left: '10px' }
    });
    map.addControl(toolbar);

    markerCluster = new AMap.MarkerClusterer(map, [], {
      gridSize: 80,
      maxZoom: 16
    });
    
    console.log('高德地图创建成功');
  } catch (error) {
    console.error('创建高德地图时出错:', error);
  }
};

// 添加地图切换函数
const toggleMapMode = async () => {
  is3DMap.value = !is3DMap.value;
  
  if (is3DMap.value) {
    // 完全隐藏原有3D地图层
    if (app && app.world) {
      // 停止渲染和动画
      app.world.stopAllAnimations();
      // 移除canvas的内容
      const canvas = document.getElementById('canvas');
      if (canvas) {
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
      // 隐藏图表
      Object.keys(chartVisible).forEach(key => {
        chartVisible[key] = false;
      });
    }
    
    await nextTick();
    if (!map) {
      initAMap();
    }
    try {
      const response = await axios.get('/api/map3d/companies');
      if (response.data && response.data.companies) {
        createMarkers(response.data.companies);
      }
    } catch (error) {
      console.error('获取3D地图数据失败:', error);
    }
  } else {
    // 恢复原有3D地图层
    if (app && app.world) {
      // 重新开始渲染和动画
      app.world.startAllAnimations();
      // 重新初始化第一层地图
      app.world.initMap();
      // 恢复图表显示
      Object.keys(chartVisible).forEach(key => {
        chartVisible[key] = true;
      });
    }
    
    if (map) {
      markers.forEach(marker => marker.setMap(null));
      markers = [];
      if (markerCluster) {
        markerCluster.setMarkers([]);
      }
    }
  }
};

// 添加动画控制方法
const stopAllAnimations = function() {
  if (this.animationFrameId) {
    cancelAnimationFrame(this.animationFrameId);
    this.animationFrameId = null;
  }
};

const startAllAnimations = function() {
  if (!this.animationFrameId) {
    this.animate();
  }
};

// 添加创建标记点函数
const createMarkers = (companies) => {
  try {
    // 清除之前的标记
    markers.forEach(marker => marker.setMap(null));
    markers = [];

    // 检查companies数据有效性
    if (!Array.isArray(companies) || companies.length === 0) {
      console.warn('公司数据无效或为空');
      return;
    }

    // 过滤掉无效的经纬度数据
    const validCompanies = companies.filter(company => {
      return company && company.value && 
             Array.isArray(company.value) && 
             company.value.length >= 2 &&
             !isNaN(company.value[0]) && 
             !isNaN(company.value[1]);
    });

    if (validCompanies.length === 0) {
      console.warn('没有有效的公司位置数据');
      return;
    }

    validCompanies.forEach(company => {
      try {
        const marker = new AMap.Marker({
          position: new AMap.LngLat(company.value[0], company.value[1]),
          title: company.name,
          extData: company
        });
        markers.push(marker);
      } catch (error) {
        console.error(`为公司 ${company.name} 创建标记时出错:`, error);
      }
    });

    if (markers.length > 0) {
      markerCluster.setMarkers(markers);
      map.setFitView(markers);
      console.log(`成功添加了 ${markers.length} 个公司标记`);
    }
  } catch (error) {
    console.error('创建标记点时出错:', error);
  }
};

// 修改onBeforeUnmount，添加地图清理
onBeforeUnmount(() => {
  // 保持现有的清理代码
  if (map) {
    map.destroy();
    map = null;
  }
});

// 添加搜索相关的响应式变量
const searchKeyword = ref('');
const searchResults = ref([]);
const activeIndex = ref(-1);
const map3d = ref(null);
const currentMarker = ref(null);

// 初始化3D地图
const init3DMap = () => {
  try {
    if (!window.AMap) {
      console.error('AMap未加载');
      return null;
    }

    const container = document.getElementById('amap-container');
    if (!container) {
      console.error('地图容器未找到');
      return null;
    }

    if (!map3d.value) {
      map3d.value = new AMap.Map('amap-container', {
        viewMode: '3D',
        zoom: 12,
        center: [106.55, 29.57],
        pitch: 50,
        mapStyle: 'amap://styles/fresh',
        features: ['bg', 'building', 'point'],
        buildingAnimation: true,
        showBuildingBlock: true
      });

      map3d.value.addControl(new AMap.ControlBar({
        position: { top: '10px', right: '10px' }
      }));

      console.log('3D地图初始化完成');
    }
    return map3d.value;
  } catch (error) {
    console.error('初始化3D地图失败:', error);
    return null;
  }
};

// 清除搜索
const clearSearch = () => {
  searchKeyword.value = '';
  searchResults.value = [];
  if (currentMarker.value) {
    map3d.value.remove(currentMarker.value);
    currentMarker.value = null;
  }
};

// 定位到公司
const locateCompany = async (company) => {
  console.log('定位到公司:', company);
  
  if (is3DMap.value) {
    try {
      // 清除之前的标记
      if (currentMarker.value) {
        map3d.value.remove(currentMarker.value);
      }

      const [longitude, latitude] = company.value;
      
      // 验证经纬度是否有效
      if (!longitude || !latitude || isNaN(longitude) || isNaN(latitude)) {
        ElMessage.error('公司位置信息无效');
        return;
      }

      const position = new AMap.LngLat(longitude, latitude);
      console.log('设置标记位置:', position.toString());

      // 创建新标记
      currentMarker.value = new AMap.Marker({
        position: position,
        title: company.name,
        animation: 'AMAP_ANIMATION_DROP',
        zIndex: 100,
        offset: new AMap.Pixel(0, 0)
      });

      // 创建信息窗体
      const infoWindow = new AMap.InfoWindow({
        content: `
          <div style="padding: 10px">
            <h4>${company.name}</h4>
            <p>类型：${company.type || '未知'}</p>
            <p>注册资金：${company.C11 || '未知'}</p>
            <p>主营业务：${company.C13 || '暂无描述'}</p>
          </div>
        `,
        offset: new AMap.Pixel(0, -30)
      });

      // 添加标记到地图
      map3d.value.add(currentMarker.value);

      // 点击标记显示信息窗体
      currentMarker.value.on('click', () => {
        infoWindow.open(map3d.value, position);
      });

      // 设置地图状态
      map3d.value.setStatus({
        animateEnable: true,
        dragEnable: true,
        zoomEnable: true,
        rotateEnable: true,
        pitchEnable: true
      });

      // 1. 先移动到位置，使用中等缩放级别
      await new Promise(resolve => {
        map3d.value.setZoomAndCenter(17, position, false, {
          duration: 800
        });
        setTimeout(resolve, 800);
      });

      // 2. 调整视角和旋转
      await new Promise(resolve => {
        map3d.value.setPitch(60);
        map3d.value.setRotation(30);
        setTimeout(resolve, 400);
      });

      // 3. 最终缩放到最大级别
      map3d.value.setZoom(20, {
        duration: 600
      });

      // 4. 确保标记在视图中心并微调视角
      setTimeout(() => {
        map3d.value.setCenter(position, true);
        map3d.value.setPitch(65);
        infoWindow.open(map3d.value, position);
      }, 400);

    } catch (error) {
      console.error('定位过程出错:', error);
      ElMessage.error('地图定位失败，请重试');
    }
  }
};

// 修改 handleSearch 函数中的错误处理
const handleSearch = async () => {
  if (!searchKeyword.value) {
    ElMessage.warning('请输入公司名称');
    return;
  }

  try {
    console.log('发送搜索请求，关键词:', searchKeyword.value);
    
    // 构建请求URL和参数
    const params = new URLSearchParams({
      keyword: searchKeyword.value
    });
    
    const searchUrl = `/api/company/search?${params.toString()}`;
    console.log('完整请求URL:', searchUrl);
    
    const response = await axios({
      method: 'get',
      url: searchUrl,
      timeout: 10000,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      },
      withCredentials: true
    });

    console.log('搜索响应:', response);
    const data = response.data;
    console.log('响应数据:', data);

    if (data.status === 'success' && data.companies && data.companies.length > 0) {
      searchResults.value = data.companies;
      console.log('找到公司:', data.companies);
      // 自动定位到第一个结果
      await locateCompany(data.companies[0]);
      ElMessage.success(`找到 ${data.companies.length} 个匹配的公司`);
    } else {
      console.log('未找到匹配的公司');
      ElMessage.warning('未找到匹配的公司');
      searchResults.value = [];
    }
  } catch (error) {
    console.error('搜索出错:', error);
    console.error('错误详情:', {
      code: error.code,
      message: error.message,
      response: error.response,
      request: error.request,
      config: error.config
    });
    
    if (error.code === 'ECONNABORTED') {
      ElMessage.error('搜索请求超时，请重试');
    } else if (error.response) {
      const message = error.response.data?.message || '搜索失败，请稍后重试';
      console.error('服务器响应错误:', {
        status: error.response.status,
        statusText: error.response.statusText,
        data: error.response.data,
        headers: error.response.headers
      });
      ElMessage.error(message);
    } else if (error.request) {
      console.error('未收到响应:', error.request);
      ElMessage.error('无法连接到服务器，请检查网络连接');
    } else {
      console.error('请求配置错误:', error.message);
      ElMessage.error('搜索失败，请稍后重试');
    }
    searchResults.value = [];
  }
};

// 监听地图模式切换
watch(is3DMap, async (newVal) => {
  if (newVal) {
    // 切换到3D模式时初始化地图
    await nextTick();
    const mapInstance = init3DMap();
    
    // 如果有搜索结果，重新定位
    if (searchResults.value?.length > 0) {
      handleSearch();
    }
  }
});

// 组件挂载时初始化地图
onMounted(async () => {
  if (is3DMap.value) {
    await nextTick();
    init3DMap();
  }
});

// 处理返回上一级
const handleReturn = () => {
  if (map3d.value) {
    // 重置地图视角
    map3d.value.setZoom(10, {
      duration: 800
    });
    map3d.value.setPitch(0);
    map3d.value.setRotation(0);
    
    // 清除标记
    if (currentMarker.value) {
      map3d.value.remove(currentMarker.value);
      currentMarker.value = null;
    }
    
    // 重置搜索结果
    searchResults.value = [];
    searchKeyword.value = '';
  }
};
// 添加半圆环显示控制变量
const showArcCarousel = ref(true);

// 切换半圆环显示/隐藏状态
const toggleArcCarousel = () => {
  showArcCarousel.value = !showArcCarousel.value;
  // 如果需要停止轮播，也可以在这里控制
  if (!showArcCarousel.value && carouselInterval) {
    clearInterval(carouselInterval);
  } else if (showArcCarousel.value) {
    startCarousel();
  }
};
const showJobRecommendation = ref(false);
const showJobAlert = ref(false);
const showPathPlanning = ref(false);
const jobRecommendationRef = ref(null)
const jobAlertRef = ref(null)

const handleJobRecommend = () => {
  jobRecommendationRef.value.show()
}

const handleJobAlert = () => {
  jobAlertRef.value?.show()
}

const openJobRecommendation = () => {
     showJobRecommendation.value = true;
     handleJobRecommend();
}

const openJobAlert = () => {
     showJobAlert.value = true;
     handleJobAlert();
}

const openPathPlanning = () => {
     showPathPlanning.value = true;
     showRoutePlanning();
}
// 添加职业测试弹窗控制变量
const showCareerTestModal = ref(false);

const closeJobRecommendation = () => {
  showJobRecommendation.value = false;
}

const closeJobAlert = () => {
  showJobAlert.value = false;
}

const closePathPlanning = () => {
  showPathPlanning.value = false;
}
// 添加职业测试相关变量
const currentTest = ref(null);

// 添加职业测试相关函数
const startTest = (testType) => {
  currentTest.value = testType;
  showCareerTestModal.value = true;
};

// 添加AI面试打开函数
const openAiInterview = () => {
  window.open('http://127.0.0.1:5333', '_blank');
};

// 添加职业测试URL获取函数
const getTestUrl = (testType) => {
  switch (testType) {
    case 'valueTest':
      return 'https://c.chameiwang.com/theme/426.html';
    case 'careerAnchor':
      return 'https://types.yuzeli.com/survey/anchors';
    case 'bigFive':
      return 'https://www.luomashu.com/tests/big-five';
    case 'holland':
      return 'https://www.luomashu.com/tests/holland';
    case 'strong':
      return 'http://zyds2.zhuyu01.top/#/questions/HLD?log_id=ae19e28be3f844a29087223f7251c01b&swid=zycc&sou=wzzy2&pt=direct&bd_vid=7096925869313431574';
    case 'mbti':
      return 'https://www.luomashu.com/tests/mbti';
    default:
      return 'https://www.luomashu.com/tests/enneagram';
  }
};

// 添加职业测试相关函数
const openCareerTest = () => {
  showCareerTestModal.value = true;
};

// 获取测试名称的函数
const getTestName = (testType) => {
  switch (testType) {
    case 'valueTest':
      return '职业价值观测评';
    case 'careerAnchor':
      return '职业锚测评';
    case 'bigFive':
      return '大五人格测验';
    case 'holland':
      return '霍兰德职业兴趣测评';
    case 'strong':
      return '斯特朗职业兴趣量表';
    case 'mbti':
      return 'MBTI性格类型测试';
    default:
      return '九型人格测试';
  }
};

const routeDialogRef = ref(null)

const showRoutePlanning = () => {
  routeDialogRef.value.show()
}

// 添加setupAMap函数 - 用于解决"setupAMap is not defined"错误
const setupAMap = () => {
  // 延迟初始化高德地图
  setTimeout(() => {
    // 尝试初始化3D地图
    initAMap();
  }, 1000);
};

// 添加调试辅助函数 - 在控制台中可以手动调用
window.refreshJobChart = (provinceName) => {
  if (!provinceName) {
    provinceName = currentArea.value.name || '上海';
  }
  console.log(`手动刷新${provinceName}图表...`);
  loadJobTimelineData(provinceName);
};

// 添加调试辅助函数 - 在控制台中可以手动调用
window.forceRedrawJobChart = () => {
  const container = jobTimelineChart.value;
  if (!container) {
    console.error('图表容器不存在');
    return;
  }
  
  // 强制重绘
  if (jobChartInstance) {
    jobChartInstance.dispose();
  }
  
  console.log('强制重绘职位图表...');
  setTimeout(() => {
    jobChartInstance = echarts.init(container);
    jobChartInstance.setOption({
      backgroundColor: 'transparent',
      grid: {
        left: '5%',
        right: '5%',
        top: '10%',
        bottom: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: ['1月', '2月', '3月', '4月', '5月', '6月'],
        axisLine: { lineStyle: { color: 'rgba(0, 198, 255, 0.5)' } },
        axisLabel: { color: '#fff' }
      },
      yAxis: {
        type: 'value',
        name: '职位数量',
        axisLine: { lineStyle: { color: 'rgba(0, 198, 255, 0.5)' } },
        splitLine: { lineStyle: { color: 'rgba(0, 198, 255, 0.15)' } },
        axisLabel: { color: '#fff' }
      },
      series: [{
        name: '职位数量',
        type: 'line',
        data: [500, 800, 1200, 1000, 1500, 1800],
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: {
          width: 3,
          color: 'rgba(0, 255, 255, 1)'
        },
        itemStyle: { color: '#00c6ff' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(0, 255, 255, 0.4)' },
              { offset: 1, color: 'rgba(51, 102, 255, 0.1)' }
            ]
          }
        }
      }]
    });
    console.log('职位图表重绘完成');
  }, 100);
};

// 添加全局调试辅助函数，帮助用户排查问题
window.debugArea = () => {
  console.log('===== 地图状态调试 =====');
  console.log('当前场景:', app?.currentScene);
  console.log('当前区域:', currentArea.value);
  console.log('面板可见性:', panelVisibility);
  console.log('图表初始化状态:', jobTimelineInitialized);
  
  // 检查当前CSV文件是否存在
  if (currentArea.value && currentArea.value.name) {
    const provinceName = currentArea.value.name;
    console.log(`测试访问 ${provinceName} 的CSV文件...`);
    
    fetch(`/职业动态时间图/${provinceName}_monthly_stats.csv`)
      .then(response => {
        if (response.ok) {
          console.log(`✅ 文件存在，状态码: ${response.status}`);
          return response.text();
        } else {
          console.error(`❌ 文件不存在或无法访问，状态码: ${response.status}`);
          throw new Error('文件不存在');
        }
      })
      .then(text => {
        console.log('文件内容预览:', text.substring(0, 200));
      })
      .catch(err => {
        console.error('文件访问出错:', err);
      });
  }
};

// 薪资范围与工作年限散点图数据加载函数
const loadSalaryExperienceData = async (provinceName) => {
  try {
    console.log(`★★★ 开始加载${provinceName}的薪资与工作年限数据 ★★★`);
    
    // 确认省份名称和格式
    if (!provinceName) {
      console.warn('⚠️ 未提供省份名称，使用默认值');
      provinceName = '上海'; // 默认值
    } else {
      // 输出确切的省份名称，以便检查格式和空格
      console.log(`省份名称: "${provinceName}" (长度: ${provinceName.length})`);
    }
    
    // 确保DOM已经完全渲染
    await nextTick();
    
    // 等待一小段时间确保容器尺寸已经计算完成
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // 使用默认数据
    const defaultData = {
      experience: [0, 0, 1, 1, 3, 3, 5, 5, 10, 10],
      salary: [5000, 8000, 8000, 12000, 15000, 18000, 20000, 25000, 30000, 35000]
    };
    
    // 确保容器存在且有尺寸
    if (!salaryExperienceChart.value) {
      console.error('❌ 薪资范围与工作年限散点图表容器未找到');
      return;
    }

    // 强制设置容器尺寸
    const container = salaryExperienceChart.value;
    container.style.width = '100%';
    container.style.height = '380px';
    
    try {
      // 使用规范化函数获取标准省份名称
      const fileProvinceName = normalizeProvinceName(provinceName);
      if (fileProvinceName !== provinceName) {
        console.log(`省份名称规范化: "${provinceName}" → "${fileProvinceName}"`);
      }
      
      // 构建准确的CSV文件路径
      const csvPath = `/薪资范围与工作年限散点图/${fileProvinceName}_processed.csv`;
      console.log(`🔍 尝试加载CSV文件: "${csvPath}"`);
      
      // 使用fetch加载数据
      const response = await fetch(csvPath);
      console.log(`📊 文件请求状态: ${response.status} ${response.statusText}`);
      
      if (response.ok) {
        const csvText = await response.text();
        console.log('CSV文件内容预览:', csvText.substring(0, 100) + '...');
        
        // 解析CSV数据
        const rows = csvText.trim().split('\n');
        const headers = rows[0].split(',');
        const expIndex = headers.findIndex(h => h.trim() === 'experience_years');
        const salaryIndex = headers.findIndex(h => h.trim() === 'salary_numeric');
        
        if (expIndex === -1 || salaryIndex === -1) {
          console.warn(`CSV格式不匹配，使用默认数据`);
          drawSalaryExperienceChart(defaultData.experience, defaultData.salary);
          return;
        }
        
        // 存储解析后的数据
        const data = {
          experience: [],
          salary: []
        };
        
        // 随机抽取200条数据
        let allRows = [];
        for (let i = 1; i < rows.length; i++) {
          const cols = rows[i].split(',');
          if (cols.length > Math.max(expIndex, salaryIndex)) {
            const expValue = parseFloat(cols[expIndex]);
            const salaryValue = parseFloat(cols[salaryIndex]);
            
            if (!isNaN(expValue) && !isNaN(salaryValue) && salaryValue > 0) {
              allRows.push({
                experience: expValue,
                salary: salaryValue
              });
            }
          }
        }
        
        // 随机抽样或使用全部数据
        let sampleRows = allRows;
        if (allRows.length > 200) {
          // 随机抽样200条数据
          sampleRows = [];
          const indices = new Set();
          while (indices.size < 200) {
            indices.add(Math.floor(Math.random() * allRows.length));
          }
          
          // 根据索引获取抽样数据
          indices.forEach(idx => {
            sampleRows.push(allRows[idx]);
          });
        }
        
        // 提取数据到数组
        sampleRows.forEach(row => {
          data.experience.push(row.experience);
          data.salary.push(row.salary);
        });
        
        if (data.experience.length > 0) {
          console.log(`成功解析${provinceName}的薪资与工作年限数据:`, {
            count: data.experience.length,
            sampleData: data.experience.slice(0, 5).map((exp, i) => ({ 
              experience: exp, 
              salary: data.salary[i] 
            }))
          });
          drawSalaryExperienceChart(data.experience, data.salary);
        } else {
          console.warn(`${provinceName}数据为空，使用默认数据`);
          drawSalaryExperienceChart(defaultData.experience, defaultData.salary);
        }
      } else {
        console.warn(`加载${provinceName}的CSV文件失败，状态码:`, response.status);
        
        // 尝试其他可能的文件名格式 (原始名称)
        console.log(`尝试使用原始省份名称加载: "${provinceName}"`);
        const alternativePath = `/薪资范围与工作年限散点图/${provinceName}_processed.csv`;
        
        try {
          const altResponse = await fetch(alternativePath);
          
          if (altResponse.ok) {
            // 处理成功加载的情况，代码类似上面的处理逻辑
            // ...
            const csvText = await altResponse.text();
            // 这里重复上面的解析逻辑
            // ...
          } else {
            // 尝试第三种可能的文件名格式 - 使用前两个字符
            if (provinceName.length > 2) {
              const shortName = provinceName.substring(0, 2);
              console.log(`尝试使用简化名称加载: "${shortName}"`);
              const shortPath = `/薪资范围与工作年限散点图/${shortName}_processed.csv`;
              
              const shortResponse = await fetch(shortPath);
              
              if (shortResponse.ok) {
                // 处理成功加载的情况
                // ...
              } else {
                console.warn(`所有尝试都失败，使用默认数据`);
                drawSalaryExperienceChart(defaultData.experience, defaultData.salary);
              }
            } else {
              drawSalaryExperienceChart(defaultData.experience, defaultData.salary);
            }
          }
        } catch (error) {
          console.warn(`尝试备选路径时出错:`, error);
          drawSalaryExperienceChart(defaultData.experience, defaultData.salary);
        }
      }
    } catch (error) {
      console.warn(`加载${provinceName}的薪资与工作年限数据失败:`, error);
      // 使用默认数据作为后备方案
      drawSalaryExperienceChart(defaultData.experience, defaultData.salary);
    }
  } catch (error) {
    console.error('初始化薪资与工作年限散点图表失败:', error);
  }
};

// 薪资与工作年限散点图绘制函数
const drawSalaryExperienceChart = (experience, salary) => {
  if (!salaryExperienceChart.value) {
    console.error('薪资与工作年限散点图表容器未找到');
    return;
  }
  
  // 确保容器尺寸正确
  const container = salaryExperienceChart.value;
  if (container.clientWidth === 0 || container.clientHeight === 0) {
    console.warn('图表容器尺寸为零，强制设置尺寸');
    container.style.width = '100%';
    container.style.height = '380px';
  }
  
  console.log('图表容器尺寸:', {
    width: container.clientWidth,
    height: container.clientHeight,
    offsetWidth: container.offsetWidth,
    offsetHeight: container.offsetHeight
  });
  
  // 销毁旧的实例
  if (salaryChartInstance) {
    salaryChartInstance.dispose();
  }
  
  // 使用setTimeout延迟创建实例，确保DOM已经完全渲染
  setTimeout(() => {
    try {
      // 创建新的实例
      salaryChartInstance = echarts.init(container);
      
      // 组合数据点
      const dataPoints = experience.map((exp, index) => ([exp, salary[index]]));
      
      const option = {
        backgroundColor: 'transparent',
        grid: {
          left: '5%',
          right: '5%',
          top: '10%',
          bottom: '10%',
          containLabel: true
        },
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(6, 23, 46, 0.8)',
          borderColor: 'rgba(0, 198, 255, 0.3)',
          textStyle: {
            color: '#fff'
          },
          formatter: function(params) {
            return `工作年限: ${params.value[0]} 年<br/>薪资: ${params.value[1]} 元`;
          }
        },
        xAxis: {
          type: 'category',  // 改为类别轴
          data: [0, 1, 3, 5, 10],  // 只显示这几个特定刻度
          name: '工作年限',
          axisLabel: {
            color: 'rgba(255, 255, 255, 0.7)',
            formatter: function(value) {
              if (value == 0) return '无经验';
              if (value == 1) return '1-3年';
              if (value == 3) return '3-5年';
              if (value == 5) return '5-10年';
              if (value == 10) return '10年+';
              return value;
            }
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(0, 198, 255, 0.5)'
            }
          },
          splitLine: {
            lineStyle: {
              color: 'rgba(0, 198, 255, 0.15)'
            }
          }
        },
        yAxis: {
          type: 'value',
          name: '薪资（元）',
          nameTextStyle: {
            color: 'rgba(255, 255, 255, 0.7)'
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(0, 198, 255, 0.5)'
            }
          },
          splitLine: {
            lineStyle: {
              color: 'rgba(0, 198, 255, 0.15)'
            }
          },
          axisLabel: {
            color: 'rgba(255, 255, 255, 0.7)'
          }
        },
        series: [{
          name: '薪资与工作年限',
          type: 'scatter',
          data: dataPoints,
          symbol: 'circle',
          symbolSize: 10,
          itemStyle: {
            color: function(params) {
              // 根据薪资值设置不同的颜色
              const salary = params.value[1];
              if (salary < 10000) {
                return 'rgba(51, 204, 255, 0.8)'; // 低薪资
              } else if (salary < 20000) {
                return 'rgba(51, 255, 153, 0.8)'; // 中薪资
              } else {
                return 'rgba(255, 204, 0, 0.8)'; // 高薪资
              }
            },
            shadowBlur: 10,
            shadowColor: 'rgba(0, 198, 255, 0.5)'
          }
        }]
      };
      
      // 设置图表选项
      salaryChartInstance.setOption(option);
      console.log('薪资与工作年限散点图表绘制完成');
      
      // 创建ResizeObserver监听容器尺寸变化
      const resizeObserver = new ResizeObserver(() => {
        if (salaryChartInstance) {
          console.log('容器尺寸变化，重新调整图表大小');
          salaryChartInstance.resize();
        }
      });
      resizeObserver.observe(container);
      
      // 另外再添加窗口大小变化的监听
      window.addEventListener('resize', () => {
        if (salaryChartInstance) {
          salaryChartInstance.resize();
        }
      });
      
      // 强制触发一次resize，解决一些渲染问题
      setTimeout(() => {
        if (salaryChartInstance) {
          salaryChartInstance.resize();
        }
      }, 200);
    } catch (error) {
      console.error('创建薪资与工作年限图表实例失败:', error);
    }
  }, 300); // 使用300ms延迟确保DOM已渲染
};

// 薪资范围分布的职位数量图表绘制函数
const drawSalaryCountsChart = (salaryRanges, jobCounts) => {
  const container = salaryCountsChart.value;
  if (!container) {
    console.warn('薪资范围分布图表容器未找到');
    return;
  }

  // 确保容器尺寸正确
  if (container.clientWidth === 0 || container.clientHeight === 0) {
    console.warn('薪资图表容器尺寸为零，强制设置尺寸');
    container.style.width = '100%';
    container.style.height = '380px';
  }

  console.log('薪资图表容器尺寸:', {
    width: container.clientWidth,
    height: container.clientHeight,
    offsetWidth: container.offsetWidth,
    offsetHeight: container.offsetHeight
  });

  // 销毁旧的实例
  if (salaryCountsChartInstance) {
    salaryCountsChartInstance.dispose();
  }
  
  // 使用setTimeout延迟创建实例，确保DOM已经完全渲染
  setTimeout(() => {
    try {
      // 创建新的实例
      salaryCountsChartInstance = echarts.init(container);
      
      const option = {
        backgroundColor: 'transparent',
        grid: {
          left: '5%',
          right: '5%',
          top: '10%',
          bottom: '10%',
          containLabel: true
        },
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(6, 23, 46, 0.8)',
          borderColor: 'rgba(0, 198, 255, 0.3)',
          textStyle: {
            color: '#fff'
          },
          formatter: function(params) {
            return `薪资范围: ${params[0].name}<br/>职位数量: ${params[0].value}`;
          }
        },
        xAxis: {
          type: 'category',
          data: salaryRanges,
          name: '薪资范围',
          axisLabel: {
            color: 'rgba(255, 255, 255, 0.7)',
            interval: 0,
            rotate: 45
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(0, 198, 255, 0.5)'
            }
          },
          splitLine: {
            lineStyle: {
              color: 'rgba(0, 198, 255, 0.15)'
            }
          }
        },
        yAxis: {
          type: 'value',
          name: '职位数量',
          nameTextStyle: {
            color: 'rgba(255, 255, 255, 0.7)'
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(0, 198, 255, 0.5)'
            }
          },
          splitLine: {
            lineStyle: {
              color: 'rgba(0, 198, 255, 0.15)'
            }
          },
          axisLabel: {
            color: 'rgba(255, 255, 255, 0.7)'
          }
        },
        series: [{
          name: '职位数量',
          type: 'bar',
          data: jobCounts,
          itemStyle: {
            color: 'rgba(51, 204, 255, 0.8)',
            shadowBlur: 10,
            shadowColor: 'rgba(0, 198, 255, 0.5)'
          }
        }]
      };
      
      // 设置图表选项
      salaryCountsChartInstance.setOption(option);
      console.log('薪资范围分布的职位数量图表绘制完成');
      
      // 创建ResizeObserver监听容器尺寸变化
      const resizeObserver = new ResizeObserver(() => {
        if (salaryCountsChartInstance) {
          console.log('容器尺寸变化，重新调整图表大小');
          salaryCountsChartInstance.resize();
        }
      });
      resizeObserver.observe(container);
      
      // 另外再添加窗口大小变化的监听
      window.addEventListener('resize', () => {
        if (salaryCountsChartInstance) {
          salaryCountsChartInstance.resize();
        }
      });
      
      // 标记为已初始化
      salaryCountsInitialized = true;
      
      // 强制触发一次resize，解决一些渲染问题
      setTimeout(() => {
        if (salaryCountsChartInstance) {
          salaryCountsChartInstance.resize();
        }
      }, 200);
    } catch (error) {
      console.error('创建薪资范围分布的职位数量图表实例失败:', error);
    }
  }, 300); // 使用300ms延迟确保DOM已渲染
};

// 在组件卸载时清理图表实例
onBeforeUnmount(() => {
  if (salaryCountsChartInstance) {
    salaryCountsChartInstance.dispose();
    salaryCountsChartInstance = null;
  }
});

// 窗口大小变化时调整图表大小
const resizeSalaryCountsChart = () => {
  if (salaryCountsChartInstance) {
    salaryCountsChartInstance.resize();
  }
};

window.addEventListener('resize', resizeSalaryCountsChart);
onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeSalaryCountsChart);
  miniMaxTTS.cleanup();
});
// 处理薪资数据分组的函数
const processSalaryData = (data) => {
  // 预定义的薪资范围
  const predefinedRanges = ['0-5K', '5K-10K', '10K-15K', '15K-20K', '20K-30K', '30K+'];
  const counts = [0, 0, 0, 0, 0, 0]; // 每个范围的计数初始化为0
  
  // 对输入数据进行处理
  data.forEach(item => {
    // 解析薪资范围，提取数字部分
    let rangeStr = item.range;
    let lowerBound = 0;
    
    // 尝试从字符串中提取数字
    const matches = rangeStr.match(/(\d+)/g);
    if (matches && matches.length > 0) {
      lowerBound = parseInt(matches[0], 10) / 1000; // 转换为K单位
    }
    
    // 根据薪资值确定应该放入哪个范围
    if (lowerBound < 5) {
      counts[0] += item.count;
    } else if (lowerBound < 10) {
      counts[1] += item.count;
    } else if (lowerBound < 15) {
      counts[2] += item.count;
    } else if (lowerBound < 20) {
      counts[3] += item.count;
    } else if (lowerBound < 30) {
      counts[4] += item.count;
    } else {
      counts[5] += item.count;
    }
  });
  
  return {
    salaryRanges: predefinedRanges,
    counts: counts
  };
};

// 加载薪资范围分布数据的函数
const loadSalaryCountsData = async (provinceName) => {
  try {
    // 进行省份名称规范化
    const normalizedProvinceName = normalizeProvinceName(provinceName);
    console.log(`尝试加载${normalizedProvinceName}的薪资范围分布数据`);
    
    // 更新标题
    salaryCountsTitle.value = `${normalizedProvinceName}薪资范围分布的职位数量`;
    
    // 显示面板
    panelVisibility.panel3 = true;
    
    // 获取图表容器
    const container = salaryCountsChart.value;
    if (!container) {
      console.warn('薪资范围分布图表容器未找到，使用备选方案');
      // 尝试使用DOM查询获取容器
      const domContainer = document.getElementById('salaryCounts');
      if (domContainer) {
        console.log('通过DOM查询找到了图表容器');
        // 使用模拟数据直接绘制图表
        useMockDataForChart(normalizedProvinceName, domContainer);
        return;
      } else {
        console.error('图表容器完全未找到');
        // 等待DOM渲染后重试
        setTimeout(() => {
          const retryContainer = document.getElementById('salaryCounts');
          if (retryContainer) {
            useMockDataForChart(normalizedProvinceName, retryContainer);
          }
        }, 500);
        return;
      }
    }
    
    // 尝试从服务器读取CSV数据
    const csvUrl = `/薪资范围分布的职位数量/${normalizedProvinceName}_salary_counts.csv`;
    console.log('请求CSV文件:', csvUrl);
    
    try {
      const response = await fetch(csvUrl);
      if (!response.ok) {
        throw new Error(`CSV文件请求失败: ${response.status}`);
      }
      
      const csvText = await response.text();
      console.log('CSV数据预览:', csvText.substring(0, 100));
      
      // 解析CSV数据
      const rows = csvText.trim().split('\n');
      const headers = rows[0].split(',');
      const salaryRangeIndex = headers.findIndex(h => h.trim() === '岗位薪资');
      const jobCountIndex = headers.findIndex(h => h.trim() === '数量');
      
      if (salaryRangeIndex === -1 || jobCountIndex === -1) {
        console.warn(`CSV格式不匹配，使用默认数据`);
        const defaultData = {
          salaryRanges: ['0-5K', '5K-10K', '10K-15K', '15K-20K', '20K-30K', '30K+'],
          counts: [120, 350, 280, 150, 80, 40]
        };
        drawSalaryCountsChart(defaultData.salaryRanges, defaultData.counts);
        return;
      }
      
      // 提取数据
      const data = rows.slice(1).map(row => {
        const cols = row.split(',');
        return {
          range: cols[salaryRangeIndex].trim(),
          count: parseInt(cols[jobCountIndex].trim(), 10)
        };
      }).filter(item => !isNaN(item.count));
      
      console.log('解析后的薪资范围数据:', data);
      
      // 处理数据分组
      const processed = processSalaryData(data);
      
      // 绘制图表
      drawSalaryCountsChart(processed.salaryRanges, processed.counts);
      
    } catch (error) {
      console.error('加载薪资范围分布数据失败:', error);
      console.log('尝试使用模拟数据回退方案');
      useMockDataForChart(normalizedProvinceName, container);
    }
  } catch (error) {
    console.error(`初始化薪资范围分布的职位数量图表失败:`, error);
    // 最后的回退方案
    setTimeout(() => {
      const container = document.getElementById('salaryCounts');
      if (container) {
        useMockDataForChart(normalizedProvinceName, container);
      }
    }, 1000);
  }
};

// 使用模拟数据绘制图表的辅助函数
const useMockDataForChart = (provinceName, container) => {
  console.log(`使用模拟数据绘制${provinceName}的薪资范围分布图表`);
  
  // 更新标题
  salaryCountsTitle.value = `${provinceName}薪资范围分布的职位数量`;
  
  // 更新标题文本
  const titleElement = document.querySelector('.region-box-3 .holo-header h2');
  if (titleElement) {
    titleElement.textContent = `${provinceName}薪资范围分布的职位数量`;
  }
  
  // 模拟CSV数据
  const mockData = [
    { range: '5000-8000', count: 120 },
    { range: '8000-12000', count: 350 },
    { range: '12000-15000', count: 280 },
    { range: '15000-20000', count: 150 },
    { range: '20000-30000', count: 80 },
    { range: '30000-50000', count: 40 }
  ];
  
  // 处理数据分组
  const processed = window.processSalaryData ? window.processSalaryData(mockData) : {
    salaryRanges: ['0-5K', '5K-10K', '10K-15K', '15K-20K', '20K-30K', '30K+'],
    counts: [120, 350, 280, 150, 80, 40]
  };
  
  // 销毁旧实例
  if (window.salaryCountsChartInstance) {
    window.salaryCountsChartInstance.dispose();
  }
  
  // 创建新实例
  window.salaryCountsChartInstance = echarts.init(container);
  
  // 配置选项
  const option = {
    backgroundColor: 'transparent',
    grid: { left: '5%', right: '5%', top: '10%', bottom: '15%', containLabel: true },
    tooltip: { 
      trigger: 'axis',
      backgroundColor: 'rgba(6, 23, 46, 0.8)',
      borderColor: 'rgba(0, 198, 255, 0.3)',
      textStyle: { color: '#fff' },
      formatter: function(params) {
        return `薪资范围: ${params[0].name}<br/>职位数量: ${params[0].value}`;
      }
    },
    xAxis: { 
      type: 'category', 
      data: processed.salaryRanges,
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.7)',
        interval: 0,
        rotate: 45
      }
    },
    yAxis: { 
      type: 'value', 
      name: '职位数量',
      axisLabel: { color: 'rgba(255, 255, 255, 0.7)' }
    },
    series: [{
      name: '职位数量',
      type: 'bar',
      data: processed.counts,
      itemStyle: { 
        color: 'rgba(51, 204, 255, 0.8)',
        shadowBlur: 10,
        shadowColor: 'rgba(0, 198, 255, 0.5)'
      }
    }]
  };
  
  // 设置选项
  window.salaryCountsChartInstance.setOption(option);
  console.log('薪资范围分布图表绘制完成（使用模拟数据）');
  
  // 显示面板
  if (typeof panelVisibility !== 'undefined') {
    panelVisibility.panel3 = true;
  }
};

// 优化drawJobTimelineChart函数
// ... existing code ...
</script>

<style lang="scss">

/* 添加新的子地图模块框样式 */
.region-box {
  width: 500px;
  height: 500px;
  max-height: 500px;
  opacity: 1 !important;
  transform: none !important;
  transition: box-shadow 0.3s ease-in-out !important;
  border: 1px solid rgba(0, 198, 255, 0.4);
  box-shadow: 0 0 15px rgba(0, 198, 255, 0.2);
  position: absolute;
  
  &:hover {
    box-shadow: 0 0 20px rgba(0, 198, 255, 0.4);
  }
  
  /* 定位三个模块框 */
  &.region-box-1 {
    top: 120px;
    left: 500px;
    z-index: 100;
  }
  
  &.region-box-2 {
    top: 120px;
    right: 480px;
    z-index: 100;
  }
  
  &.region-box-3 {
    bottom: 100px;
    left: 500px;
    z-index: 100;
  }
  
  .holo-content {
    height: 400px !important; // 确保内容区域有足够高度
    overflow: hidden !important; // 防止出现滚动条
    padding: 10px;
    position: relative;
    
    #jobTimelineChart {
      width: 100% !important;
      height: 100% !important;
      min-height: 380px !important; // 设置最小高度
    }
  }

  .holo-header h2 {
    font-size: 16px;
  }
  
  .section-header h3 {
    font-size: 14px;
  }
  
  .item-header {
    font-size: 13px;
  }
  
  .item-body {
    font-size: 12px;
    line-height: 1.5;
  }
}

.career-test-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.modal-content {
  background: rgba(4, 19, 36, 0.95);
  border: 1px solid #0e4b80;
  border-radius: 8px;
  width: 90%;
  height: 90%;
  max-width: 1200px;
  position: relative;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 15px 20px;
  border-bottom: 1px solid rgba(14, 75, 128, 0.5);
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #fff;
}
/* 添加右侧控制栏样式 */
.control-panels {
  position: fixed;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 15px;
  z-index: 1000;
}

.control-panel-btn {
  width: 48px;
  height: 48px;
  background: rgba(6, 23, 46, 0.7);
  border: 1px solid rgba(0, 198, 255, 0.6);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(0, 198, 255, 0.9);
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 0 10px rgba(0, 198, 255, 0.2);
  position: relative;
  
  &:hover {
    background: rgba(6, 23, 46, 0.9);
    box-shadow: 0 0 15px rgba(0, 198, 255, 0.4);
    transform: translateX(-5px);
  }
  
  &.active {
    background: rgba(0, 198, 255, 0.3);
    color: #fff;
    border: 1px solid rgba(0, 198, 255, 1);
    
    &::before {
      content: '';
      position: absolute;
      top: 50%;
      right: -12px;
      transform: translateY(-50%);
      border-left: 12px solid rgba(0, 198, 255, 0.8);
      border-top: 6px solid transparent;
      border-bottom: 6px solid transparent;
    }
  }
  
  svg {
    width: 20px;
    height: 20px;
    filter: drop-shadow(0 0 2px rgba(0, 198, 255, 0.5));
  }
}

.modal-body {
  flex: 1;
  overflow: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  position: relative;
  min-height: 0;
  
  > div {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
}

.test-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  padding: 20px;
  overflow-y: auto;
  height: 100%;
}

.test-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  
  iframe {
    flex: 1;
    width: 100%;
    height: 100%;
    border: none;
    background: #fff;
    border-radius: 4px;
  }
}

.test-item {
  background: rgba(14, 75, 128, 0.3);
  border: 1px solid rgba(14, 75, 128, 0.5);
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  h3 {
    color: #00a0e9;
    margin: 0 0 10px 0;
    font-size: 18px;
  }
  
  p {
    color: #fff;
    margin: 0;
    font-size: 14px;
    opacity: 0.8;
  }
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 160, 233, 0.2);
    background: rgba(14, 75, 128, 0.5);
  }
}

@keyframes pulse {
  0% { opacity: 0.3; }
  50% { opacity: 0.7; }
  100% { opacity: 0.3; }
}
.test-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr); /* 每行3个 */
  grid-gap: 20px;
  padding: 20px;
  overflow-y: auto;
  max-height: calc(100vh - 200px); /* 限制最大高度，确保在小屏幕上可滚动 */
}

.test-item {
  /* 减小每个测试项的大小，使更多内容可见 */
  height: 180px;
  padding: 15px;
}
.map-level {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;

  #canvas {
    width: 100%;
    height: 100%;
    background: #000;
  }
}

/* 使用CSS变量定义基础尺寸 */
:root {
  --base-spacing: clamp(8px, 1vw, 20px);
  --chart-width: clamp(250px, 25vw, 400px);
  --chart-height: clamp(200px, 30vh, 400px);
}

/* 响应式表格布局 */
.table {
  position: absolute;
  z-index: 10; /* 确保图表显示在地图上层 */
  width: var(--chart-width);
  height: var(--chart-height);
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid #2bc4dc;
  padding: 0;
  font-size: clamp(12px, 1vw, 14px);
  color: #fff;
  text-align: center;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  transition: all 0.3s ease;
  
  .chart-container {
    flex: 1;
    padding: var(--base-spacing);
    min-height: 0;
  }
}

/* 表格位置调整 */
.left-table {
  &.top {
    left: var(--base-spacing);
    top: var(--base-spacing);
  }
  &.bottom {
    left: var(--base-spacing);
    bottom: var(--base-spacing);
  }
}

.right-table {
  &.top {
    right: var(--base-spacing);
    top: var(--base-spacing);
  }
  &.bottom {
    right: 100px;
    bottom: 80px;
    width: 240px !important;
    height: 580px !important;
    background: rgba(0, 0, 0, 0.5);
    border-radius: 8px;
    overflow: hidden;
    display: flex !important;
    flex-direction: column !important;
    z-index: 1000;
  }
}

/* 聊天窗口样式 */
.chat-window {
  display: flex !important;
  flex-direction: column !important;
  width: 100% !important;
  height: 100% !important;
  background: transparent;
  z-index: 1001;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  height: calc(100% - 50px);
  min-height: 0;
  background: rgba(0, 0, 0, 0.3);
}

.message {
  padding: 8px 12px;
  border-radius: 6px;
  max-width: 95%;
  word-break: break-word;
  font-size: 12px;
  line-height: 1.5;
  margin: 4px 0;

  &.user {
    align-self: flex-end;
    background: rgba(43, 196, 220, 0.25);
    color: #fff;
    border: 1px solid rgba(43, 196, 220, 0.4);
  }

  &.ai {
    align-self: flex-start;
    background: rgba(255, 255, 255, 0.15);
    color: #fff;
    border: 1px solid rgba(255, 255, 255, 0.3);
    white-space: pre-wrap;
  }

  &.error {
    align-self: center;
    background: rgba(255, 0, 0, 0.15);
    color: #ff4444;
    border: 1px solid rgba(255, 0, 0, 0.3);
  }
}

/* 显示聊天输入框 */
.chat-input {
  display: flex !important;
  height: 50px;
  min-height: 50px;
  padding: 8px;
  background: rgba(0, 0, 0, 0.3);
  border-top: 1px solid rgba(43, 196, 220, 0.3);
  gap: 8px;
  margin-top: auto;

  input {
    flex: 1;
    min-width: 0;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(43, 196, 220, 0.3);
    border-radius: 4px;
    padding: 6px 10px;
    color: #fff;
    font-size: 12px;

    &::placeholder {
      color: rgba(255, 255, 255, 0.5);
    }

    &:focus {
      outline: none;
      border-color: rgba(43, 196, 220, 0.6);
    }
  }

  button {
    background: rgba(43, 196, 220, 0.2);
    border: 1px solid rgba(43, 196, 220, 0.3);
    color: #fff;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s;
    font-size: 12px;
    white-space: nowrap;

    &:hover {
      background: rgba(43, 196, 220, 0.3);
    }
  }
}

/* 右侧按钮组样式 */
.map-btn-group {
  position: fixed;
  right: 20px;
  top: 45%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 6px;
  z-index: 99;

  .btn {
    padding: 6px 10px;
    color: #fff;
    border: 1px solid #2bc4dc;
    font-size: 11px;
    min-width: 50px;
    text-align: center;
    white-space: nowrap;
    opacity: 0.7;
    cursor: pointer;
    transition: all 0.3s;
    background: rgba(0, 0, 0, 0.5);
    border-radius: 4px;

    &:hover {
      opacity: 1;
      background: rgba(43, 196, 220, 0.2);
    }

    &.active {
      opacity: 1;
      background: rgba(43, 196, 220, 0.2);
    }

    &.career-test-btn {
      background: rgba(0, 32, 12, 0.85);
      color: #00ff9d;
      border-color: #00ff9d;
      
      &:hover, &.active {
        background: rgba(0, 42, 16, 0.95);
        box-shadow: 0 0 10px rgba(0, 255, 157, 0.3);
      }
    }
  }
}

/* 响应式调整 */
@media (max-width: 1280px) {
  .map-btn-group .btn {
    padding: 5px 8px;
    font-size: 10px;
    min-width: 45px;
  }
}

@media (max-width: 768px) {
  .map-btn-group .btn {
    padding: 4px 6px;
    font-size: 9px;
    min-width: 40px;
  }
}

/* 信息面板响应式调整 */
.info-panel {
  position: absolute;
  width: 280px;
  background: rgba(0, 20, 40, 0.7);
  border: 1px solid #2bc4dc;
  color: #fff;
  padding: 0;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px); /* 添加Safari支持 */
  z-index: 100;
  transition: all 0.3s ease;

  .panel-content {
    max-height: clamp(300px, 50vh, 600px);
    overflow-y: auto;
  }

  @media (max-width: 1280px) {
    width: clamp(200px, 30vw, 300px);
  }

  @media (max-width: 768px) {
    width: clamp(180px, 40vw, 250px);
  }
}

/* 确保所有图表容器都能正确重绘 */
.chart-container {
  width: 100% !important;
  height: 100% !important;
  min-height: 0;
  position: relative;
}

/* 添加全局响应式字体 */
body {
  font-size: clamp(12px, 1vw, 14px);
}

@media (max-width: 1280px) {
  :root {
    --base-spacing: clamp(6px, 0.8vw, 16px);
  }
}

@media (max-width: 768px) {
  :root {
    --base-spacing: clamp(4px, 0.6vw, 12px);
  }
}

/* 每个表原先大小为屏幕的1/3 x 1/3，现在缩放为其2/3 */
.table {
  position: absolute;
  width: calc((100% / 3) * (2 / 3));
  height: calc((100% / 3) * (2 / 3));
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid #2bc4dc;
  padding: 0;
  font-size: 14px;
  color: #fff;
  text-align: center;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  transition: all 0.3s ease; // 添加过渡效果
  
  .chart-container {
    flex: 1;
    padding: 10px;
  }
}

/* 返回按钮 */
.return-btn {
  position: absolute;
  left: 50%;
  bottom: 10px;
  transform: translateX(-50%);
  padding: 5px 24px;
  color: #fff;
  border: 1px solid #2bc4dc;
  margin-bottom: 10px;
  font-size: 12px;
  text-align: center;
  opacity: 0.5;
  display: none;
  cursor: pointer;
  transition: all 0.3s;
  &:hover {
    opacity: 1;
  }
}

/* 以下为原有其他样式 */
.info-point {
  background: rgba(0, 0, 0, 0.5);
  color: #a3dcde;
  font-size: 14px;
  width: 170px;
  height: 106px;
  padding: 16px 12px 0;
  margin-bottom: 30px;
  &-wrap {
    &:after,
    &:before {
      display: block;
      content: "";
      position: absolute;
      top: 0;
      width: 15px;
      height: 15px;
      border-top: 1px solid #4b87a6;
    }
    &:before {
      left: 0;
      border-left: 1px solid #4b87a6;
    }
    &:after {
      right: 0;
      border-right: 1px solid #4b87a6;
    }
    &-inner {
      &:after,
      &:before {
        display: block;
        content: "";
        position: absolute;
        bottom: 0;
        width: 15px;
        height: 15px;
        border-bottom: 1px solid #4b87a6;
      }
      &:before {
        left: 0;
        border-left: 1px solid #4b87a6;
      }
      &:after {
        right: 0;
        border-right: 1px solid #4b87a6;
      }
    }
  }
  &-line {
    position: absolute;
    top: 7px;
    right: 12px;
    display: flex;
    .line {
      width: 5px;
      height: 2px;
      margin-right: 5px;
      background: #17e5c3;
    }
  }
  &-content {
    .content-item {
      display: flex;
      height: 28px;
      line-height: 28px;
      background: rgba(35, 47, 58, 0.6);
      margin-bottom: 5px;
      .label {
        width: 60px;
        padding-left: 10px;
      }
      .value {
        color: #fff;
      }
    }
  }
}
.badges-label {
  z-index: 99999;
  &-outline {
    position: absolute;
  }
  &-wrap {
    position: relative;
    padding: 10px 10px;
    background: #0e1937;
    border: 1px solid #1e7491;
    font-size: 12px;
    font-weight: bold;
    color: #fff;
    bottom: 50px;
    z-index: 99999;
    span {
      color: #ffe70b;
    }
    &:after {
      position: absolute;
      right: 0;
      bottom: 0;
      width: 10px;
      height: 10px;
      display: block;
      content: "";
      border-right: 2px solid #6cfffe;
      border-bottom: 2px solid #6cfffe;
    }
    &:before {
      position: absolute;
      left: 0;
      top: 0;
      width: 10px;
      height: 10px;
      display: block;
      content: "";
      border-left: 2px solid #6cfffe;
      border-top: 2px solid #6cfffe;
    }
    .icon {
      position: absolute;
      width: 27px;
      height: 20px;
      left: 50%;
      transform: translateX(-13px);
      bottom: -40px;
    }
  }
}
.area-name-label {
  &-wrap {
    color: #5fc6dc;
    opacity: 1;
    text-shadow: 1px 1px 0px #000;
  }
}
.provinces-name-label {
  &-wrap {
    color: #5fc6dc;
    opacity: 0;
    text-shadow: 1px 1px 0px #000;
  }
}
.provinces-label-style02 {
  z-index: 2;
  &-wrap {
    transform: translate(0%, 200%);
    opacity: 0;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 40px;
    z-index: 2;
  }
  .number {
    color: #fff;
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 10px;
  }
  .no {
    display: flex;
    justify-content: center;
    align-items: center;
    color: #7efbf6;
    text-shadow: 0 0 5px #7efbf6;
    font-size: 16px;
    width: 30px;
    height: 30px;
    background: rgba(0, 0, 0, 0.5);
    border-radius: 50%;
    border: 2px solid rgba(255, 255, 255, 0.5);
  }
  .yellow {
    .no {
      color: #fef99e !important;
      text-shadow: 0 0 5px #fef99e !important;
    }
  }
}
.fixed-loading {
  position: absolute;
  left: 0;
  top: 0;
  z-index: 99;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(0, 0, 0, 0.5);
}
.page-loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 60px;
  height: 60px;
  background: rgba(0, 0, 0, 0.8);
  border-radius: 10px;
}
.page-loading {
  width: 30px;
  height: 30px;
  border: 2px solid #fff;
  border-top-color: transparent;
  border-radius: 100%;
  animation: loading infinite 0.75s linear;
}

@keyframes loading {
  from {
    transform: rotate(0);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 添加图表头部样式 */
.chart-header {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 8px;
  background: rgba(43, 196, 220, 0.1);
  border-bottom: 1px solid #2bc4dc;
  
  span {
    color: #fff;
    font-size: 14px;
  }
}

/* 独立的切换按钮样式 */
.standalone-btn {
  display: none;
}

/* Chat window styles */
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 4px;
  overflow: hidden;
  z-index: 11;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: calc(100% - 70px);
  min-height: 400px;

  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.2);
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(43, 196, 220, 0.6);
    border-radius: 4px;
  }
}

.message {
  padding: 15px 20px;
  border-radius: 8px;
  max-width: 95%;
  word-break: break-word;
  font-size: 14px;
  line-height: 1.6;
  margin: 8px 0;

  &.user {
    align-self: flex-end;
    background: rgba(43, 196, 220, 0.25);
    color: #fff;
    border: 1px solid rgba(43, 196, 220, 0.4);
  }

  &.ai {
    align-self: flex-start;
    background: rgba(255, 255, 255, 0.15);
    color: #fff;
    border: 1px solid rgba(255, 255, 255, 0.3);
    white-space: pre-wrap;
  }

  &.error {
    align-self: center;
    background: rgba(255, 0, 0, 0.15);
    color: #ff4444;
    border: 1px solid rgba(255, 0, 0, 0.3);
  }
}

.chat-input {
  height: 70px;
  display: flex;
  padding: 15px;
  gap: 12px;
  background: rgba(0, 0, 0, 0.3);
  border-top: 1px solid rgba(43, 196, 220, 0.3);

  input {
    flex: 1;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(43, 196, 220, 0.3);
    border-radius: 6px;
    padding: 12px 16px;
    color: #fff;
    font-size: 14px;

    &::placeholder {
      color: rgba(255, 255, 255, 0.5);
    }

    &:focus {
      outline: none;
      border-color: rgba(43, 196, 220, 0.6);
      box-shadow: 0 0 5px rgba(43, 196, 220, 0.3);
    }
  }

  button {
    background: rgba(43, 196, 220, 0.2);
    border: 1px solid rgba(43, 196, 220, 0.3);
    color: #fff;
    padding: 12px 24px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s;
    font-size: 14px;

    &:hover {
      background: rgba(43, 196, 220, 0.3);
      box-shadow: 0 0 8px rgba(43, 196, 220, 0.4);
    }
  }
}

.info-panel {
  position: absolute;
  width: 280px;
  background: rgba(0, 20, 40, 0.7);
  border: 1px solid #2bc4dc;
  color: #fff;
  padding: 0;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px); /* 添加Safari支持 */
  z-index: 100;
  transition: all 0.3s ease;

  // 定位样式
  &.left-top {
    left: 15%;
    top: 10%;
  }

  .panel-header {
    background: rgba(43, 196, 220, 0.1);
    padding: 12px 20px;
    font-size: 14px;
    color: #2bc4dc;
    border-bottom: 1px solid rgba(43, 196, 220, 0.3);
  }

  .panel-content {
    padding: 15px 20px;
  }

  .info-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 12px;
    font-size: 13px;

    .label {
      color: #a3dcde;
    }

    .value {
      color: #fff;
      font-weight: 500;
    }
  }

  .job-list {
    .job-item {
      display: flex;
      align-items: center;
      padding: 8px 0;
      border-bottom: 1px solid rgba(43, 196, 220, 0.1);

      .rank {
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(43, 196, 220, 0.2);
        border-radius: 4px;
        margin-right: 12px;
        color: #2bc4dc;
        font-size: 12px;
      }

      .job-name {
        flex: 1;
        color: #fff;
      }

      .job-count {
        color: #2bc4dc;
        font-weight: 500;
      }
    }
  }

  // 添加边框装饰
  &::before, &::after {
    content: '';
    position: absolute;
    width: 10px;
    height: 10px;
    border: 2px solid #2bc4dc;
  }

  &::before {
    top: -2px;
    left: -2px;
    border-right: none;
    border-bottom: none;
  }

  &::after {
    bottom: -2px;
    right: -2px;
    border-left: none;
    border-top: none;
  }

  .policy-content {
    color: #fff;
    font-size: 13px;
    line-height: 1.6;
    text-align: justify;
    padding: 15px;
    max-height: 500px; // 增加高度以容纳更多内容
    overflow-y: auto;
    
    .section-title {
      color: #2bc4dc;
      font-size: 15px;
      font-weight: bold;
      margin: 15px 0 10px;
      border-bottom: 1px solid rgba(43, 196, 220, 0.3);
      padding-bottom: 5px;
    }

    .condition-item {
      margin-bottom: 15px;
      
      .item-title {
        color: #a3dcde;
        font-weight: bold;
        margin-bottom: 5px;
      }
      
      .item-content {
        color: rgba(255, 255, 255, 0.9);
        padding-left: 10px;
      }
    }

    .benefit-list {
      .benefit-item {
        margin-bottom: 10px;
        
        .benefit-title {
          color: #a3dcde;
          font-weight: bold;
        }
      }
    }

    &::-webkit-scrollbar {
      width: 4px;
    }
    
    &::-webkit-scrollbar-track {
      background: rgba(0, 0, 0, 0.1);
    }
    
    &::-webkit-scrollbar-thumb {
      background: rgba(43, 196, 220, 0.5);
      border-radius: 2px;
    }
  }

  // 调整面板宽度，使其更适合显示政策文本
  &.left-top {
    width: 280px; // 增加宽度以更好地显示内容
    max-height: 600px; // 设置最大高度
  }

  .subsidy-list {
    padding: 10px;
    
    .subsidy-item {
      margin-bottom: 15px;
      padding: 10px;
      border-radius: 4px;
      background: rgba(43, 196, 220, 0.1);
      border: 1px solid rgba(43, 196, 220, 0.2);
      
      &:hover {
        background: rgba(43, 196, 220, 0.2);
        border-color: rgba(43, 196, 220, 0.3);
      }
      
      .subsidy-title {
        color: #2bc4dc;
        font-weight: bold;
        margin-bottom: 5px;
        font-size: 14px;
      }
      
      .subsidy-content {
        color: rgba(255, 255, 255, 0.9);
        font-size: 13px;
        line-height: 1.5;
      }
    }
  }

  .no-data {
    text-align: center;
    color: rgba(255, 255, 255, 0.6);
    padding: 20px;
    font-size: 14px;
  }
}
//输入框位置调整
/* 添加新的固定聊天输入框样式 */
.fixed-chat-input {
  position: fixed;
  right: 100px;
  bottom: 15px;
  width: 220px;
  height: 40px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 10px;
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid rgba(43, 196, 220, 0.5);
  border-radius: 6px;
  z-index: 9999; /* 提高z-index确保在其他元素之上 */

  input {
    flex: 1;
    height: 30px;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(43, 196, 220, 0.3);
    border-radius: 4px;
    padding: 0 10px;
    color: #fff;
    font-size: 12px;
    pointer-events: auto; /* 确保输入框可以点击 */

    &::placeholder {
      color: rgba(255, 255, 255, 0.5);
    }

    &:focus {
      outline: none;
      border-color: rgba(43, 196, 220, 0.6);
    }
  }

  button {
    height: 30px;
    background: rgba(43, 196, 220, 0.2);
    border: 1px solid rgba(43, 196, 220, 0.3);
    color: #fff;
    padding: 0 7.5px;  /* 增加水平内边距 */
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s;
    font-size: 12px;
    white-space: nowrap;
    pointer-events: auto; /* 确保按钮可以点击 */

    &:hover {
      background: rgba(43, 196, 220, 0.3);
    }
  }
}

/* 移除 scoped，确保样式可以正确应用 */
.hologram-panel {
  position: absolute;
  width: 400px;
  background: rgba(6, 23, 46, 0.85);
  backdrop-filter: blur(10px);
  border-radius: 4px;
  overflow: hidden;
  z-index: 100;
  box-shadow: 0 0 30px rgba(0, 255, 255, 0.15);
  animation: hologramAppear 0.5s ease-out;

  &.left-top { top: 20px; left: 20px; }
  &.right-top { top: 20px; right: 20px; }

  .holo-frame {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;

    .frame-line {
      position: absolute;
      background: linear-gradient(90deg, 
        rgba(0, 255, 255, 0.3),
        rgba(0, 255, 255, 0.8),
        rgba(0, 255, 255, 0.3)
      );

      &.top, &.bottom {
        height: 1px;
        width: 100%;
        animation: horizontalScan 3s linear infinite;
      }

      &.left, &.right {
        width: 1px;
        height: 100%;
        animation: verticalScan 3s linear infinite;
      }

      &.top { top: 0; }
      &.bottom { bottom: 0; }
      &.left { left: 0; }
      &.right { right: 0; }
    }

    .corner-box {
      position: absolute;
      width: 20px;
      height: 20px;
      border: 2px solid rgba(0, 255, 255, 0.8);
      
      &.tl { top: 0; left: 0; border-right: none; border-bottom: none; }
      &.tr { top: 0; right: 0; border-left: none; border-bottom: none; }
      &.bl { bottom: 0; left: 0; border-right: none; border-top: none; }
      &.br { bottom: 0; right: 0; border-left: none; border-top: none; }
    }
  }

  .holo-header {
    position: relative;
    padding: 15px;
    background: rgba(0, 255, 255, 0.1);

    .header-grid {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-image: 
        linear-gradient(rgba(0, 255, 255, 0.1) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 255, 255, 0.1) 1px, transparent 1px);
      background-size: 10px 10px;
    }

    .header-content {
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 15px;

      h2 {
        color: #00ffff;
        font-size: 20px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 0;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
      }

      .tech-dots {
        display: flex;
        gap: 4px;

        span {
          width: 4px;
          height: 4px;
          background: #00ffff;
          border-radius: 50%;
          animation: dotPulse 1.5s infinite;

          &:nth-child(2) { animation-delay: 0.5s; }
          &:nth-child(3) { animation-delay: 1s; }
        }
      }
    }
  }

  .holo-content {
    padding: 20px;
  max-height: 500px;
    overflow-y: auto;

    &::-webkit-scrollbar {
      width: 4px;
    }

    &::-webkit-scrollbar-track {
      background: rgba(0, 255, 255, 0.1);
    }

    &::-webkit-scrollbar-thumb {
      background: rgba(0, 255, 255, 0.5);
      border-radius: 2px;
    }
    
    // 添加平滑滚动效果
    scroll-behavior: smooth;
    
    // 隐藏滚动条但保持可滚动
    &::-webkit-scrollbar {
      width: 0px;
    }
    
    // 添加渐变遮罩
    mask-image: linear-gradient(
      to bottom,
      transparent 0%,
      black 5%,
      black 95%,
      transparent 100%
    );
    -webkit-mask-image: linear-gradient(
      to bottom,
      transparent 0%,
      black 5%,
      black 95%,
      transparent 100%
    );
  }

  .holo-section {
    margin-bottom: 20px;

    .section-header {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 15px;

      h3 {
        color: #00ffff;
        font-size: 16px;
        font-weight: 500;
        margin: 0;
        text-transform: uppercase;
      }

      .tech-line {
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg,
          transparent,
          rgba(0, 255, 255, 0.5),
          transparent
        );
      }
    }
  }

  .holo-item {
    margin-bottom: 15px;
    background: rgba(0, 255, 255, 0.05);
    border: 1px solid rgba(0, 255, 255, 0.2);
    border-radius: 4px;
    transition: all 0.3s ease;

    &:hover {
      background: rgba(0, 255, 255, 0.1);
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(0, 255, 255, 0.1);

      .tech-icon {
        transform: scale(1.2);
      }
    }

    .item-header {
      padding: 10px 15px;
      color: #00ffff;
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 10px;
      border-bottom: 1px solid rgba(0, 255, 255, 0.2);

      .tech-icon {
        width: 8px;
        height: 8px;
        background: #00ffff;
        clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
        transition: transform 0.3s ease;
      }
    }

    .item-body {
      padding: 15px;
      color: rgba(255, 255, 255, 0.9);
      font-size: 14px;
      line-height: 1.6;
    }
  }

  .scan-line {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg,
      transparent,
      rgba(0, 255, 255, 0.5),
      transparent
    );
    animation: scanLine 3s linear infinite;
    pointer-events: none;
  }

  .holo-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: repeating-linear-gradient(
      0deg,
      rgba(0, 255, 255, 0.03) 0px,
      rgba(0, 255, 255, 0.03) 1px,
      transparent 1px,
      transparent 2px
    );
    pointer-events: none;
  }
}

@keyframes hologramAppear {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes scanLine {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(1000%); }
}

@keyframes horizontalScan {
  0% { transform: scaleX(0); opacity: 0; }
  50% { transform: scaleX(1); opacity: 1; }
  100% { transform: scaleX(0); opacity: 0; }
}

@keyframes verticalScan {
  0% { transform: scaleY(0); opacity: 0; }
  50% { transform: scaleY(1); opacity: 1; }
  100% { transform: scaleY(0); opacity: 0; }
}

@keyframes dotPulse {
  0% { transform: scale(1); opacity: 0.3; }
  50% { transform: scale(1.5); opacity: 1; }
  100% { transform: scale(1); opacity: 0.3; }
}

.hologram-panel {
  // ... 原有样式保持不变 ...

  .no-data {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 30px;
    color: rgba(0, 255, 255, 0.7);
    text-align: center;

    .tech-icon {
      width: 20px;
      height: 20px;
      margin-bottom: 15px;
      border: 2px solid rgba(0, 255, 255, 0.7);
      border-radius: 50%;
      position: relative;
      animation: rotate 2s linear infinite;

      &::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 8px;
        height: 8px;
        background: rgba(0, 255, 255, 0.7);
        transform: translate(-50%, -50%);
        clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
      }
    }

    span {
      font-size: 14px;
      line-height: 1.5;
      text-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
    }
  }

  &.left-middle {
    top: 60%;
    left: 20px;
    transform: translateY(-50%);
    height: 380px; // 添加固定高度
  }

  .holo-content {
    // ... existing styles ...
    max-height: 450px; // 调整内容区域高度，考虑到header和其他元素的高度
  }
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.hologram-panel {
  // ... existing styles ...
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  
  &.panel-enter {
    opacity: 1;
    transform: translateY(0);
  }
  
  // 为每个面板添加不同的延迟
  &.left-top {
    transition-delay: 0.2s;
  }
  
  &.left-middle {
    transition-delay: 0.4s;
  }
  
  &.right-top {
    transition-delay: 0.6s;
  }
  
  // 添加进入动画时的光效
  &.panel-enter::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(
      45deg,
      transparent,
      rgba(0, 255, 255, 0.1),
      transparent
    );
    animation: panelGlow 1.5s ease-out forwards;
    pointer-events: none;
  }
}

@keyframes panelGlow {
  0% {
    opacity: 1;
    transform: translateX(-100%);
  }
  100% {
    opacity: 0;
    transform: translateX(100%);
  }
}
//人物位置设置
/* 添加Live2D相关样式 */
.live2d-container {
  position: fixed;
  right: 100px;
  bottom: 120px;
  width: 200px;
  height: 240px;
  pointer-events: auto;
  z-index: 9999;
  transform: translateY(-20px);
  
  canvas {
    width: 100%;
    height: 100%;
    position: relative;
    z-index: 9999;
  }
//文字云样式
  .message-bubble {
    position: absolute;
    top: 30px; /* 调整到头部高度 */
    left: -160px; /* 移动到左侧 */
    transform: none; /* 移除原有的水平居中变换 */
    background: rgba(0, 0, 0, 0.7);
    border: 1px solid rgba(43, 196, 220, 0.5);
    border-radius: 8px;
    padding: 8px 12px;
    color: #fff;
    font-size: 12px;
    min-width: 200px; /* 设置最小宽度 */
    max-width: 200px; /* 设置最大宽度 */
    word-break: break-word;
    text-align: left; /* 文字左对齐 */
    z-index: 1001;
    
    &::after {
      content: '';
      position: absolute;
      top: 50%; /* 将尾巴移动到中间 */
      right: -8px; /* 将尾巴移动到右侧 */
      transform: translateY(-50%) rotate(-90deg); /* 旋转尾巴方向 */
      border-left: 8px solid transparent;
      border-right: 8px solid transparent;
      border-top: 8px solid rgba(0, 0, 0, 0.7);
    }
  }
}

/* 移除旧的聊天窗口相关样式 */
.chat-window, .chat-messages {
  display: none !important;
}

.fixed-chat-input .voice-btn {
  background: rgba(43, 196, 220, 0.2);
  border: 1px solid rgba(43, 196, 220, 0.3);
  color: #fff;
  padding: 0 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 12px;
  white-space: nowrap;
  pointer-events: auto;
}

.fixed-chat-input .voice-btn:hover:not(:disabled) {
  background: rgba(43, 196, 220, 0.3);
}

.fixed-chat-input .voice-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.record-error {
  color: #D32F2F;
  font-size: 12px;
  margin-top: 5px;
  position: absolute;
  bottom: -20px;
  left: 0;
  right: 0;
  text-align: center;
}
/* 视频按钮样式 */
.video-btn {
  position: absolute;
  left: -80%;
  bottom: -51%;
  background: rgba(43, 196, 220, 0.2);
  border: 1px solid #2bc4dc;
  border-radius: 4px;
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(43, 196, 220, 0.4);
  }
  
  .video-icon {
    width: 16px;
    height: 16px;
    background: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTIxIDN2MThoLTE4di0xOGgxOHptLTE2IDE2aDE0di0xNGgtMTR2MTR6bTEwLTEwbC02IDN2LTZsNiAzeiIvPjwvc3ZnPg==') no-repeat center;
    background-size: contain;
  }
  
  span {
    color: #fff;
    font-size: 14px;
  }
}
/* AI面试按钮样式 */
.ai-interview-btn {
  position: absolute;
  left: -160%; /* 放置在学习推荐按钮的左侧 */
  bottom: -51%;
  background: rgba(43, 196, 220, 0.2);
  border: 1px solid #2bc4dc;
  border-radius: 4px;
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(43, 196, 220, 0.4);
  }
  
  .ai-icon {
    width: 16px;
    height: 16px;
    background: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTEyIDJjMi45NzYgMCA4IDQuNjc4IDggOXMtNS4wMjQgOS04IDktOC00LjY3OC04LTkgNS4wMjQtOSA4LTl6TTEyIDRDOS4yOCA0IDYgNy40MiA2IDExczMuMjggNyA2IDcgNi0zLjQyIDYtNy0zLjI4LTctNi03ek0xMSAxMHYyYTEgMSAwIDAwMiAwdi0yYTEgMSAwIDEwLTIgMHptNSAydi0yYTEgMSAwIDEwLTIgMHYyYTEgMSAwIDAwMiAweiIvPjwvc3ZnPg==') no-repeat center;
    background-size: contain;
  }
  
  span {
    color: #fff;
    font-size: 14px;
  }
}
/* 视频弹窗样式 */
.video-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  
  .modal-content {
    background: linear-gradient(to bottom, #0f1b2d, #0a1018);
    border: 1px solid #2bc4dc;
    border-radius: 12px;
    width: 80%;
    max-width: 1200px;
    height: 80vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 0 30px rgba(0, 225, 255, 0.2);
    overflow: hidden;
  }
  
  .modal-header {
    padding: 15px 20px;
    background: rgba(43, 196, 220, 0.1);
    border-bottom: 1px solid rgba(43, 196, 220, 0.3);
    
    span {
      color: #00e1ff;
      font-size: 18px;
      font-weight: 500;
      letter-spacing: 1px;
      text-shadow: 0 0 10px rgba(0, 225, 255, 0.5);
    }
    
    .header-buttons {
      .back-btn {
        background: rgba(0, 225, 255, 0.15);
        border: 1px solid rgba(0, 225, 255, 0.3);
        color: #fff;
        padding: 6px 12px;
        border-radius: 4px;
        transition: all 0.3s;
        
        &:hover {
          background: rgba(0, 225, 255, 0.3);
          transform: translateY(-2px);
        }
      }
    }
  }
  
  .modal-body {
    flex: 1;
    padding: 16px;
    
    iframe {
      width: 100%;
      height: 100%;
      background: #000;
    }
  }
}

/* 添加高德地图容器样式 */
.amap-container {
  width: 100%;
  height: 100%;
  background: #000;
}

.canvas-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.amap-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  background: #000;
}

.search-container {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 100;
  width: 350px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.search-box {
  padding: 10px;
  
  .input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: #fff;
    
    input {
      flex: 1;
      padding: 8px 35px 8px 12px;
      border: none;
      font-size: 14px;
      
      &:focus {
        outline: none;
      }
      
      &::placeholder {
        color: #999;
      }
    }
    
    .clear-btn {
      position: absolute;
      right: 40px;
      color: #999;
      cursor: pointer;
      font-size: 18px;
      padding: 0 8px;
      
      &:hover {
        color: #666;
      }
    }

    .search-btn {
      width: 36px;
      height: 34px;
      border: none;
      background: #1890ff;
      border-radius: 0 4px 4px 0;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      
      &:hover {
        background: #40a9ff;
      }
      
      .search-icon {
        font-size: 16px;
        color: #fff;
      }
    }
  }
}

.search-results {
  max-height: 400px;
  overflow-y: auto;
  border-top: 1px solid #eee;
  background: #fff;
}

.result-item {
  padding: 10px 15px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  
  &:hover, &.active {
    background: #f5f5f5;
  }
  
  .company-name {
    color: #333;
    font-size: 14px;
    margin-bottom: 4px;
  }
  
  .company-address {
    color: #999;
    font-size: 12px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

.info-window {
  padding: 15px;
  max-width: 300px;
  
  h4 {
    margin: 0 0 10px 0;
    color: #1890ff;
    font-size: 16px;
    font-weight: bold;
  }
  
  p {
    margin: 8px 0;
    color: #333;
    font-size: 13px;
    line-height: 1.5;
    
    strong {
      color: #666;
      margin-right: 5px;
    }
  }
}

/* 2D地图返回按钮样式 */
.map2d-return-btn-container {
  position: fixed !important;
  bottom: 20px !important;
  left: 50% !important;
  transform: translateX(-50%) !important;
  z-index: 99999 !important;
  pointer-events: none !important;
}

.map2d-return-btn {
  position: relative !important;
  padding: 12px 30px !important;
  background: rgba(0, 12, 32, 0.85) !important;
  color: #00e1ff !important;
  border-radius: 4px !important;
  cursor: pointer !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 8px !important;
  font-size: 14px !important;
  min-width: 140px !important;
  pointer-events: auto !important;
  transition: all 0.3s ease !important;
  text-shadow: 0 0 10px rgba(0, 225, 255, 0.5) !important;
  border: 1px solid rgba(0, 225, 255, 0.2) !important;
  box-shadow: 0 0 15px rgba(0, 225, 255, 0.1),
              inset 0 0 15px rgba(0, 225, 255, 0.1) !important;
  backdrop-filter: blur(5px) !important;
  letter-spacing: 1px !important;
  font-weight: 500 !important;
  overflow: hidden !important;

  &::before {
    content: '' !important;
    position: absolute !important;
    top: 0 !important;
    left: -100% !important;
    width: 100% !important;
    height: 100% !important;
    background: linear-gradient(
      90deg,
      transparent,
      rgba(0, 225, 255, 0.2),
      transparent
    ) !important;
    transition: 0.5s !important;
  }

  &:hover {
    background: rgba(0, 16, 42, 0.95) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 0 20px rgba(0, 225, 255, 0.2),
                inset 0 0 20px rgba(0, 225, 255, 0.2) !important;
    border-color: rgba(0, 225, 255, 0.4) !important;
    
    &::before {
      left: 100% !important;
    }
  }

  i {
    font-size: 16px !important;
    color: #00e1ff !important;
    text-shadow: 0 0 10px rgba(0, 225, 255, 0.5) !important;
    margin-right: 2px !important;
  }

  &::after {
    content: '' !important;
    position: absolute !important;
    top: -2px !important;
    left: -2px !important;
    right: -2px !important;
    bottom: -2px !important;
    border: 2px solid transparent !important;
    border-radius: 4px !important;
    background: linear-gradient(45deg, 
      transparent 25%,
      rgba(0, 225, 255, 0.1) 50%,
      transparent 75%) !important;
    background-size: 200% 200% !important;
    animation: borderFlow 3s linear infinite !important;
    pointer-events: none !important;
  }
}

@keyframes borderFlow {
  0% {
    background-position: 0% 0% !important;
  }
  100% {
    background-position: 200% 200% !important;
  }
}

/* 移除3D地图返回按钮相关样式 */
.map3d-return-btn-container,
.map3d-return-btn {
  display: none !important;
}

.job-recommend-btn-container {
  position: absolute !important;
  right: 20px !important;
  bottom: 400px !important; /* 调整到更高的位置，确保在3D地图按钮上方 */
  z-index: 99999 !important;
}

.job-recommend-btn {
  position: relative !important;
  padding: 12px 25px !important;
  background: rgba(0, 12, 32, 0.85) !important;
  color: #00e1ff !important;
  border-radius: 4px !important;
  cursor: pointer !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 8px !important;
  font-size: 14px !important;
  min-width: 120px !important;
  transition: all 0.3s ease !important;
  text-shadow: 0 0 10px rgba(0, 225, 255, 0.5) !important;
  border: 1px solid rgba(0, 225, 255, 0.2) !important;
  box-shadow: 0 0 15px rgba(0, 225, 255, 0.1),
              inset 0 0 15px rgba(0, 225, 255, 0.1) !important;
  backdrop-filter: blur(5px) !important;

  &::before {
    content: '' !important;
    position: absolute !important;
    top: 0 !important;
    left: -100% !important;
    width: 100% !important;
    height: 100% !important;
    background: linear-gradient(
      90deg,
      transparent,
      rgba(0, 225, 255, 0.2),
      transparent
    ) !important;
    transition: 0.5s !important;
  }

  &:hover {
    background: rgba(0, 16, 42, 0.95) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 0 20px rgba(0, 225, 255, 0.2),
                inset 0 0 20px rgba(0, 225, 255, 0.2) !important;
    border-color: rgba(0, 225, 255, 0.4) !important;
    
    &::before {
      left: 100% !important;
    }
  }

  i {
    font-size: 16px !important;
    color: #00e1ff !important;
    text-shadow: 0 0 10px rgba(0, 225, 255, 0.5) !important;
  }
}

.job-alert-btn-container {
  position: absolute !important;
  right: 200px !important; /* 修改位置到岗位推荐按钮左侧 */
  bottom: 400px !important; /* 与岗位推荐按钮保持相同高度 */
  z-index: 99999 !important;
}

.job-alert-btn {
  position: relative !important;
  padding: 12px 25px !important;
  background: rgba(32, 12, 0, 0.85) !important; /* 修改背景色为偏橙色 */
  color: #ff9900 !important; /* 修改文字颜色为橙色 */
  border-radius: 4px !important;
  cursor: pointer !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 8px !important;
  font-size: 14px !important;
  min-width: 120px !important;
  transition: all 0.3s ease !important;
  text-shadow: 0 0 10px rgba(255, 153, 0, 0.5) !important; /* 修改文字阴影为橙色 */
  border: 1px solid rgba(255, 153, 0, 0.2) !important; /* 修改边框颜色为橙色 */
  box-shadow: 0 0 15px rgba(255, 153, 0, 0.1),
              inset 0 0 15px rgba(255, 153, 0, 0.1) !important; /* 修改阴影颜色为橙色 */
  backdrop-filter: blur(5px) !important;

  &::before {
    content: '' !important;
    position: absolute !important;
    top: 0 !important;
    left: -100% !important;
    width: 100% !important;
    height: 100% !important;
    background: linear-gradient(
      90deg,
      transparent,
      rgba(255, 153, 0, 0.2),
      transparent
    ) !important; /* 修改渐变颜色为橙色 */
    transition: 0.5s !important;
  }

  &:hover {
    background: rgba(42, 16, 0, 0.95) !important; /* 修改悬停背景色为偏橙色 */
    transform: translateY(-2px) !important;
    box-shadow: 0 0 20px rgba(255, 153, 0, 0.2),
                inset 0 0 20px rgba(255, 153, 0, 0.2) !important; /* 修改悬停阴影颜色为橙色 */
    border-color: rgba(255, 153, 0, 0.4) !important; /* 修改悬停边框颜色为橙色 */
    
    &::before {
      left: 100% !important;
    }
  }

  i {
    font-size: 16px !important;
    color: #ff9900 !important; /* 修改图标颜色为橙色 */
    text-shadow: 0 0 10px rgba(255, 153, 0, 0.5) !important; /* 修改图标阴影为橙色 */
  }
}

.career-test-btn {
  position: absolute !important;
  right: 20px !important;
  bottom: 400px !important; /* 调整到更高的位置，确保在3D地图按钮上方 */
  z-index: 99999 !important;
}

.career-test-btn {
  position: relative !important;
  padding: 12px 25px !important;
  background: rgba(0, 12, 32, 0.85) !important;
  color: #00e1ff !important;
  border-radius: 4px !important;
  cursor: pointer !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 8px !important;
  font-size: 14px !important;
  min-width: 120px !important;
  transition: all 0.3s ease !important;
  text-shadow: 0 0 10px rgba(0, 225, 255, 0.5) !important;
  border: 1px solid rgba(0, 225, 255, 0.2) !important;
  box-shadow: 0 0 15px rgba(0, 225, 255, 0.1),
              inset 0 0 15px rgba(0, 225, 255, 0.1) !important;
  backdrop-filter: blur(5px) !important;

  &::before {
    content: '' !important;
    position: absolute !important;
    top: 0 !important;
    left: -100% !important;
    width: 100% !important;
    height: 100% !important;
    background: linear-gradient(
      90deg,
      transparent,
      rgba(0, 225, 255, 0.2),
      transparent
    ) !important;
    transition: 0.5s !important;
  }

  &:hover {
    background: rgba(0, 16, 42, 0.95) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 0 20px rgba(0, 225, 255, 0.2),
                inset 0 0 20px rgba(0, 225, 255, 0.2) !important;
    border-color: rgba(0, 225, 255, 0.4) !important;
    
    &::before {
      left: 100% !important;
    }
  }

  i {
    font-size: 16px !important;
    color: #00e1ff !important;
    text-shadow: 0 0 10px rgba(0, 225, 255, 0.5) !important;
  }
}

.career-test-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  
  .modal-content {
    background: #1a1a1a;
    border: 1px solid #2bc4dc;
    border-radius: 8px;
    width: 80%;
    max-width: 1800px;
    height: 80vh;
    display: flex;
    flex-direction: column;
  }
  
  .modal-header {
    padding: 12px 16px;
    border-bottom: 1px solid rgba(43, 196, 220, 0.3);
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    span {
      color: #fff;
      font-size: 16px;
    }
    
    .header-buttons {
      display: flex;
      gap: 10px;
    }
    
    .back-btn {
      background: rgba(43, 196, 220, 0.2);
      border: 1px solid rgba(43, 196, 220, 0.3);
      color: #fff;
      font-size: 14px;
      padding: 4px 10px;
      border-radius: 4px;
      cursor: pointer;
      
      &:hover {
        background: rgba(43, 196, 220, 0.3);
      }
    }
    
    .close-btn {
      background: none;
      border: none;
      color: #fff;
      font-size: 24px;
      cursor: pointer;
      padding: 0 4px;
      
      &:hover {
        color: #2bc4dc;
      }
    }
  }
  
  .modal-body {
    flex: 1;
    padding: 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
}

.test-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr); /* 每行3个 */
  grid-gap: 20px;
  padding: 20px;
  overflow-y: auto;
  max-height: calc(100vh - 200px); /* 限制最大高度，确保在小屏幕上可滚动 */
}

.test-item {
  /* 减小每个测试项的大小，使更多内容可见 */
  height: 180px;
  padding: 15px;
}

.test-content {
  flex: 1;
  height: 100%;
  
  iframe {
    width: 100%;
    height: 100%;
    border: none;
    background: #fff;
  }
}

.test-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
  padding: 30px;
  width: 100%;
}

.test-item {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 25px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, transparent 0%, rgba(0, 225, 255, 0.7), transparent);
    transform: scaleX(0);
    transition: transform 0.5s;
  }
  
  &:hover {
    background: rgba(0, 225, 255, 0.1);
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
    
    &::before {
      transform: scaleX(1);
    }
    
    h3 {
      color: #00e1ff;
    }
  }
  
  .test-icon {
    width: 60px;
    height: 60px;
    margin: 0 auto 15px;
    background: rgba(0, 225, 255, 0.1);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  }
  
  h3 {
    color: #ffffff;
    font-size: 18px;
    margin-bottom: 12px;
    transition: color 0.3s;
  }
  
  p {
    color: rgba(255, 255, 255, 0.7);
    font-size: 14px;
    line-height: 1.6;
  }
}

.value-icon::before {
  content: '价';
  color: #00e1ff;
  font-size: 24px;
}

.anchor-icon::before {
  content: '锚';
  color: #ffcc00;
  font-size: 24px;
}

/* 添加主要动画类 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s, transform 0.5s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

.slide-fade-enter-active, .slide-fade-leave-active {
  transition: all 0.5s ease;
}

.slide-fade-enter-from {
  transform: translateX(-30px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(30px);
  opacity: 0;
}

.source-link-dialog {
  .el-dialog {
    background: rgba(0, 12, 32, 0.95) !important;
    border: 1px solid rgba(0, 225, 255, 0.2) !important;
    border-radius: 8px !important;
    
    .el-dialog__header {
      border-bottom: 1px solid rgba(0, 225, 255, 0.2) !important;
      padding: 15px 20px !important;
      
      .el-dialog__title {
        color: #00e1ff !important;
        font-size: 16px !important;
      }
    }
    
    .el-dialog__body {
      padding: 20px !important;
      height: 650px !important;  // 设置固定高度
      overflow: hidden !important;  // 防止出现双滚动条
      
      .source-link-content {
        height: 100% !important;
        
        iframe {
          border-radius: 4px !important;
          background: #fff !important;  // iframe 背景设为白色
        }
      }
    }
  }
}

.holo-item {
  cursor: pointer !important;
  transition: all 0.3s ease !important;
  
  &:hover {
    background: rgba(0, 225, 255, 0.1) !important;
    transform: translateY(-2px) !important;
  }
}

.holo-section {
  cursor: pointer !important;
  transition: all 0.3s ease !important;
  
  &:hover {
    background: rgba(0, 225, 255, 0.1) !important;
    transform: translateY(-2px) !important;
  }
}

.data-title {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  width: 90%;
  max-width: 1200px;
}

.title-box {
  position: relative;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, 
    rgba(0,28,71,0.6) 0%,
    rgba(0,40,80,0.4) 100%
  );
  backdrop-filter: blur(8px);
  border-radius: 4px;
  overflow: hidden;
}

.title-bg {
  position: absolute;
  inset: 0;
  
  .bg-line {
    position: absolute;
    inset: 0;
    background: 
      linear-gradient(90deg, transparent 0%, rgba(0,255,200,0.1) 50%, transparent 100%);
    animation: bgMove 8s linear infinite;
  }
}

.title-content {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  
  .tech-line {
    position: relative;
    width: 120px;
    height: 2px;
    
    &.left {
      margin-right: 20px;
      background: linear-gradient(90deg,
        rgba(0,255,200,0.2) 0%,
        rgba(0,198,255,0.8) 100%
      );
      
      .tech-dots {
        position: absolute;
        left: 0;
        top: -10px;
        display: flex;
        gap: 6px;
        
        span {
          width: 4px;
          height: 4px;
          background: #00ffc8;
          border-radius: 50%;
          animation: dotPulse 2s infinite;
          box-shadow: 0 0 8px rgba(0,255,200,0.8);
          
          &:nth-child(2) {
            animation-delay: 0.4s;
            background: #00e1ff;
          }
          
          &:nth-child(3) {
            animation-delay: 0.8s;
            background: #00ffc8;
          }
        }
      }
    }
    
    &.right {
      margin-left: 20px;
      background: linear-gradient(90deg,
        rgba(0,198,255,0.8) 0%,
        rgba(0,255,200,0.2) 100%
      );
      
      .tech-dots {
        position: absolute;
        right: 0; /* 将亮点移到右侧 */
        top: -10px;
        display: flex;
        gap: 6px;
        
        span {
          width: 4px;
          height: 4px;
          background: #00ffc8;
          border-radius: 50%;
          animation: dotPulse 2s infinite;
          box-shadow: 0 0 8px rgba(0,255,200,0.8);
          
          &:nth-child(2) {
            animation-delay: 0.4s;
            background: #00e1ff;
          }
          
          &:nth-child(3) {
            animation-delay: 0.8s;
            background: #00ffc8;
          }
        }
      }
    }
  }
}

.tech-dots {
  position: absolute;
  top: -10px;
  display: flex;
  gap: 6px;
  
  span {
    width: 4px;
    height: 4px;
    background: #00ffc8;
    border-radius: 50%;
    animation: dotPulse 2s infinite;
    box-shadow: 0 0 8px rgba(0,255,200,0.8);
    
    &:nth-child(2) {
      animation-delay: 0.4s;
      background: #00e1ff;
    }
    
    &:nth-child(3) {
      animation-delay: 0.8s;
      background: #00ffc8;
    }
  }
}

.title-text {
  color: #fff;
  font-size: 32px;
  font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
  font-weight: 400;
  letter-spacing: 2px;
  text-shadow: 0 0 15px rgba(0,255,200,0.5),
               0 0 30px rgba(0,198,255,0.3);
  background: linear-gradient(180deg, #ffffff, #00ffc8);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.tech-border {
  position: absolute;
  inset: 0;
  pointer-events: none;
  
  .border-line {
    position: absolute;
    background: linear-gradient(90deg,
      rgba(0,255,200,0) 0%,
      rgba(0,198,255,0.8) 50%,
      rgba(0,255,200,0) 100%
    );
    
    &.top, &.bottom {
      height: 1px;
      width: 100%;
      left: 0;
    }
    
    &.left, &.right {
      width: 1px;
      height: 100%;
      top: 0;
    }
    
    &.top { top: 0; animation: borderFlowX 4s linear infinite; }
    &.right { right: 0; animation: borderFlowY 4s linear infinite 1s; }
    &.bottom { bottom: 0; animation: borderFlowX 4s linear infinite 2s; }
    &.left { left: 0; animation: borderFlowY 4s linear infinite 3s; }
  }
}

.border-corner {
  position: absolute;
  width: 24px;
  height: 24px;
  
  &::before, &::after {
    content: '';
    position: absolute;
    background: rgba(0,255,200,0.8);
    box-shadow: 0 0 10px rgba(0,198,255,0.5);
  }
  
  &.tl {
    top: 0;
    left: 0;
    border-top: 2px solid rgba(0,255,200,0.8);
    border-left: 2px solid rgba(0,255,200,0.8);
    animation: cornerRotate 4s linear infinite;
  }
  
  &.tr {
    top: 0;
    right: 0;
    border-top: 2px solid rgba(0,255,200,0.8);
    border-right: 2px solid rgba(0,255,200,0.8);
    animation: cornerRotate 4s linear infinite 1s;
  }
  
  &.bl {
    bottom: 0;
    left: 0;
    border-bottom: 2px solid rgba(0,255,200,0.8);
    border-left: 2px solid rgba(0,255,200,0.8);
    animation: cornerRotate 4s linear infinite 2s;
  }
  
  &.br {
    bottom: 0;
    right: 0;
    border-bottom: 2px solid rgba(0,255,200,0.8);
    border-right: 2px solid rgba(0,255,200,0.8);
    animation: cornerRotate 4s linear infinite 3s;
  }
}

@keyframes bgMove {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

@keyframes dotPulse {
  0% { transform: scale(0.8); opacity: 0.3; }
  50% { transform: scale(1.2); opacity: 1; }
  100% { transform: scale(0.8); opacity: 0.3; }
}

@keyframes borderFlowX {
  0% { transform: scaleX(0); opacity: 0; }
  50% { transform: scaleX(1); opacity: 1; }
  100% { transform: scaleX(0); opacity: 0; }
}

@keyframes borderFlowY {
  0% { transform: scaleY(0); opacity: 0; }
  50% { transform: scaleY(1); opacity: 1; }
  100% { transform: scaleY(0); opacity: 0; }
}

@keyframes cornerRotate {
  0% { opacity: 0.3; transform: rotate(0deg); }
  50% { opacity: 1; transform: rotate(180deg); }
  100% { opacity: 0.3; transform: rotate(360deg); }
}

.video-modal {
  .modal-content {
    .modal-header {
      display: flex;
      justify-content: space-between; /* 使标题和按钮分布在两端 */
      align-items: center;
      padding: 10px 20px;
      
      span {
        color: #fff;
        font-size: 16px;
      }
      
      .close-btn {
        position: relative;
        right: 0; /* 移到右侧 */
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        border-radius: 4px;
        background: rgba(0, 198, 255, 0.1);
        border: 1px solid rgba(0, 198, 255, 0.3);
        color: #00c6ff;
        transition: all 0.3s ease;
        
        &:hover {
          background: rgba(0, 198, 255, 0.2);
          border-color: rgba(0, 198, 255, 0.5);
        }
      }
    }
  }
}

.footer {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;

  .policy-link {
    display: flex;
    align-items: center;
    background: rgba(0, 198, 255, 0.1);
    border: 1px solid rgba(0, 198, 255, 0.3);
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      background: rgba(0, 198, 255, 0.2);
      border-color: rgba(0, 198, 255, 0.5);
    }

    .link-icon {
      margin-right: 8px;
    }

    .link-text {
      color: #00c6ff;
      margin-right: 8px;
    }

    .link-arrow {
      color: #00c6ff;
    }
  }
}



.policy-recommend-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(26, 111, 192, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: white;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
  backdrop-filter: blur(10px);
}

.policy-recommend-btn:hover {
  background: rgba(26, 111, 192, 1);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.policy-recommend-btn .el-icon {
  font-size: 16px;
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.route-planning-btn {
  position: fixed;
  right: 20px;
  top: calc(50% + 200px);
  transform: translateY(-50%);
  background: rgba(4, 19, 36, 0.95);
  border: 1px solid #0e4b80;
  color: #00a0e9;
  padding: 10px 15px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  z-index: 100;
  width: auto;
  min-width: 100px;
  justify-content: center;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.route-planning-btn:hover {
  background: rgba(14, 75, 128, 0.3);
}

.route-icon {
  display: inline-block;
  width: 20px;
  height: 20px;
  margin-right: 5px;
  font-family: element-icons;
  content: "\e6e1";  /* 使用 Element Plus 的位置图标 */
}

/* 圆环相关样式 */
.carousel-container {
  position: fixed;
  bottom: 490px;
  right: -250px;
  width: 550px;
  height: 500px;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

/* Arc container */
.segmented-arc-container {
  position: relative;
  width: 450px;
  height: 450px;
}

/* 圆环主体 - 增强透明度和颜色深度 */
.segmented-arc {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  position: relative;
  transition: background 0.5s ease-in-out;
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0.95; /* 增加透明度 */
  backdrop-filter: blur(4px); /* 增加模糊效果 */
  box-shadow: 0 0 30px rgba(0, 140, 255, 0.15); /* 添加发光效果 */
}

/* 圆环中心 - 加深颜色 */
.segmented-arc::before {
  content: '';
  position: absolute;
  width: 45%;
  height: 45%;
  background: rgba(16, 22, 48, 0.9); /* 更深的背景色 */
  border-radius: 50%;
  box-shadow: inset 0 0 25px rgba(0, 0, 0, 0.6), 0 0 15px rgba(0, 140, 255, 0.2); /* 增强阴影 */
}

/* 标签容器 */
.arc-labels {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 6;
}

/* 标签样式 - 增强对比度 */
.arc-labels span {
  position: absolute;
  transform: translate(-50%, -50%);
  color: #e8f5ff; /* 更亮的字体颜色 */
  padding: 6px 12px;
  border-radius: 5px;
  font-size: 15px;
  font-weight: 600; /* 加粗字体 */
  text-align: center;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.5s ease-in-out, visibility 0s linear 0.5s, top 0.4s ease-out, left 0.4s ease-out;
  cursor: pointer;
  text-shadow: 0 0 8px rgba(0, 0, 0, 0.4); /* 添加文字阴影增强可读性 */
}

/* 标签悬停效果 - 更明显的高亮 */
.arc-labels span:hover {
  color: #ffce77; /* 更亮的黄色 */
  text-decoration: underline;
  transform: translate(-50%, -50%) scale(1.05); /* 轻微放大效果 */
  transition: all 0.2s ease-out;
}

/* 标签可见状态 */
.arc-labels span.visible {
  opacity: 1;
  visibility: visible;
  transition: opacity 0.5s ease-in-out, top 0.4s ease-out, left 0.4s ease-out;
}

/* 标签激活样式 - 更强的视觉效果 */
.arc-labels span.active {
  background-color: rgba(50, 140, 255, 0.25); /* 更鲜明的背景 */
  color: #ffd88a; /* 更亮的高亮色 */
  box-shadow: 0 0 12px rgba(107, 190, 253, 0.5), 0 0 20px rgba(107, 190, 253, 0.3); /* 双层阴影 */
  font-weight: 700; /* 更粗的字体 */
}

/* 分页导航 */
.pagination {
  position: absolute;
  top: 50%;
  left: 265px;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 10;
}

.pagination .dot {
  
  width: 20px;
  height: 20px;
  background-color: rgba(100, 150, 200, 0.3);
  border: none;
  border-radius: 50%;
  margin: 7px 0;
  cursor: pointer;
  transition: all 0.3s ease-in-out;
  box-shadow: inset 0 0 2px rgba(0, 0, 0, 0.2);
}

.pagination .dot.active {
  background-color: #6bbefd;
  transform: scale(1.4);
  box-shadow: 0 0 8px rgba(107, 190, 253, 0.7), 0 0 12px rgba(107, 190, 253, 0.5);
}

/* 隐藏原始按钮组 */
.map-btn-group {
  display: none;
}
/* 半圆环控制按钮样式 */
.arc-toggle-btn {
  position: absolute;
  top: 523px;
  right: 25px;
  transform: translate(-50%, -50%);
  z-index: 999999;
}

.arc-toggle-btn .checkbox-wrapper * {
  -webkit-tap-highlight-color: transparent;
  outline: none;
}

.arc-toggle-btn .checkbox-wrapper input[type="checkbox"] {
  display: none;
}

.arc-toggle-btn .checkbox-wrapper label {
  --size: 50px;
  --shadow: calc(var(--size) * 0.07) calc(var(--size) * 0.1);
  position: relative;
  display: block;
  width: var(--size);
  height: var(--size);
  margin: 0 auto;
  background-color: #4158d0;
  background-image: linear-gradient(
    43deg,
    #4158d0 0%,
    #c850c0 46%,
    #ffcc70 100%
  );
  border-radius: 50%;
  box-shadow: 0 var(--shadow) #ffbeb8;
  cursor: pointer;
  transition: 0.2s ease transform, 0.2s ease background-color,
    0.2s ease box-shadow;
  overflow: hidden;
  z-index: 1;
}

.arc-toggle-btn .checkbox-wrapper label:before {
  content: "";
  position: absolute;
  top: 50%;
  right: 0;
  left: 0;
  width: calc(var(--size) * 0.7);
  height: calc(var(--size) * 0.7);
  margin: 0 auto;
  background-color: #fff;
  transform: translateY(-50%);
  border-radius: 50%;
  box-shadow: inset 0 var(--shadow) #ffbeb8;
  transition: 0.2s ease width, 0.2s ease height;
}

.arc-toggle-btn .checkbox-wrapper label:hover:before {
  width: calc(var(--size) * 0.55);
  height: calc(var(--size) * 0.55);
  box-shadow: inset 0 var(--shadow) #ff9d96;
}

.arc-toggle-btn .checkbox-wrapper label:active {
  transform: scale(0.9);
}

.arc-toggle-btn .checkbox-wrapper .tick_mark {
  position: absolute;
  top: 9px;
  left: 2px;
  right: 0;
  width: calc(var(--size) * 0.6);
  height: calc(var(--size) * 0.6);
  margin: 0 auto;
  margin-left: calc(var(--size) * 0.14);
  transform: rotateZ(-92deg);
}

.arc-toggle-btn .checkbox-wrapper .tick_mark:before,
.arc-toggle-btn .checkbox-wrapper .tick_mark:after {
  content: "";
  position: absolute;
  background-color: #fff;
  border-radius: 2px;
  opacity: 0;
  transition: 0.2s ease transform, 0.2s ease opacity;
}

.arc-toggle-btn .checkbox-wrapper .tick_mark:before {
  left: 0;
  bottom: 0;
  width: calc(var(--size) * 0.1);
  height: calc(var(--size) * 0.3);
  box-shadow: -2px 0 5px rgba(0, 0, 0, 0.23);
  transform: translateY(calc(var(--size) * -0.68));
}

.arc-toggle-btn .checkbox-wrapper .tick_mark:after {
  left: 0;
  bottom: 0;
  width: 100%;
  height: calc(var(--size) * 0.1);
  box-shadow: 0 3px 5px rgba(0, 0, 0, 0.23);
  transform: translateX(calc(var(--size) * 0.78));
}

.arc-toggle-btn .checkbox-wrapper input[type="checkbox"]:checked + label {
  background-color: #4158d0;
  background-image: linear-gradient(
    43deg,
    #f7805c 0%,
    #fb4545 46%,
    #e1236a 100%
  );
  box-shadow: rgba(0, 0, 0, 0.3) 0px 19px 38px,
    rgba(0, 0, 0, 0.22) 0px 15px 12px;
}

.arc-toggle-btn .checkbox-wrapper input[type="checkbox"]:checked + label:before {
  width: 0;
  height: 0;
}

.arc-toggle-btn .checkbox-wrapper input[type="checkbox"]:checked + label .tick_mark:before,
.arc-toggle-btn .checkbox-wrapper input[type="checkbox"]:checked + label .tick_mark:after {
  background-color: #fff;
  width: calc(var(--size) * 0.4);
  height: calc(var(--size) * 0.1);
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  opacity: 1;
}

.arc-toggle-btn .checkbox-wrapper input[type="checkbox"]:checked + label .tick_mark:before {
  transform: translate(-50%, -50%) rotate(45deg);
}

.arc-toggle-btn .checkbox-wrapper input[type="checkbox"]:checked + label .tick_mark:after {
  transform: translate(-50%, -50%) rotate(-45deg);
}
</style>
