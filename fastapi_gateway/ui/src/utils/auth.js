import VueCookie from 'vue-cookie'

const TokenKey = 'fastapiusersauth'

export function getToken() {
  return VueCookie.get(TokenKey)
}

export function setToken(token) {
  return VueCookie.set(TokenKey, token)
}

export function removeToken() {
  return VueCookie.delete(TokenKey)
}
