import request from '@/utils/request'

export function login(data) {
  return request({
    url: '/api/auth/jwt/login',
    method: 'post',
    data
  })
}

export function getInfo() {
  return request({
    url: '/api/users/me',
    method: 'get'
  })
}

export function logout() {
  return request({
    url: '/api/auth/jwt/logout',
    method: 'post'
  })
}

export function getUserList(query) {
  return request({
    url: '/api/users',
    method: 'get',
    params: query
  })
}

export function createUser(data) {
  return request({
    url: '/api/auth/register',
    method: 'post',
    data
  })
}

export function updateUser(id, data) {
  return request({
    url: `/api/users/${id}`,
    method: 'patch',
    data
  })
}

export function deleteUser(id) {
  return request({
    url: `/api/users/${id}`,
    method: 'delete'
  })
}
