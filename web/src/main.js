import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import axios from 'axios'

const app = createApp(App)

// 配置axios
axios.defaults.baseURL = 'http://localhost:5001/api' // 修改为正确的后端地址
app.config.globalProperties.$axios = axios

app.use(ElementPlus)
app.use(router)
app.mount('#app') 