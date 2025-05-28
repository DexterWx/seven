import API from '../../config/api'

Page({
  data: {
    deviceId: '',
    incomeList: [],
    page: 1,
    pageSize: 10,
    loading: false,
    noMore: false
  },

  onLoad(options) {
    if (options.deviceId) {
      this.setData({
        deviceId: options.deviceId
      })
      this.loadIncomeHistory()
    }
  },

  handleBack() {
    wx.navigateBack({
      delta: 1
    })
  },

  async loadIncomeHistory() {
    if (this.data.loading || this.data.noMore) return

    this.setData({ loading: true })

    try {
      const response = await wx.request({
        url: API.DEVICE.INCOME_HISTORY(this.data.deviceId),
        method: 'GET',
        data: {
          page: this.data.page,
          page_size: this.data.pageSize
        }
      })

      if (response.data && response.data.success) {
        const newList = response.data.data || []
        
        // 如果没有新数据，标记为没有更多
        if (newList.length < this.data.pageSize) {
          this.setData({ noMore: true })
        }

        // 追加新数据到列表
        this.setData({
          incomeList: [...this.data.incomeList, ...newList],
          page: this.data.page + 1
        })
      }
    } catch (error) {
      console.error('获取收益历史失败:', error)
      wx.showToast({
        title: '获取数据失败',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  onReachBottom() {
    this.loadIncomeHistory()
  }
}) 