<template>
  <div class="user-management">
    <div class="header-actions">
      <el-button type="primary" @click="showCreateDialog">创建子账号</el-button>
    </div>

    <el-card>
      <el-table :data="users" style="width: 100%" v-loading="loading">
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="phone" label="手机号" width="150" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button link type="primary" @click="editUser(row)">编辑</el-button>
            <el-button link type="danger" @click="deleteUser(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @current-change="loadUsers"
        @size-change="loadUsers"
        style="margin-top: 20px; justify-content: center;"
      />
    </el-card>

    <!-- 创建/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
    >
      <el-form :model="userForm" :rules="rules" ref="userFormRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="isEdit" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" />
        </el-form-item>

        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" />
        </el-form-item>

        <el-form-item label="密码" :prop="isEdit ? '' : 'password'">
          <el-input v-model="userForm.password" type="password" show-password 
            :placeholder="isEdit ? '不修改请留空' : '请输入密码'" />
        </el-form-item>

        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" style="width: 100%;">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="userForm.is_active" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitUser" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTenantUsers, createTenantUser, updateTenantUser, deleteTenantUser } from '@/api/tenant'

const users = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const dialogVisible = ref(false)
const dialogTitle = ref('创建子账号')
const isEdit = ref(false)
const submitting = ref(false)
const userFormRef = ref(null)

const userForm = reactive({
  id: null,
  username: '',
  email: '',
  phone: '',
  password: '',
  role: 'user',
  is_active: true
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

const loadUsers = async () => {
  loading.value = true
  try {
    const res = await getTenantUsers({
      page: currentPage.value,
      per_page: pageSize.value
    })
    if (res.code === 200) {
      users.value = res.data.items
      total.value = res.data.total
    }
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

const showCreateDialog = () => {
  isEdit.value = false
  dialogTitle.value = '创建子账号'
  resetForm()
  dialogVisible.value = true
}

const editUser = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑用户'
  Object.assign(userForm, {
    id: row.id,
    username: row.username,
    email: row.email,
    phone: row.phone,
    password: '',
    role: row.role,
    is_active: row.is_active
  })
  dialogVisible.value = true
}

const resetForm = () => {
  Object.assign(userForm, {
    id: null,
    username: '',
    email: '',
    phone: '',
    password: '',
    role: 'user',
    is_active: true
  })
  if (userFormRef.value) {
    userFormRef.value.resetFields()
  }
}

const submitUser = async () => {
  if (!userFormRef.value) return
  
  await userFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEdit.value) {
          const data = {
            email: userForm.email,
            phone: userForm.phone,
            role: userForm.role,
            is_active: userForm.is_active
          }
          if (userForm.password) {
            data.password = userForm.password
          }
          const res = await updateTenantUser(userForm.id, data)
          if (res.code === 200) {
            ElMessage.success('更新成功')
            dialogVisible.value = false
            await loadUsers()
          }
        } else {
          const res = await createTenantUser(userForm)
          if (res.code === 201) {
            ElMessage.success('创建成功')
            dialogVisible.value = false
            await loadUsers()
          }
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const deleteUser = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${row.username}" 吗?`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const res = await deleteTenantUser(row.id)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      await loadUsers()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-management {
  padding: 20px;
}

.header-actions {
  margin-bottom: 20px;
}
</style>
