// pages/mine/mine.js
import API from '../../config/api'

Page({

    /**
     * 页面的初始数据
     */
    data: {
        userName: '用户',
        userPhone: '',
        superiorPhone: '',
        showBindModal: false,
        inputPhone: ''
    },

    /**
     * 生命周期函数--监听页面加载
     */
    onLoad(options) {
        // 这里可以加载用户信息
    },

    /**
     * 生命周期函数--监听页面初次渲染完成
     */
    onReady() {

    },

    /**
     * 生命周期函数--监听页面显示
     */
    onShow() {
        this.loadUserInfo();
    },

    /**
     * 生命周期函数--监听页面隐藏
     */
    onHide() {

    },

    /**
     * 生命周期函数--监听页面卸载
     */
    onUnload() {

    },

    /**
     * 页面相关事件处理函数--监听用户下拉动作
     */
    onPullDownRefresh() {

    },

    /**
     * 页面上拉触底事件的处理函数
     */
    onReachBottom() {

    },

    /**
     * 用户点击右上角分享
     */
    onShareAppMessage() {

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
                if (res.data && res.data.success && res.data.data) {
                    const user = res.data.data;
                    this.setData({
                        userName: user.name || '用户',
                        userPhone: phone,
                        superiorPhone: user.superior_phone || ''
                    });
                }
            },
            fail: (error) => {
                console.error('获取用户信息失败:', error);
            }
        });
    },

    // 跳转到设置页面
    goToSettings() {
        wx.navigateTo({
            url: '/pages/settings/settings'
        });
    },

    // 绑定上线
    bindSuperior() {
        if (this.data.superiorPhone) {
            // 已绑定，不允许修改
            wx.showToast({
                title: '已绑定上线，不可修改',
                icon: 'none'
            });
            return;
        }
        
        this.setData({
            showBindModal: true,
            inputPhone: ''
        });
    },

    // 输入电话号码
    onPhoneInput(e) {
        this.setData({
            inputPhone: e.detail.value
        });
    },

    // 取消绑定
    cancelBind() {
        this.setData({
            showBindModal: false,
            inputPhone: ''
        });
    },

    // 确认绑定
    confirmBind() {
        const phone = this.data.inputPhone.trim();
        if (!phone) {
            wx.showToast({
                title: '请输入上线电话',
                icon: 'none'
            });
            return;
        }

        if (phone === this.data.userPhone) {
            wx.showToast({
                title: '不能绑定自己',
                icon: 'none'
            });
            return;
        }

        // 调用后端接口绑定上线
        wx.request({
            url: API.USER.BIND_SUPERIOR,
            method: 'POST',
            data: {
                phone: this.data.userPhone,
                superior_phone: phone
            },
            success: (res) => {
                if (res.data && res.data.success) {
                    this.setData({
                        superiorPhone: phone,
                        showBindModal: false,
                        inputPhone: ''
                    });
                    wx.showToast({
                        title: '绑定成功',
                        icon: 'success'
                    });
                } else {
                    wx.showToast({
                        title: res.data.message || '绑定失败',
                        icon: 'none'
                    });
                }
            },
            fail: (error) => {
                console.error('绑定失败:', error);
                wx.showToast({
                    title: '网络请求失败',
                    icon: 'none'
                });
            }
        });
    },

    // 联系我们
    contactUs() {
        wx.showModal({
            title: '联系我们',
            content: '客服电话：13940598165',
            showCancel: true,
            cancelText: '取消',
            confirmText: '拨打',
            success: (res) => {
                if (res.confirm) {
                    wx.makePhoneCall({
                        phoneNumber: '13940598165'
                    });
                }
            }
        });
    },

    // 跳转到结算信息页面
    goToPayment() {
        wx.navigateTo({
            url: '/pages/payment-info/payment-info'
        });
    },

    // 退出登录
    logout() {
        wx.showModal({
            title: '退出登录',
            content: '确定要退出登录吗？',
            success: (res) => {
                if (res.confirm) {
                    wx.clearStorageSync();
                    wx.reLaunch({
                        url: '/pages/login/login'
                    });
                }
            }
        });
    }
})