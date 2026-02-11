import request from '@/utils/request'

export function getLogistics(params) {
    return request({
        url: '/logistics',
        method: 'get',
        params
    })
}
