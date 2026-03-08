<template>
  <div class="chat-container">
    <div class="chat-box" ref="chatBoxRef">
      <div v-for="(msg, index) in conversation" :key="index" class="message" :class="msg.type">
        <div class="text">{{ msg.text }}</div>

        <div v-if="msg.type === 'ai' && msg.showFeedback" class="feedback">
          <span>评分：</span>
          <input type="range" min="0" max="5" v-model="msg.rating" />
          <input
            v-if="isEditingFeedback"
            v-model="msg.feedback"
            placeholder="请输入反馈"
            @keyup.enter="handleFeedbackSubmit(index)"
          />
          <button @click="handleFeedbackSubmit(index)">提交</button>
        </div> 
      </div>
    </div>

    <div class="input-box">
      <input v-model="inputValue" placeholder="请输入内容..." @keyup.enter="callApi" />
      <button @click="callApi" :disabled="isLoading">发送</button>
      <button @click="clearChat">清空</button>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'

const inputValue = ref('')
const isLoading = ref(false)
const conversation = ref([])
const isEditingFeedback = ref(false)
const chatBoxRef = ref(null)

const callApi = async () => {
  if (!inputValue.value.trim() || isLoading.value) return
  isLoading.value = true

  conversation.value.push({ type: 'user', text: inputValue.value })

  try {
    const response = await axios.get("http://192.168.26.251:8085/generate", {
      params: { user_input: inputValue.value }
    })

    conversation.value.push({
      type: 'ai',
      text: response.data.response || '没有返回内容',
      rating: 0,
      feedback: '',
      showFeedback: true,
      callApiState: 'success',
    })
  } catch (err) {
    console.error(err)
    conversation.value.push({
      type: 'ai',
      text: '请求失败，请稍后重试。',
      rating: 0,
      feedback: '',
      showFeedback: false,
      callApiState: 'failed',
    })
  } finally {
    isLoading.value = false
    inputValue.value = ''
    scrollToBottom()
  }
}

const handleFeedbackSubmit = async (index) => {
  const msg = conversation.value[index]
  const payload = {
    index,
    score: msg.rating,
    feedback: msg.feedback,
  }

  try {
    await axios.post("http://192.168.26.251:8085/generate_pg/feedback", payload)
    msg.showFeedback = false
    isEditingFeedback.value = false
    scrollToBottom()
  } catch (err) {
    alert('提交反馈失败，请重试！')
  }
}

const clearChat = async () => {
  conversation.value = []
  try {
    await axios.post("http://192.168.26.251:8085/clear_history")
  } catch (err) {
    console.error('清空失败', err)
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatBoxRef.value) {
      chatBoxRef.value.scrollTop = chatBoxRef.value.scrollHeight
    }
  })
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.chat-container {
  width: 600px;
  margin: 0 auto;
  font-family: sans-serif;
}

.chat-box {
  height: 400px;
  overflow-y: auto;
  border: 1px solid #ccc;
  padding: 10px;
}

.message {
  margin-bottom: 10px;
}

.message.user .text {
  text-align: right;
  color: #333;
}

.message.ai .text {
  text-align: left;
  color: #1e90ff;
}

.feedback {
  margin-top: 5px;
}

.input-box {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}
input[type="range"] {
  width: 100px;
}
</style>
