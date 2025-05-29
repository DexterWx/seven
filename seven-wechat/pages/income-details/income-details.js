// income-details.js
import API from '../../config/api'
import auth from '../../utils/auth'

Page({
  data: {
    type: 'personal',  // personal 或 team
    incomeList: [],
    page: 1,
    pageSize: 20,      // 改为每页10条
    loading: false,
    noMore: false,
    phone: '',
    retryCount: 0,
    maxRetries: 3,
    totalIncome: '0.00',    // 个人总收益
    monthIncome: '0.00',    // 个人月收益
    teamTotalIncome: '0.00', // 团队总收益
    teamMonthIncome: '0.00'  // 团队月收益
  },

  onLoad() {
    if (!auth.checkAndRedirectToLogin()) {
      return;
    }
    // 获取本地存储的手机号
    const phone = wx.getStorageSync('phone')
    if (!phone) {
      wx.reLaunch({
        url: '/pages/login/login'
      })
      return
    }
    this.setData({ phone })
    this.loadUserInfo()
    this.loadIncomeHistory()
  },

  loadUserInfo() {
    wx.request({
      url: API.USER.INFO(this.data.phone),
      method: 'GET',
      success: (res) => {
        if (res.data && res.data.success && res.data.data) {
          const user = res.data.data
          const withdrawn = Number(user.withdrawn_amount || 0)
          const unwithdrawn = Number(user.unwithdrawn_amount || 0)
          const totalIncome = (withdrawn + unwithdrawn).toFixed(2)
          const monthIncome = Number(user.month_income || 0).toFixed(2)
          const teamMonthIncome = Number(user.team_month_income || 0).toFixed(2)
          
          this.setData({
            totalIncome,
            monthIncome,
            teamMonthIncome,
            teamTotalIncome: Number(user.team_total_income || 0).toFixed(2)
          })
        } else {
          wx.showToast({
            title: '获取用户信息失败',
            icon: 'none'
          })
        }
      },
      fail: (error) => {
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        })
      }
    })
  },

  backToHome() {
    wx.navigateBack()
  },

  switchType(e) {
    const type = e.currentTarget.dataset.type
    if (type === this.data.type) return
    
    this.setData({
      type,
      incomeList: [],
      page: 1,
      noMore: false
    })
    this.loadIncomeHistory()
  },

  loadIncomeHistory() {
    if (this.data.loading || this.data.noMore) return
    
    this.setData({ loading: true })
    
    wx.request({
      url: API.USER.INCOME_HISTORY(this.data.phone),
      method: 'GET',
      data: {
        page: this.data.page,
        page_size: this.data.pageSize,
        type: this.data.type
      },
      success: (res) => {
        if (res.data && res.data.success) {
          const { data: newList = [], total = 0 } = res.data.data || {}
          
          // 格式化数据
          const formattedList = newList.map(item => ({
            date: item.date,
            amount: Number(item.amount).toFixed(2),
            date_amount: `${item.date}_${item.amount}`
          }))
          
          const currentTotal = this.data.incomeList.length + formattedList.length
          const noMore = currentTotal >= total || formattedList.length < this.data.pageSize
          
          this.setData({
            incomeList: [...this.data.incomeList, ...formattedList],
            page: this.data.page + 1,
            noMore,
            retryCount: 0
          })
        } else {
          this.handleError('获取收益记录失败')
        }
      },
      fail: () => {
        this.handleError('网络请求失败')
      },
      complete: () => {
        this.setData({ loading: false })
      }
    })
  },

  handleError(message) {
    const retryCount = this.data.retryCount + 1
    if (retryCount <= this.data.maxRetries) {
      this.setData({ retryCount })
      setTimeout(() => {
        this.loadIncomeHistory()
      }, 1000 * retryCount)
    } else {
      wx.showToast({
        title: message,
        icon: 'none'
      })
    }
  },

  onReachBottom() {
    if (!this.data.noMore) {
      this.loadIncomeHistory()
    }
  }
}) 