import { defineStore } from 'pinia'
import { reactive } from 'vue'

export const useMlWorkflowStore = defineStore('mlWorkflow', () => {
  // nodeId -> { status: 'idle'|'running'|'completed'|'error', result, error, progress }
  const nodeStates = reactive({})
  const pollingTimers = reactive({})

  function getNodeState(nodeId) {
    return nodeStates[nodeId] || { status: 'idle', result: null, error: null }
  }

  function setNodeState(nodeId, state) {
    nodeStates[nodeId] = { ...getNodeState(nodeId), ...state }
  }

  function startPolling(taskId, nodeId, fetchFn) {
    const timer = setInterval(async () => {
      try {
        const res = await fetchFn(taskId)
        if (res.data.status === 'completed') {
          setNodeState(nodeId, { status: 'completed', result: res.data.result })
          stopPolling(taskId)
        } else if (res.data.status === 'failed') {
          setNodeState(nodeId, { status: 'error', error: res.data.error })
          stopPolling(taskId)
        } else {
          setNodeState(nodeId, { status: 'running', progress: res.data.progress })
        }
      } catch (err) {
        setNodeState(nodeId, { status: 'error', error: err.message })
        stopPolling(taskId)
      }
    }, 1500)
    pollingTimers[taskId] = timer
  }

  function stopPolling(taskId) {
    if (pollingTimers[taskId]) {
      clearInterval(pollingTimers[taskId])
      delete pollingTimers[taskId]
    }
  }

  function stopAllPolling() {
    for (const id of Object.keys(pollingTimers)) {
      clearInterval(pollingTimers[id])
    }
    Object.keys(pollingTimers).forEach(k => delete pollingTimers[k])
  }

  return { nodeStates, getNodeState, setNodeState, startPolling, stopPolling, stopAllPolling }
})
