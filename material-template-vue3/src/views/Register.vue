<template>
  <div class="register-page">
    <!-- 动态背景 -->
    <div class="background">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
      <div class="mesh-grid"></div>
    </div>

    <!-- 顶部导航 -->
    <header class="header animate-slide-up">
      <div class="logo">
        <div class="logo-icon">
          <el-icon :size="32"><Aim /></el-icon>
        </div>
        <h1 class="logo-text">生物医用材料数据资源节点</h1>
      </div>
    </header>

    <!-- 注册卡片 -->
    <div class="register-container">
      <div class="register-card glass animate-scale-in">
        <!-- 装饰元素 -->
        <div class="card-decoration">
          <div class="deco-ring"></div>
          <div class="deco-dots">
            <span v-for="i in 6" :key="i"></span>
          </div>
        </div>

        <!-- 表单区域 -->
        <div class="card-content">
          <div class="form-header">
            <h2 class="title">创建账户</h2>
            <p class="subtitle">加入我们，开启数据探索之旅</p>
          </div>

          <el-form 
            ref="formRef" 
            :model="form" 
            :rules="rules" 
            class="register-form"
            @submit.prevent="handleRegister"
          >
            <div class="form-row">
              <el-form-item prop="username" class="form-col">
                <el-input 
                  v-model="form.username" 
                  placeholder="用户名"
                  size="large"
                  :prefix-icon="User"
                />
              </el-form-item>

              <el-form-item prop="name" class="form-col">
                <el-input 
                  v-model="form.name" 
                  placeholder="真实姓名"
                  size="large"
                  :prefix-icon="UserFilled"
                />
              </el-form-item>
            </div>

            <el-form-item prop="email">
              <el-input 
                v-model="form.email" 
                placeholder="邮箱地址"
                size="large"
                :prefix-icon="Message"
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input 
                v-model="form.password" 
                type="password"
                placeholder="设置密码（至少6位）"
                size="large"
                show-password
                :prefix-icon="Lock"
              />
            </el-form-item>

            <el-form-item prop="confirmPassword">
              <el-input 
                v-model="form.confirmPassword" 
                type="password"
                placeholder="确认密码"
                size="large"
                show-password
                :prefix-icon="Lock"
              />
            </el-form-item>

            <!-- 密码强度指示器 -->
            <div class="password-strength" v-if="form.password">
              <div class="strength-bar">
                <div 
                  class="strength-fill" 
                  :class="passwordStrengthClass"
                  :style="{ width: passwordStrengthWidth }"
                ></div>
              </div>
              <span class="strength-text" :class="passwordStrengthClass">
                {{ passwordStrengthText }}
              </span>
            </div>

            <el-form-item>
              <el-checkbox v-model="form.agreement" class="agreement-checkbox">
                我已阅读并同意
                <el-link type="primary" :underline="false">《用户协议》</el-link>
                和
                <el-link type="primary" :underline="false">《隐私政策》</el-link>
              </el-checkbox>
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary" 
                size="large" 
                class="register-btn"
                :loading="loading"
                :disabled="!form.agreement"
                @click="handleRegister"
              >
                <span v-if="!loading">立即注册</span>
                <span v-else>注册中...</span>
              </el-button>
            </el-form-item>
          </el-form>

          <div class="form-footer">
            <p>
              已有账号？
              <router-link to="/login" class="login-link">立即登录</router-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, UserFilled, Lock, Message, Aim } from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreement: false
})

// 密码强度计算
const passwordStrength = computed(() => {
  const pwd = form.password
  if (!pwd) return 0
  let strength = 0
  if (pwd.length >= 6) strength++
  if (pwd.length >= 10) strength++
  if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) strength++
  if (/\d/.test(pwd)) strength++
  if (/[!@#$%^&*(),.?":{}|<>]/.test(pwd)) strength++
  return Math.min(strength, 4)
})

const passwordStrengthClass = computed(() => {
  const levels = ['weak', 'weak', 'medium', 'strong', 'very-strong']
  return levels[passwordStrength.value]
})

const passwordStrengthWidth = computed(() => {
  return `${(passwordStrength.value / 4) * 100}%`
})

const passwordStrengthText = computed(() => {
  const texts = ['', '弱', '中等', '强', '非常强']
  return texts[passwordStrength.value]
})

// 验证规则
const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为3-20个字符', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请设置密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 注册处理
const handleRegister = async () => {
  if (!formRef.value) return
  
  if (!form.agreement) {
    ElMessage.warning('请先阅读并同意用户协议')
    return
  }
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      const response = await request.post('/user/register', {
        username: form.username,
        name: form.name,
        email: form.email,
        password: form.password,
        passwordConfirm: form.confirmPassword
      })

      if (!response || !response.data) {
        ElMessage.error('注册失败，请稍后重试')
        return
      }

      const data = response.data

      // 后端统一返回结构：{ code: 1/0, message, data }
      if (data.code === 1) {
        ElMessage.success('注册成功！请登录')
        router.push('/login')
      } else {
        ElMessage.error(data.message || '注册失败')
      }
    } catch (error) {
      console.error('注册请求失败:', error)
      ElMessage.error('注册失败，请稍后重试')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style lang="scss" scoped>
.register-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

// 动态背景
.background {
  position: fixed;
  inset: 0;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
  z-index: 0;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.5;
  animation: float 10s ease-in-out infinite;
  
  &.orb-1 {
    width: 500px;
    height: 500px;
    background: linear-gradient(135deg, #06b6d4, #3b82f6);
    top: -150px;
    right: -150px;
  }
  
  &.orb-2 {
    width: 600px;
    height: 600px;
    background: linear-gradient(135deg, #8b5cf6, #d946ef);
    bottom: -200px;
    left: -200px;
    animation-delay: 3s;
  }
  
  &.orb-3 {
    width: 300px;
    height: 300px;
    background: linear-gradient(135deg, #10b981, #34d399);
    top: 40%;
    right: 20%;
    animation-delay: 5s;
  }
}

.mesh-grid {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: meshMove 20s linear infinite;
  
  @keyframes meshMove {
    0% { transform: translateX(0) translateY(0); }
    100% { transform: translateX(50px) translateY(50px); }
  }
}

// 顶部导航
.header {
  position: relative;
  z-index: 10;
  padding: 24px 48px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #06b6d4, #3b82f6);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 10px 30px rgba(6, 182, 212, 0.4);
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  letter-spacing: 1px;
}

// 注册容器
.register-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  position: relative;
  z-index: 10;
}

.register-card {
  width: 100%;
  max-width: 520px;
  border-radius: 24px;
  overflow: hidden;
  position: relative;
}

.card-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 6px;
  background: linear-gradient(90deg, #06b6d4, #3b82f6, #8b5cf6, #d946ef);
  background-size: 300% 100%;
  animation: gradientShift 4s ease infinite;
}

.deco-ring {
  position: absolute;
  top: -80px;
  right: -80px;
  width: 160px;
  height: 160px;
  border: 3px solid rgba(6, 182, 212, 0.2);
  border-radius: 50%;
  animation: rotate 20s linear infinite;
}

.deco-dots {
  position: absolute;
  bottom: 30px;
  right: 30px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  
  span {
    width: 8px;
    height: 8px;
    background: rgba(6, 182, 212, 0.3);
    border-radius: 50%;
    animation: pulse 2s ease-in-out infinite;
    
    @for $i from 1 through 6 {
      &:nth-child(#{$i}) {
        animation-delay: #{$i * 0.2}s;
      }
    }
  }
}

.card-content {
  padding: 48px;
  position: relative;
}

.form-header {
  text-align: center;
  margin-bottom: 36px;
}

.title {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin-bottom: 8px;
}

.subtitle {
  color: rgba(255, 255, 255, 0.6);
  font-size: 1rem;
}

// 表单样式
.register-form {
  :deep(.el-form-item) {
    margin-bottom: 20px;
  }
  
  :deep(.el-input) {
    --el-input-bg-color: rgba(255, 255, 255, 0.08);
    --el-input-border-color: rgba(255, 255, 255, 0.15);
    --el-input-text-color: white;
    --el-input-placeholder-color: rgba(255, 255, 255, 0.4);
    
    .el-input__wrapper {
      background: var(--el-input-bg-color);
      border-radius: 12px;
      box-shadow: none;
      border: 1px solid var(--el-input-border-color);
      transition: all 0.3s ease;
      
      &:hover, &.is-focus {
        border-color: #06b6d4;
        box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.15);
      }
    }
    
    .el-input__prefix {
      color: rgba(255, 255, 255, 0.5);
    }
  }

  // 处理浏览器自动填充导致的白色背景问题（特别是邮箱输入框）
  :deep(input:-webkit-autofill),
  :deep(input:-webkit-autofill:hover),
  :deep(input:-webkit-autofill:focus) {
    -webkit-box-shadow: 0 0 0 1000px rgba(255, 255, 255, 0.08) inset !important;
    -webkit-text-fill-color: #fff !important;
    transition: background-color 5000s ease-in-out 0s;
    caret-color: #fff;
  }
}

.form-row {
  display: flex;
  gap: 16px;
  
  .form-col {
    flex: 1;
  }
}

// 密码强度
.password-strength {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  margin-top: -12px;
}

.strength-bar {
  flex: 1;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  border-radius: 2px;
  transition: all 0.3s ease;
  
  &.weak { background: #ef4444; }
  &.medium { background: #f59e0b; }
  &.strong { background: #10b981; }
  &.very-strong { background: #06b6d4; }
}

.strength-text {
  font-size: 12px;
  min-width: 50px;
  
  &.weak { color: #ef4444; }
  &.medium { color: #f59e0b; }
  &.strong { color: #10b981; }
  &.very-strong { color: #06b6d4; }
}

.agreement-checkbox {
  :deep(.el-checkbox__label) {
    color: rgba(255, 255, 255, 0.6);
    font-size: 13px;
  }
  
  :deep(.el-link) {
    font-size: 13px;
  }
}

.register-btn {
  width: 100%;
  height: 48px;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(135deg, #06b6d4, #3b82f6);
  border: none;
  transition: all 0.3s ease;
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(6, 182, 212, 0.4);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.form-footer {
  text-align: center;
  margin-top: 24px;
  
  p {
    color: rgba(255, 255, 255, 0.6);
    font-size: 0.875rem;
  }
}

.login-link {
  color: #06b6d4;
  font-weight: 600;
  
  &:hover {
    text-decoration: underline;
  }
}

// 响应式
@media (max-width: 768px) {
  .header {
    padding: 16px 24px;
  }
  
  .logo-text {
    font-size: 1.125rem;
  }
  
  .register-container {
    padding: 20px;
  }
  
  .card-content {
    padding: 32px 24px;
  }
  
  .title {
    font-size: 1.5rem;
  }
  
  .form-row {
    flex-direction: column;
    gap: 0;
  }
}
</style>
