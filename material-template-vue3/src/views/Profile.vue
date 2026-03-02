<template>
  <div class="profile-page">
    <Navbar />
    
    <div class="page-container">
      <div class="profile-content">
        <!-- 用户卡片 -->
        <div class="user-card animate-scale-in">
          <div class="card-bg">
            <div class="bg-pattern"></div>
          </div>
          <div class="card-content">
            <div class="avatar-section">
              <el-avatar :size="120" :src="userInfo.avatar" class="user-avatar">
                {{ userInfo.name?.charAt(0) || 'U' }}
              </el-avatar>
              <el-button class="change-avatar-btn" :icon="Camera" circle />
            </div>
            <h2 class="user-name">{{ userInfo.name || '用户' }}</h2>
            <p class="user-role">
              <el-tag :type="isAdmin ? 'danger' : 'primary'" effect="plain">
                {{ isAdmin ? '管理员' : '普通用户' }}
              </el-tag>
            </p>
            <div class="user-stats">
            <div class="stat">
              <span class="stat-value">12</span>
              <span class="stat-label">创建数据集</span>
            </div>
              <div class="divider"></div>
              <div class="stat">
                <span class="stat-value">156</span>
                <span class="stat-label">上传数据</span>
              </div>
              <div class="divider"></div>
              <div class="stat">
                <span class="stat-value">28</span>
                <span class="stat-label">获得点赞</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 信息表单 -->
        <div class="info-card animate-slide-up delay-1">
          <div class="card-header">
            <h3>
              <el-icon><User /></el-icon>
              个人信息
            </h3>
            <el-button type="primary" text @click="toggleEdit">
              {{ isEditing ? '取消编辑' : '编辑信息' }}
            </el-button>
          </div>
          
          <el-form 
            ref="formRef"
            :model="userInfo" 
            :rules="rules"
            label-width="100px"
            :disabled="!isEditing"
            class="info-form"
          >
            <div class="form-grid">
              <el-form-item label="用户名" prop="username">
                <el-input v-model="userInfo.username" :disabled="true" />
              </el-form-item>
              
              <el-form-item label="姓名" prop="name">
                <el-input v-model="userInfo.name" placeholder="请输入姓名" />
              </el-form-item>
              
              <el-form-item label="邮箱" prop="email">
                <el-input v-model="userInfo.email" placeholder="请输入邮箱" />
              </el-form-item>
              
              <el-form-item label="手机号" prop="phone">
                <el-input v-model="userInfo.phone" placeholder="请输入手机号" />
              </el-form-item>
            </div>
            
            <el-form-item label="个人简介" prop="bio">
              <el-input 
                v-model="userInfo.bio" 
                type="textarea" 
                :rows="4"
                placeholder="请输入个人简介"
                resize="none"
              />
            </el-form-item>
            
            <div v-if="isEditing" class="form-actions">
              <el-button @click="cancelEdit">取消</el-button>
              <el-button type="primary" @click="saveInfo">保存修改</el-button>
            </div>
          </el-form>
        </div>

        <!-- 安全设置 -->
        <div class="security-card animate-slide-up delay-2">
          <div class="card-header">
            <h3>
              <el-icon><Lock /></el-icon>
              安全设置
            </h3>
          </div>
          
          <div class="security-list">
            <div class="security-item">
              <div class="item-info">
                <span class="item-title">登录密码</span>
                <span class="item-desc">定期更改密码有助于保护账户安全</span>
              </div>
              <el-button type="primary" text @click="changePassword">
                修改密码
              </el-button>
            </div>
            
            <div class="security-item">
              <div class="item-info">
                <span class="item-title">绑定邮箱</span>
                <span class="item-desc">{{ userInfo.email || '未绑定' }}</span>
              </div>
              <el-button type="primary" text>
                {{ userInfo.email ? '更换' : '绑定' }}
              </el-button>
            </div>
            
            <div class="security-item">
              <div class="item-info">
                <span class="item-title">绑定手机</span>
                <span class="item-desc">{{ userInfo.phone || '未绑定' }}</span>
              </div>
              <el-button type="primary" text>
                {{ userInfo.phone ? '更换' : '绑定' }}
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="400px">
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
        <el-form-item label="当前密码" prop="oldPassword">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPassword">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Lock, Camera } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import Navbar from '@/components/Navbar.vue'

const userStore = useUserStore()

const formRef = ref(null)
const passwordFormRef = ref(null)
const isEditing = ref(false)
const passwordDialogVisible = ref(false)

const isAdmin = computed(() => userStore.isAdmin)

const userInfo = reactive({
  username: userStore.userName || '',
  name: userStore.name || '',
  email: userStore.email || '',
  phone: '',
  bio: '',
  avatar: userStore.avatar || ''
})

// 同步 store 中的用户信息到 userInfo
const syncUserInfo = () => {
  userInfo.username = userStore.userName || ''
  userInfo.name = userStore.name || ''
  userInfo.email = userStore.email || ''
  userInfo.avatar = userStore.avatar || ''
}

// 监听 store 变化
watch([() => userStore.userName, () => userStore.name, () => userStore.email, () => userStore.avatar], () => {
  syncUserInfo()
})

onMounted(() => {
  syncUserInfo()
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  oldPassword: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const toggleEdit = () => {
  isEditing.value = !isEditing.value
}

const cancelEdit = () => {
  isEditing.value = false
  // 重置表单数据到 store 中的值
  syncUserInfo()
}

const saveInfo = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate((valid) => {
    if (valid) {
      // 保存逻辑
      ElMessage.success('信息更新成功')
      isEditing.value = false
    }
  })
}

const changePassword = () => {
  passwordDialogVisible.value = true
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
}

const submitPassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate((valid) => {
    if (valid) {
      // 提交密码修改
      ElMessage.success('密码修改成功')
      passwordDialogVisible.value = false
    }
  })
}
</script>

<style lang="scss" scoped>
.profile-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  background-attachment: fixed;
}

.page-container {
  padding-top: 72px;
  min-height: 100vh;
}

.profile-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 24px;
}

// 用户卡片
.user-card {
  background: white;
  border-radius: 24px;
  overflow: hidden;
  margin-bottom: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.card-bg {
  height: 120px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  position: relative;
  
  .bg-pattern {
    position: absolute;
    inset: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  }
}

.card-content {
  text-align: center;
  padding: 0 32px 32px;
  margin-top: -60px;
  position: relative;
}

.avatar-section {
  position: relative;
  display: inline-block;
}

.user-avatar {
  border: 4px solid white;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.change-avatar-btn {
  position: absolute;
  bottom: 4px;
  right: 4px;
  background: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.user-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin: 16px 0 8px;
}

.user-role {
  margin-bottom: 24px;
}

.user-stats {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 24px;
  padding-top: 24px;
  border-top: 1px solid #f1f5f9;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 0.875rem;
  color: #64748b;
}

.divider {
  width: 1px;
  height: 40px;
  background: #e2e8f0;
}

// 信息卡片
.info-card,
.security-card {
  background: white;
  border-radius: 20px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f1f5f9;
  
  h3 {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.125rem;
    font-weight: 600;
    color: #1e293b;
    
    .el-icon {
      color: #667eea;
    }
  }
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0 24px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #f1f5f9;
}

// 安全设置
.security-list {
  display: flex;
  flex-direction: column;
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  border-bottom: 1px solid #f1f5f9;
  
  &:last-child {
    border-bottom: none;
  }
}

.item-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-title {
  font-weight: 500;
  color: #1e293b;
}

.item-desc {
  font-size: 0.875rem;
  color: #64748b;
}

// 响应式
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .user-stats {
    gap: 16px;
  }
  
  .stat-value {
    font-size: 1.25rem;
  }
}
</style>
