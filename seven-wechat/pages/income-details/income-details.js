// income-details.js
import API from '../../config/api'

Page({
  data: {
    yesterdayIncome: '0.00',
    monthIncome: '0.00',
    teamYesterdayIncome: '0.00',
    teamMonthIncome: '0.00'
  },

  onLoad() {
    this.loadUserData();
  },

  loadUserData() {
    const phone = wx.getStorageSync('phone');
    if (!phone) {
      wx.reLaunch({
        url: '/pages/login/login'
      });
      return;
    }

    wx.request({
      url: API.USER.INFO(phone),
      method: 'GET',
      success: (res) => {
        if (res.data && res.data.success && res.data.data) {
          const user = res.data.data;
          
          this.setData({
            yesterdayIncome: (user.yesterday_income || 0).toFixed(2),
            monthIncome: (user.month_income || 0).toFixed(2),
            teamYesterdayIncome: (user.team_yesterday_income || 0).toFixed(2),
            teamMonthIncome: (user.team_month_income || 0).toFixed(2)
          });
        } else {
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
  },

  backToHome() {
    wx.switchTab({
      url: '/pages/index/index'
    });
  }
}); 