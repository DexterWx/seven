const BASE_URL = 'http://localhost:5001/api';
// const BASE_URL = 'http://192.168.40.1:5001/api';


const API = {
  BASE_URL,
  // 用户相关接口
  USER: {
    REGISTER: `${BASE_URL}/wechat/users/register`,
    LOGIN: `${BASE_URL}/wechat/users/login`,
    INFO: function(phone) {
      return `${BASE_URL}/wechat/users/${phone}`;
    },
    GET_BY_PHONE: function(phone) {
      return `${BASE_URL}/wechat/users/${phone}`;
    },
    BIND_SUPERIOR: `${BASE_URL}/wechat/users/bind-superior`,
    CHANGE_PASSWORD: `${BASE_URL}/wechat/users/change-password`,
    PAYMENT_INFO: function(phone) {
      return `${BASE_URL}/wechat/users/${phone}/payment-info`;
    },
    UPDATE_BANK_CARD: function(phone) {
      return `${BASE_URL}/wechat/users/${phone}/bank-card`;
    },
    UPDATE_ALIPAY: function(phone) {
      return `${BASE_URL}/wechat/users/${phone}/alipay`;
    }
  },
  // 设备相关接口
  DEVICE: {
    MY_COUNT: function(phone) {
      return `${BASE_URL}/wechat/users/${phone}/devices/count`;
    },
    SUBORDINATE_COUNT: function(phone) {
      return `${BASE_URL}/wechat/users/${phone}/subordinate-devices/count`;
    },
    MY_LIST: function(phone) {
      return `${BASE_URL}/wechat/users/${phone}/devices`;
    },
    SUBORDINATE_LIST: function(phone) {
      return `${BASE_URL}/wechat/users/${phone}/subordinate-devices`;
    },
    SET_FIRST_COMMISSION_RATE: function(deviceId) {
      return `${BASE_URL}/wechat/devices/${deviceId}/commission-rate`;
    },
    UPDATE_PHONE: function(deviceId) {
      return `${BASE_URL}/wechat/devices/${deviceId}/phone`;
    }
  }
};

export default API; 