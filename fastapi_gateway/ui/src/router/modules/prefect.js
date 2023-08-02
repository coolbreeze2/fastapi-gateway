import Layout from '@/layout'

const prefectRouter = {
  path: '/prefect',
  component: Layout,
  name: 'Prefect',
  meta: {
    title: 'Prefect',
    icon: 'prefect'
  },
  children: [
    {
      path: 'prefect',
      component: () => import('@/views/prefect/index'),
      name: 'Prefect',
      meta: { title: 'Prefect' }
    }
  ]
}
export default prefectRouter
