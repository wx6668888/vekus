<template>
  <div class="admin-view">
    <Sidebar />
    <main class="admin-view__main">
      <TopBar title="用户管理" description="管理系统用户、角色和权限" eyebrow="管理员" />

      <!-- Toolbar -->
      <div class="admin-view__toolbar">
        <div class="admin-view__stats">
          <span>共 {{ users.length }} 个用户</span>
          <span class="admin-view__stat-sep">·</span>
          <span>老板 {{ roleCount('boss') }} 人</span>
          <span class="admin-view__stat-sep">·</span>
          <span>业务员 {{ roleCount('sales') }} 人</span>
        </div>
        <Button variant="primary" @click="openCreate">
          <Plus :size="16" class="mr-2" /> 新增用户
        </Button>
      </div>

      <!-- User table -->
      <Card class="admin-view__table">
        <div v-if="loading" class="admin-view__loading">
          <div class="vk-skeleton-row" v-for="i in 5" :key="i"></div>
        </div>
        <table v-else class="vk-table">
          <thead>
            <tr>
              <th>姓名</th>
              <th>手机号</th>
              <th>角色</th>
              <th>工厂</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td>
                <div class="admin-view__user">
                  <div class="admin-view__avatar">{{ u.name.charAt(0) }}</div>
                  <span>{{ u.name }}</span>
                </div>
              </td>
              <td>{{ u.phone }}</td>
              <td>
                <Badge :variant="u.role === 'boss' ? 'danger' : 'info'" size="sm">
                  {{ u.role === 'boss' ? '老板' : '业务员' }}
                </Badge>
              </td>
              <td class="vk-text-muted">{{ u.factoryName }}</td>
              <td>
                <div class="admin-view__actions">
                  <button class="admin-view__action" @click="openEdit(u)">编辑</button>
                  <button class="admin-view__action admin-view__action--danger" @click="confirmDelete(u)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </Card>
    </main>
    <MobileNav />

    <!-- Create / Edit dialog -->
    <div v-if="showDialog" class="vk-overlay" @click.self="showDialog = false">
      <Card class="vk-dialog">
        <h3 class="vk-dialog__title">{{ editingUser ? '编辑用户' : '新增用户' }}</h3>
        <div class="vk-dialog__form">
          <Input v-model="form.name" label="姓名" placeholder="输入姓名" />
          <Input v-model="form.phone" label="手机号" placeholder="输入手机号" />
          <Input v-model="form.password" label="密码" placeholder="留空则不修改" />
          <div class="post-view__select">
            <label class="vk-input__label">角色</label>
            <SelectMenu v-model="form.role" :options="roleOptions" />
          </div>
          <Input v-model="form.factoryName" label="工厂名称" placeholder="如：Vekus" />
        </div>
        <div class="vk-dialog__actions">
          <Button variant="ghost" @click="showDialog = false">取消</Button>
          <Button variant="primary" :loading="saving" @click="saveUser">保存</Button>
        </div>
      </Card>
    </div>

    <!-- Delete confirm -->
    <ConfirmDialog
      v-if="deleteTarget"
      title="确认删除"
      :message="`确定要删除用户「${deleteTarget.name}」吗？此操作不可撤销。`"
      confirm-text="删除"
      confirm-variant="danger"
      @confirm="doDelete"
      @cancel="deleteTarget = null"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { Plus } from 'lucide-vue-next';
import Sidebar from '@/components/layout/Sidebar.vue';
import TopBar from '@/components/layout/TopBar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';
import Card from '@/components/base/Card.vue';
import Button from '@/components/base/Button.vue';
import Input from '@/components/base/Input.vue';
import Badge from '@/components/base/Badge.vue';
import SelectMenu from '@/components/base/SelectMenu.vue';
import ConfirmDialog from '@/components/base/ConfirmDialog.vue';
import { api } from '@/api';

interface UserItem {
  id: string;
  username: string;
  name: string;
  phone: string;
  role: string;
  factoryName: string;
}

const users = ref<UserItem[]>([]);
const loading = ref(true);
const showDialog = ref(false);
const saving = ref(false);
const editingUser = ref<UserItem | null>(null);
const deleteTarget = ref<UserItem | null>(null);

const form = reactive({ name: '', phone: '', password: '', role: 'sales', factoryName: 'Vekus' });

const roleOptions = [
  { value: 'boss', label: '老板' },
  { value: 'sales', label: '业务员' },
];

function roleCount(role: string) {
  return users.value.filter(u => u.role === role).length;
}

onMounted(async () => {
  await fetchUsers();
});

async function fetchUsers() {
  loading.value = true;
  const res = await api.get<UserItem[]>('/admin/users');
  if (res.data) users.value = res.data;
  loading.value = false;
}

function openCreate() {
  editingUser.value = null;
  form.name = '';
  form.phone = '';
  form.password = '123456';
  form.role = 'sales';
  form.factoryName = 'Vekus';
  showDialog.value = true;
}

function openEdit(u: UserItem) {
  editingUser.value = u;
  form.name = u.name;
  form.phone = u.phone;
  form.password = '';
  form.role = u.role;
  form.factoryName = u.factoryName;
  showDialog.value = true;
}

async function saveUser() {
  if (!form.name) return;
  saving.value = true;
  try {
    if (editingUser.value) {
      const body: Record<string, string> = {
        name: form.name, phone: form.phone,
        role: form.role, factory_name: form.factoryName,
      };
      if (form.password) body.password = form.password;
      await api.put(`/admin/users/${editingUser.value.id}`, body);
    } else {
      await api.post('/admin/users', {
        name: form.name, phone: form.phone,
        password: form.password, role: form.role,
        factory_name: form.factoryName,
      });
    }
    showDialog.value = false;
    await fetchUsers();
  } catch { alert('保存失败'); }
  finally { saving.value = false; }
}

function confirmDelete(u: UserItem) {
  deleteTarget.value = u;
}

async function doDelete() {
  if (!deleteTarget.value) return;
  await api.delete(`/admin/users/${deleteTarget.value.id}`);
  deleteTarget.value = null;
  await fetchUsers();
}
</script>

<style scoped>
.admin-view { display: block; min-height: 100vh; }
.admin-view__main { padding: 24px 32px 120px; max-width: 960px; margin: 0 auto; }

.admin-view__toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.admin-view__stats {
  font-size: var(--fz-sm);
  color: var(--text-muted);
  display: flex;
  gap: 4px;
}

.admin-view__stat-sep { color: var(--text-faint); margin: 0 2px; }

.admin-view__table { padding: 0; overflow: hidden; }

.admin-view__loading { padding: 20px; display: flex; flex-direction: column; gap: 12px; }

.vk-skeleton-row {
  height: 48px; background: var(--surface-sunken);
  border-radius: var(--r-input); animation: pulse 1.5s infinite;
}

@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

.vk-table { width: 100%; border-collapse: collapse; }
.vk-table th {
  text-align: left; padding: 12px 16px; font-size: var(--fz-sm);
  font-weight: var(--fw-semibold); color: var(--text-muted);
  border-bottom: 1px solid var(--border);
}
.vk-table td {
  padding: 14px 16px; font-size: var(--fz-body);
  border-bottom: 1px solid var(--border); color: var(--text);
}
.vk-table tr:last-child td { border-bottom: none; }
.vk-table tr:hover td { background: var(--surface-sunken); }

.admin-view__user { display: flex; align-items: center; gap: 10px; }

.admin-view__avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: var(--brand-light); color: var(--brand);
  display: grid; place-items: center;
  font-size: var(--fz-sm); font-weight: var(--fw-bold);
}

.admin-view__actions { display: flex; gap: 8px; }

.admin-view__action {
  padding: 5px 12px; border-radius: var(--r-tag); border: 1px solid var(--border);
  background: transparent; color: var(--text-muted); font-size: var(--fz-sm);
  cursor: pointer; transition: all var(--duration-fast); font-family: inherit;
}
.admin-view__action:hover { border-color: var(--brand); color: var(--brand); }
.admin-view__action--danger:hover { border-color: var(--danger); color: var(--danger); }

.mr-2 { margin-right: 8px; }

/* Dialog */
.vk-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: grid; place-items: center; z-index: 100; }
.vk-dialog { width: 420px; max-width: 90vw; padding: 24px; }
.vk-dialog__title { margin: 0 0 20px; font-size: var(--fz-h2); font-weight: var(--fw-semibold); }
.vk-dialog__form { display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px; }
.vk-dialog__actions { display: flex; justify-content: flex-end; gap: 8px; }
.vk-input__label { font-size: var(--fz-sm); font-weight: var(--fw-medium); color: var(--text); margin-bottom: 6px; display: block; }
.post-view__select { display: flex; flex-direction: column; gap: 6px; }

@media (max-width: 768px) {
  .admin-view__main { padding: 16px 16px 100px; }
  .admin-view__toolbar { flex-direction: column; gap: 10px; align-items: stretch; }
}
</style>
