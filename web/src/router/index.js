import { createRouter, createWebHistory } from 'vue-router'
import Device from '../views/Device.vue'
import User from '../views/User.vue'
import Profile from '../views/Profile.vue'

const routes = [
  {
    path: '/',
    redirect: '/device'
  },
  {
    path: '/device',
    name: 'Device',
    component: Device
  },
  {
    path: '/user',
    name: 'User',
    component: User
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 