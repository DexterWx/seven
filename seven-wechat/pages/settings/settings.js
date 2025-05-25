const app = getApp()
import API from '../../config/api'

Page({
  data: {
    showPasswordModal: false,
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  },

  // 返回我的页面
  navigateBack() {
    wx.switchTab({ url: '/pages/mine/mine' });
  },

  // 输入原密码
  onOldPasswordInput(e) {
    this.setData({
      oldPassword: e.detail.value
    });
  },

  // 输入新密码
  onNewPasswordInput(e) {
    this.setData({
      newPassword: e.detail.value
    });
  },

  // 输入确认密码
  onConfirmPasswordInput(e) {
    this.setData({
      confirmPassword: e.detail.value
    });
  },

  // 取消修改密码
  cancelChangePassword() {
    this.setData({
      showPasswordModal: false,
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    });
  },

  // 确认修改密码
  confirmChangePassword() {
    const { oldPassword, newPassword, confirmPassword } = this.data;

    if (!oldPassword) {
      wx.showToast({
        title: '请输入原密码',
        icon: 'none'
      });
      return;
    }

    if (!newPassword) {
      wx.showToast({
        title: '请输入新密码',
        icon: 'none'
      });
      return;
    }

    if (newPassword.length < 6) {
      wx.showToast({
        title: '新密码至少6位',
        icon: 'none'
      });
      return;
    }

    if (newPassword !== confirmPassword) {
      wx.showToast({
        title: '两次密码不一致',
        icon: 'none'
      });
      return;
    }

    const phone = wx.getStorageSync('phone');
    if (!phone) {
      wx.showToast({
        title: '用户信息异常',
        icon: 'none'
      });
      return;
    }

    // 调用后端接口修改密码
    wx.request({
      url: API.USER.CHANGE_PASSWORD,
      method: 'POST',
      data: {
        phone: phone,
        old_password: oldPassword,
        new_password: newPassword
      },
      success: (res) => {
        if (res.data && res.data.success) {
          this.setData({
            showPasswordModal: false,
            oldPassword: '',
            newPassword: '',
            confirmPassword: ''
          });
          wx.showToast({
            title: '密码修改成功',
            icon: 'success'
          });
        } else {
          wx.showToast({
            title: res.data.message || '密码修改失败',
            icon: 'none'
          });
        }
      },
      fail: (error) => {
        console.error('修改密码失败:', error);
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        });
      }
    });
  },

  showPasswordModal() {
    this.setData({ showPasswordModal: true })
  }
}); 