<template>
  <div class="chat-container">
    <Navbar />
    
    <div class="chat-widget">
      <h1>智能对话助手</h1>

      <div class="chat-area" ref="chatArea">
        <div v-for="(msg, index) in conversation" :key="index" class="message">
          <div v-if="msg.type === 'ai'" class="ai-message">
            <span class="ai-icon">🤖</span>
            <div class="message-content">
              <p>{{ msg.text }}</p>
              <div v-if="msg.callApiState === 'success' && msg.showFeedback" class="feedback">
                <div>
                  <label>评分:</label>
                  <span 
                    v-for="star in 5" 
                    :key="star" 
                    @click="handleRatingChange(index, star)"
                    class="star" 
                    :style="{ color: msg.rating >= star ? '#ffc107' : '#e4e5e9' }"
                  >
                    ★
                  </span>
                </div>
                <textarea v-model="msg.feedback" placeholder="请输入您的评价..." />
                <button @click="handleFeedbackSubmit(index)">提交反馈</button>
              </div>
              <button v-if="!msg.showFeedback" @click="reopenFeedback(index)">修改评价</button>
            </div>
          </div>
          <div v-else class="user-message">
            <div class="message-content1">
              <p>{{ msg.text }}</p>
            </div>
          </div>
        </div>

        <div v-if="isLoading" class="loading">
          <span>⏳</span>
          <p>思考中...</p>
        </div>
        <div class="chat-end" ref="chatEnd" />
      </div>

      <div class="input-area">
        <textarea 
          v-model="inputValue" 
          placeholder="输入你的问题..." 
          @input="handleInputChange"
          @keyup.enter.ctrl="callApi"
        />
        <div class="buttons">
          <button @click="callApi" :disabled="isLoading">
            📤 {{ isLoading ? '发送中...' : '发送' }}
          </button>
          <button @click="clearChat">🗑️清除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import axios from 'axios'
import Navbar from '@/components/Navbar.vue'
import request from '@/utils/request'

const inputValue = ref('')
const conversation = reactive([])
const isLoading = ref(false)
const isEditingFeedback = ref(false)
const chatEnd = ref(null)
const chatArea = ref(null)

const handleInputChange = (e) => {
  inputValue.value = e.target.value
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatEnd.value) {
      chatEnd.value.scrollIntoView({ behavior: "smooth" })
    }
  })
}

const callApi = async () => {
  if (!inputValue.value.trim() || isLoading.value) return

  const inputContent = inputValue.value
  inputValue.value = ""
  isLoading.value = true

  conversation.push({ type: 'user', text: inputContent })

  try {
    // 根据实际后端API地址修改
    const response = await request.get('/api/chat/generate', {
      params: { user_input: inputContent }
    })

    const bot_response = response.data?.response || response.data?.data || "No response from API"
    conversation.push({
      type: 'ai',
      text: bot_response,
      rating: 0,
      feedback: "",
      showFeedback: true,
      callApiState: 'success'
    })
  } catch (error) {
    console.error('API 调用失败:', error)
    conversation.push({
      type: 'ai',
      text: "⚠️ 无法从后端获取响应，请检查网络连接或联系管理员",
      rating: 0,
      feedback: "",
      showFeedback: false,
      callApiState: 'failed'
    })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

const handleRatingChange = (index, rating) => {
  isEditingFeedback.value = true
  conversation[index].rating = rating
}

const handleFeedbackSubmit = async (index) => {
  const feedbackData = {
    index: index,
    score: conversation[index].rating,
    feedback: conversation[index].feedback
  }

  try {
    await request.post('/api/chat/feedback', feedbackData)
    console.log('反馈提交成功')
    conversation[index].showFeedback = false
    isEditingFeedback.value = false
    scrollToBottom()
  } catch (error) {
    console.error('反馈提交失败:', error)
    alert('提交反馈失败，请重试！')
  }
}

const reopenFeedback = (index) => {
  isEditingFeedback.value = true
  conversation[index].showFeedback = true
}

const clearChat = async () => {
  conversation.splice(0)
  try {
    await request.post('/api/chat/clear_history')
    console.log("历史清除成功")
  } catch (error) {
    console.error("清空历史失败:", error)
  }
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Roboto', sans-serif;
}

.chat-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  overflow-y: auto;
  padding-bottom: 20px;
}

.chat-widget {
  border: 2px solid #007bff;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  font-family: Arial, sans-serif;
  overflow: hidden;
  position: relative;
  width: 76%;
  margin-left: 12%;
  max-height: calc(100vh - 100px);
  min-height: 600px;
  background-color: #fff;
  margin-top: 80px;
  margin-bottom: 20px;
}

h1 {
  padding: 20px;
  background-color: #fff;
  border-bottom: 1px solid #ddd;
  margin: 0;
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.chat-area {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 20px;
  background-color: #f9f9f9;
  min-height: 0;
  /* 自定义滚动条样式 */
  scrollbar-width: thin;
  scrollbar-color: #c0c4cc #f5f7fa;
}

.chat-area::-webkit-scrollbar {
  width: 8px;
}

.chat-area::-webkit-scrollbar-track {
  background: #f5f7fa;
  border-radius: 4px;
}

.chat-area::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 4px;
  transition: background 0.3s ease;
}

.chat-area::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

.message {
  margin-bottom: 20px;
}

.ai-message {
  justify-content: flex-start;
  display: flex;
  margin-right: 10px;
}

.ai-icon {
  font-size: 24px;
}

.message-content {
  max-width: 60%;
  padding: 12px 16px;
  border-radius: 10px;
  background-color: #f1f1f1;
  color: #333;
  font-size: 16px;
  line-height: 1.5;
  font-weight: 400;
  word-wrap: break-word;
  white-space: pre-wrap;
  text-align: left;
}

.message-content1 {
  max-width: 60%;
  padding: 12px 16px;
  border-radius: 10px;
  background-color: #007bff;
  color: #fff;
  font-size: 16px;
  line-height: 1.5;
  font-weight: 500;
  word-wrap: break-word;
  white-space: pre-wrap;
  text-align: left;
}

.user-message {
  justify-content: flex-end;
  display: flex;
}

.loading {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 20px;
  align-items: flex-start;
}

.loading span {
  font-size: 24px;
}

.chat-end {
  height: 0;
}

.input-area {
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 10px 20px;
  background-color: #fff;
  border-top: 1px solid #ddd;
  flex-shrink: 0;
}

textarea {
  width: 95%;
  padding: 12px 16px;
  border-radius: 4px;
  border: 1px solid #ddd;
  outline: none;
  font-size: 15px;
  font-weight: 400;
  font-family: Arial, sans-serif;
  resize: vertical;
}

.buttons {
  bottom: 20px;
  right: 25px;
  display: flex;
  gap: 5px;
  margin-top: 10px;
  margin-left: 85%;
}

button {
  padding: 8px 16px;
  background-color: #007bff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

button:disabled {
  background-color: #ccc;
}

.feedback {
  margin-top: 10px;
}

.star {
  cursor: pointer;
  font-size: 24px;
}
</style>


