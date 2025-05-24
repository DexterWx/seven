// subordinate-devices.js
import API from '../../config/api'

Page({
  data: {
    devices: [],
    page: 1,
    per_page: 10,
    loading: false,
    noMore: false
  },

  onLoad() {
    this.loadDevices();
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
          const updatedDevices = isLoadMore 
            ? [...this.data.devices, ...newDevices]
            : newDevices;
          
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
        console.error('请求失败:', error);
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
  }
}); 