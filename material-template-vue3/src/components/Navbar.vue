<template>
  <header class="navbar" :class="{ 'scrolled': isScrolled }">
    <div class="navbar-container">
      <!-- Logo -->
      <div class="logo" @click="goHome">
        <div class="logo-icon">
          <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <!-- 数据库形状 -->
            <ellipse cx="24" cy="12" rx="16" ry="6" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M8 12v24c0 3.3 7.2 6 16 6s16-2.7 16-6V12" stroke="currentColor" stroke-width="2" fill="none"/>
            <ellipse cx="24" cy="24" rx="16" ry="6" stroke="currentColor" stroke-width="2" fill="none" opacity="0.5"/>
            <!-- 数据节点 -->
            <circle cx="24" cy="24" r="4" fill="currentColor"/>
            <circle cx="14" cy="20" r="2.5" fill="currentColor" opacity="0.7"/>
            <circle cx="34" cy="20" r="2.5" fill="currentColor" opacity="0.7"/>
            <circle cx="18" cy="30" r="2" fill="currentColor" opacity="0.5"/>
            <circle cx="30" cy="30" r="2" fill="currentColor" opacity="0.5"/>
            <!-- 连接线 -->
            <path d="M16 20l6 3M32 20l-6 3M19 29l4-4M29 29l-4-4" stroke="currentColor" stroke-width="1.5" opacity="0.6"/>
          </svg>
        </div>
        <div class="logo-text-group">
          <h1 class="logo-text">生物医用材料数据资源节点</h1>
        </div>
      </div>

      <!-- 导航菜单 -->
      <nav class="nav-menu">
        <!-- 数据资源中心 - 下拉菜单 -->
        <el-dropdown trigger="hover" @command="handleNavCommand">
          <div class="nav-item dropdown-trigger" :class="{ active: isTemplateActive }">
            <el-icon><Folder /></el-icon>
            <span>数据资源中心</span>
            <el-icon class="arrow-icon"><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="/template">
                <el-icon><HomeFilled /></el-icon>
                首页
              </el-dropdown-item>
              <el-dropdown-item command="/template/library">
                <el-icon><FolderOpened /></el-icon>
                数据资源目录
              </el-dropdown-item>
              <el-dropdown-item command="/template/create">
                <el-icon><DocumentAdd /></el-icon>
                创建数据集
              </el-dropdown-item>
              <el-dropdown-item command="/template/upload">
                <el-icon><Upload /></el-icon>
                上传数据
              </el-dropdown-item>
              <el-dropdown-item command="/template/statistic" divided>
                <el-icon><DataAnalysis /></el-icon>
                数据统计
              </el-dropdown-item>
              <el-dropdown-item command="/template/search">
                <el-icon><Search /></el-icon>
                数据检索
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <!-- 算法中心 - 下拉菜单 -->
        <el-dropdown trigger="hover" @command="handleNavCommand">
          <div class="nav-item dropdown-trigger" :class="{ active: isAlgorithmActive }">
            <el-icon><DataAnalysis /></el-icon>
            <span>算法中心</span>
            <el-icon class="arrow-icon"><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="/algorithm">
                <el-icon><Cpu /></el-icon>
                工作空间
              </el-dropdown-item>
              <el-dropdown-item command="/algorithm/chat">
                <el-icon><ChatLineRound /></el-icon>
                智能对话
              </el-dropdown-item>
              <el-dropdown-item command="/algorithm/sinter-curve">
                <el-icon><TrendCharts /></el-icon>
                机器学习
              </el-dropdown-item>
              <el-dropdown-item command="/algorithm/training" disabled>
                <el-icon><TrendCharts /></el-icon>
                模型训练
              </el-dropdown-item>
              <el-dropdown-item command="/algorithm/predict" disabled>
                <el-icon><MagicStick /></el-icon>
                智能预测
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <!-- 语料中心 - 下拉菜单 -->
        <el-dropdown trigger="hover" @command="handleNavCommand">
          <div class="nav-item dropdown-trigger" :class="{ active: isCorpusActive }">
            <el-icon><Reading /></el-icon>
            <span>语料中心</span>
            <el-icon class="arrow-icon"><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="/corpus" disabled>
                <el-icon><Document /></el-icon>
                语料概览
              </el-dropdown-item>
              <el-dropdown-item command="/corpus/library" disabled>
                <el-icon><Collection /></el-icon>
                语料库
              </el-dropdown-item>
              <el-dropdown-item command="/corpus/annotation" disabled>
                <el-icon><EditPen /></el-icon>
                语料标注
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <!-- 模版管理中心 - 下拉菜单 -->
        <el-dropdown trigger="hover" @command="handleNavCommand">
          <div class="nav-item dropdown-trigger" :class="{ active: isTplManageActive }">
            <el-icon><Coin /></el-icon>
            <span>模版管理中心</span>
            <el-icon class="arrow-icon"><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="/tplmanage/my-templates">
                <el-icon><User /></el-icon>
                我的模版
              </el-dropdown-item>
              <el-dropdown-item command="/tplmanage/library">
                <el-icon><Box /></el-icon>
                模版库
              </el-dropdown-item>
              <el-dropdown-item command="/tplmanage/data">
                <el-icon><DataLine /></el-icon>
                模版数据
              </el-dropdown-item>
              <el-dropdown-item command="/tplmanage/create">
                <el-icon><DocumentAdd /></el-icon>
                新建模版
              </el-dropdown-item>
              <el-dropdown-item command="/tplmanage/upload">
                <el-icon><Upload /></el-icon>
                数据上传
              </el-dropdown-item>
              <el-dropdown-item command="/tplmanage/audit" divided>
                <el-icon><Checked /></el-icon>
                模版审核（审核员）
              </el-dropdown-item>
              <el-dropdown-item command="/tplmanage/data-audit">
                <el-icon><DataAnalysis /></el-icon>
                数据审核（审核员）
              </el-dropdown-item>
              <el-dropdown-item command="/tplmanage/edit">
                <el-icon><EditPen /></el-icon>
                模版修改（审核员）
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </nav>

      <!-- 用户区域 -->
      <div class="user-section">
        <el-dropdown trigger="click" @command="handleCommand">
          <div class="user-info">
            <el-avatar :size="40" :src="avatarUrl" class="user-avatar">
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
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { 
  Aim, HomeFilled, FolderOpened, DocumentAdd, Upload,
  User, SwitchButton, ArrowDown, Checked, Folder,
  DataAnalysis, Cpu, TrendCharts, MagicStick,
  Reading, Document, Collection, EditPen,
  Coin, Monitor, Box, PieChart, DataLine, ChatLineRound, Search
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const isScrolled = ref(false)

const userName = computed(() => userStore.userName || '用户')
const userInitial = computed(() => userName.value.charAt(0).toUpperCase())
const avatarUrl = computed(() => userStore.avatar || '')

// 判断模板管理中心是否激活
const isTemplateActive = computed(() => {
  return route.path.startsWith('/template')
})

// 判断算法中心是否激活
const isAlgorithmActive = computed(() => {
  return route.path.startsWith('/algorithm')
})

// 判断语料中心是否激活
const isCorpusActive = computed(() => {
  return route.path.startsWith('/corpus')
})

// 判断数据中心是否激活
const isDataCenterActive = computed(() => {
  return route.path.startsWith('/datacenter')
})

// 判断模版管理中心是否激活
const isTplManageActive = computed(() => {
  return route.path.startsWith('/tplmanage')
})

const goHome = () => {
  router.push('/home')
}

// 处理导航菜单点击
const handleNavCommand = (command) => {
  if (command) {
    router.push(command)
  }
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

const handleScroll = () => {
  isScrolled.value = window.scrollY > 20
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style lang="scss" scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 72px;
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(20, 184, 166, 0.15);
  z-index: 1000;
  transition: all 0.3s ease;
  
  &.scrolled {
    height: 64px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    background: rgba(15, 23, 42, 0.98);
  }
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
  gap: 14px;
  cursor: pointer;
  transition: transform 0.3s ease;
  
  &:hover {
    transform: scale(1.02);
  }
}

.logo-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #0d9488, #14b8a6);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 6px 20px rgba(20, 184, 166, 0.35);
  transition: all 0.3s ease;
  
  svg {
    width: 28px;
    height: 28px;
  }
  
  .scrolled & {
    width: 42px;
    height: 42px;
    border-radius: 12px;
    
    svg {
      width: 24px;
      height: 24px;
    }
  }
}

.logo-text-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 700;
  color: #fff;
  line-height: 1.2;
}

.logo-subtext {
  font-size: 0.65rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 0.95rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: all 0.3s ease;
  position: relative;
  cursor: pointer;
  
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    width: 0;
    height: 2px;
    background: linear-gradient(90deg, #0d9488, #14b8a6);
    border-radius: 1px;
    transition: all 0.3s ease;
    transform: translateX(-50%);
  }
  
  &:hover {
    color: #14b8a6;
    background: rgba(20, 184, 166, 0.1);
  }
  
  &.active {
    color: #14b8a6;
    background: rgba(20, 184, 166, 0.15);
    
    &::after {
      width: 60%;
    }
  }
  
  .el-icon {
    font-size: 18px;
  }
}

.dropdown-trigger {
  &:hover {
    .arrow-icon {
      transform: rotate(180deg);
    }
  }
}

.arrow-icon {
  font-size: 12px;
  transition: transform 0.3s ease;
  margin-left: 4px;
}

.user-section {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px 6px 6px;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(20, 184, 166, 0.1);
  }
}

.user-avatar {
  border: 2px solid rgba(20, 184, 166, 0.3);
  transition: all 0.3s ease;
  
  .user-info:hover & {
    border-color: #14b8a6;
    transform: scale(1.05);
  }
}

.user-name {
  font-size: 0.95rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.dropdown-icon {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  transition: transform 0.3s ease;
}

// 响应式
@media (max-width: 1024px) {
  .logo-text {
    display: none;
  }
  
  .nav-item span {
    display: none;
  }
  
  .nav-item {
    padding: 12px;
    
    .el-icon {
      font-size: 22px;
    }
  }
}

@media (max-width: 768px) {
  .navbar-container {
    padding: 0 16px;
  }
  
  .user-name {
    display: none;
  }
}
</style>
