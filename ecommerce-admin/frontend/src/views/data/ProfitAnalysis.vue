<template>
  <div class="page-container">
    <div class="page-header">
      <h2>盈亏分析</h2>
      <div class="actions">
        <el-button type="primary" :loading="calculating" @click="handleCalculate">
          <el-icon><Refresh /></el-icon>
          重新计算盈亏
        </el-button>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>总销售额</span>
            </div>
          </template>
          <div class="card-value">¥ {{ stats.total_revenue.toFixed(2) }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>总订单数</span>
            </div>
          </template>
          <div class="card-value">{{ stats.total_orders }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>总毛利</span>
            </div>
          </template>
          <div class="card-value" :class="stats.total_profit >= 0 ? 'positive' : 'negative'">
            ¥ {{ stats.total_profit.toFixed(2) }}
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>毛利率</span>
            </div>
          </template>
          <div class="card-value" :class="stats.profit_margin >= 0 ? 'positive' : 'negative'">
            {{ stats.profit_margin }}%
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="chart-card" style="margin-top: 20px;">
        <template #header>
            <div class="card-header">
              <span>分析说明</span>
            </div>
        </template>
        <div class="analysis-desc">
            <p>1. <strong>毛利计算公式</strong>: 订单实付金额 - (下单数量 * 产品最新采购价) - 对应物流单的实际运费 - 税费</p>
            <p>2. <strong>数据关联</strong>: </p>
            <ul>
                <li>产品成本: 依据 SKU 关联采购记录中最新的采购单价。</li>
                <li>物流费用: 依据 平台订单号(Order No) 关联 物流单中的 参考号/客户订单号。</li>
            </ul>
            <p>3. <strong>注意</strong>: 如果 SKU 不存在采购记录，则成本为 0。如果订单没有匹配到物流单，则物流费用为 0。</p>
        </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { calculateProfit, getProfitStats } from '@/api/analysis'
import { ElMessage } from 'element-plus'

const calculating = ref(false)
const stats = ref({
    total_revenue: 0,
    total_profit: 0,
    total_orders: 0,
    profit_margin: 0
})

const fetchStats = async () => {
    try {
        const res = await getProfitStats()
        if (res.code === 200) {
            stats.value = res.data
        }
    } catch (error) {
        console.error(error)
        // ElMessage.error('获取统计数据失败')
    }
}

const handleCalculate = async () => {
    calculating.value = true
    try {
        const res = await calculateProfit()
        if (res.code === 200) {
            ElMessage.success(res.message)
            fetchStats()
        }
    } catch (error) {
        console.error(error)
        ElMessage.error('计算失败')
    } finally {
        calculating.value = false
    }
}

onMounted(() => {
    fetchStats()
})
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
.page-header h2 {
    margin: 0;
    font-size: 20px;
    font-weight: 500;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-value {
    font-size: 24px;
    font-weight: bold;
    color: #303133;
    margin-top: 10px;
}
.positive {
    color: #67C23A;
}
.negative {
    color: #F56C6C;
}
.analysis-desc {
    font-size: 14px;
    color: #606266;
    line-height: 1.8;
}
.analysis-desc ul {
    margin: 5px 0;
    padding-left: 20px;
}
</style>
