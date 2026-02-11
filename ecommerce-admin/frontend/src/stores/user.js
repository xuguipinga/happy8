import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi, getUserInfo } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
    const token = ref(localStorage.getItem('token') || '')
    const userInfo = ref(null)

    const login = async (username, password) => {
        const res = await loginApi(username, password)
        if (res.code === 200) {
            token.value = res.data.token
            userInfo.value = res.data.user
            localStorage.setItem('token', res.data.token)
            return true
        }
        return false
    }

    const logout = () => {
        token.value = ''
        userInfo.value = null
        localStorage.removeItem('token')
    }

    const fetchUserInfo = async () => {
        const res = await getUserInfo()
        if (res.code === 200) {
            userInfo.value = res.data
        }
    }

    return {
        token,
        userInfo,
        login,
        logout,
        fetchUserInfo
    }
})
