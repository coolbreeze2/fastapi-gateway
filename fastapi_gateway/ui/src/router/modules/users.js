/** When your routing table is too long, you can split it into small modules **/

import Layout from '@/layout'

const userRouter = {
  path: '/users',
  component: Layout,
  name: 'users',
  meta: {
    title: '用户管理',
    icon: 'user'
  },
  children: [
    {
      path: 'users',
      component: () => import('@/views/users/UserList'),
      name: 'UserList',
      meta: { title: '用户列表' }
    }
  ]
}
export default userRouter
