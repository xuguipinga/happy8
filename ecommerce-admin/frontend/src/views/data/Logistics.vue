<template>
  <div class="page-container">
    <div class="page-header">
      <h2>物流管理</h2>
      <div class="header-right">
        <div class="search-box">
             <el-input
                v-model="searchQuery"
                placeholder="搜索运单号/参考号"
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
                导入物流单 (Excel)
            </el-button>
            </el-upload>
        </div>
      </div>
    </div>

    <!-- 时间选择器 -->
    <PeriodSelector v-model="periodParams" @change="handleSearch" style="margin-bottom: 20px;" />

    <!-- 统计汇总卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">物流总费用</div>
            <div class="stat-value warning">¥{{ statistics.total_shipping_fee.toLocaleString() }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">物流单数</div>
            <div class="stat-value info">{{ statistics.total_shipment_count }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">平均物流费</div>
            <div class="stat-value">¥{{ statistics.avg_shipping_fee.toFixed(2) }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>


    <el-card class="content-card">
      <!-- 表格 -->
      <el-table :data="tableData" v-loading="tableLoading" style="width: 100%" border stripe>
        <el-table-column prop="tracking_no" label="运单号" width="180" fixed />
        <el-table-column label="参考号/订单号" width="180">
          <template #default="scope">
            <div v-if="scope.row.ref_no" class="link-text" @click="handleViewOrderDetails(scope.row.ref_no)">
                {{ scope.row.ref_no }}
            </div>
            <div v-if="scope.row.customer_order_no" class="sub-text" title="客户订单号">
                Cust: {{ scope.row.customer_order_no }}
            </div>
            <span v-if="!scope.row.ref_no && !scope.row.customer_order_no">-</span>
          </template>
        </el-table-column>
        
        <el-table-column label="渠道信息" min-width="200">
          <template #default="scope">
            <div>{{ scope.row.logistics_channel }}</div>
            <div class="sub-text" v-if="scope.row.service_type">类型: {{ scope.row.service_type }}</div>
            <div class="sub-text">{{ scope.row.destination }} ({{ scope.row.zone }})</div>
            <div class="sub-text" v-if="scope.row.warehouse">仓库: {{ scope.row.warehouse }}</div>
          </template>
        </el-table-column>
        
        <el-table-column label="重量(kg)" width="150">
          <template #default="scope">
            <div>预报: {{ scope.row.pre_weight }}</div>
            <div>实际: {{ scope.row.actual_weight }}</div>
          </template>
        </el-table-column>

        <el-table-column label="费用" width="150">
          <template #default="scope">
            <div class="fee-info">
              <div>申报: {{ scope.row.declared_value }}</div>
              <div>标准: {{ scope.row.shipping_fee }}</div>
              <div>优惠: {{ scope.row.discount_fee }}</div>
              <div>实收: {{ scope.row.actual_fee }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="order_status" label="状态" width="100">
          <template #default="scope">
            <el-tag>{{ scope.row.order_status }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="sent_date" label="发货日期" width="120" />
        <el-table-column prop="create_time" label="创建时间" width="180" />

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
        title="物流单详情"
        width="60%"
      >
        <el-descriptions :column="2" border v-if="currentLogistics">
            <el-descriptions-item label="运单号">{{ currentLogistics.tracking_no }}</el-descriptions-item>
            <el-descriptions-item label="参考号/订单号">{{ currentLogistics.ref_no }}</el-descriptions-item>
            <el-descriptions-item label="物流渠道">{{ currentLogistics.logistics_channel }}</el-descriptions-item>
            <el-descriptions-item label="目的地">{{ currentLogistics.destination }}</el-descriptions-item>
            <el-descriptions-item label="分区">{{ currentLogistics.zone }}</el-descriptions-item>
            <el-descriptions-item label="状态">{{ currentLogistics.order_status }}</el-descriptions-item>
            <el-descriptions-item label="发货日期">{{ currentLogistics.sent_date }}</el-descriptions-item>
            <el-descriptions-item label="预报重量">{{ currentLogistics.pre_weight }}</el-descriptions-item>
            <el-descriptions-item label="实际重量">{{ currentLogistics.actual_weight }}</el-descriptions-item>
            <el-descriptions-item label="申报价值">{{ currentLogistics.declared_value }}</el-descriptions-item>
            <el-descriptions-item label="运费">{{ currentLogistics.shipping_fee }}</el-descriptions-item>
            <el-descriptions-item label="优惠金额">{{ currentLogistics.discount_fee }}</el-descriptions-item>
            <el-descriptions-item label="实付运费">{{ currentLogistics.actual_fee }}</el-descriptions-item>
            <el-descriptions-item label="付款方式">{{ currentLogistics.payment_method }}</el-descriptions-item>
            
            <el-descriptions-item label="服务类型">{{ currentLogistics.service_type }}</el-descriptions-item>
            <el-descriptions-item label="仓库">{{ currentLogistics.warehouse }}</el-descriptions-item>
            <el-descriptions-item label="下单账号">{{ currentLogistics.ordering_account }}</el-descriptions-item>
            <el-descriptions-item label="客单号">{{ currentLogistics.customer_order_no }}</el-descriptions-item>
            <el-descriptions-item label="发件人">{{ currentLogistics.sender_name }} ({{ currentLogistics.sender_email }})</el-descriptions-item>
            <el-descriptions-item label="入库时间">{{ currentLogistics.inbound_time }}</el-descriptions-item>
            <el-descriptions-item label="出库时间">{{ currentLogistics.outbound_time }}</el-descriptions-item>
            <el-descriptions-item label="支付时间">{{ currentLogistics.payment_time }}</el-descriptions-item>
            
            <el-descriptions-item label="创建时间">{{ currentLogistics.create_time }}</el-descriptions-item>
        </el-descriptions>
      </el-dialog>

      <!-- 订单详情弹窗 -->
      <el-dialog
        v-model="orderDialogVisible"
        title="关联订单详情"
        width="60%"
      >
        <el-descriptions :column="2" border v-if="currentOrder">
            <el-descriptions-item label="平台订单号">{{ currentOrder.platform_order_no }}</el-descriptions-item>
            <el-descriptions-item label="下单时间">{{ currentOrder.order_time }}</el-descriptions-item>
            <el-descriptions-item label="买家姓名">{{ currentOrder.buyer_name }}</el-descriptions-item>
            <el-descriptions-item label="买家国家">{{ currentOrder.buyer_country }}</el-descriptions-item>
            <el-descriptions-item label="SKU">{{ currentOrder.sku }}</el-descriptions-item>
            <el-descriptions-item label="商品名称">{{ currentOrder.product_name }}</el-descriptions-item>
            <el-descriptions-item label="数量">{{ currentOrder.quantity }}</el-descriptions-item>
            <el-descriptions-item label="单价">{{ currentOrder.unit_price }} {{ currentOrder.currency }}</el-descriptions-item>
            <el-descriptions-item label="订单总额">{{ currentOrder.order_amount }}</el-descriptions-item>
            <el-descriptions-item label="实付金额">{{ currentOrder.actual_paid }}</el-descriptions-item>
            <el-descriptions-item label="采购成本">{{ currentOrder.cost_price }}</el-descriptions-item>
            <el-descriptions-item label="物流支出">{{ currentOrder.logistics_cost }}</el-descriptions-item>
            <el-descriptions-item label="毛利">
                <span :class="currentOrder.profit >= 0 ? 'profit-positive' : 'profit-negative'">{{ currentOrder.profit }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="收货地址" :span="2">{{ currentOrder.shipping_address }}</el-descriptions-item>
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
                    <el-table-column prop="tracking_no" label="运单号" />
                    <el-table-column prop="ref_no" label="参考号" />
                    <el-table-column prop="fee" label="运费" />
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
import { uploadLogistics, previewLogistics } from '@/api/upload'
import { getLogistics } from '@/api/logistics'
import { getOrders } from '@/api/orders'
import { getLogisticsStatistics } from '@/api/statistics'
import PeriodSelector from '@/components/PeriodSelector.vue'
import { ElMessage } from 'element-plus'

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
const detailsDialogVisible = ref(false)
const currentLogistics = ref(null)

// 统计数据
const getFormattedDate = (date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const today = new Date()
const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)

const periodParams = ref({
  period: 'month',
  startDate: getFormattedDate(firstDayOfMonth),
  endDate: getFormattedDate(today)
})


// ... existing code ...

const statistics = ref({
  total_shipping_fee: 0,
  total_shipment_count: 0,
  avg_shipping_fee: 0
})

const fetchStatistics = async (val) => {
  // If val is the params object from PeriodSelector change event, use it
  const params = (val && val.period) ? val : periodParams.value
  
  try {
    const res = await getLogisticsStatistics({
      period: params.period,
      start_date: params.startDate,
      end_date: params.endDate,
      search: searchQuery.value
    })
    
    if (res.code === 200) {
      const items = res.data.items
      const totalFee = items.reduce((sum, item) => sum + item.shipping_fee, 0)
      const totalCount = items.reduce((sum, item) => sum + item.shipment_count, 0)
      
      // Update Summary
      statistics.value = {
        total_shipping_fee: totalFee,
        total_shipment_count: totalCount,
        avg_shipping_fee: totalCount > 0 ? totalFee / totalCount : 0
      }
    }
  } catch (error) {
    console.error(error)
  }
}

const orderDialogVisible = ref(false)
const currentOrder = ref(null)

const handleViewOrderDetails = async (refNo) => {
    if (!refNo) return
    try {
        // Use the search API to find the order
        const res = await getOrders({
            page: 1,
            per_page: 1,
            search: refNo
        })
        if (res.code === 200 && res.data.items && res.data.items.length > 0) {
            currentOrder.value = res.data.items[0]
            orderDialogVisible.value = true
        } else {
            ElMessage.warning('未找到关联的订单信息')
        }
    } catch(err) {
        console.error(err)
        ElMessage.error('获取订单详情失败')
    }
}

const fetchData = async () => {
    tableLoading.value = true
    try {
        const res = await getLogistics({
            page: currentPage.value,
            per_page: pageSize.value,
            search: searchQuery.value,
            start_date: periodParams.value.startDate,
            end_date: periodParams.value.endDate
        })
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

const handleSearch = () => {
    currentPage.value = 1
    fetchData()
    fetchStatistics() // Refresh statistics with search
}

const handleViewDetails = (row) => {
    currentLogistics.value = row
    detailsDialogVisible.value = true
}

onMounted(() => {
    fetchData()
    // Statistics will be fetched automatically by PeriodSelector initialization
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
    const res = await previewLogistics(formData)
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
        const res = await uploadLogistics(formData)
        if (res.code === 200) {
            if (res.data.errors && res.data.errors.length > 0) {
                importResult.value = {
                    count: parseInt(res.message.match(/\d+/)[0]) || 0,
                    errors: res.data.errors
                }
                errorDialogVisible.value = true
            } else {
                ElMessage.success(res.message)
            }
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
.sub-text {
    font-size: 12px;
    color: #909399;
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
.profit-positive {
    color: #67C23A;
    font-weight: bold;
}
.profit-negative {
    color: #F56C6C;
    font-weight: bold;
}

.stat-card {
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-value.warning {
  color: #E6A23C;
}

.stat-value.info {
  color: #409EFF;
}
</style>
