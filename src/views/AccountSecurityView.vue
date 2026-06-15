<template>
  <div class="security-view">
    <Sidebar />
    <main class="security-view__main">
      <button class="security-view__back" @click="$router.back()">
        <ChevronLeft :size="20" /> 返回
      </button>
      <h1 class="security-view__title">账户安全</h1>

      <Card class="security-view__card">
        <div class="security-view__item" @click="showChangePassword = true">
          <Key :size="20" />
          <span>修改密码</span>
          <span class="security-view__hint">········</span>
          <ChevronRight :size="16" />
        </div>
        <div class="security-view__item">
          <Smartphone :size="20" />
          <span>绑定手机</span>
          <span class="security-view__hint">138****1234</span>
          <ChevronRight :size="16" />
        </div>
        <div class="security-view__item">
          <Mail :size="20" />
          <span>绑定邮箱</span>
          <span class="security-view__hint">未绑定</span>
          <ChevronRight :size="16" />
        </div>
      </Card>

      <Card class="security-view__card">
        <h3 class="security-view__section-title">登录设备</h3>
        <div class="security-view__device">
          <Monitor :size="20" />
          <div>
            <div class="security-view__device-name">Windows PC - Chrome</div>
            <div class="security-view__device-time">当前设备 · 深圳</div>
          </div>
          <Badge variant="success" size="sm">当前</Badge>
        </div>
        <div class="security-view__device">
          <Smartphone :size="20" />
          <div>
            <div class="security-view__device-name">iPhone 15 - Safari</div>
            <div class="security-view__device-time">6月7日 14:30 · 广州</div>
          </div>
        </div>
      </Card>

      <Card class="security-view__card">
        <div class="security-view__item" style="color: var(--danger)">
          <AlertTriangle :size="20" />
          <span>注销账户</span>
          <ChevronRight :size="16" />
        </div>
      </Card>
    </main>
    <MobileNav />
    <ConfirmDialog
      :visible="showChangePassword"
      title="修改密码"
      message="将在后续版本支持，如需重置请联系管理员。"
      confirm-text="知道了"
      @confirm="showChangePassword = false"
      @cancel="showChangePassword = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { ChevronLeft, ChevronRight, Key, Smartphone, Mail, Monitor, AlertTriangle } from 'lucide-vue-next';
import Sidebar from '@/components/layout/Sidebar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';
import Card from '@/components/base/Card.vue';
import Badge from '@/components/base/Badge.vue';
import ConfirmDialog from '@/components/base/ConfirmDialog.vue';

const showChangePassword = ref(false);
</script>

<style scoped>
.security-view { display: grid; display: block; min-height: 100vh; }
.security-view__main { padding: 24px 32px 120px; max-width: 640px; }
.security-view__back { display: flex; align-items: center; gap: 4px; padding: 8px 0; margin-bottom: 8px; border: none; background: none; color: var(--text-muted); font-size: var(--fz-body); cursor: pointer; }
.security-view__back:hover { color: var(--brand); }
.security-view__title { font-size: var(--fz-h1); font-weight: var(--fw-bold); margin: 0 0 24px; }
.security-view__card { padding: 4px 0; margin-bottom: 16px; }
.security-view__section-title { font-size: var(--fz-h3); font-weight: var(--fw-semibold); margin: 0; padding: 16px 20px 8px; }
.security-view__item { display: flex; align-items: center; gap: 12px; padding: 16px 20px; cursor: pointer; transition: background var(--duration-fast); color: var(--text); font-size: var(--fz-body); }
.security-view__item:hover { background: var(--surface-sunken); }
.security-view__item span:first-of-type { flex: 1; }
.security-view__hint { font-size: var(--fz-sm); color: var(--text-muted); margin-right: 4px; }
.security-view__device { display: flex; align-items: center; gap: 12px; padding: 14px 20px; }
.security-view__device > div { flex: 1; }
.security-view__device-name { font-size: var(--fz-body); color: var(--text); }
.security-view__device-time { font-size: var(--fz-sm); color: var(--text-muted); margin-top: 2px; }
@media (max-width: 768px) { .security-view { grid-template-columns: 1fr; } .security-view__main { padding: 16px 16px 100px; } }
</style>
