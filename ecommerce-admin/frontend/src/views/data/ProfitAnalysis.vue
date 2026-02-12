<template>
  <div class="profit-analysis">
    <div class="page-header">
      <h2>盈亏分析</h2>
    </div>

    <!-- 时间选择器 -->
    <PeriodSelector v-model="queryParams" @change="fetchData" />

    <!-- 汇总卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">总收入</div>
            <div class="stat-value positive">¥{{ summary.total_revenue.toLocaleString() }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">总成本</div>
            <div class="stat-value">¥{{ summary.total_cost.toLocaleString() }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">总利润</div>
            <div class="stat-value" :class="summary.total_profit >= 0 ? 'positive' : 'negative'">
              ¥{{ summary.total_profit.toLocaleString() }}
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">平均利润率</div>
            <div class="stat-value" :class="summary.avg_profit_rate >= 0 ? 'positive' : 'negative'">
              {{ summary.avg_profit_rate }}%
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 趋势图表 -->
    <el-card style="margin-bottom: 20px;">
      <template #header>
        <span>收入成本利润趋势</span>
      </template>
      <div ref="trendChart" style="height: 400px;"></div>
    </el-card>

    <!-- 利润率趋势 -->
    <el-card style="margin-bottom: 20px;">
      <template #header>
        <span>利润率趋势</span>
      </template>
      <div ref="rateChart" style="height: 300px;"></div>
    </el-card>

    <!-- 详细数据表格 -->
    <el-card>
      <template #header>
        <span>详细数据</span>
      </template>
      <el-table :data="tableData" border stripe>
        <el-table-column prop="date" label="时间" width="150" />
        <el-table-column prop="revenue" label="收入" width="150">
          <template #default="{ row }">
            ¥{{ row.revenue.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="cost" label="成本" width="150">
          <template #default="{ row }">
            ¥{{ row.cost.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="profit" label="利润" width="150">
          <template #default="{ row }">
            <span :class="row.profit >= 0 ? 'positive' : 'negative'">
              ¥{{ row.profit.toLocaleString() }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="profit_rate" label="利润率" width="120">
          <template #default="{ row }">
            <span :class="row.profit_rate >= 0 ? 'positive' : 'negative'">
              {{ row.profit_rate }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="order_count" label="订单数" width="100" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { getProfitStatistics } from '@/api/statistics'
import PeriodSelector from '@/components/PeriodSelector.vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

const queryParams = ref({
  period: 'month',
  startDate: '',
  endDate: ''
})

const tableData = ref([])
const summary = ref({
  total_revenue: 0,
  total_cost: 0,
  total_profit: 0,
  avg_profit_rate: 0
})

const trendChart = ref(null)
const rateChart = ref(null)
let trendChartInstance = null
let rateChartInstance = null

const fetchData = async () => {
  try {
    const res = await getProfitStatistics({
      period: queryParams.value.period,
      start_date: queryParams.value.startDate,
      end_date: queryParams.value.endDate
    })
    
    if (res.code === 200) {
      tableData.value = res.data.items
      summary.value = res.data.summary
      
      await nextTick()
      renderCharts()
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取数据失败')
  }
}

const renderCharts = () => {
  if (!tableData.value.length) return
  
  // 趋势图
  if (!trendChartInstance) {
    trendChartInstance = echarts.init(trendChart.value)
  }
  
  const dates = tableData.value.map(item => item.date)
  const revenues = tableData.value.map(item => item.revenue)
  const costs = tableData.value.map(item => item.cost)
  const profits = tableData.value.map(item => item.profit)
  
  trendChartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['收入', '成本', '利润']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { rotate: 45 }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [
      {
        name: '收入',
        type: 'line',
        data: revenues,
        smooth: true,
        itemStyle: { color: '#67C23A' }
      },
      {
        name: '成本',
        type: 'line',
        data: costs,
        smooth: true,
        itemStyle: { color: '#E6A23C' }
      },
      {
        name: '利润',
        type: 'line',
        data: profits,
        smooth: true,
        itemStyle: { color: '#409EFF' }
      }
    ]
  })
  
  // 利润率图
  if (!rateChartInstance) {
    rateChartInstance = echarts.init(rateChart.value)
  }
  
  const profitRates = tableData.value.map(item => item.profit_rate)
  
  rateChartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>{a}: {c}%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { rotate: 45 }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: '利润率',
        type: 'bar',
        data: profitRates,
        itemStyle: {
          color: (params) => {
            return params.value >= 0 ? '#67C23A' : '#F56C6C'
          }
        }
      }
    ]
  })
}

onMounted(() => {
  // 初始数据会在PeriodSelector初始化时自动触发
})
</script>

<style scoped>
.profit-analysis {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
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

.positive {
  color: #67C23A;
}

.negative {
  color: #F56C6C;
}
</style>
