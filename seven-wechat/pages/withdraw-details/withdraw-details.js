// withdraw-details.js
import API from '../../config/api'

Page({
  data: {
    withdrawnAmount: '0.00',
    unwithdrawnAmount: '0.00',
    totalAmount: '0.00',
    showWithdrawModal: false,
    withdrawAmount: '',
    useBank: false  // 默认使用支付宝
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

  showWithdrawModal() {
    this.setData({
      showWithdrawModal: true,
      withdrawAmount: ''
    });
  },

  cancelWithdraw() {
    this.setData({
      showWithdrawModal: false,
      withdrawAmount: ''
    });
  },

  onWithdrawAmountInput(e) {
    this.setData({
      withdrawAmount: e.detail.value
    });
  },

  onPaymentMethodChange(e) {
    this.setData({
      useBank: e.detail.value === 'bank'
    });
  },

  confirmWithdraw() {
    const amount = parseFloat(this.data.withdrawAmount);
    const unwithdrawn = parseFloat(this.data.unwithdrawnAmount);
    
    if (isNaN(amount) || amount <= 0) {
      wx.showToast({
        title: '请输入有效的提现金额',
        icon: 'none'
      });
      return;
    }

    if (amount > unwithdrawn) {
      wx.showToast({
        title: '提现金额不能大于未提现金额',
        icon: 'none'
      });
      return;
    }

    const phone = wx.getStorageSync('phone');
    if (!phone) {
      wx.reLaunch({
        url: '/pages/login/login'
      });
      return;
    }

    wx.request({
      url: API.USER.APPLY_WITHDRAW(phone),
      method: 'POST',
      data: {
        amount: amount,
        use_bank: this.data.useBank  // 添加支付方式参数
      },
      success: (res) => {
        if (res.data && res.data.success) {
          wx.showToast({
            title: res.data.message || '提现申请已提交',
            icon: 'success'
          });
          
          this.setData({
            showWithdrawModal: false,
            withdrawAmount: ''
          });
          
          // 重新加载用户数据
          this.loadUserData();
        } else {
          wx.showToast({
            title: res.data.message || '提现申请失败',
            icon: 'none'
          });
        }
      },
      fail: (error) => {
        console.error('提现申请失败:', error);
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        });
      }
    });
  }
}); 