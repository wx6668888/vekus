<template>
  <div class="register-view">
    <div class="register-view__bg blueprint-grid"></div>
    <div class="register-view__container">
      <div class="register-view__brand">
        <div class="register-view__logo">V</div>
        <div class="register-view__brand-text">
          <div class="register-view__brand-name">Vekus</div>
          <div class="register-view__brand-sub">AI 报价工作台</div>
        </div>
      </div>
      <Card class="register-view__card">
        <h3 class="register-view__title">创建账户</h3>
        <div class="register-view__form">
          <div class="register-view__role-toggle">
            <button :class="['register-view__role-btn', { 'register-view__role-btn--active': form.role === 'sales' }]" @click="form.role = 'sales'">
              <User :size="18" /> 业务员
            </button>
            <button :class="['register-view__role-btn', { 'register-view__role-btn--active': form.role === 'boss' }]" @click="form.role = 'boss'">
              <Briefcase :size="18" /> 老板
            </button>
          </div>
          <Input v-model="form.name" label="姓名" placeholder="请输入姓名" />
          <Input v-model="form.phone" label="手机号" placeholder="请输入手机号" />
          <Input v-model="form.password" type="password" label="密码" placeholder="请输入密码（至少6位）" />
          <Input v-if="form.role === 'boss'" v-model="form.factory_name" label="工厂/公司名称" placeholder="选填" />
          <p v-if="errorMsg" class="register-view__error">{{ errorMsg }}</p>
          <Button variant="primary" size="lg" block :loading="loading" @click="handleRegister">注册</Button>
        </div>
        <div class="register-view__footer">
          <p>已有账户？<router-link to="/login">立即登录</router-link></p>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { User, Briefcase } from 'lucide-vue-next';
import Card from '@/components/base/Card.vue';
import Input from '@/components/base/Input.vue';
import Button from '@/components/base/Button.vue';
import { useAuthStore } from '@/stores/auth';
import { api, setToken } from '@/api/client';

const router = useRouter();
const authStore = useAuthStore();
const loading = ref(false);
const errorMsg = ref('');
const form = reactive({ name: '', phone: '', password: '', role: 'sales', factory_name: '' });

async function handleRegister() {
  if (!form.phone || !form.password || !form.name) { errorMsg.value = '请填写必填项'; return; }
  if (form.password.length < 6) { errorMsg.value = '密码至少6位'; return; }
  loading.value = true; errorMsg.value = '';
  try {
    const result = await api.post<{ token: string; user: any }>('/auth/register', form);
    if (result.error) { errorMsg.value = result.error; return; }
    setToken(result.data.token);
    authStore.setUser(result.data.user);
    authStore.setToken(result.data.token);
    router.push('/quote');
  } catch { errorMsg.value = '注册失败，请重试'; }
  finally { loading.value = false; }
}
</script>

<style scoped>
.register-view { min-height: 100vh; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; }
.register-view__bg { position: absolute; inset: 0; background: linear-gradient(135deg, var(--surface-blueprint), var(--surface-blueprint-light)); z-index: 0; }
.register-view__container { position: relative; z-index: 1; width: 100%; max-width: 420px; padding: 24px; display: flex; flex-direction: column; gap: 24px; }
.register-view__brand { display: flex; align-items: center; justify-content: center; gap: 12px; color: white; }
.register-view__logo { width: 48px; height: 48px; border-radius: 14px; background: linear-gradient(135deg, var(--brand), var(--accent)); display: grid; place-items: center; font-size: 24px; font-weight: var(--fw-bold); }
.register-view__brand-name { font-size: 22px; font-weight: var(--fw-bold); }
.register-view__brand-sub { font-size: 13px; opacity: 0.7; }
.register-view__card { padding: 28px; box-shadow: var(--sh-blueprint); }
.register-view__title { font-size: var(--fz-h2); font-weight: var(--fw-semibold); margin: 0 0 20px; text-align: center; }
.register-view__form { display: flex; flex-direction: column; gap: 14px; }
.register-view__role-toggle { display: flex; gap: 8px; margin-bottom: 4px; }
.register-view__role-btn { flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px; padding: 10px; border-radius: var(--r-input); border: 2px solid var(--border); background: transparent; color: var(--text-muted); font-size: var(--fz-body); font-weight: var(--fw-medium); cursor: pointer; transition: all var(--duration-fast); }
.register-view__role-btn--active { border-color: var(--brand); background: var(--brand-light); color: var(--brand); }
.register-view__error { color: var(--danger); font-size: var(--fz-sm); margin: 0; }
.register-view__footer { margin-top: 16px; text-align: center; font-size: var(--fz-sm); color: var(--text-muted); }
.register-view__footer a { color: var(--brand); text-decoration: none; font-weight: var(--fw-medium); }
</style>
