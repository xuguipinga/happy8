<template>
  <div class="period-selector">
    <el-row :gutter="20">
      <el-col :span="18">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          :range-separator="$t('common.to')"
          :start-placeholder="$t('common.startDate')"
          :end-placeholder="$t('common.endDate')"
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
              <el-dropdown-item command="today">{{ $t('shortcuts.today') }}</el-dropdown-item>
              <el-dropdown-item command="week">本周</el-dropdown-item>
              <el-dropdown-item command="month">{{ $t('shortcuts.thisMonth') }}</el-dropdown-item>
              <el-dropdown-item command="quarter">本季度</el-dropdown-item>
              <el-dropdown-item command="year">本年</el-dropdown-item>
              <el-dropdown-item command="last30">{{ $t('shortcuts.last30Days') }}</el-dropdown-item>
              <el-dropdown-item command="all" divided>全部时间</el-dropdown-item>
              <el-dropdown-item command="last_year" divided>{{ $t('shortcuts.lastMonth') }}</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import dayjs from 'dayjs'

const { t } = useI18n()

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

const dateRange = ref([props.modelValue.startDate, props.modelValue.endDate])
const currentCommand = ref(props.modelValue.period || 'month')

const currentLabel = computed(() => {
    if (currentCommand.value === 'custom') return t('common.dateRange')
    const labels = {
        'today': t('shortcuts.today'),
        'month': t('shortcuts.thisMonth'),
        'last30': t('shortcuts.last30Days'),
        'last_year': t('shortcuts.lastMonth'),
        'week': '本周',
        'quarter': '本季度',
        'year': '本年',
        'all': '全部时间'
    }
    return labels[currentCommand.value] || '快捷选择'
})

const handleDateChange = () => {
  currentCommand.value = 'custom'
  emitChange()
}

const handleQuickSelect = (command) => {
  currentCommand.value = command
  let startDate, endDate
  
  const today = dayjs()
  
  switch (command) {
    case 'today':
      startDate = endDate = today.format('YYYY-MM-DD')
      break
    case 'week':
      startDate = today.startOf('week').format('YYYY-MM-DD')
      endDate = today.format('YYYY-MM-DD')
      break
    case 'month':
      startDate = today.startOf('month').format('YYYY-MM-DD')
      endDate = today.endOf('month').format('YYYY-MM-DD')
      break
    case 'quarter':
      startDate = today.startOf('quarter').format('YYYY-MM-DD')
      endDate = today.format('YYYY-MM-DD')
      break
    case 'year':
      startDate = today.startOf('year').format('YYYY-MM-DD')
      endDate = today.format('YYYY-MM-DD')
      break
    case 'last30':
      startDate = today.subtract(29, 'day').format('YYYY-MM-DD')
      endDate = today.format('YYYY-MM-DD')
      break
    case 'all':
      startDate = '2020-01-01'
      endDate = today.format('YYYY-MM-DD')
      break
    case 'last_year':
      startDate = today.subtract(1, 'month').startOf('month').format('YYYY-MM-DD')
      endDate = today.subtract(1, 'month').endOf('month').format('YYYY-MM-DD')
      break
  }
  
  dateRange.value = [startDate, endDate]
  emitChange()
}

const emitChange = () => {
  const value = {
    period: currentCommand.value,
    startDate: dateRange.value ? dateRange.value[0] : '',
    endDate: dateRange.value ? dateRange.value[1] : ''
  }
  emit('update:modelValue', value)
  emit('change', value)
}

// Initial setup if empty
if (!dateRange.value[0]) {
  handleQuickSelect('month')
}
</script>

<style scoped>
.period-selector {
  margin-bottom: 20px;
}
</style>
