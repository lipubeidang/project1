import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const userName = ref('')
  const userRole = ref(1) // 1=普通用户，2=管理员
  const token = ref('')
  const avatar = ref('')
  const name = ref('')
  const email = ref('')

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userRole.value === 2)

  function setUser(userInfo) {
    userName.value = userInfo.username || ''
    userRole.value = userInfo.role || 1
    token.value = userInfo.token || ''
    avatar.value = userInfo.avatar || ''
    name.value = userInfo.name || ''
    email.value = userInfo.email || ''
    
    // 持久化存储
    localStorage.setItem('token', token.value)
    localStorage.setItem('userInfo', JSON.stringify({
      username: userName.value,
      role: userRole.value,
      avatar: avatar.value,
      name: name.value,
      email: email.value
    }))
  }

  function initUser() {
    const storedToken = localStorage.getItem('token')
    const storedUserInfo = localStorage.getItem('userInfo')
    
    if (storedToken && storedUserInfo) {
      token.value = storedToken
      try {
        const userInfo = JSON.parse(storedUserInfo)
        userName.value = userInfo.username || ''
        userRole.value = userInfo.role || 1
        avatar.value = userInfo.avatar || ''
        name.value = userInfo.name || ''
        email.value = userInfo.email || ''
      } catch (e) {
        console.error('解析用户信息失败', e)
      }
    }
  }

  function logout() {
    userName.value = ''
    userRole.value = 1
    token.value = ''
    avatar.value = ''
    name.value = ''
    email.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  return {
    userName,
    userRole,
    token,
    avatar,
    name,
    email,
    isLoggedIn,
    isAdmin,
    setUser,
    initUser,
    logout
  }
})
