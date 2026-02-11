import request from '@/utils/request'

export function calculateProfit() {
    return request({
        url: '/analysis/calculate',
        method: 'post'
    })
}

export function getProfitStats() {
    return request({
        url: '/analysis/dashboard',
        method: 'get'
    })
}
