// app.js
import auth from './utils/auth'

App({
  onLaunch() {
    // 检查登录状态
    auth.checkLoginStatus();
  },
  
  globalData: {
    userInfo: null
  }
});
