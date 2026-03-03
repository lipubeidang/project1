import axios from 'axios'

const BASE_URL = 'http://localhost:8000'

export const getSessionId = () => {
  let sid = sessionStorage.getItem('ml_session_id')
  if (!sid) {
    sid = 'sess_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8)
    sessionStorage.setItem('ml_session_id', sid)
  }
  return sid
}

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 120000,
})

// Automatically attach session id to every request
client.interceptors.request.use(config => {
  config.headers['X-Session-Id'] = getSessionId()
  return config
})

export const mlApi = {
  // ── Dataset ──
  uploadDataset(file) {
    const fd = new FormData()
    fd.append('file', file)
    return client.post('/ml/upload-dataset', fd)
  },
  listDatasets() {
    return client.get('/ml/datasets')
  },
  deleteDataset(datasetId) {
    return client.delete(`/ml/datasets/${datasetId}`)
  },
  deleteSession(sessionId) {
    return client.delete(`/ml/session/${sessionId}`)
  },
  cleanSession(sessionId) {
    // sendBeacon is reliable even when the tab is closing
    navigator.sendBeacon(`${BASE_URL}/ml/session/${sessionId}/cleanup`, '')
  },

  // ── ML Pipeline ──
  selectFeatures(data) {
    return client.post('/ml/select-features', data)
  },
  train(data) {
    return client.post('/ml/train', data)
  },
  getTask(taskId) {
    return client.get(`/ml/task/${taskId}`)
  },
  predict(data) {
    return client.post('/ml/predict', data)
  },
  getVisualization(modelId, chartType) {
    return client.get(`/ml/model/${modelId}/visualization`, {
      params: { chart_type: chartType },
    })
  },
}
