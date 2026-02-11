import request from '@/utils/request'

export function getOrders(params) {
    return request({
        url: '/orders',
        method: 'get',
        params
    })
}

export function recalculateProfit() {
    return request({
        url: '/orders/recalculate-profit',
        method: 'post'
    })
}

export function getOrdersKPI() {
    return request({
        url: '/orders/kpi',
        method: 'get'
    })
}
