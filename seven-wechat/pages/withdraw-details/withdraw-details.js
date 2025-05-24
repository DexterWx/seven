// withdraw-details.js
import API from '../../config/api'

Page({
  data: {
    withdrawnAmount: '0.00',
    unwithdrawnAmount: '0.00',
    totalAmount: '0.00'
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
          const withdrawn = user.withdrawn_amount || 0;
          const unwithdrawn = user.unwithdrawn_amount || 0;
          const total = withdrawn + unwithdrawn;

          this.setData({
            withdrawnAmount: withdrawn.toFixed(2),
            unwithdrawnAmount: unwithdrawn.toFixed(2),
            totalAmount: total.toFixed(2)
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
  },

  goToWithdraw() {
    wx.showToast({
      title: '联系您的上线或者管理员',
      icon: 'none',
      duration: 2000
    });
  }
}); 