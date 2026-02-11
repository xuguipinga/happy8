import request from '@/utils/request'

export const login = (username, password) => {
    return request({
        url: '/auth/login',
        method: 'post',
        data: { username, password }
    })
}

export const register = (data) => {
    return request({
        url: '/auth/register',
        method: 'post',
        data
    })
}

export const getUserInfo = () => {
    return request({
        url: '/auth/info',
        method: 'get'
    })
}
