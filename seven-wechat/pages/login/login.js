import { post } from '../../utils/request';
import API from '../../config/api';

Page({
  data: {
    isLogin: true,
    phone: '',
    password: '',
    name: ''
  },

  onPhoneInput(e) {
    this.setData({
      phone: e.detail.value
    });
  },

  onPasswordInput(e) {
    this.setData({
      password: e.detail.value
    });
  },

  onNameInput(e) {
    this.setData({
      name: e.detail.value
    });
  },

  switchMode() {
    this.setData({
      isLogin: !this.data.isLogin
    });
  },

  async handleSubmit() {
    const { isLogin, phone, password, name } = this.data;

    if (!phone || !password) {
      wx.showToast({
        title: '请填写完整信息',
        icon: 'none'
      });
      return;
    }

    if (!isLogin && !name) {
      wx.showToast({
        title: '请填写姓名',
        icon: 'none'
      });
      return;
    }

    try {
      if (isLogin) {
        const res = await post(API.USER.LOGIN, { phone, password });
        
        if (res && res.success) {
          wx.showToast({
            title: '登录成功',
            icon: 'success'
          });
          
          // 存储用户信息和手机号
          wx.setStorageSync('userInfo', res.data);
          wx.setStorageSync('phone', phone);
          wx.setStorageSync('isLoggedIn', true);
          wx.setStorageSync('loginTime', Date.now());
          
          // 跳转到首页
          wx.reLaunch({
            url: '/pages/index/index'
          });
        } else {
          throw new Error(res.message || '登录失败');
        }
      } else {
        const res = await post(API.USER.REGISTER, { phone, password, name });
        
        if (res && res.success) {
          wx.showToast({
            title: '注册成功',
            icon: 'success'
          });
          // 注册成功后切换到登录模式
          this.setData({
            isLogin: true
          });
        } else {
          throw new Error(res.message || '注册失败');
        }
      }
    } catch (error) {
      let msg = '操作失败';
      if (error && error.message) {
        msg = error.message;
      } else if (error && error.data && error.data.message) {
        msg = error.data.message;
      } else if (error && error.errMsg) {
        msg = error.errMsg;
      }
      wx.showToast({
        title: msg,
        icon: 'none',
        duration: 3000
      });
      console.error('登录/注册失败', error);
    }
  },

  handleLogin() {
    const { phone, password } = this.data;
    
    if (!phone || !password) {
      wx.showToast({
        title: '请输入手机号和密码',
        icon: 'none'
      });
      return;
    }
    
    wx.request({
      url: API.USER.LOGIN,
      method: 'POST',
      data: {
        phone,
        password
      },
      success: (res) => {
        if (res.data && res.data.success) {
          // 存储用户信息和登录状态
          wx.setStorageSync('phone', phone);
          wx.setStorageSync('userInfo', res.data.data);
          wx.setStorageSync('isLoggedIn', true);
          wx.setStorageSync('loginTime', Date.now());
          
          // 跳转到首页
          wx.switchTab({
            url: '/pages/index/index'
          });
        } else {
          wx.showToast({
            title: res.data.message || '登录失败',
            icon: 'none'
          });
        }
      },
      fail: (error) => {
        console.error('登录请求失败:', error);
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        });
      }
    });
  }
}); 