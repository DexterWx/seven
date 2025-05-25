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
    // this.loadPaymentInfo(); // 移除重复调用
  },

  onShow() {
    this.loadPaymentInfo();
  },

  // 返回我的页面
  backToMine() {
    wx.reLaunch({
      url: '/pages/mine/mine'
    });
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
        console.log('接口返回：', res.data);
        if (res.data && res.data.success) {
          const data = res.data.data || {};
          const alipay = data.alipay || {};
          const bank = data.bank_card || {};
          console.log('alipayInfo赋值内容:', alipay);
          this.setData({
            bankInfo: {
              bank_card_number: bank.card_number || '',
              bank_holder_name: bank.holder_name || '',
              bank_id_number: bank.id_number || '',
              bank_phone: bank.phone || ''
            },
            alipayInfo: {
              alipay_account: alipay.account || '',
              alipay_holder_name: alipay.holder_name || '',
              alipay_id_number: alipay.id_number || '',
              alipay_phone: alipay.phone || ''
            }
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
        bank_card_number: this.data.bankInfo.bank_card_number || '',
        bank_holder_name: this.data.bankInfo.bank_holder_name || '',
        bank_id_number: this.data.bankInfo.bank_id_number || '',
        bank_phone: this.data.bankInfo.bank_phone || ''
      }
    });
  },

  // 银行卡输入事件
  onBankCardInput(e) {
    this.setData({
      'bankInfo.bank_card_number': e.detail.value
    });
  },

  onBankNameInput(e) {
    this.setData({
      'bankInfo.bank_holder_name': e.detail.value
    });
  },

  onBankIdCardInput(e) {
    this.setData({
      'bankInfo.bank_id_number': e.detail.value
    });
  },

  onBankPhoneInput(e) {
    this.setData({
      'bankInfo.bank_phone': e.detail.value
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

    if (!editBankCard.bank_card_number) {
      wx.showToast({
        title: '请输入银行卡号',
        icon: 'none'
      });
      return;
    }

    if (!editBankCard.bank_holder_name) {
      wx.showToast({
        title: '请输入持卡人姓名',
        icon: 'none'
      });
      return;
    }

    if (!editBankCard.bank_id_number) {
      wx.showToast({
        title: '请输入身份证号',
        icon: 'none'
      });
      return;
    }

    if (!editBankCard.bank_phone) {
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
        alipay_account: this.data.alipayInfo.alipay_account || '',
        alipay_holder_name: this.data.alipayInfo.alipay_holder_name || '',
        alipay_id_number: this.data.alipayInfo.alipay_id_number || '',
        alipay_phone: this.data.alipayInfo.alipay_phone || ''
      }
    });
  },

  // 支付宝输入事件
  onAlipayAccountInput(e) {
    this.setData({
      'alipayInfo.alipay_account': e.detail.value
    });
  },

  onAlipayNameInput(e) {
    this.setData({
      'alipayInfo.alipay_holder_name': e.detail.value
    });
  },

  onAlipayIdCardInput(e) {
    this.setData({
      'alipayInfo.alipay_id_number': e.detail.value
    });
  },

  onAlipayPhoneInput(e) {
    this.setData({
      'alipayInfo.alipay_phone': e.detail.value
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

    if (!editAlipay.alipay_account) {
      wx.showToast({
        title: '请输入支付宝账号',
        icon: 'none'
      });
      return;
    }

    if (!editAlipay.alipay_holder_name) {
      wx.showToast({
        title: '请输入姓名',
        icon: 'none'
      });
      return;
    }

    if (!editAlipay.alipay_id_number) {
      wx.showToast({
        title: '请输入身份证号',
        icon: 'none'
      });
      return;
    }

    if (!editAlipay.alipay_phone) {
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
    const phone = wx.getStorageSync('phone')

    // 验证银行卡信息
    if (this.data.activeTab === 'bank') {
      if (!bankInfo.bank_card_number || !bankInfo.bank_holder_name || !bankInfo.bank_id_number || !bankInfo.bank_phone) {
        wx.showToast({
          title: '请填写完整的银行卡信息',
          icon: 'none'
        })
        return
      }

      // 调用更新银行卡信息API
      wx.request({
        url: API.USER.UPDATE_BANK_CARD(phone),
        method: 'PUT',
        data: {
          bank_card_number: bankInfo.bank_card_number,
          bank_holder_name: bankInfo.bank_holder_name,
          bank_id_number: bankInfo.bank_id_number,
          bank_phone: bankInfo.bank_phone
        },
        success: (res) => {
          if (res.data && res.data.success) {
            wx.showToast({
              title: '保存成功',
              icon: 'success'
            })
          } else {
            wx.showToast({
              title: res.data.message || '保存失败',
              icon: 'none'
            })
          }
        },
        fail: (error) => {
          console.error('保存银行卡信息失败:', error)
          wx.showToast({
            title: '保存失败',
            icon: 'none'
          })
        }
      })
    }

    // 验证支付宝信息
    if (this.data.activeTab === 'alipay') {
      if (!alipayInfo.alipay_account || !alipayInfo.alipay_holder_name || !alipayInfo.alipay_id_number || !alipayInfo.alipay_phone) {
        wx.showToast({
          title: '请填写完整的支付宝信息',
          icon: 'none'
        })
        return
      }

      // 调用更新支付宝信息API
      wx.request({
        url: API.USER.UPDATE_ALIPAY(phone),
        method: 'PUT',
        data: {
          alipay_account: alipayInfo.alipay_account,
          alipay_holder_name: alipayInfo.alipay_holder_name,
          alipay_id_number: alipayInfo.alipay_id_number,
          alipay_phone: alipayInfo.alipay_phone
        },
        success: (res) => {
          if (res.data && res.data.success) {
            wx.showToast({
              title: '保存成功',
              icon: 'success'
            })
          } else {
            wx.showToast({
              title: res.data.message || '保存失败',
              icon: 'none'
            })
          }
        },
        fail: (error) => {
          console.error('保存支付宝信息失败:', error)
          wx.showToast({
            title: '保存失败',
            icon: 'none'
          })
        }
      })
    }
  },

  navigateBack() {
    wx.reLaunch({
      url: '/pages/mine/mine'
    });
  },

  // 银行卡弹窗输入事件
  onEditBankCardNumber(e) {
    this.setData({
      'editBankCard.bank_card_number': e.detail.value
    });
  },
  onEditBankName(e) {
    this.setData({
      'editBankCard.bank_holder_name': e.detail.value
    });
  },
  onEditBankIdCard(e) {
    this.setData({
      'editBankCard.bank_id_number': e.detail.value
    });
  },
  onEditBankPhone(e) {
    this.setData({
      'editBankCard.bank_phone': e.detail.value
    });
  },
  // 支付宝弹窗输入事件
  onEditAlipayAccount(e) {
    this.setData({
      'editAlipay.alipay_account': e.detail.value
    });
  },
  onEditAlipayName(e) {
    this.setData({
      'editAlipay.alipay_holder_name': e.detail.value
    });
  },
  onEditAlipayIdCard(e) {
    this.setData({
      'editAlipay.alipay_id_number': e.detail.value
    });
  },
  onEditAlipayPhone(e) {
    this.setData({
      'editAlipay.alipay_phone': e.detail.value
    });
  },
}); 