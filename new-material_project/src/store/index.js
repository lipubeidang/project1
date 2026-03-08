import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    userName: '',
    userRole: null // 用户角色：1=普通用户，2=管理员
  },
  getters: {
    getUserName: (state) => state.userName,
    getUserRole: (state) => state.userRole,
    isAdmin: (state) => state.userRole === 2 // 是否为管理员
  },
  mutations: {
    setUserName(state, name) {
      state.userName = name
    },
    setUserRole(state, role) {
      state.userRole = role
    },
    setUserInfo(state, { username, role }) {
      state.userName = username
      state.userRole = role
    }
  },
  actions: {
  },
  modules: {
  }
})
