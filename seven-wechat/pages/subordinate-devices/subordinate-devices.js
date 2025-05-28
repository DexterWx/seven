// subordinate-devices.js
import API from '../../config/api'

Page({
  data: {
    devices: [],
    page: 1,
    per_page: 10,
    loading: false,
    noMore: false,
    showCommissionModal: false,
    commissionInput: '',
    currentDeviceId: '',
    currentDeviceIndex: null,
    showRecycleConfirmModal: false,
    recycleDeviceId: '',
    recycleDeviceIndex: null,
    userInfo: null,
    deviceList: [],
    pageSize: 10,
    showRecycleModal: false,
    selectedDeviceId: null,
    selectedDeviceIndex: null
  },

  onLoad() {
    this.loadDevices();
    this.loadUserInfo();
  },

  loadDevices(isLoadMore = false) {
    if (this.data.loading) return;
    
    const phone = wx.getStorageSync('phone');
    if (!phone) {
      wx.reLaunch({
        url: '/pages/login/login'
      });
      return;
    }

    this.setData({ loading: true });

    const currentPage = isLoadMore ? this.data.page + 1 : 1;

    wx.request({
      url: `${API.DEVICE.SUBORDINATE_LIST(phone)}?page=${currentPage}&per_page=${this.data.per_page}`,
      method: 'GET',
      success: (res) => {
        if (res.data && res.data.success) {
          const newDevices = res.data.data || [];
          const updatedDevices = (isLoadMore 
            ? [...this.data.devices, ...newDevices]
            : newDevices
          ).map(d => {
            const rate = Number(d.first_commission_rate);
            return {
              ...d,
              first_commission_rate: rate,
              first_commission_rate_str: isFinite(rate) ? (rate * 100).toFixed(0) + '%' : '0%'
            };
          });
          this.setData({
            devices: updatedDevices,
            page: currentPage,
            loading: false,
            noMore: newDevices.length < this.data.per_page
          });
        } else {
          this.setData({ loading: false });
          wx.showToast({
            title: '获取设备列表失败',
            icon: 'none'
          });
        }
      },
      fail: (error) => {
        this.setData({ loading: false });
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        });
      }
    });
  },

  loadMore() {
    if (!this.data.noMore && !this.data.loading) {
      this.loadDevices(true);
    }
  },

  copyDeviceId(e) {
    const deviceId = e.currentTarget.dataset.id;
    wx.setClipboardData({
      data: deviceId,
      success: () => {
        wx.showToast({
          title: '设备ID已复制',
          icon: 'success'
        });
      },
      fail: () => {
        wx.showToast({
          title: '复制失败',
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

  loadUserInfo() {
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
        if (res.data && res.data.success) {
          this.setData({
            userInfo: res.data.data
          });
        }
      }
    });
  },

  showSetCommissionModal(e) {
    const { id, index } = e.currentTarget.dataset;
    const { userInfo } = this.data;
    
    if (!userInfo) {
      wx.showToast({
        title: '获取用户信息失败',
        icon: 'none'
      });
      return;
    }

    this.setData({
      showCommissionModal: true,
      commissionInput: '',
      currentDeviceId: id,
      currentDeviceIndex: index
    });
  },

  cancelSetCommission() {
    this.setData({
      showCommissionModal: false,
      commissionInput: '',
      currentDeviceId: '',
      currentDeviceIndex: null
    });
  },

  confirmSetCommission() {
    const { commissionInput, currentDeviceId, userInfo } = this.data;
    const rateNum = Number(commissionInput);
    
    if (!commissionInput || isNaN(rateNum)) {
      wx.showToast({
        title: '请输入分成比例',
        icon: 'none'
      });
      return;
    }

    // 检查分成比例是否在允许范围内
    const minRate = userInfo.min_commission_rate * 100;
    const maxRate = userInfo.max_commission_rate * 100;
    
    if (rateNum < minRate || rateNum > maxRate) {
      wx.showToast({
        title: `分成比例必须在${minRate}%-${maxRate}%之间`,
        icon: 'none'
      });
      return;
    }

    wx.request({
      url: API.DEVICE.SET_FIRST_COMMISSION_RATE(currentDeviceId),
      method: 'PUT',
      data: {
        first_commission_rate: rateNum / 100
      },
      success: (res) => {
        this.setData({
          showCommissionModal: false,
          commissionInput: '',
          currentDeviceId: '',
          currentDeviceIndex: null
        });
        if (res.data && res.data.success) {
          wx.showToast({
            title: '设置成功',
            icon: 'success'
          });
          this.loadDevices(); // 重新拉取设备列表
        } else {
          wx.showToast({
            title: res.data.message || '设置失败',
            icon: 'none'
          });
        }
      },
      fail: (error) => {
        this.setData({ showCommissionModal: false });
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
      }
    });
  },

  onCommissionInput(e) {
    this.setData({
      commissionInput: e.detail.value
    });
  },

  showRecycleModal(e) {
    const { id, index } = e.currentTarget.dataset;
    this.setData({
      showRecycleConfirmModal: true,
      recycleDeviceId: id,
      recycleDeviceIndex: index
    });
  },

  cancelRecycle() {
    this.setData({
      showRecycleConfirmModal: false,
      recycleDeviceId: '',
      recycleDeviceIndex: null
    });
  },

  confirmRecycle() {
    const { recycleDeviceId } = this.data;
    const phone = wx.getStorageSync('phone');
    
    if (!phone) {
      wx.reLaunch({
        url: '/pages/login/login'
      });
      return;
    }

    wx.request({
      url: API.DEVICE.UPDATE_PHONE(recycleDeviceId),
      method: 'PUT',
      data: {
        phone: phone
      },
      success: (res) => {
        this.setData({
          showRecycleConfirmModal: false,
          recycleDeviceId: '',
          recycleDeviceIndex: null
        });
        
        if (res.data && res.data.success) {
          wx.showToast({
            title: '回收成功',
            icon: 'success'
          });
          this.loadDevices(); // 重新拉取设备列表
        } else {
          wx.showToast({
            title: res.data.message || '回收失败',
            icon: 'none'
          });
        }
      },
      fail: (error) => {
        this.setData({
          showRecycleConfirmModal: false,
          recycleDeviceId: '',
          recycleDeviceIndex: null
        });
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
      }
    });
  },

  handleIncomeDetail(e) {
    const device = e.currentTarget.dataset.device
    wx.navigateTo({
      url: `/pages/device-income/device-income?deviceId=${device.device_id}`
    })
  },

  onReachBottom() {
    this.loadDevices()
  }
}); 