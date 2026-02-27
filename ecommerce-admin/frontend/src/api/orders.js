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

export function getOrdersKPI(params) {
    return request({
        url: '/orders/kpi',
        method: 'get',
        params
    })
}

export function linkOrderPurchases(orderId, purchaseIds) {
    return request({
        url: `/orders/${orderId}/link-purchases`,
        method: 'post',
        data: { purchase_ids: purchaseIds }
    })
}

export function getOrderPurchases(orderId) {
    return request({
        url: `/orders/${orderId}/purchases`,
        method: 'get'
    })
}

export function unlinkOrderPurchase(orderId, purchaseId) {
    return request({
        url: `/orders/${orderId}/unlink-purchase/${purchaseId}`,
        method: 'delete'
    })
}
