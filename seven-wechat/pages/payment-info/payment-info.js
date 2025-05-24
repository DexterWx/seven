import API from '../../config/api'

const app = getApp()

Page({
  data: {
    activeTab: 'bank',
    bankInfo: {
      cardNumber: '',
      name: '',
      idCard: '',
      phone: ''
    },
    alipayInfo: {
      account: '',
      name: '',
      idCard: '',
      phone: ''
    },
    showBankModal: false,
    showAlipayModal: false,
    editBankCard: {},
    editAlipay: {}
  },

  onLoad() {
    this.loadPaymentInfo();
  },

  // 返回我的页面
  backToMine() {
    wx.navigateBack();
  },

  // 加载结算信息
  loadPaymentInfo() {
    const phone = wx.getStorageSync('phone');
    if (!phone) {
      wx.reLaunch({
        url: '/pages/login/login'
      });
      return;
    }

    wx.request({
      url: API.USER.PAYMENT_INFO(phone),
      method: 'GET',
      success: (res) => {
        if (res.data && res.data.success) {
          const data = res.data.data || {};
          this.setData({
            bankInfo: data.bank_card || {},
            alipayInfo: data.alipay || {}
          });
        }
      },
      fail: (error) => {
        console.error('获取结算信息失败:', error);
      }
    });
  },

  // 编辑银行卡
  editBankCard() {
    this.setData({
      showBankModal: true,
      editBankCard: {
        card_number: this.data.bankInfo.card_number || '',
        holder_name: this.data.bankInfo.holder_name || '',
        id_number: this.data.bankInfo.id_number || '',
        phone: this.data.bankInfo.phone || ''
      }
    });
  },

  // 银行卡输入事件
  onBankCardInput(e) {
    this.setData({
      'bankInfo.card_number': e.detail.value
    });
  },

  onBankNameInput(e) {
    this.setData({
      'bankInfo.holder_name': e.detail.value
    });
  },

  onBankIdCardInput(e) {
    this.setData({
      'bankInfo.id_number': e.detail.value
    });
  },

  onBankPhoneInput(e) {
    this.setData({
      'bankInfo.phone': e.detail.value
    });
  },

  // 取消编辑银行卡
  cancelEditBank() {
    this.setData({
      showBankModal: false,
      editBankCard: {}
    });
  },

  // 确认编辑银行卡
  confirmEditBank() {
    const { editBankCard } = this.data;

    if (!editBankCard.card_number) {
      wx.showToast({
        title: '请输入银行卡号',
        icon: 'none'
      });
      return;
    }

    if (!editBankCard.holder_name) {
      wx.showToast({
        title: '请输入持卡人姓名',
        icon: 'none'
      });
      return;
    }

    if (!editBankCard.id_number) {
      wx.showToast({
        title: '请输入身份证号',
        icon: 'none'
      });
      return;
    }

    if (!editBankCard.phone) {
      wx.showToast({
        title: '请输入手机号',
        icon: 'none'
      });
      return;
    }

    const phone = wx.getStorageSync('phone');
    
    wx.request({
      url: API.USER.UPDATE_BANK_CARD(phone),
      method: 'PUT',
      data: editBankCard,
      success: (res) => {
        if (res.data && res.data.success) {
          this.setData({
            bankInfo: editBankCard,
            showBankModal: false,
            editBankCard: {}
          });
          wx.showToast({
            title: '银行卡信息保存成功',
            icon: 'success'
          });
        } else {
          wx.showToast({
            title: res.data.message || '保存失败',
            icon: 'none'
          });
        }
      },
      fail: (error) => {
        console.error('保存银行卡信息失败:', error);
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        });
      }
    });
  },

  // 编辑支付宝
  editAlipay() {
    this.setData({
      showAlipayModal: true,
      editAlipay: {
        account: this.data.alipayInfo.account || '',
        holder_name: this.data.alipayInfo.holder_name || '',
        id_number: this.data.alipayInfo.id_number || '',
        phone: this.data.alipayInfo.phone || ''
      }
    });
  },

  // 支付宝输入事件
  onAlipayAccountInput(e) {
    this.setData({
      'alipayInfo.account': e.detail.value
    });
  },

  onAlipayNameInput(e) {
    this.setData({
      'alipayInfo.holder_name': e.detail.value
    });
  },

  onAlipayIdCardInput(e) {
    this.setData({
      'alipayInfo.id_number': e.detail.value
    });
  },

  onAlipayPhoneInput(e) {
    this.setData({
      'alipayInfo.phone': e.detail.value
    });
  },

  // 取消编辑支付宝
  cancelEditAlipay() {
    this.setData({
      showAlipayModal: false,
      editAlipay: {}
    });
  },

  // 确认编辑支付宝
  confirmEditAlipay() {
    const { editAlipay } = this.data;

    if (!editAlipay.account) {
      wx.showToast({
        title: '请输入支付宝账号',
        icon: 'none'
      });
      return;
    }

    if (!editAlipay.holder_name) {
      wx.showToast({
        title: '请输入姓名',
        icon: 'none'
      });
      return;
    }

    if (!editAlipay.id_number) {
      wx.showToast({
        title: '请输入身份证号',
        icon: 'none'
      });
      return;
    }

    if (!editAlipay.phone) {
      wx.showToast({
        title: '请输入手机号',
        icon: 'none'
      });
      return;
    }

    const phone = wx.getStorageSync('phone');
    
    wx.request({
      url: API.USER.UPDATE_ALIPAY(phone),
      method: 'PUT',
      data: editAlipay,
      success: (res) => {
        if (res.data && res.data.success) {
          this.setData({
            alipayInfo: editAlipay,
            showAlipayModal: false,
            editAlipay: {}
          });
          wx.showToast({
            title: '支付宝信息保存成功',
            icon: 'success'
          });
        } else {
          wx.showToast({
            title: res.data.message || '保存失败',
            icon: 'none'
          });
        }
      },
      fail: (error) => {
        console.error('保存支付宝信息失败:', error);
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        });
      }
    });
  },

  switchTab(e) {
    const tab = e.currentTarget.dataset.tab
    this.setData({
      activeTab: tab
    })
  },

  savePaymentInfo() {
    const { bankInfo, alipayInfo } = this.data

    // 验证银行卡信息
    if (this.data.activeTab === 'bank') {
      if (!bankInfo.card_number || !bankInfo.holder_name || !bankInfo.id_number || !bankInfo.phone) {
        wx.showToast({
          title: '请填写完整的银行卡信息',
          icon: 'none'
        })
        return
      }
    }

    // 验证支付宝信息
    if (this.data.activeTab === 'alipay') {
      if (!alipayInfo.account || !alipayInfo.holder_name || !alipayInfo.id_number || !alipayInfo.phone) {
        wx.showToast({
          title: '请填写完整的支付宝信息',
          icon: 'none'
        })
        return
      }
    }

    // 保存到本地存储
    wx.setStorageSync('bankInfo', bankInfo)
    wx.setStorageSync('alipayInfo', alipayInfo)

    wx.showToast({
      title: '保存成功',
      icon: 'success'
    })
  },

  navigateBack() {
    wx.navigateBack()
  },

  // 银行卡弹窗输入事件
  onEditBankCardNumber(e) {
    this.setData({
      'editBankCard.card_number': e.detail.value
    });
  },
  onEditBankName(e) {
    this.setData({
      'editBankCard.holder_name': e.detail.value
    });
  },
  onEditBankIdCard(e) {
    this.setData({
      'editBankCard.id_number': e.detail.value
    });
  },
  onEditBankPhone(e) {
    this.setData({
      'editBankCard.phone': e.detail.value
    });
  },
  // 支付宝弹窗输入事件
  onEditAlipayAccount(e) {
    this.setData({
      'editAlipay.account': e.detail.value
    });
  },
  onEditAlipayName(e) {
    this.setData({
      'editAlipay.holder_name': e.detail.value
    });
  },
  onEditAlipayIdCard(e) {
    this.setData({
      'editAlipay.id_number': e.detail.value
    });
  },
  onEditAlipayPhone(e) {
    this.setData({
      'editAlipay.phone': e.detail.value
    });
  },
}); 