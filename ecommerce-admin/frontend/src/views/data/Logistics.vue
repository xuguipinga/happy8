<template>
  <div class="page-container">
    <div class="page-header">
      <h2>{{ $t('logistics.title') }}</h2>
      <div class="header-right">
        <div class="search-box">
             <el-input
                v-model="searchQuery"
                :placeholder="$t('common.search') + '...'"
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
                {{ $t('logistics.importExcel') }}
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
            <div class="stat-label">{{ $t('logistics.stats.totalFee') }}</div>
            <div class="stat-value warning">¥{{ statistics.total_shipping_fee.toLocaleString() }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">{{ $t('logistics.stats.count') }}</div>
            <div class="stat-value info">{{ statistics.total_shipment_count }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">{{ $t('logistics.stats.avgFee') }}</div>
            <div class="stat-value">¥{{ statistics.avg_shipping_fee.toFixed(2) }}</div>
          </div>
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
        <el-table-column prop="tracking_no" :label="$t('logistics.trackingNo')" width="180" fixed />
        <el-table-column :label="$t('logistics.refNo')" width="180">
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
        
        <el-table-column :label="$t('logistics.channel')" min-width="200">
          <template #default="scope">
            <div>{{ scope.row.logistics_channel }}</div>
            <div class="sub-text" v-if="scope.row.service_type">类型: {{ scope.row.service_type }}</div>
            <div class="sub-text">{{ scope.row.destination }} ({{ scope.row.zone }})</div>
            <div class="sub-text" v-if="scope.row.warehouse">仓库: {{ scope.row.warehouse }}</div>
          </template>
        </el-table-column>
        
        <el-table-column :label="$t('logistics.weight')" width="150">
          <template #default="scope">
            <div>预报: {{ scope.row.pre_weight }}</div>
            <div>实际: {{ scope.row.actual_weight }}</div>
          </template>
        </el-table-column>

        <el-table-column :label="$t('logistics.fee')" width="150">
          <template #default="scope">
            <div class="fee-info">
              <div>申报: {{ scope.row.declared_value }}</div>
              <div>标准: {{ scope.row.shipping_fee }}</div>
              <div>优惠: {{ scope.row.discount_fee }}</div>
              <div>实收: {{ scope.row.actual_fee }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="order_status" :label="$t('common.status')" width="100">
          <template #default="scope">
            <el-tag>{{ scope.row.order_status }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="sent_date" :label="$t('logistics.sentDate')" width="120" />
        <el-table-column prop="create_time" label="创建时间" width="180" />

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
        <el-descriptions :column="2" border v-if="currentLogistics">
            <el-descriptions-item :label="$t('logistics.trackingNo')">{{ currentLogistics.tracking_no }}</el-descriptions-item>
            <el-descriptions-item :label="$t('logistics.refNo')">{{ currentLogistics.ref_no }}</el-descriptions-item>
            <el-descriptions-item label="物流渠道">{{ currentLogistics.logistics_channel }}</el-descriptions-item>
            <el-descriptions-item label="目的地">{{ currentLogistics.destination }}</el-descriptions-item>
            <el-descriptions-item label="分区">{{ currentLogistics.zone }}</el-descriptions-item>
            <el-descriptions-item :label="$t('common.status')">{{ currentLogistics.order_status }}</el-descriptions-item>
            <el-descriptions-item :label="$t('logistics.sentDate')">{{ currentLogistics.sent_date }}</el-descriptions-item>
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
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { uploadLogistics, previewLogistics } from '@/api/upload'
import { getLogistics } from '@/api/logistics'
import { getOrders } from '@/api/orders'
import { getLogisticsStatistics } from '@/api/statistics'
import PeriodSelector from '@/components/PeriodSelector.vue'
import { ElMessage } from 'element-plus'

const { t } = useI18n()
const router = useRouter()
const loading = ref(false)
const tableLoading = ref(false)
const tableData = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

const searchQuery = ref('')
const detailsDialogVisible = ref(false)
const currentLogistics = ref(null)

const periodParams = ref({
  period: 'month',
  startDate: '', // Will be set by PeriodSelector
  endDate: ''
})

const statistics = ref({
  total_shipping_fee: 0,
  total_shipment_count: 0,
  avg_shipping_fee: 0
})

const fetchStatistics = async () => {
  try {
    const res = await getLogisticsStatistics({
      period: periodParams.value.period,
      start_date: periodParams.value.startDate,
      end_date: periodParams.value.endDate,
      search: searchQuery.value
    })
    
    if (res.code === 200) {
      const items = res.data.items
      const totalFee = items.reduce((sum, item) => sum + item.shipping_fee, 0)
      const totalCount = items.reduce((sum, item) => sum + item.shipment_count, 0)
      statistics.value = {
        total_shipping_fee: totalFee,
        total_shipment_count: totalCount,
        avg_shipping_fee: totalCount > 0 ? totalFee / totalCount : 0
      }
    }
  } catch (error) {}
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
        ElMessage.error(t('common.loading') + ' ' + t('common.noData'))
    } finally {
        tableLoading.value = false
    }
}

const handleSearch = () => {
    currentPage.value = 1
    fetchData()
    fetchStatistics()
}
onMounted(() => {
    // fetchData called by handleSearch when PeriodSelector emits change on mount
})

const handleSizeChange = (val) => {
    pageSize.value = val
    fetchData()
}
const handleCurrentChange = (val) => {
    currentPage.value = val
    fetchData()
}
const handleViewDetails = (row) => {
    currentLogistics.value = row
    detailsDialogVisible.value = true
}
const handleViewOrderDetails = (refNo) => {
    router.push(`/orders?search=${refNo}`)
}

// Upload methods...
const beforeUpload = (file) => true
const handleUpload = async (option) => {
    loading.value = true
    const formData = new FormData()
    formData.append('file', option.file)
    try {
        const res = await uploadLogistics(formData)
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
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.header-right { display: flex; align-items: center; }
.page-header h2 { margin: 0; font-size: 20px; font-weight: 500; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }
.sub-text { font-size: 12px; color: #909399; }
.content-card { min-height: calc(100vh - 140px); }
.link-text { color: #409EFF; cursor: pointer; text-decoration: underline; }
.stat-card { text-align: center; }
.stat-label { font-size: 14px; color: #909399; margin-bottom: 10px; }
.stat-value { font-size: 24px; font-weight: bold; color: #303133; }
.stat-value.warning { color: #E6A23C; }
.stat-value.info { color: #409EFF; }
</style>
