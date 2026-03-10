import request from '@/utils/request'

export const uploadOrders = (formData) => {
    return request({
        url: '/upload/orders',
        method: 'post',
        data: formData
    })
}

export const previewOrders = (formData) => {
    return request({
        url: '/upload/orders/preview',
        method: 'post',
        data: formData
    })
}

export const uploadPurchases = (formData) => {
    return request({
        url: '/upload/purchases',
        method: 'post',
        data: formData
    })
}

export const previewPurchases = (formData) => {
    return request({
        url: '/upload/purchases/preview',
        method: 'post',
        data: formData
    })
}

export const uploadLogistics = (formData) => {
    return request({
        url: '/upload/logistics',
        method: 'post',
        data: formData
    })
}

export const previewLogistics = (formData) => {
    return request({
        url: '/upload/logistics/preview',
        method: 'post',
        data: formData
    })
}
