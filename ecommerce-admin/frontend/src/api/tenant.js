import request from '@/utils/request'

// 获取当前租户信息
export const getCurrentTenant = () => {
    return request({
        url: '/tenants/current',
        method: 'get'
    })
}

// 更新当前租户信息
export const updateCurrentTenant = (data) => {
    return request({
        url: '/tenants/current',
        method: 'put',
        data
    })
}

// 获取租户下的用户列表
export const getTenantUsers = (params) => {
    return request({
        url: '/tenants/users',
        method: 'get',
        params
    })
}

// 创建子账号
export const createTenantUser = (data) => {
    return request({
        url: '/tenants/users',
        method: 'post',
        data
    })
}

// 更新用户信息
export const updateTenantUser = (userId, data) => {
    return request({
        url: `/tenants/users/${userId}`,
        method: 'put',
        data
    })
}

// 删除用户
export const deleteTenantUser = (userId) => {
    return request({
        url: `/tenants/users/${userId}`,
        method: 'delete'
    })
}
