<template>
  <div class="home-page">
    <!-- 背景动画 -->
    <div class="bg-container">
      <div class="gradient-bg"></div>
      <div class="particles">
        <div v-for="i in 20" :key="i" class="particle" :style="getParticleStyle(i)"></div>
      </div>
      <div class="grid-lines"></div>
    </div>

    <!-- 导航栏 -->
    <header class="home-navbar">
      <div class="navbar-container">
        <div class="logo">
          <div class="logo-icon">
            <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
              <ellipse cx="24" cy="12" rx="16" ry="6" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M8 12v24c0 3.3 7.2 6 16 6s16-2.7 16-6V12" stroke="currentColor" stroke-width="2" fill="none"/>
              <ellipse cx="24" cy="24" rx="16" ry="6" stroke="currentColor" stroke-width="2" fill="none" opacity="0.5"/>
              <circle cx="24" cy="24" r="4" fill="currentColor"/>
              <circle cx="14" cy="20" r="2.5" fill="currentColor" opacity="0.7"/>
              <circle cx="34" cy="20" r="2.5" fill="currentColor" opacity="0.7"/>
              <circle cx="18" cy="30" r="2" fill="currentColor" opacity="0.5"/>
              <circle cx="30" cy="30" r="2" fill="currentColor" opacity="0.5"/>
              <path d="M16 20l6 3M32 20l-6 3M19 29l4-4M29 29l-4-4" stroke="currentColor" stroke-width="1.5" opacity="0.6"/>
            </svg>
          </div>
          <div class="logo-text-group">
            <h1 class="logo-text">生物医用材料数据资源节点</h1>
          </div>
        </div>
        
        <div class="user-section">
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="40" class="user-avatar">
                {{ userInitial }}
              </el-avatar>
              <span class="user-name">{{ userName }}</span>
              <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="main-content">
      <div class="hero-section">
        <div class="hero-content animate-fade-in">
          <h1 class="hero-title">
            <span class="gradient-text">生物医用材料数据库</span>
          </h1>
          <p class="hero-subtitle">
            整合生物医用材料领域的科研数据，构建标准化数据资源体系，<br>
            助力材料科学研究与创新发展
          </p>
          
          <div class="hero-stats">
            <div class="stat-item">
              <span class="stat-number">128+</span>
              <span class="stat-label">数据集</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-number">50,000+</span>
              <span class="stat-label">数据条目</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-number">15+</span>
              <span class="stat-label">数据类型</span>
            </div>
          </div>
        </div>

        <!-- 数据节点入口 -->
        <div class="nodes-section animate-slide-up">
          <div class="node-card primary" @click="enterDataCenter">
            <div class="card-glow"></div>
            <div class="card-content">
              <div class="node-icon">
                <el-icon :size="48"><Folder /></el-icon>
              </div>
              <h3 class="node-title">数据资源中心</h3>
              <p class="node-desc">浏览、创建和管理数据集，上传和导出数据</p>
              <div class="enter-btn">
                <span>进入节点</span>
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </div>

          <div class="node-card secondary" @click="enterAlgorithmCenter">
            <div class="card-content">
              <div class="node-icon">
                <el-icon :size="48"><DataAnalysis /></el-icon>
              </div>
              <h3 class="node-title">算法中心</h3>
              <p class="node-desc">数据分析、模型训练与智能预测</p>
              <div class="enter-btn">
                <span>进入节点</span>
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </div>

          <div class="node-card secondary disabled">
            <div class="card-content">
              <div class="node-icon">
                <el-icon :size="48"><Reading /></el-icon>
              </div>
              <h3 class="node-title">语料中心</h3>
              <p class="node-desc">语料管理与标注（即将上线）</p>
              <div class="enter-btn">
                <span>敬请期待</span>
              </div>
            </div>
          </div>

          <div class="node-card secondary" @click="enterTemplateManageCenter">
            <div class="card-content">
              <div class="node-icon">
                <el-icon :size="48"><Coin /></el-icon>
              </div>
              <h3 class="node-title">模版管理中心</h3>
              <p class="node-desc">模版管理与审核</p>
              <div class="enter-btn">
                <span>进入节点</span>
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="home-footer">
      <p>© 2024 生物医用材料数据资源节点 · 版权所有</p>
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { 
  ArrowDown, ArrowRight, User, SwitchButton, 
  Folder, DataAnalysis, Reading, Coin 
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const userName = computed(() => userStore.userName || '用户')
const userInitial = computed(() => userName.value.charAt(0).toUpperCase())

const enterDataCenter = () => {
  router.push('/template')
}

const enterAlgorithmCenter = () => {
  router.push('/algorithm')
}

const enterTemplateManageCenter = () => {
  router.push('/tplmanage')
}

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'logout':
      ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        userStore.logout()
        router.push('/login')
      }).catch(() => {})
      break
  }
}

const getParticleStyle = (index) => {
  const size = Math.random() * 4 + 2
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`,
    animationDelay: `${Math.random() * 5}s`,
    animationDuration: `${Math.random() * 10 + 10}s`
  }
}
</script>

<style lang="scss" scoped>
.home-page {
  min-height: 100vh;
  position: relative;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

// 背景
.bg-container {
  position: fixed;
  inset: 0;
  z-index: 0;
}

.gradient-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
  
  &::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 30% 30%, rgba(102, 126, 234, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 70% 70%, rgba(20, 184, 166, 0.1) 0%, transparent 50%);
    animation: rotate 30s linear infinite;
  }
}

.particles {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.particle {
  position: absolute;
  background: rgba(102, 126, 234, 0.6);
  border-radius: 50%;
  animation: float-particle linear infinite;
}

.grid-lines {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(102, 126, 234, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(102, 126, 234, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
}

// 导航栏
.home-navbar {
  position: relative;
  z-index: 100;
  height: 72px;
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(20, 184, 166, 0.15);
}

.navbar-container {
  max-width: 1400px;
  height: 100%;
  margin: 0 auto;
  padding: 0 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
}

.logo-icon {
  width: 48px;
  height: 48px;
  color: #14b8a6;
  
  svg {
    width: 100%;
    height: 100%;
  }
}

.logo-text-group {
  display: flex;
  flex-direction: column;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #f1f5f9;
  letter-spacing: 1px;
}

.logo-subtext {
  font-size: 10px;
  color: #64748b;
  letter-spacing: 2px;
  margin-top: 2px;
}

.user-section {
  .user-info {
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;
    padding: 8px 16px;
    border-radius: 12px;
    transition: all 0.3s ease;
    
    &:hover {
      background: rgba(102, 126, 234, 0.1);
    }
  }
  
  .user-avatar {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    font-weight: 600;
  }
  
  .user-name {
    color: #e2e8f0;
    font-weight: 500;
  }
  
  .dropdown-icon {
    color: #94a3b8;
    transition: transform 0.3s ease;
  }
}

// 主内容
.main-content {
  flex: 1;
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 32px;
}

.hero-section {
  text-align: center;
  max-width: 1200px;
}

.hero-content {
  margin-bottom: 60px;
}

.hero-title {
  font-size: 56px;
  font-weight: 800;
  margin-bottom: 24px;
  
  .gradient-text {
    background: linear-gradient(135deg, #667eea 0%, #14b8a6 50%, #667eea 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradient-shift 5s ease infinite;
  }
}

.hero-subtitle {
  font-size: 18px;
  color: #94a3b8;
  line-height: 1.8;
  margin-bottom: 40px;
}

.hero-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 40px;
  
  .stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  
  .stat-number {
    font-size: 32px;
    font-weight: 700;
    color: #14b8a6;
  }
  
  .stat-label {
    font-size: 14px;
    color: #64748b;
    margin-top: 4px;
  }
  
  .stat-divider {
    width: 1px;
    height: 40px;
    background: rgba(100, 116, 139, 0.3);
  }
}

// 节点卡片
.nodes-section {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  max-width: 1000px;
  margin: 0 auto;
}

.node-card {
  position: relative;
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(100, 116, 139, 0.2);
  border-radius: 20px;
  padding: 40px 32px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  
  &:hover:not(.disabled) {
    transform: translateY(-8px);
    border-color: rgba(102, 126, 234, 0.5);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    
    .card-glow {
      opacity: 1;
    }
    
    .enter-btn {
      background: linear-gradient(135deg, #667eea, #764ba2);
      color: white;
    }
  }
  
  &.primary {
    border-color: rgba(102, 126, 234, 0.3);
    
    .node-icon {
      color: #667eea;
    }
  }
  
  &.secondary {
    .node-icon {
      color: #14b8a6;
    }
  }
  
  &.disabled {
    opacity: 0.6;
    cursor: not-allowed;
    
    .node-icon {
      color: #64748b;
    }
  }
}

.card-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at center, rgba(102, 126, 234, 0.1), transparent 70%);
  opacity: 0;
  transition: opacity 0.4s ease;
}

.card-content {
  position: relative;
  z-index: 1;
}

.node-icon {
  margin-bottom: 20px;
}

.node-title {
  font-size: 22px;
  font-weight: 600;
  color: #f1f5f9;
  margin-bottom: 12px;
}

.node-desc {
  font-size: 14px;
  color: #94a3b8;
  line-height: 1.6;
  margin-bottom: 24px;
}

.enter-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: rgba(102, 126, 234, 0.15);
  border-radius: 12px;
  color: #667eea;
  font-weight: 500;
  transition: all 0.3s ease;
  
  .el-icon {
    transition: transform 0.3s ease;
  }
  
  &:hover .el-icon {
    transform: translateX(4px);
  }
}

// 页脚
.home-footer {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 24px;
  color: #64748b;
  font-size: 14px;
}

// 动画
@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes float-particle {
  0%, 100% {
    transform: translateY(0) translateX(0);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100vh) translateX(20px);
    opacity: 0;
  }
}

@keyframes gradient-shift {
  0%, 100% {
    background-position: 0% center;
  }
  50% {
    background-position: 200% center;
  }
}

.animate-fade-in {
  animation: fadeIn 1s ease forwards;
}

.animate-slide-up {
  animation: slideUp 1s ease 0.3s forwards;
  opacity: 0;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 响应式
@media (max-width: 900px) {
  .nodes-section {
    grid-template-columns: 1fr;
    max-width: 400px;
  }
  
  .hero-title {
    font-size: 36px;
  }
  
  .hero-stats {
    flex-direction: column;
    gap: 20px;
    
    .stat-divider {
      width: 60px;
      height: 1px;
    }
  }
}
</style>
