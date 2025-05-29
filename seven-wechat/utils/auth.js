// auth.js

const checkLoginStatus = () => {
  const isLoggedIn = wx.getStorageSync('isLoggedIn');
  const loginTime = wx.getStorageSync('loginTime');
  const currentTime = Date.now();
  
  // 检查登录状态和登录时间（7天有效期）
  if (isLoggedIn && loginTime && (currentTime - loginTime) < 7 * 24 * 60 * 60 * 1000) {
    return true;
  }
  
  // 清除过期的登录信息
  wx.removeStorageSync('isLoggedIn');
  wx.removeStorageSync('loginTime');
  wx.removeStorageSync('userInfo');
  wx.removeStorageSync('phone');
  return false;
};

const redirectToLogin = () => {
  wx.reLaunch({
    url: '/pages/login/login'
  });
};

const checkAndRedirectToLogin = () => {
  if (!checkLoginStatus()) {
    redirectToLogin();
    return false;
  }
  return true;
};

export default {
  checkLoginStatus,
  redirectToLogin,
  checkAndRedirectToLogin
}; 