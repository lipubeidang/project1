<template>
  <div class="template-page">
    <Navbar @dropdown-action="handleDropdownAction" />
    <TemplateNavbar @nav-action="handleNavAction" @audit-action="handleAuditAction" />
    
    <!-- 统计数据 -->
    <div class="statistics">
      <div class="stat-item">
        <div class="number">0</div>
        <div class="label">模版量</div>
      </div>
      <div class="stat-item">
        <div class="number">0</div>
        <div class="label">模版数</div>
      </div>
      <div class="stat-item">
        <div class="number">0</div>
        <div class="label">提集量</div>
      </div>
      <div class="stat-item">
        <div class="number">0</div>
        <div class="label">数据量</div>
      </div>
      <div class="stat-item">
        <div class="number">0</div>
        <div class="label">已发布数据量</div>
      </div>
      <div class="stat-item">
        <div class="number">0</div>
        <div class="label">发布中数据量</div>
      </div>
    </div>

    <!-- 功能卡片 -->
    <div class="feature-cards">
      <div class="card">
        <div class="card-header">
          <span class="title">模版创建</span>
          <span class="number">1</span>
        </div>
        <div class="card-content">
          <p>可自定义模版或根据片段、模版片段用于创建数据集</p>
          <div class="image-container">
            <img src="../assets/code.png" alt="模版创建" class="feature-image">
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <span class="title">模版审核</span>
          <span class="number">2</span>
        </div>
        <div class="card-content">
          <p>审核已创建的模版，确保数据规范性</p>
          <div class="image-container">
            <img src="../assets/mode.jpg" alt="模版审核" class="feature-image">
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <span class="title">数据上传</span>
          <span class="number">3</span>
        </div>
        <div class="card-content">
          <p>根据已定义好的模版创建数据集，并提交数据</p>
          <div class="image-container">
            <img src="../assets/data1.png" alt="数据上传" class="feature-image">
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Navbar from '../components/Navbar.vue'
import TemplateNavbar from '../components/TemplateNavbar.vue'

export default {
  name: 'TemplateHome',
  components: {
    Navbar,
    TemplateNavbar
  },
  methods: {
    handleDropdownAction(action) {
      switch (action) {
        case 'profile':
          this.$router.push('/person')
          break
        case 'logout':
          this.$router.push('/login')
          break
      }
    },
    handleNavAction(action) {
      if (action === 'create') {
        this.$router.push('/template-create').catch(() => {})
      }
    },
    handleAuditAction(action) {
      switch (action) {
        case 'templateAudit':
          this.$router.push('/template-audit').catch(() => {})
          break
        case 'templateStop':
          this.$message.info('模版停用功能开发中')
          break
        default:
          this.$message.info('功能开发中...')
      }
    }
  }
}
</script>

<style scoped>
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

@keyframes glow {
  0%, 100% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.3); }
  50% { box-shadow: 0 0 40px rgba(99, 102, 241, 0.6); }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.template-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-size: 200% 200%;
  animation: gradientShift 15s ease infinite;
  padding-top: 140px;
  position: relative;
  overflow-x: hidden;
}

.template-page::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(255, 132, 228, 0.3) 0%, transparent 50%);
  pointer-events: none;
  z-index: 1;
}

@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.statistics {
  display: flex;
  justify-content: space-around;
  padding: 50px 20px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.9) 0%, rgba(139, 92, 246, 0.9) 100%);
  margin: 20px;
  border-radius: 20px;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(99, 102, 241, 0.4),
              0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  position: relative;
  z-index: 2;
  animation: fadeInUp 0.6s ease;
  overflow: hidden;
}

.statistics::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, 
    transparent 30%, 
    rgba(255, 255, 255, 0.05) 50%, 
    transparent 70%);
  animation: shimmer 3s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-50%) translateY(-50%) rotate(0deg); }
  100% { transform: translateX(-50%) translateY(-50%) rotate(360deg); }
}

.stat-item {
  text-align: center;
  color: white;
  position: relative;
  padding: 15px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(5px);
  transition: all 0.3s ease;
  cursor: pointer;
}

.stat-item:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-5px) scale(1.05);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.stat-item .number {
  font-size: 36px;
  font-weight: 900;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #fff 0%, #e0e7ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
  animation: pulse 2s infinite;
}

.stat-item .label {
  font-size: 14px;
  opacity: 0.95;
  font-weight: 500;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.feature-cards {
  display: flex;
  justify-content: center;
  gap: 40px;
  padding: 40px 20px;
  margin-top: 40px;
  position: relative;
  z-index: 2;
  flex-wrap: wrap;
}

.card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  width: 320px;
  padding: 30px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.6s ease;
  animation-fill-mode: both;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.card:nth-child(1) { animation-delay: 0.1s; }
.card:nth-child(2) { animation-delay: 0.2s; }
.card:nth-child(3) { animation-delay: 0.3s; }

.card::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, 
    transparent 30%, 
    rgba(99, 102, 241, 0.1) 50%, 
    transparent 70%);
  transform: rotate(45deg);
  transition: all 0.6s ease;
  opacity: 0;
}

.card:hover::before {
  opacity: 1;
  animation: shimmer 1.5s infinite;
}

.card:hover {
  transform: translateY(-15px) scale(1.02);
  box-shadow: 0 20px 60px rgba(99, 102, 241, 0.4),
              0 0 0 1px rgba(99, 102, 241, 0.1) inset;
  animation: glow 2s infinite;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  position: relative;
  z-index: 1;
}

.card-header .title {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 0.5px;
}

.card-header .number {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
  transition: all 0.3s ease;
}

.card:hover .card-header .number {
  transform: rotate(360deg) scale(1.1);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
}

.card-content {
  text-align: center;
  position: relative;
  z-index: 1;
}

.card-content p {
  color: #606266;
  margin-bottom: 25px;
  min-height: 45px;
  line-height: 1.6;
  font-size: 14px;
}

.image-container {
  height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 12px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ebf0 100%);
  position: relative;
  transition: all 0.4s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) inset;
}

.card:hover .image-container {
  transform: scale(1.05);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) inset;
}

.feature-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  transition: all 0.4s ease;
  filter: grayscale(0%) brightness(1);
}

.card:hover .feature-image {
  transform: scale(1.1);
  filter: grayscale(0%) brightness(1.1);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .feature-cards {
    flex-direction: column;
    align-items: center;
    gap: 30px;
  }

  .card {
    width: 100%;
    max-width: 500px;
  }
}

@media (max-width: 768px) {
  .statistics {
    flex-wrap: wrap;
    gap: 15px;
    padding: 30px 15px;
  }

  .stat-item {
    width: calc(50% - 10px);
  }

  .stat-item .number {
    font-size: 28px;
  }

  .card {
    width: 100%;
    max-width: 100%;
    margin: 0 10px;
  }

  .feature-cards {
    gap: 20px;
    padding: 20px 10px;
  }
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 10px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  border: 2px solid rgba(255, 255, 255, 0.2);
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}
</style>
