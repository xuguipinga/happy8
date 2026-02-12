<template>
  <div class="user-profile">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>个人信息</span>
          <el-button v-if="!isEditing" type="primary" @click="startEdit">编辑</el-button>
          <div v-else>
            <el-button @click="cancelEdit">取消</el-button>
            <el-button type="primary" @click="saveEdit" :loading="saving">保存</el-button>
          </div>
        </div>
      </template>

      <el-form :model="profileForm" label-width="120px" :disabled="!isEditing">
        <el-form-item label="用户名">
          <el-input v-model="profileForm.username" disabled />
        </el-form-item>

        <el-form-item label="邮箱">
          <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
        </el-form-item>

        <el-form-item label="手机号">
          <el-input v-model="profileForm.phone" placeholder="请输入手机号" />
        </el-form-item>

        <el-form-item label="角色">
          <el-tag :type="profileForm.role === 'admin' ? 'danger' : 'info'">
            {{ profileForm.role === 'admin' ? '管理员' : '普通用户' }}
          </el-tag>
        </el-form-item>

        <el-form-item label="租户">
          <span>{{ profileForm.tenant_name || '未分配' }}</span>
        </el-form-item>

        <el-form-item label="账号状态">
          <el-tag :type="profileForm.is_active ? 'success' : 'danger'">
            {{ profileForm.is_active ? '启用' : '禁用' }}
          </el-tag>
        </el-form-item>

        <el-form-item label="注册时间">
          <span>{{ profileForm.created_at }}</span>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="password-card" style="margin-top: 20px;">
      <template #header>
        <span>修改密码</span>
      </template>

      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="120px">
        <el-form-item label="当前密码" prop="oldPassword">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password />
        </el-form-item>

        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" show-password />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="changePassword" :loading="changingPassword">
            修改密码
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import request from '@/utils/request'

const userStore = useUserStore()

const profileForm = reactive({
  username: '',
  email: '',
  phone: '',
  role: '',
  tenant_name: '',
  is_active: true,
  created_at: ''
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const passwordFormRef = ref(null)
const isEditing = ref(false)
const saving = ref(false)
const changingPassword = ref(false)
const originalData = ref({})

const validatePass2 = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validatePass2, trigger: 'blur' }
  ]
}

const loadUserInfo = async () => {
  try {
    await userStore.fetchUserInfo()
    const userInfo = userStore.userInfo
    if (userInfo) {
      Object.assign(profileForm, {
        username: userInfo.username,
        email: userInfo.email || '',
        phone: userInfo.phone || '',
        role: userInfo.role || 'user',
        tenant_name: userInfo.tenant_name || '',
        is_active: userInfo.is_active,
        created_at: userInfo.created_at || ''
      })
      originalData.value = { ...profileForm }
    }
  } catch (error) {
    ElMessage.error('加载用户信息失败')
  }
}

const startEdit = () => {
  isEditing.value = true
}

const cancelEdit = () => {
  Object.assign(profileForm, originalData.value)
  isEditing.value = false
}

const saveEdit = async () => {
  saving.value = true
  try {
    const res = await request({
      url: '/auth/profile',
      method: 'put',
      data: {
        email: profileForm.email,
        phone: profileForm.phone
      }
    })
    if (res.code === 200) {
      ElMessage.success('保存成功')
      originalData.value = { ...profileForm }
      isEditing.value = false
      await loadUserInfo()
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

const changePassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      changingPassword.value = true
      try {
        const res = await request({
          url: '/auth/change-password',
          method: 'post',
          data: {
            old_password: passwordForm.oldPassword,
            new_password: passwordForm.newPassword
          }
        })
        if (res.code === 200) {
          ElMessage.success('密码修改成功,请重新登录')
          // 清空表单
          Object.assign(passwordForm, {
            oldPassword: '',
            newPassword: '',
            confirmPassword: ''
          })
          passwordFormRef.value.resetFields()
          
          // 延迟后退出登录
          setTimeout(() => {
            userStore.logout()
            window.location.href = '/login'
          }, 1500)
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '密码修改失败')
      } finally {
        changingPassword.value = false
      }
    }
  })
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.user-profile {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
