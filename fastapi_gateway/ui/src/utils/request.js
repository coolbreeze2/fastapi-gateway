import axios from 'axios'
import { MessageBox } from 'element-ui'
import store from '@/store'
import { getToken } from '@/utils/auth'

// create an axios instance
const service = axios.create({
  baseURL: process.env.VUE_APP_BASE_API, // url = base url + request url
  // withCredentials: true, // send cookies when cross-domain requests
  timeout: 5000 // request timeout
})

// request interceptor
service.interceptors.request.use(
  config => {
    // do something before request is sent

    if (store.getters.token) {
      // let each request carry token
      // ['X-Token'] is a custom headers key
      // please modify it according to the actual situation
      config.headers['Authorization'] = 'bearer ' + getToken()
    }
    return config
  },
  error => {
    // do something with request error
    console.log(error) // for debug
    return Promise.reject(error)
  }
)

function ifUnauthorized({ response, error }) {
  if (response.status === 401) {
    // to re-login
    MessageBox.confirm('您已经注销，您可以取消停留在该页面，或者重新登录', '确认注销', '退出登录', {
      confirmButtonText: '重新登录',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      store.dispatch('user/resetToken').then(() => {
        location.reload()
      })
    })
  }
}

function ifBadRequest({ response, error }) {
  if (response.status === 400) {
    error.message = '请求错误：请检查填写内容'
    console.log('err' + error.message) // for debug
  }
}

// response interceptor
service.interceptors.response.use(
  /**
   * If you want to get http information such as headers or status
   * Please return  response => response
  */

  /**
   * Determine the request status by custom code
   * Here is just an example
   * You can also judge the status by HTTP Status Code
   */
  response => {
    const res = response.data

    if (response.config.raw === 1) {
      return response
    }

    return res
  },
  error => {
    console.log('err' + error) // for debug
    if (!error.response) {
      return Promise.reject(error)
    }

    const response = error.response
    ifUnauthorized({ response, error })
    ifBadRequest({ response, error })
    return Promise.reject(error)
  }
)

export default service
