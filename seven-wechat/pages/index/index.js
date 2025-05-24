// index.js
import API from '../../config/api'

Page({
  data: {
    userName: '',
    yesterdayIncome: '0.00',
    monthIncome: '0.00',
    totalIncome: '0.00'
  },
  onShow() {
    // 获取本地存储的手机号
    const phone = wx.getStorageSync('phone');
    console.log('首页获取到的手机号:', phone);
    
    if (!phone) {
      // 如果没有手机号，跳转到登录页
      wx.reLaunch({
        url: '/pages/login/login'
      });
      return;
    }
    
    wx.request({
      url: API.USER.INFO(phone),
      method: 'GET',
      success: (res) => {
        console.log('后端返回的数据:', res.data);
        
        if (res.data && res.data.success && res.data.data) {
          const user = res.data.data;
          this.setData({
            userName: user.name || '用户',
            yesterdayIncome: (user.yesterday_income || 0).toFixed(2),
            monthIncome: (user.month_income || 0).toFixed(2),
            totalIncome: ((user.withdrawn_amount || 0) + (user.unwithdrawn_amount || 0)).toFixed(2)
          });
        } else {
          console.error('获取用户信息失败:', res.data);
          wx.showToast({
            title: '获取用户信息失败',
            icon: 'none'
          });
        }
      },
      fail: (error) => {
        console.error('请求失败:', error);
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        });
      }
    });
  }
});
