const BASE_URL = 'http://localhost:5001/api';

const API = {
  BASE_URL,
  // 用户相关接口
  USER: {
    REGISTER: `${BASE_URL}/wechat/users/register`,
    LOGIN: `${BASE_URL}/wechat/users/login`,
    INFO: function(phone) {
      return `${BASE_URL}/wechat/users/${phone}`;
    }
  }
};

export default API; 