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
            <!-- 隐藏的多选文件框 -->
            <input 
              type="file" 
              ref="fileInput" 
              multiple 
              accept=".xlsx,.xls" 
              style="display: none" 
              @change="handleFilesSelected" 
            />
            <el-button type="primary" :loading="loading" @click="$refs.fileInput.click()" :disabled="loading">
                <el-icon class="el-icon--left"><Upload /></el-icon>
                批量导入 Excel
            </el-button>
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
        @sort-change="handleSortChange"
        :default-sort="{ prop: 'create_time', order: 'descending' }"
      >
        <el-table-column type="expand">
          <template #default="props">
            <div style="padding: 15px; background-color: #f8f9fc;">
              <el-table :data="props.row.items" border size="small" style="width: 100%">
                <el-table-column prop="sku" label="SKU" width="180" />
                <el-table-column prop="product_name" label="商品名称" min-width="200" />
                <el-table-column prop="model" label="型号" width="120" />
                <el-table-column prop="quantity" label="数量" width="100" align="center" />
                <el-table-column prop="unit_price" label="单价(元)" width="120" align="right">
                    <template #default="scope">¥{{ scope.row.unit_price }}</template>
                </el-table-column>
                <el-table-column prop="goods_amount" label="总价(元)" width="120" align="right">
                    <template #default="scope">¥{{ scope.row.goods_amount }}</template>
                </el-table-column>
              </el-table>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="purchase_no" :label="$t('purchases.purchaseNo')" width="180" fixed sortable="custom" />
        
        <el-table-column label="概览" min-width="150">
          <template #default="scope">
            <div class="product-info">
              <div class="product-name">{{ scope.row.sku }}</div>
              <div class="product-sku" v-if="scope.row.items && scope.row.items.length > 0">
                 共 {{ scope.row.items.length }} 种商品
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column :label="$t('purchases.purchaseInfo')" width="180">
          <template #default="scope">
            <div class="purchase-info">
              <div>总件数: {{ scope.row.quantity }}</div>
              <div>货单价: {{ scope.row.goods_amount }}</div>
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

        <el-table-column prop="create_time" label="创建时间" width="180" sortable="custom" />

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
        width="65%"
      >
        <div v-if="currentPurchase">
            <el-descriptions :column="2" border>
                <el-descriptions-item :label="$t('purchases.purchaseNo')">{{ currentPurchase.purchase_no }}</el-descriptions-item>
                <el-descriptions-item label="创建时间">{{ currentPurchase.create_time }}</el-descriptions-item>
                <el-descriptions-item label="供应商公司">{{ currentPurchase.supplier_company }}</el-descriptions-item>
                <el-descriptions-item label="供应商会员">{{ currentPurchase.supplier_member }}</el-descriptions-item>
                <el-descriptions-item :label="$t('common.status')">{{ currentPurchase.order_status }}</el-descriptions-item>
                <el-descriptions-item label="总数量">{{ currentPurchase.quantity }}</el-descriptions-item>
                <el-descriptions-item label="货品总价">{{ currentPurchase.goods_amount }}</el-descriptions-item>
                <el-descriptions-item label="运费">{{ currentPurchase.shipping_fee }}</el-descriptions-item>
                <el-descriptions-item label="折扣/涨价">{{ currentPurchase.discount }}</el-descriptions-item>
                <el-descriptions-item label="实付金额">{{ currentPurchase.actual_payment }}</el-descriptions-item>
                <el-descriptions-item label="物流公司">{{ currentPurchase.logistics_company }}</el-descriptions-item>
                <el-descriptions-item label="物流单号">{{ currentPurchase.logistics_no }}</el-descriptions-item>
                <el-descriptions-item label="付款时间">{{ currentPurchase.pay_time }}</el-descriptions-item>
                <el-descriptions-item label="收件人：">{{ currentPurchase.receiver_name || '-' }} {{ currentPurchase.receiver_mobile }}</el-descriptions-item>
                <el-descriptions-item label="收货地址" :span="2">{{ currentPurchase.receiver_address }}</el-descriptions-item>
            </el-descriptions>
            
            <el-divider content-position="left">商品明细</el-divider>
            
            <el-table :data="currentPurchase.items" border stripe style="width: 100%; margin-top: 15px;">
                <el-table-column prop="sku" label="SKU" width="150" />
                <el-table-column prop="product_name" label="商品名称" min-width="180" />
                <el-table-column prop="model" label="型号/规格" width="120" />
                <el-table-column prop="quantity" label="数量" width="80" align="center" />
                <el-table-column prop="unit_price" label="单价" width="100" align="right" />
                <el-table-column prop="goods_amount" label="总价" width="100" align="right" />
            </el-table>
        </div>
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

const sortBy = ref('create_time')
const sortOrder = ref('descending')

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
            end_date: periodParams.value.endDate,
            sort_by: sortBy.value,
            sort_order: sortOrder.value
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

const handleSortChange = ({ prop, order }) => {
    if (order) {
        sortBy.value = prop
        sortOrder.value = order
    } else {
        sortBy.value = 'create_time'
        sortOrder.value = 'descending'
    }
    currentPage.value = 1
    fetchData()
}

// Upload methods...
const fileInput = ref(null)

const handleFilesSelected = async (event) => {
    const files = event.target.files
    if (!files || files.length === 0) return
    
    loading.value = true
    const formData = new FormData()
    for (let i = 0; i < files.length; i++) {
        formData.append('file', files[i])
    }
    
    try {
        const res = await uploadPurchases(formData)
        if (res.code === 200) {
            ElMessage.success(res.message)
            if (res.data && res.data.errors && res.data.errors.length > 0) {
                // 如果有部分错误，提示一下
                ElMessage.warning(`其中有 ${res.data.errors.length} 个警告/错误，请核对`)
                console.warn("Import warning:", res.data.errors)
            }
            handleSearch()
        } else {
            ElMessage.error(res.message || '导入失败')
        }
    } catch (e) {
        ElMessage.error('上传出错')
    } finally {
        loading.value = false
        if (fileInput.value) {
            fileInput.value.value = '' // Reset input so same files can be selected again
        }
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
