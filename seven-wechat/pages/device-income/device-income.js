import API from '../../config/api'
import { md5 } from '../../utils/md5'

Page({
  data: {
    deviceId: '',
    displayDeviceId: '',
    incomeList: [],
    page: 1,
    pageSize: 20,
    loading: false,
    noMore: false,
    retryCount: 0,
    maxRetries: 3
  },

  onLoad(options) {
    if (options.deviceId) {
      const encryptedId = md5(options.deviceId).substring(0, 12)
      this.setData({
        deviceId: options.deviceId,
        displayDeviceId: encryptedId
      })
      this.loadIncomeHistory()
    }
  },

  handleBack() {
    wx.navigateBack()
  },

  async loadIncomeHistory() {
    if (this.data.loading || this.data.noMore) return

    this.setData({ loading: true })

    try {
      const response = await new Promise((resolve, reject) => {
        wx.request({
          url: API.DEVICE.INCOME_HISTORY(this.data.deviceId),
          method: 'GET',
          data: {
            page: this.data.page,
            page_size: this.data.pageSize
          },
          success: (res) => {
            resolve(res)
          },
          fail: (error) => {
            // 检查是否是网络错误
            if (error.errMsg && (
              error.errMsg.includes('fail') || 
              error.errMsg.includes('ERR_CONNECTION_RESET') ||
              error.errMsg.includes('timeout')
            )) {
              // 如果还可以重试
              if (this.data.retryCount < this.data.maxRetries) {
                this.setData({
                  retryCount: this.data.retryCount + 1
                })
                // 延迟1秒后重试
                setTimeout(() => {
                  this.loadIncomeHistory()
                }, 1000)
                return
              }
            }
            reject(error)
          },
          timeout: 10000
        })
      })

      if (!response || !response.data) {
        throw new Error('响应数据为空')
      }

      // 重置重试计数
      this.setData({
        retryCount: 0
      })

      if (response.data && response.data.success) {
        const result = response.data.data
        const newList = result.data || []
        
        // 如果没有新的数据或者已经到达总数，说明已经到底了
        const total = result.total || 0
        const currentTotal = (this.data.page - 1) * this.data.pageSize + newList.length
        if (newList.length === 0 || currentTotal >= total) {
          this.setData({ 
            noMore: true,
            loading: false
          })
          if (newList.length === 0) {
            return // 如果没有新数据，直接返回
          }
        }

        const formattedList = newList.map(item => ({
          ...item,
          amount: Number(item.amount).toFixed(2)
        }))

        this.setData({
          incomeList: [...this.data.incomeList, ...formattedList],
          page: this.data.page + 1
        })
      } else {
        wx.showToast({
          title: response.data?.message || '获取数据失败',
          icon: 'none'
        })
      }
    } catch (error) {
      let errorMessage = '获取数据失败'
      if (error.errMsg) {
        if (error.errMsg.includes('ERR_CONNECTION_RESET')) {
          errorMessage = '网络连接断开，请检查网络'
        } else if (error.errMsg.includes('timeout')) {
          errorMessage = '请求超时，请稍后重试'
        } else if (error.errMsg.includes('fail')) {
          errorMessage = '网络请求失败，请检查网络'
        }
      }
      
      wx.showToast({
        title: errorMessage,
        icon: 'none',
        duration: 2000
      })
    } finally {
      if (this.data.retryCount === 0) {
        this.setData({ loading: false })
      }
    }
  },

  onReachBottom() {
    this.loadIncomeHistory()
  }
}) 