import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { requiresAuth: true, transition: 'fade' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false, transition: 'fade' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false, transition: 'fade' }
  },
  {
    path: '/template',
    name: 'DataResourceHome',
    component: () => import('@/views/template/DataResourceHome.vue'),
    meta: { requiresAuth: true, transition: 'slide' }
  },
  {
    path: '/template/library',
    name: 'DataResourceLibrary',
    component: () => import('@/views/template/DataResourceLibrary.vue'),
    meta: { requiresAuth: true, transition: 'slide' }
  },
  {
    path: '/template/create',
    name: 'DataResourceCreate',
    component: () => import('@/views/template/DataResourceCreate.vue'),
    meta: { requiresAuth: true, transition: 'slide' }
  },
  {
    path: '/template/detail/:id',
    name: 'DataResourceDetail',
    component: () => import('@/views/template/DataResourceDetail.vue'),
    meta: { requiresAuth: true, transition: 'slide' }
  },
  {
    path: '/template/upload',
    name: 'DataResourceUpload',
    component: () => import('@/views/template/DataResourceUpload.vue'),
    meta: { requiresAuth: true, transition: 'slide' }
  },
  {
    path: '/template/data-entry/:moduleId',
    name: 'DataResourceEntry',
    component: () => import('@/views/template/DataResourceEntry.vue'),
    meta: { requiresAuth: true, transition: 'slide' }
  },
  {
    path: '/template/audit',
    name: 'DataResourceAudit',
    component: () => import('@/views/template/DataResourceAudit.vue'),
    meta: { requiresAuth: true, transition: 'slide' }
  },
  {
    path: '/template/field-edit/:templateId',
    name: 'DataResourceFieldEdit',
    component: () => import('@/views/template/DataResourceFieldEdit.vue'),
    meta: { requiresAuth: true, transition: 'slide' }
  },
  {
    path: '/template/statistic',
    name: 'DataStatistic',
    component: () => import('@/views/template/DataStatistic.vue'),
    meta: { requiresAuth: true, transition: 'slide' }
  },
  {
    path: '/template/search',
    name: 'DataSearch',
    component: () => import('@/views/template/DataSearch.vue'),
    meta: { requiresAuth: true, transition: 'slide' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { requiresAuth: true, transition: 'fade' }
  },
  {
    path: '/algorithm',
    name: 'AlgorithmHome',
    component: () => import('@/views/algorithm/WorkspaceHome.vue'),
    meta: { requiresAuth: true, transition: 'slide' }
  },
  {
    path: '/algorithm/chat',
    name: 'Chat',
    component: () => import('@/views/algorithm/Chat.vue'),
    meta: { requiresAuth: true, transition: 'slide' }
  },
  {
    path: '/algorithm/sinter-curve',
    name: 'SinterCurveRecommend',
    component: () => import('@/views/algorithm/SinterCurveRecommend.vue'),
    meta: { requiresAuth: true, transition: 'slide' }
  },
  // 模版管理中心路由
  {
    path: '/tplmanage',
    name: 'TplManageHome',
    component: () => import('@/views/tplmanage/TplManageHome.vue'),
    meta: { requiresAuth: true, transition: 'slide' }
  },
  {
    path: '/tplmanage/my-templates',
    name: 'MyTemplates',
    component: () => import('@/views/tplmanage/MyTemplates.vue'),
    meta: { requiresAuth: true, transition: 'slide' }
  },
  {
    path: '/tplmanage/library',
    name: 'TplLibrary',
    component: () => import('@/views/tplmanage/TplLibrary.vue'),
    meta: { requiresAuth: true, transition: 'slide' }
  },
  {
    path: '/tplmanage/create',
    name: 'TplCreate',
    component: () => import('@/views/tplmanage/TplCreate.vue'),
    meta: { requiresAuth: true, transition: 'slide' }
  },
  {
    path: '/tplmanage/upload',
    name: 'TplUpload',
    component: () => import('@/views/tplmanage/TplUpload.vue'),
    meta: { requiresAuth: true, transition: 'slide' }
  },
  {
    path: '/tplmanage/audit',
    name: 'TplAudit',
    component: () => import('@/views/tplmanage/TplAudit.vue'),
    meta: { requiresAuth: true, transition: 'slide' }
  },
  {
    path: '/tplmanage/data-audit',
    name: 'TplDataAudit',
    component: () => import('@/views/tplmanage/TplDataAudit.vue'),
    meta: { requiresAuth: true, transition: 'slide' }
  },
  {
    path: '/tplmanage/data',
    name: 'TplData',
    component: () => import('@/views/tplmanage/TplData.vue'),
    meta: { requiresAuth: true, transition: 'slide' }
  },
  {
    path: '/tplmanage/edit/:templateId?',
    name: 'TplEdit',
    component: () => import('@/views/tplmanage/TplEdit.vue'),
    meta: { requiresAuth: true, transition: 'slide' }
  },
  {
    path: '/tplmanage/field-edit/:templateId',
    name: 'TplFieldEdit',
    component: () => import('@/views/tplmanage/TplFieldEdit.vue'),
    meta: { requiresAuth: true, transition: 'slide' }
  },
  {
    path: '/tplmanage/detail/:templateId',
    name: 'TplDetail',
    component: () => import('@/views/tplmanage/TplDetail.vue'),
    meta: { requiresAuth: true, transition: 'slide' }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const isLoggedIn = !!token

  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && isLoggedIn) {
    next('/home')
  } else {
    next()
  }
})

export default router
