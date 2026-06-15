<template>
  <div class="login-view">
    <div class="login-view__bg blueprint-grid"></div>
    <div class="login-view__container">
      <div class="login-view__brand">
        <div class="login-view__logo">V</div>
        <div class="login-view__brand-text">
          <div class="login-view__brand-name">Vekus</div>
          <div class="login-view__brand-sub">AI 报价工作台</div>
        </div>
      </div>

      <Card class="login-view__card">
        <div class="login-view__tabs">
          <button
            :class="['login-view__tab', { 'login-view__tab--active': tab === 'phone' }]"
            @click="tab = 'phone'"
          >
            手机号登录
          </button>
          <button
            :class="['login-view__tab', { 'login-view__tab--active': tab === 'wechat' }]"
            @click="tab = 'wechat'"
          >
            微信扫码
          </button>
        </div>

        <div v-if="tab === 'phone'" class="login-view__form">
          <Input
            v-model="phone"
            label="手机号"
            placeholder="请输入手机号"
          />
          <Input
            v-model="password"
            type="password"
            label="密码"
            placeholder="请输入密码"
          />
          <p v-if="errorMsg" class="login-view__error">{{ errorMsg }}</p>
          <Button variant="primary" size="lg" block :loading="loading" @click="handleLogin">
            登录
          </Button>
        </div>

        <div v-else class="login-view__qrcode">
          <div class="login-view__qrcode-placeholder">
            <QrCode :size="160" />
            <p>请使用微信扫码登录</p>
          </div>
        </div>

        <div class="login-view__footer">
          <p class="vk-text-faint">测试账号: sales / 123456 | <router-link to="/register" style="color:var(--brand)">注册新账户</router-link></p>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { QrCode } from 'lucide-vue-next';
import Card from '@/components/base/Card.vue';
import Input from '@/components/base/Input.vue';
import Button from '@/components/base/Button.vue';
import { useAuthStore } from '@/stores/auth';
import { api, setToken } from '@/api/client';

const router = useRouter();
const authStore = useAuthStore();
const tab = ref('phone');
const phone = ref('');
const password = ref('');
const loading = ref(false);
const errorMsg = ref('');

async function handleLogin() {
  if (!phone.value || !password.value) {
    errorMsg.value = '请输入手机号和密码';
    return;
  }
  loading.value = true;
  errorMsg.value = '';
  try {
    const result = await api.post<{ token: string; user: any }>('/auth/login', {
      phone: phone.value,
      password: password.value,
    });
    if (result.error) {
      errorMsg.value = result.error;
      return;
    }
    setToken(result.data.token);
    authStore.setUser(result.data.user);
    authStore.setToken(result.data.token);
    router.push('/quote');
  } catch {
    errorMsg.value = '登录失败，请重试';
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.login-view__bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, var(--surface-blueprint), var(--surface-blueprint-light));
  z-index: 0;
}

.login-view__container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.login-view__brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: white;
}

.login-view__logo {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, var(--brand), var(--accent));
  display: grid;
  place-items: center;
  font-size: 28px;
  font-weight: var(--fw-bold);
  box-shadow: var(--sh-lg);
}

.login-view__brand-name {
  font-size: 24px;
  font-weight: var(--fw-bold);
}

.login-view__brand-sub {
  font-size: 14px;
  opacity: 0.7;
}

.login-view__card {
  padding: 32px;
  box-shadow: var(--sh-blueprint);
}

.login-view__tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 24px;
}

.login-view__tab {
  flex: 1;
  padding: 12px;
  border-radius: var(--r-input);
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-muted);
  font-size: var(--fz-body);
  font-weight: var(--fw-medium);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.login-view__tab:hover {
  background: var(--surface-sunken);
}

.login-view__tab--active {
  background: var(--brand-light);
  border-color: var(--brand);
  color: var(--brand);
}

.login-view__form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.login-view__error {
  color: var(--danger);
  font-size: var(--fz-sm);
  margin: 0;
}

.login-view__qrcode {
  padding: 32px 0;
}

.login-view__qrcode-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: var(--text-muted);
}

.login-view__footer {
  margin-top: 24px;
  text-align: center;
}

.login-view__footer p {
  margin: 0;
  font-size: var(--fz-sm);
}
</style>

