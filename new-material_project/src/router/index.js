import Vue from 'vue'
import VueRouter from 'vue-router'
import Register from '../views/Register.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import(/* webpackChunkName: "about" */ '../views/Home.vue')
  },
  {
    path: '/about',
    name: 'about',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import(/* webpackChunkName: "about" */ '../views/Login.vue')
  },
  {
    path: '/password',
    name: 'Password',
    component: () => import(/* webpackChunkName: "about" */ '../views/Password.vue')
  },
  {
    path: '/person',
    name: 'Person',
    component: () => import(/* webpackChunkName: "about" */ '../views/Person.vue')
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import(/* webpackChunkName: "about" */ '../views/Search.vue')
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import(/* webpackChunkName: "about" */ '../views/Chat.vue')
  },
  {
    path: '/displayEchart',
    name: 'DisplayEchart',
    component: () => import(/* webpackChunkName: "about" */ '../views/DisplayEchart.vue')
  },
  {
    path: '/flow',
    name: 'Flow',
    component: () => import(/* webpackChunkName: "about" */ '../views/Flow.vue')
  },
  {
    path: '/paper',
    name: 'Paper',
    component: () => import(/* webpackChunkName: "about" */ '../views/Paper.vue')
  },
  {
    path: '/aboutus',
    name: 'AboutUs',
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutUs.vue')
  },
  {
    path: '/chatagent',
    name: 'ChatAgent',
    component: () => import(/* webpackChunkName: "about" */ '../views/ChatAgent.vue')
  },
  {
    path: '/displayexp',
    name: 'DisplayExp',
    component: () => import(/* webpackChunkName: "about" */ '../views/DisplayExp.vue')
  },
  {
    path: '/template',
    name: 'Template',
    component: () => import(/* webpackChunkName: "about" */ '../views/Template.vue')
  },
  {
    path: '/templatelibrary',
    name: 'TemplateLibrary',
    component: () => import(/* webpackChunkName: "about" */ '../views/TemplateLibrary.vue')
  },
  {
    path: '/template-create',
    name: 'TemplateCreate',
    component: () => import(/* webpackChunkName: "about" */ '../views/TemplateCreate.vue')
  },
  {
    path: '/templatedetail/:id',
    name: 'TemplateDetail',
    component: () => import(/* webpackChunkName: "about" */ '../views/TemplateDetail.vue')
  },
  {
    path: '/template-create',
    name: 'TemplateCreate',
    component: () => import(/* webpackChunkName: "about" */ '../views/TemplateCreate.vue')
  },
  {
    path: '/template-audit',
    name: 'TemplateAudit',
    component: () => import(/* webpackChunkName: "about" */ '../views/TemplateAudit.vue')
  },
  {
    path: '/upload-data',
    name: 'UploadData',
    component: () => import(/* webpackChunkName: "about" */ '../views/UploadData.vue')
  },
  {
    path: '/create-dataset',
    name: 'CreateDataset',
    component: () => import(/* webpackChunkName: "about" */ '../views/CreateDataset.vue')
  },
  {
    path: '/template-modify',
    name: 'TemplateModify',
    component: () => import(/* webpackChunkName: "about" */ '../views/TemplateModify.vue')
  },
  {
    path: '/machine-learning',
    name: 'MachineLearning',
    component: () => import(/* webpackChunkName: "about" */ '../views/MachineLearning.vue')
  },
  {
    path: '/sinter-curve-recommend',
    name: 'SinterCurveRecommend',
    component: () => import(/* webpackChunkName: "about" */ '../views/SinterCurveRecommend.vue')
  },
  {
    path: '/model-training',
    name: 'ModelTraining',
    component: () => import(/* webpackChunkName: "about" */ '../views/ModelTraining.vue')
  },
  {
    path: '/template-field-edit/:templateId/:templateName?',
    name: 'TemplateFieldEdit',
    component: () => import(/* webpackChunkName: "about" */ '../views/TemplateFieldEdit.vue')
  },
  {
    path: '/data-entry/:moduleId/:templateName?',
    name: 'DataEntryPage',
    component: () => import(/* webpackChunkName: "about" */ '../views/DataEntryPage.vue')
  },
  {
    path: '/template-audit-detail/:templateId',
    name: 'TemplateAuditDetail',
    component: () => import(/* webpackChunkName: "about" */ '../views/TemplateAuditDetail.vue')
  },
  
]

const router = new VueRouter({
  routes
})

// 路由守卫：权限控制
router.beforeEach((to, from, next) => {
  // 审核管理页面需要管理员权限（role=2）
  if (to.path === '/template-audit' || to.name === 'TemplateAudit') {
    // 从localStorage获取用户信息
    try {
      const userData = JSON.parse(localStorage.getItem('xm-user') || '{}');
      const userRole = userData.role || userData.logininfo?.type || userData.logininfo?.userType || userData.logininfo?.role || 1;
      
      // 只有管理员（role=2）可以访问审核管理页面
      if (userRole !== 2) {
        // 普通用户尝试访问审核管理页面，重定向到首页
        // 消息提示会在目标组件中显示（TemplateAudit组件的checkAdminPermission方法）
        next('/');
        return;
      }
    } catch (error) {
      console.error('获取用户信息失败:', error);
      // 如果获取用户信息失败，也阻止访问
      next('/');
      return;
    }
  }
  
  next();
})

export default router
