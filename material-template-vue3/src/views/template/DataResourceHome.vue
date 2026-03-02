<template>
  <div class="template-home">
    <Navbar />
    
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-bg">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
        <div class="wave-decoration"></div>
      </div>
      
      <div class="hero-content">
        <h1 class="hero-title animate-slide-up">
          <span class="gradient-text">数据资源中心</span>
        </h1>
        <p class="hero-subtitle animate-slide-up delay-1">
          创建、管理和发布您的数据资源，让数据标准化变得简单高效
        </p>
        
        <div class="hero-actions animate-slide-up delay-2">
          <el-button type="primary" size="large" class="action-btn primary" @click="goToCreate">
            <el-icon><Plus /></el-icon>
            创建数据集
          </el-button>
          <el-button size="large" class="action-btn secondary" @click="goToLibrary">
            <el-icon><FolderOpened /></el-icon>
            浏览数据资源目录
          </el-button>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="stats-section">
      <div class="stats-container">
        <div 
          v-for="(stat, index) in stats" 
          :key="stat.label"
          class="stat-card animate-slide-up"
          :style="{ animationDelay: `${index * 0.1}s` }"
        >
          <div class="stat-icon" :style="{ background: stat.gradient }">
            <el-icon :size="28"><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <h3 class="stat-number">
              <CountUp :end-val="stat.value" :duration="2" />
            </h3>
            <p class="stat-label">{{ stat.label }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <div class="section-header">
        <h2 class="section-title">核心功能</h2>
        <p class="section-subtitle">强大的数据资源管理功能，助力您的数据工作</p>
      </div>
      
      <div class="features-grid">
        <div 
          v-for="(feature, index) in features" 
          :key="feature.title"
          class="feature-card"
          :style="{ animationDelay: `${index * 0.15}s` }"
          @click="handleFeatureClick(feature)"
        >
          <div class="card-glow" :style="{ background: feature.gradient }"></div>
          <div class="card-content">
            <div class="feature-icon" :style="{ background: feature.gradient }">
              <el-icon :size="32"><component :is="feature.icon" /></el-icon>
            </div>
            <h3 class="feature-title">{{ feature.title }}</h3>
            <p class="feature-desc">{{ feature.description }}</p>
            <div class="feature-step">{{ feature.step }}</div>
          </div>
          <div class="card-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
    </section>

    <!-- Quick Start Section -->
    <section class="quickstart-section">
      <div class="quickstart-container">
        <div class="quickstart-content">
          <h2 class="quickstart-title">准备好开始了吗？</h2>
          <p class="quickstart-desc">
            只需几步，即可创建您的第一个数据集
          </p>
          <el-button type="primary" size="large" class="quickstart-btn" @click="goToCreate">
            立即开始
            <el-icon class="btn-icon"><ArrowRight /></el-icon>
          </el-button>
        </div>
        <div class="quickstart-visual">
          <div class="visual-card card-1">
            <el-icon :size="24"><Document /></el-icon>
            <span>基础设置</span>
          </div>
          <div class="visual-card card-2">
            <el-icon :size="24"><Edit /></el-icon>
            <span>数据结构设计</span>
          </div>
          <div class="visual-card card-3">
            <el-icon :size="24"><CircleCheck /></el-icon>
            <span>发布完成</span>
          </div>
          <svg class="connect-lines">
            <path d="M80,30 Q120,30 140,60" stroke="rgba(102, 126, 234, 0.3)" stroke-width="2" fill="none" stroke-dasharray="5,5"/>
            <path d="M180,80 Q220,80 240,110" stroke="rgba(102, 126, 234, 0.3)" stroke-width="2" fill="none" stroke-dasharray="5,5"/>
          </svg>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <p>© 2024 生物医用材料数据资源节点 · 版权所有</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Plus, FolderOpened, ArrowRight, Document, Edit, CircleCheck,
  DocumentAdd, Checked, Upload, DataAnalysis, Folder, Setting
} from '@element-plus/icons-vue'
import Navbar from '@/components/Navbar.vue'

const router = useRouter()

// 模拟数字增长动画组件
const CountUp = {
  props: ['endVal', 'duration'],
  setup(props) {
    const displayValue = ref(0)
    const step = props.endVal / (props.duration * 60)
    
    const animate = () => {
      if (displayValue.value < props.endVal) {
        displayValue.value = Math.min(displayValue.value + step, props.endVal)
        requestAnimationFrame(animate)
      }
    }
    
    setTimeout(animate, 500)
    
    return () => Math.floor(displayValue.value)
  }
}

const stats = [
  { label: '数据资源总数', value: 128, icon: markRaw(Folder), gradient: 'linear-gradient(135deg, #667eea, #764ba2)' },
  { label: '已发布', value: 96, icon: markRaw(Checked), gradient: 'linear-gradient(135deg, #10b981, #34d399)' },
  { label: '数据集', value: 1024, icon: markRaw(DataAnalysis), gradient: 'linear-gradient(135deg, #f59e0b, #fbbf24)' },
  { label: '数据条目', value: 50000, icon: markRaw(Document), gradient: 'linear-gradient(135deg, #06b6d4, #22d3ee)' }
]

const features = [
  {
    title: '数据集创建',
    description: '可自定义数据字段，支持多种数据类型，灵活配置',
    icon: markRaw(DocumentAdd),
    gradient: 'linear-gradient(135deg, #667eea, #764ba2)',
    step: '01',
    action: 'create'
  },
  {
    title: '数据查看',
    description: '浏览已发布的数据集，查看详细数据内容',
    icon: markRaw(Checked),
    gradient: 'linear-gradient(135deg, #10b981, #34d399)',
    step: '02',
    action: 'audit'
  },
  {
    title: '数据上传',
    description: '基于模板快速上传数据，支持批量导入导出',
    icon: markRaw(Upload),
    gradient: 'linear-gradient(135deg, #f59e0b, #fbbf24)',
    step: '03',
    action: 'upload'
  }
]

const goToCreate = () => {
  router.push('/template/create')
}

const goToLibrary = () => {
  router.push('/template/library')
}

const handleFeatureClick = (feature) => {
  switch (feature.action) {
    case 'create':
      router.push('/template/create')
      break
    case 'upload':
      router.push('/template/upload')
      break
    case 'audit':
      router.push('/template/library')
      break
  }
}
</script>

<style lang="scss" scoped>
.template-home {
  min-height: 100vh;
  background: #f8fafc;
}

// Hero Section
.hero-section {
  position: relative;
  min-height: 500px;
  padding: 160px 32px 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-size: 200% 200%;
  animation: gradientShift 15s ease infinite;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
  animation: float 8s ease-in-out infinite;
  
  &.orb-1 {
    width: 400px;
    height: 400px;
    background: rgba(255, 255, 255, 0.3);
    top: -100px;
    left: -100px;
  }
  
  &.orb-2 {
    width: 300px;
    height: 300px;
    background: rgba(255, 255, 255, 0.2);
    bottom: -50px;
    right: -50px;
    animation-delay: 2s;
  }
}

.wave-decoration {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 120px;
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 120'%3E%3Cpath fill='%23f8fafc' d='M0,64L48,69.3C96,75,192,85,288,80C384,75,480,53,576,48C672,43,768,53,864,69.3C960,85,1056,107,1152,101.3C1248,96,1344,64,1392,48L1440,32L1440,120L1392,120C1344,120,1248,120,1152,120C1056,120,960,120,864,120C768,120,672,120,576,120C480,120,384,120,288,120C192,120,96,120,48,120L0,120Z'%3E%3C/path%3E%3C/svg%3E") no-repeat bottom;
  background-size: cover;
}

.hero-content {
  position: relative;
  z-index: 1;
  text-align: center;
  max-width: 800px;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 800;
  margin-bottom: 20px;
  
  .gradient-text {
    color: white;
    text-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
  }
}

.hero-subtitle {
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 40px;
  line-height: 1.8;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.action-btn {
  height: 52px;
  padding: 0 32px;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  
  &.primary {
    background: white;
    color: #667eea;
    border: none;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    
    &:hover {
      transform: translateY(-3px);
      box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2);
    }
  }
  
  &.secondary {
    background: rgba(255, 255, 255, 0.15);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.3);
    backdrop-filter: blur(10px);
    
    &:hover {
      background: rgba(255, 255, 255, 0.25);
      transform: translateY(-3px);
    }
  }
}

// Stats Section
.stats-section {
  padding: 60px 32px;
  margin-top: -60px;
  position: relative;
  z-index: 10;
}

.stats-container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 28px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  }
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 0.875rem;
  color: #64748b;
}

// Features Section
.features-section {
  padding: 80px 32px;
  max-width: 1200px;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  margin-bottom: 60px;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 12px;
}

.section-subtitle {
  font-size: 1.125rem;
  color: #64748b;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
}

.feature-card {
  position: relative;
  background: white;
  border-radius: 24px;
  padding: 40px 32px;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.4s ease;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  
  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.12);
    
    .card-glow {
      opacity: 0.1;
    }
    
    .card-arrow {
      opacity: 1;
      transform: translateX(0);
    }
    
    .feature-icon {
      transform: scale(1.1) rotate(5deg);
    }
  }
}

.card-glow {
  position: absolute;
  inset: 0;
  opacity: 0;
  transition: opacity 0.4s ease;
}

.card-content {
  position: relative;
  z-index: 1;
}

.feature-icon {
  width: 72px;
  height: 72px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 24px;
  transition: transform 0.4s ease;
}

.feature-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 12px;
}

.feature-desc {
  font-size: 1rem;
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 20px;
}

.feature-step {
  font-size: 3rem;
  font-weight: 800;
  color: #f1f5f9;
  position: absolute;
  top: 32px;
  right: 32px;
}

.card-arrow {
  position: absolute;
  bottom: 32px;
  right: 32px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #667eea;
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.4s ease;
}

// Quick Start Section
.quickstart-section {
  padding: 80px 32px;
  background: linear-gradient(135deg, #1e293b, #334155);
}

.quickstart-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 60px;
}

.quickstart-content {
  max-width: 500px;
}

.quickstart-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 16px;
}

.quickstart-desc {
  font-size: 1.125rem;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 32px;
  line-height: 1.6;
}

.quickstart-btn {
  height: 52px;
  padding: 0 32px;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  
  .btn-icon {
    margin-left: 8px;
    transition: transform 0.3s ease;
  }
  
  &:hover .btn-icon {
    transform: translateX(4px);
  }
}

.quickstart-visual {
  position: relative;
  width: 400px;
  height: 200px;
}

.visual-card {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: white;
  font-weight: 500;
  animation: floatCard 4s ease-in-out infinite;
  
  &.card-1 {
    top: 0;
    left: 0;
  }
  
  &.card-2 {
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    animation-delay: 1s;
  }
  
  &.card-3 {
    bottom: 0;
    right: 0;
    animation-delay: 2s;
  }
  
  @keyframes floatCard {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
  }
}

.connect-lines {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

// Footer
.footer {
  padding: 32px;
  text-align: center;
  color: #64748b;
  font-size: 0.875rem;
}

// Responsive
@media (max-width: 1024px) {
  .stats-container {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .quickstart-container {
    flex-direction: column;
    text-align: center;
  }
  
  .quickstart-visual {
    display: none;
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .stats-container,
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .quickstart-title {
    font-size: 2rem;
  }
}
</style>
