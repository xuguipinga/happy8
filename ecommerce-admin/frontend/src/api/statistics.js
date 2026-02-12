import request from '@/utils/request'

// 采购统计
export const getPurchaseStatistics = (params) => {
    return request({
        url: '/statistics/purchases',
        method: 'get',
        params
    })
}

// 订单统计
export const getOrderStatistics = (params) => {
    return request({
        url: '/statistics/orders',
        method: 'get',
        params
    })
}

// 物流统计
export const getLogisticsStatistics = (params) => {
    return request({
        url: '/statistics/logistics',
        method: 'get',
        params
    })
}

// 综合盈亏分析
export const getProfitStatistics = (params) => {
    return request({
        url: '/statistics/profit',
        method: 'get',
        params
    })
}
