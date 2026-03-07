<template>
  <div class="page-container">
    <div class="page-header">
      <h2>{{ $t('orders.title') }}</h2>
      <div class="header-right">
        <div class="search-box">
             <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="-"
                :start-placeholder="$t('common.startDate')"
                :end-placeholder="$t('common.endDate')"
                value-format="YYYY-MM-DD"
                :shortcuts="shortcuts"
                style="width: 260px;"
                @change="handleSearch"
             />
              <!-- 移除原有的多选 Select，改为由 Tab 控制 -->
             <el-input
                v-model="searchQuery"
                :placeholder="$t('common.search') + '...'"
                clearable
                @clear="handleSearch"
                @keyup.enter="handleSearch"
                style="width: 250px;"
             >
                <template #append>
                    <el-button @click="handleSearch">
                        <el-icon><Search /></el-icon>
                    </el-button>
                </template>
             </el-input>
        </div>
        <div class="actions">
            <el-upload
            class="upload-demo"
            action="#"
            :http-request="handleUpload"
            :show-file-list="false"
            accept=".xlsx,.xls"
            :before-upload="beforeUpload"
            :disabled="loading"
            >
            <el-button type="primary" :loading="loading">
                <el-icon class="el-icon--left"><Upload /></el-icon>
                {{ $t('orders.importExcel') }}
            </el-button>
            </el-upload>
            <el-button type="warning" @click="handleRecalculate" :loading="recalcLoading">
                <el-icon class="el-icon--left"><Refresh /></el-icon>
                {{ $t('orders.recalculateProfit') }}
            </el-button>
        </div>
      </div>
    </div>

    <!-- 状态切换 Tab -->
    <div class="tabs-container">
        <el-tabs v-model="activeTab" @tab-change="handleTabChange">
            <el-tab-pane name="all">
                <template #label>
                    <span class="tab-label">
                        {{ $t('orders.tabs.all') }}
                        <span class="tab-count" v-if="kpiData.total_orders > 0">{{ kpiData.total_orders > 99 ? '99+' : kpiData.total_orders }}</span>
                    </span>
                </template>
            </el-tab-pane>
            <el-tab-pane v-for="key in ['confirming', 'pending', 'paid', 'shipped', 'refund', 'unmatched', 'closed']" :key="key" :name="key">
                <template #label>
                    <span class="tab-label">
                        {{ $t(`orders.tabs.${key}`) }}
                        <span class="tab-count" v-if="key !== 'unmatched' && kpiData.status_counts?.[key] > 0">
                            {{ kpiData.status_counts[key] > 99 ? '99+' : kpiData.status_counts[key] }}
                        </span>
                        <span class="tab-count unmatched-badge" v-if="key === 'unmatched' && kpiData.status_counts?.[key] > 0">
                            {{ kpiData.status_counts[key] > 99 ? '99+' : kpiData.status_counts[key] }}
                        </span>
                    </span>
                </template>
            </el-tab-pane>
        </el-tabs>
    </div>

    <!-- KPI 数据看板 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
        <el-col :span="4">
            <el-card shadow="hover" class="kpi-card">
                <el-statistic :title="$t('orders.kpi.todayOrders')" :value="kpiData.today_orders" />
            </el-card>
        </el-col>
        <el-col :span="4">
            <el-card shadow="hover" class="kpi-card">
                <el-statistic :title="$t('orders.kpi.todaySales')" :value="kpiData.today_sales" :precision="2">
                     <template #prefix>¥</template>
                </el-statistic>
            </el-card>
        </el-col>
        <el-col :span="4">
            <el-card shadow="hover" class="kpi-card">
                <el-statistic :title="$t('orders.kpi.todayProfit')" :value="kpiData.today_profit" :precision="2" :value-style="{ color: kpiData.today_profit >= 0 ? '#67C23A' : '#F56C6C' }">
                     <template #prefix>¥</template>
                </el-statistic>
            </el-card>
        </el-col>
        <el-col :span="4">
            <el-card shadow="hover" class="kpi-card">
                <el-statistic :title="$t('orders.kpi.totalOrders')" :value="kpiData.total_orders" />
            </el-card>
        </el-col>
        <el-col :span="4">
            <el-card shadow="hover" class="kpi-card">
                <el-statistic :title="$t('orders.kpi.totalSales')" :value="kpiData.total_sales" :precision="2">
                    <template #prefix>¥</template>
                </el-statistic>
            </el-card>
        </el-col>
        <el-col :span="4">
            <el-card shadow="hover" class="kpi-card">
                <el-statistic :title="$t('orders.kpi.totalProfit')" :value="kpiData.total_profit" :precision="2" :value-style="{ color: kpiData.total_profit >= 0 ? '#67C23A' : '#F56C6C' }">
                    <template #prefix>¥</template>
                </el-statistic>
            </el-card>
        </el-col>
    </el-row>

    <el-card class="content-card">
      
      <!-- 表格 -->
      <el-table 
        :data="tableData" 
        v-loading="tableLoading" 
        style="width: 100%" 
        border 
        stripe
        max-height="calc(100vh - 350px)"
      >
        <el-table-column :label="$t('orders.orderNo')" width="180" fixed>
            <template #default="scope">
                <el-popover
                    placement="right"
                    :width="350"
                    trigger="hover"
                    @show="handleLogisticsPreview(scope.row.platform_order_no)"
                >
                    <template #reference>
                        <span 
                            class="link-text"
                            @click="router.push(`/logistics?search=${scope.row.platform_order_no}`)"
                        >
                            {{ scope.row.platform_order_no }}
                        </span>
                    </template>
                    
                    <div v-loading="logisticsLoading[scope.row.platform_order_no]">
                        <div v-if="logisticsPreviewData[scope.row.platform_order_no] && logisticsPreviewData[scope.row.platform_order_no].length > 0">
                            <div v-for="item in logisticsPreviewData[scope.row.platform_order_no]" :key="item.id" class="logistics-preview-item">
                                <p><strong>{{ $t('common.status') }}:</strong> <el-tag size="small">{{ item.order_status }}</el-tag></p>
                                <p><strong>物流商:</strong> {{ item.logistics_channel }}</p>
                                <p><strong>运单号:</strong> {{ item.tracking_no }}</p>
                                <p><strong>发货日期:</strong> {{ item.sent_date }}</p>
                                <p><strong>运费:</strong> {{ item.actual_fee }}</p>
                                <el-divider style="margin: 10px 0;" />
                            </div>
                        </div>
                        <div v-else-if="!logisticsLoading[scope.row.platform_order_no]" class="no-data">
                            {{ $t('common.noData') }}
                        </div>
                    </div>
                </el-popover>
            </template>
        </el-table-column>
        
        <el-table-column :label="$t('orders.productInfo')" min-width="250">
          <template #default="scope">
            <div v-for="(item, index) in scope.row.items" :key="item.id" class="aggregated-item" :class="{ 'has-divider': index < scope.row.items.length - 1 }">
              <div class="product-name">{{ item.product_name }}</div>
              <div class="product-sku">
                {{ $t('orders.sku') }}: {{ item.sku }}
                <el-tag v-if="item.parsed_model" size="small" type="info" class="parsed-tag" effect="plain" style="margin-left: 8px;">
                  [识别型号: {{ item.parsed_model }}]
                </el-tag>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column :label="$t('orders.unitPrice') + '/' + $t('orders.quantity')" width="120">
          <template #default="scope">
            <div v-for="(item, index) in scope.row.items" :key="item.id" class="aggregated-item" :class="{ 'has-divider': index < scope.row.items.length - 1 }">
                <div class="money-info">
                    <div>{{ item.unit_price }}</div>
                    <div style="color: #909399; font-size: 12px;">x {{ item.quantity }}</div>
                </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column :label="$t('orders.amountDetails')" width="180">
          <template #default="scope">
            <div class="money-info">
              <div>{{ $t('orders.orderAmount') }}: {{ scope.row.order_amount }} <span style="font-size: 11px; color: #999;">{{ scope.row.currency }}</span></div>
              <div>{{ $t('orders.actualPaid') }}: {{ scope.row.actual_paid }} <span style="font-size: 11px; color: #999;">{{ scope.row.currency }}</span></div>
              <div v-if="scope.row.tax_fee > 0" style="font-size: 11px; color: #E6A23C;">{{ $t('orders.taxFee') }}: {{ scope.row.tax_fee }} <span style="font-size: 11px; color: #999;">{{ scope.row.currency }}</span></div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column :label="$t('orders.costAndProfit')" width="180">
          <template #default="scope">
            <div class="money-info">
              <div>{{ $t('orders.purchaseCost') }}: {{ scope.row.total_cost }} <span style="font-size: 11px; color: #999;">{{ scope.row.currency }}</span></div>
              <div>{{ $t('orders.logisticsCost') }}: {{ scope.row.total_logistics_cost }} <span style="font-size: 11px; color: #999;">{{ scope.row.currency }}</span></div>
              <div :class="scope.row.total_profit >= 0 ? 'profit-positive' : 'profit-negative'">
                {{ $t('orders.grossProfit') }}: {{ scope.row.total_profit }} <span style="font-size: 11px; color: #999;">{{ scope.row.currency }}</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="order_status" :label="$t('common.status')" width="120">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.order_status)">{{ mapDisplayStatus(scope.row.order_status) }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column :label="$t('orders.buyer')" width="150">
          <template #default="scope">
            <div>{{ scope.row.buyer_name }}</div>
            <div class="sub-text">{{ scope.row.buyer_country }}</div>
          </template>
        </el-table-column>
        
        <el-table-column prop="appointed_delivery_time" :label="$t('orders.appointedDelivery')" width="130" />
        <el-table-column prop="actual_delivery_time" :label="$t('orders.actualDelivery')" width="130" />
        <el-table-column prop="order_time" :label="$t('orders.orderTime')" width="180" />

        <el-table-column :label="$t('common.operation')" width="100" fixed="right">
            <template #default="scope">
              <el-button link type="primary" size="small" @click="handleViewDetails(scope.row)">{{ $t('common.details') }}</el-button>
            </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>

      <!-- 详情弹窗 -->
      <el-dialog
        v-model="detailsDialogVisible"
        :title="$t('common.details')"
        width="60%"
      >
        <el-descriptions :column="2" border v-if="currentOrder">
            <el-descriptions-item :label="$t('orders.platformOrderNo')">{{ currentOrder.platform_order_no }}</el-descriptions-item>
            <el-descriptions-item :label="$t('orders.orderTime')">{{ currentOrder.order_time }}</el-descriptions-item>
            <el-descriptions-item :label="$t('orders.buyer')">{{ currentOrder.buyer_name }}</el-descriptions-item>
            <el-descriptions-item :label="$t('orders.country')">{{ currentOrder.buyer_country }}</el-descriptions-item>
            <el-descriptions-item label="EMail">{{ currentOrder.buyer_email }}</el-descriptions-item>
            <el-descriptions-item :label="$t('orders.productInfo')" :span="2">
                <el-table :data="currentOrder.items" border size="small">
                    <el-table-column prop="product_name" :label="$t('orders.productInfo')" />
                    <el-table-column prop="sku" :label="$t('orders.sku')" width="150" />
                    <el-table-column prop="unit_price" :label="$t('orders.unitPrice')" width="100" />
                    <el-table-column prop="quantity" :label="$t('orders.quantity')" width="80" />
                    <el-table-column prop="profit" :label="$t('orders.grossProfit')" width="100" />
                </el-table>
            </el-descriptions-item>
            <el-descriptions-item :label="$t('orders.orderAmount')">{{ currentOrder.order_amount }} {{ currentOrder.currency }}</el-descriptions-item>
            <el-descriptions-item :label="$t('orders.actualPaid')">{{ currentOrder.actual_paid }} {{ currentOrder.currency }}</el-descriptions-item>
            <el-descriptions-item label="物流收入">{{ currentOrder.shipping_fee_income }} {{ currentOrder.currency }}</el-descriptions-item>
            <el-descriptions-item :label="$t('orders.taxFee')">{{ currentOrder.tax_fee }} {{ currentOrder.currency }}</el-descriptions-item>
            <el-descriptions-item label="折扣">{{ currentOrder.discount_amount }} {{ currentOrder.currency }}</el-descriptions-item>
            <el-descriptions-item :label="$t('orders.purchaseCost')">{{ currentOrder.total_cost }} {{ currentOrder.currency }}</el-descriptions-item>
            <el-descriptions-item :label="$t('orders.logisticsCost')">{{ currentOrder.total_logistics_cost }} {{ currentOrder.currency }}</el-descriptions-item>
            <el-descriptions-item :label="$t('orders.grossProfit')">
                <span :class="currentOrder.total_profit >= 0 ? 'profit-positive' : 'profit-negative'">{{ currentOrder.total_profit }} {{ currentOrder.currency }}</span>
            </el-descriptions-item>
            <el-descriptions-item :label="$t('orders.actualDelivery')">{{ currentOrder.actual_delivery_time }}</el-descriptions-item>
            <el-descriptions-item label="收货地址" :span="2">{{ currentOrder.shipping_address }}</el-descriptions-item>
            <el-descriptions-item label="备注" :span="2">{{ currentOrder.remark }}</el-descriptions-item>
        </el-descriptions>

        <!-- 关联采购单部分 -->
        <div class="linked-purchases-header">
          <h3>{{ $t('orders.associatedPurchases') }}</h3>
          <el-button type="primary" size="small" @click="openLinkPurchaseDialog">
            {{ $t('orders.linkPurchase') }}
          </el-button>
        </div>
        <el-table :data="linkedPurchases" border size="small" style="margin-top: 10px;">
          <el-table-column prop="purchase_no" :label="$t('purchases.purchaseNo')" width="180" />
          <el-table-column prop="product_name" :label="$t('orders.productInfo')" />
          <el-table-column prop="sku" :label="$t('orders.sku')" width="150" />
          <el-table-column prop="quantity" :label="$t('orders.quantity')" width="100" align="center" />
          <el-table-column prop="actual_payment" :label="$t('purchases.amount')" width="120" align="right" />
          <el-table-column :label="$t('common.operation')" width="100" align="center">
            <template #default="scope">
              <el-button link type="danger" @click="handleUnlinkPurchase(scope.row.id)">{{ $t('common.delete') }}</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-dialog>

      <!-- 采购单选择弹窗 -->
      <el-dialog
        v-model="purchaseSelectionVisible"
        :title="$t('orders.selectPurchase')"
        width="50%"
        append-to-body
      >
        <div style="margin-bottom: 15px;">
          <el-input
            v-model="purchaseSearchQuery"
            :placeholder="$t('common.search') + '...'"
            @keyup.enter="searchAvailablePurchases"
            clearable
          >
            <template #append>
              <el-button @click="searchAvailablePurchases" :icon="Search" />
            </template>
          </el-input>
        </div>
        <el-table
          :data="availablePurchases"
          v-loading="searchPurchasesLoading"
          @selection-change="val => selectedPurchaseIds = val.map(i => i.id)"
          height="400"
          border
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="purchase_no" :label="$t('purchases.purchaseNo')" width="180" />
          <el-table-column prop="product_name" :label="$t('orders.productInfo')" />
          <el-table-column prop="sku" :label="$t('orders.sku')" width="150" />
          <el-table-column prop="quantity" :label="$t('orders.quantity')" width="80" align="center" />
        </el-table>
        <template #footer>
          <el-button @click="purchaseSelectionVisible = false">{{ $t('common.cancel') }}</el-button>
          <el-button type="primary" @click="handleLinkPurchases" :loading="linkingLoading">
            {{ $t('common.confirm') }}
          </el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { uploadOrders, previewOrders } from '@/api/upload'
import { getOrders, recalculateProfit, getOrdersKPI, linkOrderPurchases, getOrderPurchases, unlinkOrderPurchase } from '@/api/orders'
import { getPurchases } from '@/api/purchases'
import { getLogistics } from '@/api/logistics'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const { t } = useI18n()
const router = useRouter()

// Helper to get current month range
const getDefaultMonth = () => {
    const start = dayjs().startOf('month').format('YYYY-MM-DD')
    const end = dayjs().endOf('month').format('YYYY-MM-DD')
    return [start, end]
}

const dateRange = ref(getDefaultMonth())
const shortcuts = [
  { text: t('shortcuts.today'), value: () => {
    const d = dayjs().format('YYYY-MM-DD'); 
    return [d, d]
  }},
  { text: t('shortcuts.yesterday'), value: () => {
    const d = dayjs().subtract(1, 'day').format('YYYY-MM-DD');
    return [d, d]
  }},
  { text: t('shortcuts.last7Days'), value: () => [dayjs().subtract(6, 'day').format('YYYY-MM-DD'), dayjs().format('YYYY-MM-DD')] },
  { text: t('shortcuts.last30Days'), value: () => [dayjs().subtract(29, 'day').format('YYYY-MM-DD'), dayjs().format('YYYY-MM-DD')] },
  { text: t('shortcuts.thisMonth'), value: () => [dayjs().startOf('month').format('YYYY-MM-DD'), dayjs().endOf('month').format('YYYY-MM-DD')] },
  { text: t('shortcuts.lastMonth'), value: () => [dayjs().subtract(1, 'month').startOf('month').format('YYYY-MM-DD'), dayjs().subtract(1, 'month').endOf('month').format('YYYY-MM-DD')] },
]

const loading = ref(false)
const tableLoading = ref(false)
const tableData = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

const searchQuery = ref('')
const filterStatus = ref([])
const detailsDialogVisible = ref(false)
const currentOrder = ref(null)
const kpiData = ref({
    today_orders: 0,
    today_sales: 0,
    today_profit: 0,
    total_orders: 0,
    total_sales: 0,
    total_profit: 0,
    status_counts: {}
})

const activeTab = ref('all')

// --- Order-Purchase Linking State ---
const linkedPurchases = ref([])
const purchaseSelectionVisible = ref(false)
const purchaseSearchQuery = ref('')
const availablePurchases = ref([])
const selectedPurchaseIds = ref([])
const linkingLoading = ref(false)
const searchPurchasesLoading = ref(false)

const handleTabChange = (name) => {
    activeTab.value = name
    if (name === 'all') {
        filterStatus.value = []
    } else {
        filterStatus.value = [name]
    }
    handleSearch()
}

const fetchData = async () => {
    tableLoading.value = true
    try {
        const params = {
            page: currentPage.value,
            per_page: pageSize.value,
            search: searchQuery.value,
            start_date: dateRange.value?.[0],
            end_date: dateRange.value?.[1],
            order_status: filterStatus.value?.join(',')
        }
        
        const res = await getOrders(params)
        if (res.code === 200) {
            tableData.value = res.data.items
            total.value = res.data.total
        }
    } catch (error) {
        ElMessage.error(t('common.loading') + ' ' + t('common.noData'))
    } finally {
        tableLoading.value = false
    }
}

const fetchKPI = async () => {
    try {
        const params = {
            search: searchQuery.value,
            start_date: dateRange.value?.[0],
            end_date: dateRange.value?.[1],
            order_status: filterStatus.value?.join(',')
        }
        const res = await getOrdersKPI(params)
        if (res.code === 200) {
            kpiData.value = res.data
        }
    } catch (error) {
        console.error('Failed to fetch KPI:', error)
    }
}

const handleSearch = () => {
    currentPage.value = 1
    fetchData()
    fetchKPI()
}

onMounted(() => {
    handleSearch()
})

const handleSizeChange = (val) => {
    pageSize.value = val
    fetchData()
}

const handleCurrentChange = (val) => {
    currentPage.value = val
    fetchData()
}

// Status Display Mappings
const statusKeyMap = {
    '待买家付款': 'Pending',
    '待卖家发货': 'Paid',
    '待买家确认收货': 'Shipped',
    '发货中': 'Shipped',
    '订单完成': 'Completed',
    '订单关闭': 'Cancelled'
}

const mapDisplayStatus = (dbStatus) => {
    const key = statusKeyMap[dbStatus] || dbStatus
    return t(`orders.status.${key}`)
}

const getStatusType = (dbStatus) => {
    const key = statusKeyMap[dbStatus]
    if (key === 'Completed') return 'success'
    if (key === 'Cancelled') return 'info'
    if (key === 'Shipped') return 'warning'
    return ''
}

const handleViewDetails = (row) => {
    currentOrder.value = row
    detailsDialogVisible.value = true
    fetchLinkedPurchases(row.id)
}

// --- Order-Purchase Linking Methods ---
const fetchLinkedPurchases = async (orderId) => {
    try {
        const res = await getOrderPurchases(orderId)
        if (res.code === 200) {
            linkedPurchases.value = res.data
        }
    } catch (error) {
        console.error('Failed to fetch linked purchases:', error)
    }
}

const openLinkPurchaseDialog = () => {
    purchaseSelectionVisible.value = true
    searchAvailablePurchases()
}

const searchAvailablePurchases = async () => {
    searchPurchasesLoading.value = true
    try {
        const params = {
            search: purchaseSearchQuery.value,
            page: 1,
            per_page: 50
        }
        const res = await getPurchases(params)
        if (res.code === 200) {
            availablePurchases.value = res.data.items
        }
    } catch (error) {
        ElMessage.error(t('common.error'))
    } finally {
        searchPurchasesLoading.value = false
    }
}

const handleLinkPurchases = async () => {
    if (selectedPurchaseIds.value.length === 0) {
        ElMessage.warning(t('inventory.selectPurchaseFirst'))
        return
    }
    
    linkingLoading.value = true
    try {
        const res = await linkOrderPurchases(currentOrder.value.id, selectedPurchaseIds.value)
        if (res.code === 200) {
            ElMessage.success(res.message)
            purchaseSelectionVisible.value = false
            selectedPurchaseIds.value = []
            fetchLinkedPurchases(currentOrder.value.id)
        }
    } catch (error) {
        ElMessage.error(t('common.error'))
    } finally {
        linkingLoading.value = false
    }
}

const handleUnlinkPurchase = (purchaseId) => {
    ElMessageBox.confirm(
        t('orders.confirmUnlink') + '?',
        t('common.confirm'),
        { type: 'warning' }
    ).then(async () => {
        try {
            const res = await unlinkOrderPurchase(currentOrder.value.id, purchaseId)
            if (res.code === 200) {
                ElMessage.success(res.message)
                fetchLinkedPurchases(currentOrder.value.id)
            }
        } catch (error) {
            ElMessage.error(t('common.error'))
        }
    })
}

const logisticsPreviewData = ref({})
const logisticsLoading = ref({})
const handleLogisticsPreview = async (orderNo) => {
    if (logisticsPreviewData.value[orderNo]) return
    logisticsLoading.value[orderNo] = true
    try {
        const res = await getLogistics({ search: orderNo, page: 1, per_page: 5 })
        if (res.code === 200) {
            logisticsPreviewData.value[orderNo] = res.data.items
        }
    } catch (e) {} finally {
        logisticsLoading.value[orderNo] = false
    }
}

const recalcLoading = ref(false)
const handleRecalculate = () => {
    ElMessageBox.confirm(
        t('orders.recalculateProfit') + '?',
        t('common.confirm'),
        { type: 'warning' }
    ).then(async () => {
        recalcLoading.value = true
        try {
            const res = await recalculateProfit()
            if (res.code === 200) {
                ElMessage.success(res.message)
                handleSearch()
            }
        } catch (e) {} finally {
            recalcLoading.value = false
        }
    })
}

const beforeUpload = (file) => true
const handleUpload = async (option) => {
    loading.value = true
    const formData = new FormData()
    formData.append('file', option.file)
    try {
        const res = await uploadOrders(formData)
        if (res.code === 200) {
            ElMessage.success(res.message)
            handleSearch()
        }
    } catch (e) {} finally {
        loading.value = false
    }
}
</script>

<style scoped>
.page-container { padding: 0; }
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.page-header h2 { margin: 0; font-size: 20px; font-weight: 500; white-space: nowrap; margin-right: 20px; }
.header-right { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; }
.search-box { display: flex; align-items: center; gap: 10px; }
.actions { display: flex; align-items: center; gap: 10px; }
.tabs-container {
    background: #fff;
    margin-bottom: 20px;
    padding: 0 20px;
    border-radius: 4px;
}
.tab-label {
    display: flex;
    align-items: center;
    font-size: 15px;
}
.tab-count {
  margin-left: 5px;
  background-color: #f56c6c;
  color: #fff;
  border-radius: 10px;
  padding: 0 6px;
  font-size: 11px;
}

.unmatched-badge {
    background-color: #E6A23C; /* 使用警告橙色或红色 */
    animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.8; }
  100% { transform: scale(1); opacity: 1; }
}
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }
.product-name { font-weight: 500; }
.product-sku { font-size: 12px; color: #909399; display: flex; align-items: center; flex-wrap: wrap; }
.product-sku .parsed-tag {
    font-size: 10px;
    height: 20px;
    padding: 0 4px;
    line-height: 18px;
}
.sub-text { font-size: 12px; color: #909399; }
.profit-positive { color: #67C23A; font-weight: bold; }
.profit-negative {
  color: #F56C6C;
  font-weight: bold;
}

.linked-purchases-header {
  margin-top: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
}

.linked-purchases-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}
.aggregated-item { padding: 8px 0; }
.aggregated-item.has-divider { border-bottom: 1px solid #ebeef5; }
.content-card { min-height: calc(100vh - 140px); }
.link-text { color: #409EFF; cursor: pointer; text-decoration: underline; }
.kpi-card { text-align: center; }
.logistics-preview-item p { margin: 5px 0; font-size: 13px; }
.no-data { text-align: center; color: #909399; padding: 10px; }
</style>
