<template>
  <div class="page-container">
    <div class="page-header">
      <h2>{{ $t('inventory.title') }}</h2>
      <div class="header-right">
        <div class="action-buttons">
          <el-button type="primary" @click="openCreateDialog">
            <el-icon class="el-icon--left"><Plus /></el-icon>
            {{ $t('inventory.addNew') }}
          </el-button>
          <el-upload
            class="upload-inline"
            action="#"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleImport"
            accept=".xlsx, .xls"
          >
            <el-button type="success" plain>
              <el-icon class="el-icon--left"><Upload /></el-icon>
              {{ $t('inventory.importExcel') }}
            </el-button>
          </el-upload>
          <el-upload
            class="upload-inline"
            action="#"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="(file) => handleImport(file, true)"
            accept=".xlsx, .xls"
          >
            <el-button type="danger" plain title="清空并重新导入">
              <el-icon class="el-icon--left"><Delete /></el-icon>
              {{ $t('inventory.resetImport') }}
            </el-button>
          </el-upload>
        </div>
        <el-input
          v-model="searchQuery"
          :placeholder="$t('common.search') + '...'"
          clearable
          @clear="handleSearch"
          @keyup.enter="handleSearch"
          class="search-input"
        >
          <template #append>
            <el-button @click="handleSearch">
              <el-icon><Search /></el-icon>
            </el-button>
          </template>
        </el-input>
      </div>
    </div>

    <!-- KPI Cards for Stock Overview -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card shadow="hover" class="kpi-card glass-card">
          <div class="kpi-label">{{ $t('inventory.totalSitus') }}</div>
          <div class="kpi-value">{{ total }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="kpi-card glass-card">
          <div class="kpi-label">{{ $t('inventory.lowStockItems') }}</div>
          <div class="kpi-value warning-text">{{ lowStockCount }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Stock Table -->
    <el-card shadow="never" class="content-card">
      <el-table 
        :data="tableData" 
        v-loading="loading" 
        style="width: 100%" 
        border 
        stripe
        @filter-change="handleFilterChange"
      >
        <el-table-column 
          prop="model" 
          :label="$t('inventory.model')" 
          width="150"
          sortable
        >
          <template #default="{ row }">
            <span class="model-tag">{{ row.model }}</span>
          </template>
        </el-table-column>
        <el-table-column 
          prop="status" 
          :label="$t('inventory.status')" 
          width="130"
          align="center"
          :filters="[
            { text: $t('inventory.normal'), value: 'NORMAL' },
            { text: $t('inventory.lowStock'), value: 'LOW' },
            { text: $t('inventory.outOfStock'), value: 'OUT' }
          ]"
          :filter-multiple="false"
          column-key="status"
        >
          <template #default="{ row }">
            <el-tag v-if="row.quantity > 5" type="success" size="small" effect="light">
              {{ $t('inventory.normal') }}
            </el-tag>
            <el-tag v-elif="row.quantity > 0" type="danger" size="small" effect="dark">
              {{ $t('inventory.lowStock') }}
            </el-tag>
            <el-tag v-else type="info" size="small" effect="plain">
              {{ $t('inventory.outOfStock') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="spec" :label="$t('inventory.spec')" width="150" />
        <el-table-column prop="quantity" :label="$t('inventory.quantity')" align="center">
          <template #default="{ row }">
            <el-tag :type="row.quantity > 5 ? 'success' : 'danger'" effect="dark">
              {{ row.quantity }} {{ row.unit }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="avg_cost" :label="$t('inventory.avgCost')" align="right">
          <template #default="{ row }">
            ¥{{ typeof row.avg_cost === 'number' ? row.avg_cost.toFixed(2) : row.avg_cost }}
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" :label="$t('common.updateTime')" width="180" />
        <el-table-column :label="$t('common.actions')" width="320" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button type="primary" size="small" @click="openAdjustDialog(row, 'IN')">
                {{ $t('inventory.inbound') }}
              </el-button>
              <el-button type="warning" size="small" @click="openAdjustDialog(row, 'OUT')">
                {{ $t('inventory.outbound') }}
              </el-button>
              <el-button type="danger" size="small" @click="openAdjustDialog(row, 'ADJ')">
                {{ $t('inventory.adjustment') }}
              </el-button>
              <el-button link type="primary" @click="viewHistory(row)">
                {{ $t('inventory.history') }}
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

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
    </el-card>

    <!-- Adjustment Dialog -->
    <el-dialog
      v-model="adjustDialogVisible"
      :title="adjustTitle"
      width="400px"
      class="premium-dialog"
    >
      <el-form :model="adjustForm" label-width="100px" style="padding: 20px 0;">
        <el-form-item :label="$t('inventory.model')">
          <el-tag>{{ currentItem?.model }}</el-tag>
        </el-form-item>
        <el-form-item :label="$t('inventory.changeQty')">
          <el-input-number v-model="adjustForm.quantity" :step="1" />
        </el-form-item>
        <el-form-item :label="$t('inventory.unitCost')" v-if="adjustForm.type === 'IN'">
          <el-input v-model="adjustForm.unit_cost" placeholder="0.00">
            <template #prefix>¥</template>
          </el-input>
        </el-form-item>
        <el-form-item :label="$t('common.remark')">
          <el-input v-model="adjustForm.remark" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="adjustDialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submitAdjustment" :loading="submitLoading">
          {{ $t('common.confirm') }}
        </el-button>
      </template>
    </el-dialog>

    <!-- Create Dialog -->
    <el-dialog
      v-model="createDialogVisible"
      :title="$t('inventory.createTitle')"
      width="450px"
      class="premium-dialog"
    >
      <el-form :model="createForm" label-width="120px" style="padding: 20px 0;">
        <el-form-item :label="$t('inventory.model')" required>
          <el-input v-model="createForm.model" placeholder="如: B002" />
        </el-form-item>
        <el-form-item :label="$t('inventory.spec')">
          <el-input v-model="createForm.spec" placeholder="如: 20cm 或 Black" />
        </el-form-item>
        <el-form-item :label="$t('inventory.unit')">
          <el-input v-model="createForm.unit" placeholder="pcs" />
        </el-form-item>
        <el-form-item :label="$t('inventory.quantity')">
          <el-input-number v-model="createForm.quantity" :step="1" />
        </el-form-item>
        <el-form-item :label="$t('inventory.avgCost')">
          <el-input v-model="createForm.avg_cost" placeholder="0.00">
            <template #prefix>¥</template>
          </el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submitCreate" :loading="submitLoading">
          {{ $t('common.confirm') }}
        </el-button>
      </template>
    </el-dialog>

    <!-- History Drawer -->
    <el-drawer
      v-model="historyVisible"
      :title="$t('inventory.movementHistory') + ' - ' + currentItem?.model"
      size="600px"
    >
      <el-timeline style="padding: 20px;">
        <el-timeline-item
          v-for="record in historyData"
          :key="record.id"
          :timestamp="record.created_at"
          :type="getRecordType(record.record_type)"
        >
          <div class="history-item">
            <div class="record-header">
              <el-tag :type="getRecordType(record.record_type)" size="small">
                {{ $t('inventory.' + record.record_type.toLowerCase()) }}
              </el-tag>
              <span class="change-qty" :class="record.change_quantity > 0 ? 'plus' : 'minus'">
                {{ record.change_quantity > 0 ? '+' : '' }}{{ record.change_quantity }}
              </span>
            </div>
            <div class="record-details">
              <p v-if="record.order_no">{{ $t('orders.orderNo') }}: {{ record.order_no }}</p>
              <p v-if="record.purchase_no">{{ $t('purchases.purchaseNo') }}: {{ record.purchase_no }}</p>
              <p v-if="record.remark">{{ $t('common.remark') }}: {{ record.remark }}</p>
              <p class="balance">{{ $t('inventory.balance') }}: {{ record.balance_quantity }}</p>
            </div>
          </div>
        </el-timeline-item>
      </el-timeline>
      <div v-if="historyData.length === 0" class="no-data">
        <el-empty :description="$t('common.noData')" />
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { Plus, Upload, Search, Delete } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import request from '@/utils/request'

const { t } = useI18n()

// Data State
const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const lowStockCount = ref(0)
const statusFilter = ref('')

// Dialog/Drawer State
const adjustDialogVisible = ref(false)
const historyVisible = ref(false)
const currentItem = ref(null)
const submitLoading = ref(false)
const adjustForm = ref({
  quantity: 1,
  unit_cost: '',
  remark: '',
  type: 'IN'
})
const createDialogVisible = ref(false)
const createForm = ref({
  model: '',
  spec: '',
  unit: 'pcs',
  quantity: 0,
  avg_cost: ''
})
const historyData = ref([])

onMounted(() => {
  fetchData()
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await request({
      url: '/inventory',
      method: 'get',
      params: {
        page: currentPage.value,
        per_page: pageSize.value,
        search: searchQuery.value,
        status: statusFilter.value
      }
    })
    if (res.code === 200) {
      tableData.value = res.data.items
      total.value = res.data.total
      lowStockCount.value = tableData.value.filter(i => i.quantity <= 5).length
    }
  } catch (error) {
    ElMessage.error(t('common.loadingError'))
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

const handleFilterChange = (filters) => {
  if (filters.status) {
    statusFilter.value = filters.status[0] || ''
    currentPage.value = 1
    fetchData()
  }
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchData()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchData()
}

const openAdjustDialog = (row, type) => {
  currentItem.value = row
  adjustForm.value = {
    quantity: 1,
    unit_cost: row.avg_cost,
    remark: '',
    type: type
  }
  adjustDialogVisible.value = true
}

const adjustTitle = computed(() => {
  if (adjustForm.value.type === 'IN') return t('inventory.inbound')
  if (adjustForm.value.type === 'OUT') return t('inventory.outbound')
  return t('inventory.adjustment')
})

const openCreateDialog = () => {
  createForm.value = {
    model: '',
    spec: '',
    unit: 'pcs',
    quantity: 0,
    avg_cost: ''
  }
  createDialogVisible.value = true
}

const submitCreate = async () => {
  if (!createForm.value.model) {
    ElMessage.warning(t('inventory.model') + ' ' + t('common.required'))
    return
  }
  submitLoading.value = true
  try {
    const res = await request({
      url: '/inventory',
      method: 'post',
      data: createForm.value
    })
    if (res.code === 200) {
      ElMessage.success(t('common.success'))
      createDialogVisible.value = false
      fetchData()
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || t('common.error'))
  } finally {
    submitLoading.value = false
  }
}

const handleImport = async (file, clearExisting = false) => {
  if (clearExisting) {
    try {
      await ElMessageBox.confirm(
        t('inventory.resetConfirm'),
        t('common.warning'),
        {
          confirmButtonText: t('common.confirm'),
          cancelButtonText: t('common.cancel'),
          type: 'warning',
        }
      )
    } catch {
      return
    }
  }

  const loadingInstance = ElLoading.service({
    lock: true,
    text: t('common.processing') || 'Processing...',
    background: 'rgba(0, 0, 0, 0.7)',
  })

  const formData = new FormData()
  formData.append('file', file.raw)
  formData.append('clear_existing', clearExisting)
  
  try {
    const res = await request({
      url: '/inventory/import',
      method: 'post',
      data: formData,
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    if (res.code === 200) {
      ElMessage.success(res.message)
      fetchData()
    } else {
      ElMessage.error(res.message || t('common.error'))
    }
  } catch (error) {
    console.error('Import error:', error)
    ElMessage.error(error.response?.data?.message || t('common.error'))
  } finally {
    loadingInstance.close()
  }
}

const submitAdjustment = async () => {
  submitLoading.value = true
  try {
    const changeQty = adjustForm.value.type === 'IN' ? adjustForm.value.quantity : -adjustForm.value.quantity
    const res = await request({
      url: '/inventory/adjust',
      method: 'post',
      data: {
        inventory_id: currentItem.value.id,
        change_quantity: changeQty,
        record_type: adjustForm.value.type,
        unit_cost: adjustForm.value.unit_cost,
        remark: adjustForm.value.remark
      }
    })
    if (res.code === 200) {
      ElMessage.success(t('common.success'))
      adjustDialogVisible.value = false
      fetchData()
    }
  } catch (error) {
    ElMessage.error(t('common.error'))
  } finally {
    submitLoading.value = false
  }
}

const viewHistory = async (row) => {
  currentItem.value = row
  historyVisible.value = true
  try {
    const res = await request({
      url: '/inventory/records',
      method: 'get',
      params: { inventory_id: row.id }
    })
    if (res.code === 200) {
      historyData.value = res.data.items
    }
  } catch (error) {
    ElMessage.error(t('common.loadingError'))
  }
}

const getRecordType = (type) => {
  if (type === 'IN') return 'primary'
  if (type === 'OUT') return 'warning'
  return 'danger'
}
</script>

<style scoped>
.page-container { padding: 0px; }
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  background: #fff;
  padding: 16px 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
}
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.action-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}
.upload-inline {
  display: inline-block;
}
.search-input {
  width: 250px;
}
.table-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: nowrap;
}
.page-header h2 { margin: 0; font-size: 20px; font-weight: 600; }

.kpi-card {
  text-align: center;
  border-radius: 12px;
}
.glass-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}
.kpi-label { font-size: 14px; color: #909399; margin-bottom: 8px; }
.kpi-value { font-size: 28px; font-weight: bold; color: #409EFF; }
.warning-text { color: #F56C6C; }

.model-tag {
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  color: #304156;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.history-item {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
}
.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.change-qty { font-weight: bold; font-size: 16px; }
.plus { color: #67C23A; }
.minus { color: #F56C6C; }
.record-details p { margin: 4px 0; font-size: 13px; color: #606266; }
.balance { font-weight: 500; font-size: 12px; color: #909399; margin-top: 8px !important; }

.no-data { padding: 40px 0; }
</style>
