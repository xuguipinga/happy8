<template>
  <div class="page-container">
    <div class="page-header">
      <h2>订单管理</h2>
      <div class="header-right">
        <div class="search-box">
             <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
                style="margin-right: 10px; width: 240px;"
                @change="handleSearch"
             />
             <el-select
                v-model="filterStatus"
                multiple
                collapse-tags
                placeholder="订单状态"
                style="width: 180px; margin-right: 10px;"
                @change="handleSearch"
                clearable
             >
                <el-option label="Pending" value="Pending" />
                <el-option label="Paid" value="Paid" />
                <el-option label="Shipped" value="Shipped" />
                <el-option label="Completed" value="Completed" />
                <el-option label="Cancelled" value="Cancelled" />
             </el-select>
             <el-input
                v-model="searchQuery"
                placeholder="搜索订单号/买家/SKU"
                clearable
                @clear="handleSearch"
                @keyup.enter="handleSearch"
                style="width: 250px; margin-right: 10px;"
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
                导入销售订单 (Excel)
            </el-button>
            </el-upload>
            <el-button type="warning" @click="handleRecalculate" :loading="recalcLoading" style="margin-left: 10px;">
                <el-icon class="el-icon--left"><Refresh /></el-icon>
                重算利润
            </el-button>
        </div>
      </div>
    </div>

    <!-- KPI 数据看板 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
            <el-card shadow="hover" class="kpi-card">
                <el-statistic :title="dateRange && dateRange.length === 2 ? '所选期间订单' : '今日订单 (Today\'s Orders)'" :value="kpiData.today_orders" />
            </el-card>
        </el-col>
        <el-col :span="6">
            <el-card shadow="hover" class="kpi-card">
                <el-statistic :title="dateRange && dateRange.length === 2 ? '所选期间销售额' : '今日销售额 (Today\'s Sales)'" :value="kpiData.today_sales" :precision="2">
                     <template #prefix>¥</template>
                </el-statistic>
            </el-card>
        </el-col>
        <el-col :span="6">
            <el-card shadow="hover" class="kpi-card">
                <el-statistic :title="dateRange && dateRange.length === 2 ? '所选期间毛利' : '今日毛利 (Today\'s Profit)'" :value="kpiData.today_profit" :precision="2" :value-style="{ color: kpiData.today_profit >= 0 ? '#67C23A' : '#F56C6C' }">
                     <template #prefix>¥</template>
                </el-statistic>
            </el-card>
        </el-col>
        <el-col :span="6">
            <el-card shadow="hover" class="kpi-card">
                <el-statistic title="累计订单 (Total Orders)" :value="kpiData.total_orders" />
            </el-card>
        </el-col>
    </el-row>

    <el-card class="content-card">
      
      <!-- 表格 -->
      <el-table :data="tableData" v-loading="tableLoading" style="width: 100%" border stripe>
        <el-table-column label="订单号" width="180" fixed>
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
                                <p><strong>物流商:</strong> {{ item.logistics_channel }}</p>
                                <p><strong>运单号:</strong> {{ item.tracking_no }}</p>
                                <p><strong>状态:</strong> <el-tag size="small">{{ item.order_status }}</el-tag></p>
                                <p><strong>发货日期:</strong> {{ item.sent_date }}</p>
                                <p><strong>运费:</strong> {{ item.actual_fee }}</p>
                                <el-divider style="margin: 10px 0;" />
                            </div>
                        </div>
                        <div v-else-if="!logisticsLoading[scope.row.platform_order_no]" class="no-data">
                            暂无物流信息
                        </div>
                    </div>
                </el-popover>
            </template>
        </el-table-column>
        
        <el-table-column label="商品信息" min-width="250">
          <template #default="scope">
            <div class="product-info">
              <div class="product-name">{{ scope.row.product_name }}</div>
              <div class="product-sku">SKU: {{ scope.row.sku }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="单价/数量" width="120">
          <template #default="scope">
            <div class="money-info">
                <div>{{ scope.row.unit_price }}</div>
                <div style="color: #909399; font-size: 12px;">x {{ scope.row.quantity }}</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="金额详情" width="180">
          <template #default="scope">
            <div class="money-info">
              <div>总价: {{ scope.row.order_amount }} <span style="font-size: 11px; color: #999;">{{ scope.row.currency }}</span></div>
              <div>实付: {{ scope.row.actual_paid }} <span style="font-size: 11px; color: #999;">{{ scope.row.currency }}</span></div>
              <div v-if="scope.row.tax_fee > 0" style="font-size: 11px; color: #E6A23C;">税费: {{ scope.row.tax_fee }} <span style="font-size: 11px; color: #999;">{{ scope.row.currency }}</span></div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="成本与利润" width="180">
          <template #default="scope">
            <div class="money-info">
              <div>采购: {{ scope.row.cost_price }} <span style="font-size: 11px; color: #999;">{{ scope.row.currency }}</span></div>
              <div>物流: {{ scope.row.logistics_cost }} <span style="font-size: 11px; color: #999;">{{ scope.row.currency }}</span></div>
              <div :class="scope.row.profit >= 0 ? 'profit-positive' : 'profit-negative'">
                毛利: {{ scope.row.profit }} <span style="font-size: 11px; color: #999;">{{ scope.row.currency }}</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="order_status" label="状态" width="100">
          <template #default="scope">
            <el-tag>{{ scope.row.order_status }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="买家" width="150">
          <template #default="scope">
            <div>{{ scope.row.buyer_name }}</div>
            <div class="sub-text">{{ scope.row.buyer_country }}</div>
          </template>
        </el-table-column>
        
        <el-table-column prop="appointed_delivery_time" label="约定发货" width="120" />
        <el-table-column prop="actual_delivery_time" label="实际发货" width="120" />
        <el-table-column prop="order_time" label="下单时间" width="180" />

        <el-table-column label="操作" width="100" fixed="right">
            <template #default="scope">
              <el-button link type="primary" size="small" @click="handleViewDetails(scope.row)">详情</el-button>
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
        title="订单详情"
        width="60%"
      >
        <el-descriptions :column="2" border v-if="currentOrder">
            <el-descriptions-item label="平台订单号">{{ currentOrder.platform_order_no }}</el-descriptions-item>
            <el-descriptions-item label="下单时间">{{ currentOrder.order_time }}</el-descriptions-item>
            <el-descriptions-item label="买家姓名">{{ currentOrder.buyer_name }}</el-descriptions-item>
            <el-descriptions-item label="买家国家">{{ currentOrder.buyer_country }}</el-descriptions-item>
            <el-descriptions-item label="买家邮箱">{{ currentOrder.buyer_email }}</el-descriptions-item>
            <el-descriptions-item label="订单状态">{{ currentOrder.order_status }}</el-descriptions-item>
            <el-descriptions-item label="SKU">{{ currentOrder.sku }}</el-descriptions-item>
            <el-descriptions-item label="商品名称">{{ currentOrder.product_name }}</el-descriptions-item>
            <el-descriptions-item label="数量">{{ currentOrder.quantity }}</el-descriptions-item>
            <el-descriptions-item label="单价">{{ currentOrder.unit_price }} {{ currentOrder.currency }}</el-descriptions-item>
            <el-descriptions-item label="订单总额">{{ currentOrder.order_amount }} {{ currentOrder.currency }}</el-descriptions-item>
            <el-descriptions-item label="实付金额">{{ currentOrder.actual_paid }} {{ currentOrder.currency }}</el-descriptions-item>
            <el-descriptions-item label="运费收入">{{ currentOrder.shipping_fee_income }} {{ currentOrder.currency }}</el-descriptions-item>
            <el-descriptions-item label="税费">{{ currentOrder.tax_fee }} {{ currentOrder.currency }}</el-descriptions-item>
            <el-descriptions-item label="折扣金额">{{ currentOrder.discount_amount }} {{ currentOrder.currency }}</el-descriptions-item>
            <el-descriptions-item label="采购成本">{{ currentOrder.cost_price }} {{ currentOrder.currency }}</el-descriptions-item>
            <el-descriptions-item label="物流支出">{{ currentOrder.logistics_cost }} {{ currentOrder.currency }}</el-descriptions-item>
            <el-descriptions-item label="毛利">
                <span :class="currentOrder.profit >= 0 ? 'profit-positive' : 'profit-negative'">{{ currentOrder.profit }} {{ currentOrder.currency }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="实际发货时间">{{ currentOrder.actual_delivery_time }}</el-descriptions-item>
            <el-descriptions-item label="收货地址" :span="2">{{ currentOrder.shipping_address }}</el-descriptions-item>
            <el-descriptions-item label="备注" :span="2">{{ currentOrder.remark }}</el-descriptions-item>
        </el-descriptions>
      </el-dialog>

      <!-- 导入预览弹窗 -->
      <el-dialog
        v-model="importPreviewDialogVisible"
        title="导入数据预览 (Pre-flight Check)"
        width="50%"
      >
        <div class="preview-content">
            <el-alert
                title="请确认以下数据变更"
                type="info"
                show-icon
                :closable="false"
                style="margin-bottom: 20px;"
            />
            
            <el-row :gutter="20" style="margin-bottom: 20px; text-align: center;">
                <el-col :span="8">
                    <el-statistic title="解析总行数" :value="previewStats.total" />
                </el-col>
                <el-col :span="8">
                    <el-statistic title="预计新增" :value="previewStats.new" value-style="color: #67C23A" />
                </el-col>
                <el-col :span="8">
                    <el-statistic title="预计更新" :value="previewStats.update" value-style="color: #409EFF" />
                </el-col>
            </el-row>

            <div v-if="previewStats.errors.length > 0" class="error-section">
                <el-alert
                    :title="`发现 ${previewStats.errors.length} 条数据异常，这些行将被跳过`"
                    type="error"
                    show-icon
                    :closable="false"
                />
                <div class="error-list">
                    <p v-for="(err, index) in previewStats.errors" :key="index" class="error-item">{{ err }}</p>
                </div>
            </div>

            <div class="data-preview">
                <h4>前5条数据示例：</h4>
                <el-table :data="previewStats.preview_data" size="small" border>
                    <el-table-column prop="order_no" label="订单号" />
                    <el-table-column prop="product" label="商品" show-overflow-tooltip/>
                    <el-table-column prop="amount" label="总金额" />
                    <el-table-column prop="status" label="操作类型">
                        <template #default="scope">
                            <el-tag :type="scope.row.status === '新增' ? 'success' : 'primary'" size="small">{{ scope.row.status }}</el-tag>
                        </template>
                    </el-table-column>
                </el-table>
            </div>
        </div>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="importPreviewDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="confirmUpload" :disabled="loading">
                确认导入
            </el-button>
          </span>
        </template>
      </el-dialog>
      <el-dialog
        v-model="errorDialogVisible"
        title="导入结果"
        width="50%"
      >
        <div class="import-result">
            <el-result
                icon="warning"
                title="部分数据导入失败"
                :sub-title="`成功导入 ${importResult.count} 条，失败 ${importResult.errors.length} 条`"
            >
            </el-result>
            <div class="error-list">
                <p v-for="(err, index) in importResult.errors" :key="index" class="error-item">
                    {{ err }}
                </p>
            </div>
        </div>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="errorDialogVisible = false">关闭</el-button>
          </span>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { uploadOrders, previewOrders } from '@/api/upload'
import { getOrders, recalculateProfit, getOrdersKPI } from '@/api/orders'
import { getLogistics } from '@/api/logistics'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const tableLoading = ref(false)
const tableData = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

const errorDialogVisible = ref(false)
const importResult = ref({ count: 0, errors: [] })

// Preview State
const importPreviewDialogVisible = ref(false)
const previewStats = ref({ total: 0, new: 0, update: 0, errors: [], preview_data: [] })
const pendingFile = ref(null)

const searchQuery = ref('')
const dateRange = ref([])
const filterStatus = ref([])
const detailsDialogVisible = ref(false)
const currentOrder = ref(null)

const fetchData = async () => {
    tableLoading.value = true
    try {
        const params = {
            page: currentPage.value,
            per_page: pageSize.value,
            search: searchQuery.value
        }
        
        // Add filters
        if (dateRange.value && dateRange.value.length === 2) {
            params.start_date = dateRange.value[0]
            params.end_date = dateRange.value[1]
        }
        if (filterStatus.value && filterStatus.value.length > 0) {
            params.order_status = filterStatus.value.join(',')
        }

        const res = await getOrders(params)
        if (res.code === 200) {
            tableData.value = res.data.items
            total.value = res.data.total
        }
    } catch (error) {
        console.error(error)
        ElMessage.error('获取数据失败')
    } finally {
        tableLoading.value = false
    }
}

const kpiData = ref({
    today_orders: 0,
    today_sales: 0,
    today_profit: 0,
    total_orders: 0
})

const fetchKPI = async () => {
    try {
        const params = {
            search: searchQuery.value
        }
        if (dateRange.value && dateRange.value.length === 2) {
            params.start_date = dateRange.value[0]
            params.end_date = dateRange.value[1]
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

const handleViewDetails = (row) => {
    currentOrder.value = row
    detailsDialogVisible.value = true
}

onMounted(() => {
    fetchData()
    fetchKPI()
})

const handleSizeChange = (val) => {
    pageSize.value = val
    fetchData()
}

const handleCurrentChange = (val) => {
    currentPage.value = val
    fetchData()
}

const beforeUpload = (file) => {
  const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || file.type === 'application/vnd.ms-excel'
  if (!isExcel) {
    ElMessage.error('只能上传 xlsx/xls 文件!')
    return false
  }
  return true
}

const handleUpload = async (option) => {
  loading.value = true
  const formData = new FormData()
  formData.append('file', option.file)

  try {
    // 1. 先调用预览接口
    const res = await previewOrders(formData)
    if (res.code === 200) {
        previewStats.value = res.data
        pendingFile.value = option.file // 暂存文件对象用于后续确认上传
        importPreviewDialogVisible.value = true
    } else {
        ElMessage.error(res.message || '预览失败')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('预览请求失败')
  } finally {
    loading.value = false
  }
}

const confirmUpload = async () => {
    if (!pendingFile.value) return
    
    // 关闭预览弹窗，显示加载中
    importPreviewDialogVisible.value = false
    loading.value = true
    
    const formData = new FormData()
    formData.append('file', pendingFile.value)
    
    try {
        const res = await uploadOrders(formData)
        if (res.code === 200) {
            if (res.data.errors && res.data.errors.length > 0) {
                // 有部分错误
                importResult.value = {
                    count: parseInt(res.message.match(/\d+/)[0]) || 0,
                    errors: res.data.errors
                }
                errorDialogVisible.value = true
            } else {
                ElMessage.success(res.message)
            }
            // 上传成功后刷新列表
            fetchData()
        }
    } catch (error) {
        console.error(error)
        ElMessage.error('上传失败')
    } finally {
        loading.value = false
        pendingFile.value = null
    }
}

const recalcLoading = ref(false)
const handleRecalculate = () => {
    ElMessageBox.confirm(
        '确定要重新计算所有订单的利润吗？这将根据当前的商品成本和物流费用更新历史数据。',
        '警告',
        {
            confirmButtonText: '确定重算',
            cancelButtonText: '取消',
            type: 'warning',
        }
    )
    .then(async () => {
        recalcLoading.value = true
        try {
            const res = await recalculateProfit()
            if (res.code === 200) {
                ElMessage.success(res.message)
                fetchData()
            } else {
                ElMessage.error(res.message || '重算失败')
            }
        } catch (error) {
            console.error(error)
            ElMessage.error('请求失败')
        } finally {
            recalcLoading.value = false
        }
    })
    .catch(() => {})
}



const logisticsPreviewData = ref({})
const logisticsLoading = ref({})

const handleLogisticsPreview = async (orderNo) => {
    if (logisticsPreviewData.value[orderNo]) return // Already loaded
    
    logisticsLoading.value[orderNo] = true
    try {
        const res = await getLogistics({ search: orderNo, page: 1, per_page: 5 })
        if (res.code === 200 && res.data.items.length > 0) {
            // Find the exact match or the most relevant one
            // filtering by order_no happens in backend search, so take the first relevant one
            logisticsPreviewData.value[orderNo] = res.data.items.filter(item => item.ref_no === orderNo || item.tracking_no === orderNo)
        } else {
            logisticsPreviewData.value[orderNo] = []
        }
    } catch (error) {
        console.error(error)
        logisticsPreviewData.value[orderNo] = []
    } finally {
        logisticsLoading.value[orderNo] = false
    }
}
</script>

<style scoped>
.page-container {
  padding: 0;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.header-right {
    display: flex;
    align-items: center;
}
.page-header h2 {
    margin: 0;
    font-size: 20px;
    font-weight: 500;
}
.pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
}
.product-name {
    font-weight: 500;
}
.product-sku {
    font-size: 12px;
    color: #909399;
}
.sub-text {
    font-size: 12px;
    color: #909399;
}
.profit-positive {
    color: #67C23A;
    font-weight: bold;
}
.profit-negative {
    color: #F56C6C;
    font-weight: bold;
}

.error-list {
    max-height: 300px;
    overflow-y: auto;
    background: #f5f7fa;
    padding: 10px;
    border-radius: 4px;
    margin-top: 10px;
}
.error-item {
    color: #f56c6c;
    font-size: 12px;
    margin-bottom: 5px;
    border-bottom: 1px solid #ebeef5;
    padding-bottom: 5px;
}
.content-card {
    min-height: calc(100vh - 140px);
}
.link-text {
    color: #409EFF;
    cursor: pointer;
    text-decoration: underline;
}
.link-text:hover {
    color: #66b1ff;
}
.kpi-card {
    text-align: center;
}
.logistics-preview-item p {
    margin: 5px 0;
    font-size: 13px;
}
.no-data {
    text-align: center;
    color: #909399;
    padding: 10px;
}
</style>
