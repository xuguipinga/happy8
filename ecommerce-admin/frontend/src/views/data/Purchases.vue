<template>
  <div class="page-container">
    <div class="page-header">
      <h2>采购管理</h2>
      <div class="header-right">
        <div class="search-box">
             <el-input
                v-model="searchQuery"
                placeholder="搜索采购单号/SKU/商品名"
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
                导入采购单 (Excel)
            </el-button>
            </el-upload>
        </div>
      </div>
    </div>

    <el-card class="content-card">
      <!-- 表格 -->
      <el-table :data="tableData" v-loading="tableLoading" style="width: 100%" border stripe>
        <el-table-column prop="purchase_no" label="采购单号" width="180" fixed />
        
        <el-table-column label="商品信息" min-width="250">
          <template #default="scope">
            <div class="product-info">
              <div class="product-name">{{ scope.row.product_name }}</div>
              <div class="product-sku">SKU: {{ scope.row.sku }}</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="采购信息" width="180">
          <template #default="scope">
            <div class="purchase-info">
              <div>数量: {{ scope.row.quantity }}</div>
              <div>单价: {{ scope.row.unit_price }}</div>
              <div>总价: {{ scope.row.goods_amount }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="费用" width="150">
          <template #default="scope">
            <div class="fee-info">
              <div>运费: {{ scope.row.shipping_fee }}</div>
              <div>折扣: {{ scope.row.discount }}</div>
              <div>实付: {{ scope.row.actual_payment }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="order_status" label="状态" width="100">
          <template #default="scope">
            <el-tag>{{ scope.row.order_status }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="供应商" width="200">
          <template #default="scope">
            <div>{{ scope.row.supplier_company }}</div>
            <div class="sub-text">{{ scope.row.supplier_member }}</div>
          </template>
        </el-table-column>
        
        <el-table-column label="物流" width="200">
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
          </template>
        </el-table-column>

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
        title="采购单详情"
        width="60%"
      >
        <el-descriptions :column="2" border v-if="currentPurchase">
            <el-descriptions-item label="采购单号">{{ currentPurchase.purchase_no }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ currentPurchase.create_time }}</el-descriptions-item>
            <el-descriptions-item label="供应商公司">{{ currentPurchase.supplier_company }}</el-descriptions-item>
            <el-descriptions-item label="供应商会员">{{ currentPurchase.supplier_member }}</el-descriptions-item>
            <el-descriptions-item label="买家公司">{{ currentPurchase.buyer_company }}</el-descriptions-item>
            <el-descriptions-item label="买家会员">{{ currentPurchase.buyer_member }}</el-descriptions-item>
            <el-descriptions-item label="订单状态">{{ currentPurchase.order_status }}</el-descriptions-item>
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
                    <el-table-column prop="purchase_no" label="采购单号" />
                    <el-table-column prop="product" label="商品" show-overflow-tooltip/>
                    <el-table-column prop="amount" label="金额" />
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
import { uploadPurchases, previewPurchases } from '@/api/upload'
import { getPurchases } from '@/api/purchases'
import { ElMessage } from 'element-plus'

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
const detailsDialogVisible = ref(false)
const currentPurchase = ref(null)

const fetchData = async () => {
    tableLoading.value = true
    try {
        const res = await getPurchases({
            page: currentPage.value,
            per_page: pageSize.value,
            search: searchQuery.value
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
}

const handleViewDetails = (row) => {
    currentPurchase.value = row
    detailsDialogVisible.value = true
}

onMounted(() => {
    fetchData()
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
    const res = await previewPurchases(formData)
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
        const res = await uploadPurchases(formData)
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
    text-decoration: underline;
}
</style>
