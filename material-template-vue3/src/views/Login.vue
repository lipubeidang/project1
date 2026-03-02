<template>
  <div class="login-page">
    <!-- 背景 -->
    <div class="background">
      <div class="bg-gradient"></div>
      <div class="bg-grid"></div>
      <div class="bg-glow"></div>
    </div>

    <!-- 主内容 -->
    <div class="login-main">
      <!-- 顶部品牌信息 -->
      <div class="brand-header">
        <div class="brand-icon">
          <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="24" cy="24" r="20" stroke="currentColor" stroke-width="2" fill="none"/>
            <circle cx="24" cy="24" r="8" fill="currentColor"/>
            <path d="M24 4v8M24 36v8M4 24h8M36 24h8" stroke="currentColor" stroke-width="2"/>
            <circle cx="12" cy="12" r="3" fill="currentColor" opacity="0.6"/>
            <circle cx="36" cy="12" r="3" fill="currentColor" opacity="0.6"/>
            <circle cx="12" cy="36" r="3" fill="currentColor" opacity="0.6"/>
            <circle cx="36" cy="36" r="3" fill="currentColor" opacity="0.6"/>
          </svg>
        </div>
        <div class="brand-text">
          <h1>生物医用材料数据资源节点</h1>
        </div>
      </div>

      <!-- 登录卡片 -->
      <div class="login-card">
        <div class="card-header">
          <h2>欢迎回来</h2>
          <p>登录您的账户，探索生物医用材料数据</p>
        </div>

        <el-form 
          ref="formRef" 
          :model="form" 
          :rules="rules" 
          class="login-form"
          @submit.prevent="handleLogin"
        >
          <el-form-item prop="username">
            <div class="input-box">
              <el-icon class="input-icon"><User /></el-icon>
              <input 
                v-model="form.username" 
                type="text"
                placeholder="请输入用户名"
                class="custom-input"
              />
            </div>
          </el-form-item>

          <el-form-item prop="password">
            <div class="input-box">
              <el-icon class="input-icon"><Lock /></el-icon>
              <input 
                v-model="form.password" 
                :type="showPassword ? 'text' : 'password'"
                placeholder="请输入密码"
                class="custom-input"
              />
              <el-icon class="toggle-password" @click="showPassword = !showPassword">
                <View v-if="showPassword" />
                <Hide v-else />
              </el-icon>
            </div>
          </el-form-item>

          <el-form-item prop="email">
            <div class="input-box">
              <el-icon class="input-icon"><Message /></el-icon>
              <input 
                v-model="form.email" 
                type="email"
                placeholder="请输入邮箱"
                class="custom-input"
              />
            </div>
          </el-form-item>

          <el-form-item prop="checkCode">
            <div class="captcha-row">
              <div class="input-box captcha-input">
                <el-icon class="input-icon"><Picture /></el-icon>
                <input 
                  v-model="form.checkCode" 
                  type="text"
                  placeholder="请输入验证码"
                  class="custom-input"
                />
              </div>
              <div class="captcha-image" @click="refreshCaptcha" title="点击刷新验证码">
                <img v-if="captchaUrl" :src="captchaUrl" alt="验证码" />
                <div v-else class="captcha-loading">
                  <el-icon class="is-loading"><Loading /></el-icon>
                </div>
              </div>
            </div>
          </el-form-item>

          <el-form-item class="btn-item">
            <button 
              type="submit"
              class="login-btn"
              :disabled="loading"
              @click.prevent="handleLogin"
            >
              <span v-if="!loading">登 录</span>
              <span v-else>登录中...</span>
            </button>
          </el-form-item>
        </el-form>

        <div class="form-footer">
          <span class="forgot-link" @click="forgotPassword">忘记密码？</span>
          <router-link to="/register" class="register-link">
            还没有账号？<span>立即注册</span>
          </router-link>
        </div>
      </div>

      <!-- 底部信息 -->
      <div class="footer-info">
        <p>© 2024 生物医用材料数据资源节点 · 安全登录</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Message, Picture, Loading, View, Hide } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import request from '@/utils/request'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)
const captchaUrl = ref('')
const showPassword = ref(false)

const form = reactive({
  username: '',
  password: '',
  email: '',
  checkCode: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  checkCode: [
    { required: true, message: '请输入验证码', trigger: 'blur' }
  ]
}

// 获取验证码
const refreshCaptcha = async () => {
  try {
    const timestamp = Date.now()
    const response = await request.get(`/user/checkCode?t=${timestamp}`, {
      responseType: 'blob'
    })
    const blob = new Blob([response.data], { type: 'image/png' })
    if (captchaUrl.value) {
      URL.revokeObjectURL(captchaUrl.value)
    }
    captchaUrl.value = URL.createObjectURL(blob)
  } catch (error) {
    console.error('获取验证码失败:', error)
    captchaUrl.value = `https://dummyimage.com/130x56/0d9488/fff&text=${Math.random().toString(36).slice(2, 6).toUpperCase()}`
  }
}

// 登录处理
const handleLogin = async () => {
  if (!formRef.value) return

  try {
    const valid = await formRef.value.validate().catch(() => false)

    if (!valid) {
      ElMessage.warning('请填写完整的登录信息')
      return
    }

    loading.value = true

    try {
      const response = await request.post('/user/login', form)
      console.log('登录响应:', response.data)

      if (!response || !response.data) {
        ElMessage.error('登录失败，请稍后重试')
        refreshCaptcha()
        return
      }

      const data = response.data

      // 后端统一返回结构：{ code: 1/0, message: string, data: {...} }
      if (data.code === 1 && data.data) {
        const loginInfo = data.data

        // 获取完整的用户信息（包括邮箱）
        try {
          const userInfoResponse = await request.get(`/user/info/${loginInfo.username || form.username}`)
          if (userInfoResponse && userInfoResponse.data && userInfoResponse.data.code === 1 && userInfoResponse.data.data) {
            const fullUserInfo = userInfoResponse.data.data
            userStore.setUser({
              username: fullUserInfo.username || loginInfo.username || form.username,
              name: fullUserInfo.name || loginInfo.name || '',
              email: fullUserInfo.email || form.email || '',
              role: fullUserInfo.role || loginInfo.role || 1,
              token: 'token-' + Date.now()
            })
          } else {
            // 如果获取完整信息失败，使用登录返回的信息
            userStore.setUser({
              username: loginInfo.username || form.username,
              name: loginInfo.name || '',
              email: form.email || '',
              role: loginInfo.role || 1,
              token: 'token-' + Date.now()
            })
          }
        } catch (error) {
          console.error('获取用户信息失败:', error)
          // 如果获取完整信息失败，使用登录返回的信息
          userStore.setUser({
            username: loginInfo.username || form.username,
            name: loginInfo.name || '',
            email: form.email || '',
            role: loginInfo.role || 1,
            token: 'token-' + Date.now()
          })
        }
        
        ElMessage.success('登录成功！')
        router.push('/template')
        return
      }

      // 业务失败
      ElMessage.error(data.message || '登录失败，请检查账号、密码或验证码')
      refreshCaptcha()
    } catch (error) {
      console.error('登录请求失败:', error)
      ElMessage.error('登录失败，请稍后重试')
      refreshCaptcha()
    }
  } finally {
    loading.value = false
  }
}

const forgotPassword = () => {
  ElMessage.info('请联系管理员重置密码')
}

onMounted(() => {
  refreshCaptcha()
})

onBeforeUnmount(() => {
  if (captchaUrl.value) {
    URL.revokeObjectURL(captchaUrl.value)
  }
})
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

// 背景
.background {
  position: fixed;
  inset: 0;
  z-index: 0;
}

.bg-gradient {
  position: absolute;
  inset: 0;
  background: 
    linear-gradient(135deg, rgba(10, 15, 26, 0.55) 0%, rgba(15, 23, 42, 0.50) 50%, rgba(30, 41, 59, 0.55) 100%),
    url('@/public/Gemini_Generated_Image_rflmajrflmajrflm.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(20, 184, 166, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(20, 184, 166, 0.03) 1px, transparent 1px);
  background-size: 60px 60px;
}

.bg-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: 
    radial-gradient(ellipse at 30% 20%, rgba(20, 184, 166, 0.08) 0%, transparent 50%),
    radial-gradient(ellipse at 70% 80%, rgba(6, 182, 212, 0.06) 0%, transparent 50%);
}

// 主内容
.login-main {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  width: 100%;
  max-width: 520px;
  margin-left: 25%;
}

// 品牌头部
.brand-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 48px;
}

.brand-icon {
  width: 64px;
  height: 64px;
  color: #14b8a6;
  flex-shrink: 0;
  
  svg {
    width: 100%;
    height: 100%;
  }
}

.brand-text {
  h1 {
    font-size: 1.5rem;
    font-weight: 700;
    color: #fff;
    margin: 0 0 6px 0;
    white-space: nowrap;
  }
  
  p {
    font-size: 0.75rem;
    color: #14b8a6;
    letter-spacing: 2px;
    margin: 0;
  }
}

// 登录卡片
.login-card {
  width: 100%;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(20, 184, 166, 0.15);
  border-radius: 20px;
  padding: 48px;
  backdrop-filter: blur(20px);
}

.card-header {
  text-align: center;
  margin-bottom: 40px;
  
  h2 {
    font-size: 2rem;
    font-weight: 700;
    color: #fff;
    margin: 0 0 12px 0;
  }
  
  p {
    font-size: 1rem;
    color: rgba(255, 255, 255, 0.5);
    margin: 0;
  }
}

// 表单
.login-form {
  :deep(.el-form-item) {
    margin-bottom: 24px;
    
    .el-form-item__error {
      padding-top: 6px;
      font-size: 12px;
    }
  }
}

// 输入框容器
.input-box {
  position: relative;
  width: 100%;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: rgba(20, 184, 166, 0.3);
    background: rgba(255, 255, 255, 0.08);
  }
  
  &:focus-within {
    border-color: #14b8a6;
    background: rgba(20, 184, 166, 0.08);
    box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.1);
  }
  
  .input-icon {
    position: absolute;
    left: 18px;
    color: #14b8a6;
    font-size: 22px;
    z-index: 1;
  }
  
  .custom-input {
    width: 100%;
    height: 60px;
    padding: 0 18px 0 56px;
    background: transparent;
    border: none;
    outline: none;
    font-size: 1.05rem;
    color: #fff;
    
    &::placeholder {
      color: rgba(255, 255, 255, 0.4);
    }
    
    &:-webkit-autofill,
    &:-webkit-autofill:hover,
    &:-webkit-autofill:focus {
      -webkit-box-shadow: 0 0 0 1000px rgba(20, 184, 166, 0.1) inset !important;
      -webkit-text-fill-color: #fff !important;
      transition: background-color 5000s ease-in-out 0s;
    }
  }
  
  .toggle-password {
    position: absolute;
    right: 18px;
    color: rgba(255, 255, 255, 0.4);
    font-size: 22px;
    cursor: pointer;
    transition: color 0.3s;
    
    &:hover {
      color: #14b8a6;
    }
  }
}

// 验证码行
.captcha-row {
  display: flex;
  gap: 16px;
  
  .captcha-input {
    flex: 1;
  }
}

.captcha-image {
  width: 180px;
  height: 60px;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.3s;
  
  &:hover {
    border-color: #14b8a6;
  }
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.captcha-loading {
  color: rgba(255, 255, 255, 0.4);
}

// 登录按钮
.btn-item {
  margin-top: 36px !important;
  margin-bottom: 0 !important;
}

.login-btn {
  width: 100%;
  height: 60px;
  background: linear-gradient(135deg, #0d9488, #14b8a6);
  border: none;
  border-radius: 12px;
  font-size: 1.15rem;
  font-weight: 600;
  color: #fff;
  cursor: pointer;
  transition: all 0.3s;
  
  &:hover:not(:disabled) {
    background: linear-gradient(135deg, #0f766e, #0d9488);
    transform: translateY(-2px);
    box-shadow: 0 12px 24px rgba(20, 184, 166, 0.3);
  }
  
  &:active:not(:disabled) {
    transform: translateY(0);
  }
  
  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
}

// 底部链接
.form-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 28px;
}

.forgot-link {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: color 0.3s;
  
  &:hover {
    color: #14b8a6;
  }
}

.register-link {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.5);
  text-decoration: none;
  
  span {
    color: #14b8a6;
    font-weight: 600;
    margin-left: 4px;
    
    &:hover {
      text-decoration: underline;
    }
  }
}

// 页脚
.footer-info {
  margin-top: 36px;
  text-align: center;
  
  p {
    font-size: 0.8rem;
    color: rgba(255, 255, 255, 0.3);
    margin: 0;
  }
}

// 响应式
@media (max-width: 520px) {
  .login-main {
    padding: 24px 16px;
  }
  
  .brand-header {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }
  
  .brand-text h1 {
    font-size: 1.25rem;
    white-space: normal;
  }
  
  .login-card {
    padding: 36px 24px;
  }
  
  .card-header h2 {
    font-size: 1.5rem;
  }
  
  .input-box .custom-input {
    height: 54px;
  }
  
  .captcha-image {
    height: 54px;
    width: 120px;
  }
  
  .login-btn {
    height: 54px;
  }
}
</style>
