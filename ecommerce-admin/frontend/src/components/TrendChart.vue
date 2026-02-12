<template>
  <div ref="chartRef" :style="{ height: height, width: '100%' }"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  option: {
    type: Object,
    required: true
  },
  height: {
    type: String,
    default: '350px'
  }
})

const chartRef = ref(null)
let chartInstance = null

const initChart = () => {
  if (!chartRef.value) return
  
  chartInstance = echarts.init(chartRef.value)
  if (props.option) {
    chartInstance.setOption(props.option)
  }
  
  window.addEventListener('resize', handleResize)
}

const handleResize = () => {
  chartInstance?.resize()
}

watch(() => props.option, (newOption) => {
  if (chartInstance && newOption) {
    chartInstance.setOption(newOption, true) // true = not merge, replace
  }
}, { deep: true })

onMounted(() => {
  nextTick(() => {
    initChart()
  })
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})
</script>
