import request from '@/utils/request'

export function getPurchases(params) {
    return request({
        url: '/purchases',
        method: 'get',
        params
    })
}
