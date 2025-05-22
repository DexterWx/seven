import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import axios from 'axios'

const app = createApp(App)

// 配置axios
axios.defaults.baseURL = 'http://localhost:3000' // 根据实际后端地址修改
app.config.globalProperties.$axios = axios

app.use(ElementPlus)
app.use(router)
app.mount('#app') 