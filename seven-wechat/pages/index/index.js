// index.js
import API from '../../config/api'

Page({
  data: {
    userName: '',
    yesterdayIncome: '0.00',
    monthIncome: '0.00',
    totalIncome: '0.00',
    totalDevices: '0',
    myDevices: '0',
    subordinateDevices: '0'
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
    
    // 加载用户数据
    this.loadUserData(phone);
    // 加载团队管理数据
    this.loadTeamData(phone);
  },
  
  loadUserData(phone) {
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
  },
  
  loadTeamData(phone) {
    // 获取我的设备数量
    wx.request({
      url: API.DEVICE.MY_COUNT(phone),
      method: 'GET',
      success: (res) => {
        if (res.data && res.data.success) {
          const myDevices = res.data.count || 0;
          this.setData({ myDevices: myDevices.toString() });
          
          // 获取下线设备数量
          wx.request({
            url: API.DEVICE.SUBORDINATE_COUNT(phone),
            method: 'GET',
            success: (res) => {
              if (res.data && res.data.success) {
                const subordinateDevices = res.data.count || 0;
                const totalDevices = myDevices + subordinateDevices;
                this.setData({ 
                  subordinateDevices: subordinateDevices.toString(),
                  totalDevices: totalDevices.toString()
                });
              }
            },
            fail: (error) => {
              console.error('获取下线设备数量失败:', error);
            }
          });
        }
      },
      fail: (error) => {
        console.error('获取我的设备数量失败:', error);
      }
    });
  },
  
  // 跳转到提现详情页面
  goToWithdrawDetails() {
    wx.navigateTo({
      url: '/pages/withdraw-details/withdraw-details'
    });
  },
  
  // 跳转到收益明细页面
  goToDetails() {
    wx.navigateTo({
      url: '/pages/income-details/income-details'
    });
  },
  
  // 跳转到我的终端页面
  goToMyDevices() {
    wx.navigateTo({
      url: '/pages/my-devices/my-devices'
    });
  },
  
  // 跳转到下线终端页面
  goToSubordinateDevices() {
    wx.navigateTo({
      url: '/pages/subordinate-devices/subordinate-devices'
    });
  }
});
