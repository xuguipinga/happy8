<template>
  <div class="page-container">
    <div class="page-header">
      <h2>{{ $t('purchases.title') }}</h2>
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
                {{ $t('purchases.importExcel') }}
            </el-button>
            </el-upload>
        </div>
      </div>
    </div>

    <!-- 时间选择器 -->
    <PeriodSelector v-model="periodParams" @change="handleSearch" style="margin-bottom: 20px;" />

    <!-- 统计汇总卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">{{ $t('purchases.stats.amount') }}</div>
            <div class="stat-value">¥{{ statistics.total_purchase_amount.toLocaleString() }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">{{ $t('purchases.stats.logisticsFee') }}</div>
            <div class="stat-value">¥{{ statistics.total_logistics_fee.toLocaleString() }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">{{ $t('purchases.stats.totalCost') }}</div>
            <div class="stat-value warning">¥{{ statistics.total_cost.toLocaleString() }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">{{ $t('purchases.stats.count') }}</div>
            <div class="stat-value info">{{ statistics.total_purchase_count }}</div>
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
        <el-table-column prop="purchase_no" :label="$t('purchases.purchaseNo')" width="180" fixed />
        
        <el-table-column :label="$t('purchases.productInfo')" min-width="250">
          <template #default="scope">
            <div class="product-info">
              <div class="product-name">{{ scope.row.product_name }}</div>
              <div class="product-sku">SKU: {{ scope.row.sku }}</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column :label="$t('purchases.purchaseInfo')" width="180">
          <template #default="scope">
            <div class="purchase-info">
              <div>数量: {{ scope.row.quantity }}</div>
              <div>单价: {{ scope.row.unit_price }}</div>
              <div>总价: {{ scope.row.goods_amount }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column :label="$t('purchases.fee')" width="150">
          <template #default="scope">
            <div class="fee-info">
              <div>运费: {{ scope.row.shipping_fee }}</div>
              <div>折扣: {{ scope.row.discount }}</div>
              <div>实付: {{ scope.row.actual_payment }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="order_status" :label="$t('common.status')" width="120">
          <template #default="scope">
            <el-tag>{{ scope.row.order_status }}</el-tag>
            <el-tag v-if="scope.row.is_dropship" type="warning" size="small" style="margin-left:5px">代发</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column :label="$t('purchases.supplier')" width="200">
          <template #default="scope">
            <div>{{ scope.row.supplier_company }}</div>
            <div class="sub-text">{{ scope.row.supplier_member }}</div>
          </template>
        </el-table-column>
        
        <el-table-column :label="$t('purchases.logistics')" width="200">
          <template #default="scope">
            <div>{{ scope.row.logistics_company }}</div>
            <div class="sub-text">
                <span 
                    v-if="scope.row.logistics_no"
                    class="link-text"
                    @click="router.push(`/logistics?search=${scope.row.logistics_no}`)"
                    title="查看物流"
                >
                    {{ scope.row.logistics_no }}
                </span>
                <span v-else>-</span>
            </div>
            <div v-if="scope.row.receiver_name" class="sub-text">收: {{ scope.row.receiver_name }}</div>
          </template>
        </el-table-column>

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
        <el-descriptions :column="2" border v-if="currentPurchase">
            <el-descriptions-item :label="$t('purchases.purchaseNo')">{{ currentPurchase.purchase_no }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ currentPurchase.create_time }}</el-descriptions-item>
            <el-descriptions-item label="供应商公司">{{ currentPurchase.supplier_company }}</el-descriptions-item>
            <el-descriptions-item label="供应商会员">{{ currentPurchase.supplier_member }}</el-descriptions-item>
            <el-descriptions-item :label="$t('common.status')">{{ currentPurchase.order_status }}</el-descriptions-item>
            <el-descriptions-item label="SKU">{{ currentPurchase.sku }}</el-descriptions-item>
            <el-descriptions-item label="商品名称" :span="2">{{ currentPurchase.product_name }}</el-descriptions-item>
            <el-descriptions-item label="数量">{{ currentPurchase.quantity }}</el-descriptions-item>
            <el-descriptions-item label="单价">{{ currentPurchase.unit_price }}</el-descriptions-item>
            <el-descriptions-item label="货品总价">{{ currentPurchase.goods_amount }}</el-descriptions-item>
            <el-descriptions-item label="运费">{{ currentPurchase.shipping_fee }}</el-descriptions-item>
            <el-descriptions-item label="折扣/涨价">{{ currentPurchase.discount }}</el-descriptions-item>
            <el-descriptions-item label="实付金额">{{ currentPurchase.actual_payment }}</el-descriptions-item>
            <el-descriptions-item label="物流公司">{{ currentPurchase.logistics_company }}</el-descriptions-item>
            <el-descriptions-item label="物流单号">{{ currentPurchase.logistics_no }}</el-descriptions-item>
            <el-descriptions-item label="付款时间">{{ currentPurchase.pay_time }}</el-descriptions-item>
            <el-descriptions-item label="收货地址" :span="2">{{ currentPurchase.receiver_address }}</el-descriptions-item>
        </el-descriptions>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { uploadPurchases, previewPurchases } from '@/api/upload'
import { getPurchases } from '@/api/purchases'
import { getPurchaseStatistics } from '@/api/statistics'
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
const currentPurchase = ref(null)

const periodParams = ref({
  period: 'month',
  startDate: '',
  endDate: ''
})

const statistics = ref({
  total_purchase_amount: 0,
  total_logistics_fee: 0,
  total_cost: 0,
  total_purchase_count: 0
})

const fetchStatistics = async () => {
  try {
    const res = await getPurchaseStatistics({
      period: periodParams.value.period,
      start_date: periodParams.value.startDate,
      end_date: periodParams.value.endDate,
      search: searchQuery.value
    })
    if (res.code === 200) {
      const items = res.data.items
      statistics.value = {
        total_purchase_amount: items.reduce((sum, item) => sum + item.purchase_amount, 0),
        total_logistics_fee: items.reduce((sum, item) => sum + item.logistics_fee, 0),
        total_cost: items.reduce((sum, item) => sum + item.total_cost, 0),
        total_purchase_count: items.reduce((sum, item) => sum + item.purchase_count, 0)
      }
    }
  } catch (error) {}
}

const fetchData = async () => {
    tableLoading.value = true
    try {
        const res = await getPurchases({
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
onMounted(() => {})

const handleSizeChange = (val) => {
    pageSize.value = val
    fetchData()
}
const handleCurrentChange = (val) => {
    currentPage.value = val
    fetchData()
}
const handleViewDetails = (row) => {
    currentPurchase.value = row
    detailsDialogVisible.value = true
}

// Upload methods...
const beforeUpload = (file) => true
const handleUpload = async (option) => {
    loading.value = true
    const formData = new FormData()
    formData.append('file', option.file)
    try {
        const res = await uploadPurchases(formData)
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
.product-name { font-weight: 500; }
.product-sku { font-size: 12px; color: #909399; }
.sub-text { font-size: 12px; color: #909399; }
.content-card { min-height: calc(100vh - 140px); }
.link-text { color: #409EFF; cursor: pointer; text-decoration: underline; }
.stat-card { text-align: center; }
.stat-label { font-size: 14px; color: #909399; margin-bottom: 10px; }
.stat-value { font-size: 24px; font-weight: bold; color: #303133; }
.stat-value.warning { color: #E6A23C; }
.stat-value.info { color: #409EFF; }
</style>
