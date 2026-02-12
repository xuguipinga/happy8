<template>
  <div class="period-selector">
    <el-row :gutter="20">
      <el-col :span="18">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="handleDateChange"
        />
      </el-col>
      <el-col :span="6" style="text-align: right;">
        <el-dropdown @command="handleQuickSelect">
          <el-button>
            {{ currentLabel }}<el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="today">今天</el-dropdown-item>
              <el-dropdown-item command="week">本周</el-dropdown-item>
              <el-dropdown-item command="month">本月</el-dropdown-item>
              <el-dropdown-item command="quarter">本季度</el-dropdown-item>
              <el-dropdown-item command="year">本年</el-dropdown-item>
              <el-dropdown-item command="last30">最近30天</el-dropdown-item>
              <el-dropdown-item command="all" divided>全部时间</el-dropdown-item>
              <el-dropdown-item command="last_year" divided>去年</el-dropdown-item>
              <el-dropdown-item command="year_before_last">前年</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      period: 'month',
      startDate: '',
      endDate: ''
    })
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const period = ref(props.modelValue.period || 'month')
const dateRange = ref([props.modelValue.startDate, props.modelValue.endDate])
const currentLabel = ref('快捷选择')

const handleDateChange = () => {
  currentLabel.value = '自定义范围'
  emitChange()
}


const handleQuickSelect = (command) => {
  const today = new Date()
  let startDate, endDate
  
  const labels = {
    'today': '今天',
    'week': '本周',
    'month': '本月',
    'quarter': '本季度',
    'year': '本年',
    'last30': '最近30天',
    'all': '全部时间',
    'last_year': '去年',
    'year_before_last': '前年'
  }
  currentLabel.value = labels[command]

  // 快捷选择同时设置范围和粒度
  switch (command) {
    case 'today':
      startDate = endDate = formatDate(today)
      break
    case 'week':
      const weekStart = new Date(today)
      weekStart.setDate(today.getDate() - today.getDay())
      startDate = formatDate(weekStart)
      endDate = formatDate(today)
      break
    case 'month':
      startDate = formatDate(new Date(today.getFullYear(), today.getMonth(), 1))
      endDate = formatDate(today)
      break
    case 'quarter':
      const quarterStart = new Date(today.getFullYear(), Math.floor(today.getMonth() / 3) * 3, 1)
      startDate = formatDate(quarterStart)
      endDate = formatDate(today)
      break
    case 'year':
      startDate = formatDate(new Date(today.getFullYear(), 0, 1))
      endDate = formatDate(today)
      break
    case 'last30':
      const last30 = new Date(today)
      last30.setDate(today.getDate() - 30)
      startDate = formatDate(last30)
      endDate = formatDate(today)
      break
    case 'all':
      startDate = '2020-01-01' // Assume a safe start date for "all"
      endDate = formatDate(today)
      break
    case 'last_year':
      startDate = formatDate(new Date(today.getFullYear() - 1, 0, 1))
      endDate = formatDate(new Date(today.getFullYear() - 1, 11, 31))
      break
    case 'year_before_last':
      startDate = formatDate(new Date(today.getFullYear() - 2, 0, 1))
      endDate = formatDate(new Date(today.getFullYear() - 2, 11, 31))
      break
  }
  
  dateRange.value = [startDate, endDate]
  emitChange()
}

const formatDate = (date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const emitChange = () => {
  const value = {
    period: 'day',
    startDate: dateRange.value ? dateRange.value[0] : '',
    endDate: dateRange.value ? dateRange.value[1] : ''
  }
  emit('update:modelValue', value)
  emit('change', value)
}

// 初始化默认值
if (!dateRange.value[0]) {
  handleQuickSelect('month')
}
</script>

<style scoped>
.period-selector {
  margin-bottom: 20px;
}
</style>
