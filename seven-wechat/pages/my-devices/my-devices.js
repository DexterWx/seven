// my-devices.js
import API from '../../config/api'
import { md5 } from '../../utils/md5'

Page({
  data: {
    devices: [],
    page: 1,
    per_page: 10,
    loading: false,
    noMore: false,
    showReleaseConfirmModal: false,
    releaseDeviceId: '',
    releaseDeviceIndex: null,
    releasePhoneInput: ''
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
      url: `${API.DEVICE.MY_LIST(phone)}?page=${currentPage}&per_page=${this.data.per_page}`,
      method: 'GET',
      timeout: 10000, // 设置10秒超时
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
        
        // 如果是超时错误，显示更友好的提示
        if (error.errMsg && error.errMsg.includes('timeout')) {
          wx.showToast({
            title: '网络请求超时，请重试',
            icon: 'none'
          });
        } else {
          wx.showToast({
            title: '网络请求失败',
            icon: 'none'
          });
        }
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
    const encryptedId = md5(deviceId).substring(0, 12);
    wx.setClipboardData({
      data: encryptedId,
      success: () => {
        wx.showToast({
          title: '已复制设备ID',
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

  showReleaseModal(e) {
    const { id, index } = e.currentTarget.dataset;
    this.setData({
      showReleaseConfirmModal: true,
      releaseDeviceId: id,
      releaseDeviceIndex: index,
      releasePhoneInput: ''
    });
  },

  cancelRelease() {
    this.setData({
      showReleaseConfirmModal: false,
      releaseDeviceId: '',
      releaseDeviceIndex: null,
      releasePhoneInput: ''
    });
  },

  onReleasePhoneInput(e) {
    this.setData({
      releasePhoneInput: e.detail.value
    });
  },

  confirmRelease() {
    const { releasePhoneInput, releaseDeviceId } = this.data;
    const currentPhone = wx.getStorageSync('phone');

    if (!releasePhoneInput) {
      wx.showToast({
        title: '请输入手机号',
        icon: 'none'
      });
      return;
    }

    // 先获取目标用户信息
    wx.request({
      url: API.USER.GET_BY_PHONE(releasePhoneInput),
      method: 'GET',
      success: (res) => {
        if (res.data && res.data.success) {
          const targetUser = res.data.data;
          
          // 验证是否是当前用户的下线
          if (targetUser.superior_phone !== currentPhone) {
            wx.showToast({
              title: '该用户不是您的下线',
              icon: 'none'
            });
            return;
          }

          // 验证通过，调用下放接口
          wx.request({
            url: API.DEVICE.UPDATE_PHONE(releaseDeviceId),
            method: 'PUT',
            data: {
              phone: releasePhoneInput
            },
            success: (res) => {
              this.setData({
                showReleaseConfirmModal: false,
                releaseDeviceId: '',
                releaseDeviceIndex: null,
                releasePhoneInput: ''
              });
              
              if (res.data && res.data.success) {
                wx.showToast({
                  title: '下放成功',
                  icon: 'success'
                });
                this.loadDevices(); // 重新拉取设备列表
              } else {
                wx.showToast({
                  title: res.data.message || '下放失败',
                  icon: 'none'
                });
              }
            },
            fail: (error) => {
              this.setData({
                showReleaseConfirmModal: false,
                releaseDeviceId: '',
                releaseDeviceIndex: null,
                releasePhoneInput: ''
              });
              wx.showToast({
                title: '网络错误',
                icon: 'none'
              });
            }
          });
        } else {
          wx.showToast({
            title: '未找到该用户',
            icon: 'none'
          });
        }
      },
      fail: (error) => {
        wx.showToast({
          title: '网络错误',
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

  handleIncomeDetail(e) {
    const device = e.currentTarget.dataset.device
    wx.navigateTo({
      url: `/pages/device-income/device-income?deviceId=${device.device_id}`
    })
  },

  processDeviceData(devices) {
    return devices.map(device => ({
      ...device,
      display_device_id: md5(device.device_id).substring(0, 12) // 只显示前12位
    }))
  }
}); 