<template>
  <div class="tenant-settings">
    <el-card class="info-card">
      <template #header>
        <div class="card-header">
          <span>租户信息</span>
          <el-button v-if="!isEditing" type="primary" @click="startEdit">编辑</el-button>
          <div v-else>
            <el-button @click="cancelEdit">取消</el-button>
            <el-button type="primary" @click="saveEdit" :loading="saving">保存</el-button>
          </div>
        </div>
      </template>

      <el-form :model="tenantForm" label-width="120px" :disabled="!isEditing">
        <el-form-item label="租户名称">
          <el-input v-model="tenantForm.name" placeholder="请输入租户名称" />
        </el-form-item>

        <el-form-item label="租户代码">
          <el-input v-model="tenantForm.code" disabled />
          <span class="form-tip">租户代码用于邀请其他用户加入</span>
        </el-form-item>

        <el-form-item label="联系人">
          <el-input v-model="tenantForm.contact_person" placeholder="请输入联系人" />
        </el-form-item>

        <el-form-item label="联系电话">
          <el-input v-model="tenantForm.contact_phone" placeholder="请输入联系电话" />
        </el-form-item>

        <el-form-item label="联系邮箱">
          <el-input v-model="tenantForm.contact_email" placeholder="请输入联系邮箱" />
        </el-form-item>

        <el-form-item label="用户数量">
          <span>{{ tenantInfo.user_count || 0 }} 个用户</span>
        </el-form-item>

        <el-form-item label="创建时间">
          <span>{{ tenantInfo.created_at }}</span>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="invite-card" style="margin-top: 20px;">
      <template #header>
        <span>邀请用户加入</span>
      </template>
      
      <el-alert
        title="邀请码"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        <template #default>
          <div style="display: flex; align-items: center; gap: 10px;">
            <el-tag size="large" type="success">{{ tenantForm.code }}</el-tag>
            <el-button size="small" @click="copyInviteCode">复制邀请码</el-button>
          </div>
          <p style="margin-top: 10px; font-size: 12px; color: #666;">
            将此邀请码分享给其他用户,他们在注册时填写此代码即可加入您的租户
          </p>
        </template>
      </el-alert>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getCurrentTenant, updateCurrentTenant } from '@/api/tenant'

const tenantInfo = ref({})
const tenantForm = reactive({
  name: '',
  code: '',
  contact_person: '',
  contact_phone: '',
  contact_email: ''
})

const isEditing = ref(false)
const saving = ref(false)
const originalData = ref({})

const loadTenantInfo = async () => {
  try {
    const res = await getCurrentTenant()
    if (res.code === 200) {
      tenantInfo.value = res.data
      Object.assign(tenantForm, res.data)
      originalData.value = { ...res.data }
    }
  } catch (error) {
    ElMessage.error('加载租户信息失败')
  }
}

const startEdit = () => {
  isEditing.value = true
}

const cancelEdit = () => {
  Object.assign(tenantForm, originalData.value)
  isEditing.value = false
}

const saveEdit = async () => {
  saving.value = true
  try {
    const res = await updateCurrentTenant({
      name: tenantForm.name,
      contact_person: tenantForm.contact_person,
      contact_phone: tenantForm.contact_phone,
      contact_email: tenantForm.contact_email
    })
    if (res.code === 200) {
      ElMessage.success('保存成功')
      originalData.value = { ...tenantForm }
      isEditing.value = false
      await loadTenantInfo()
    }
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const copyInviteCode = () => {
  navigator.clipboard.writeText(tenantForm.code)
  ElMessage.success('邀请码已复制到剪贴板')
}

onMounted(() => {
  loadTenantInfo()
})
</script>

<style scoped>
.tenant-settings {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  font-size: 12px;
  color: #999;
  margin-left: 10px;
}
</style>
