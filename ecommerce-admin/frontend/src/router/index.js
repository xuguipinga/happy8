import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/Login.vue'),
        meta: { requiresAuth: false }
    },
    {
        path: '/register',
        name: 'Register',
        component: () => import('@/views/Register.vue'),
        meta: { requiresAuth: false }
    },
    {
        path: '/',
        name: 'Layout',
        component: () => import('@/views/Layout.vue'),
        meta: { requiresAuth: true },
        redirect: '/dashboard',
        children: [
            {
                path: 'dashboard',
                name: 'Dashboard',
                component: () => import('@/views/Dashboard.vue'),
                meta: { title: '首页' }
            },
            {
                path: 'orders',
                name: 'Orders',
                component: () => import('@/views/data/Orders.vue'),
                meta: { title: '订单管理' }
            },
            {
                path: 'purchases',
                name: 'Purchases',
                component: () => import('@/views/data/Purchases.vue'),
                meta: { title: '采购管理' }
            },
            {
                path: 'logistics',
                name: 'Logistics',
                component: () => import('@/views/data/Logistics.vue'),
                meta: { title: '物流管理' }
            },
            {
                path: 'products',
                name: 'Products',
                component: () => import('@/views/data/Products.vue'),
                meta: { title: '商品管理' }
            },
            {
                path: 'analysis',
                name: 'ProfitAnalysis',
                component: () => import('@/views/data/ProfitAnalysis.vue'),
                meta: { title: '盈亏分析' }
            },
            {
                path: 'tenant-settings',
                name: 'TenantSettings',
                component: () => import('@/views/TenantSettings.vue'),
                meta: { title: '租户设置' }
            },
            {
                path: 'user-management',
                name: 'UserManagement',
                component: () => import('@/views/UserManagement.vue'),
                meta: { title: '用户管理' }
            },
            {
                path: 'profile',
                name: 'UserProfile',
                component: () => import('@/views/UserProfile.vue'),
                meta: { title: '个人中心' }
            }
        ]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
    const userStore = useUserStore()
    const token = userStore.token

    if (to.meta.requiresAuth && !token) {
        next('/login')
    } else if (to.path === '/login' && token) {
        next('/')
    } else {
        next()
    }
})

export default router
