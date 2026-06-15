<template>
  <header class="vk-topnav">
    <div class="vk-topnav__brand">
      <div class="vk-topnav__logo">V</div>
      <span class="vk-topnav__brand-name">Vekus</span>
    </div>
    <nav class="vk-topnav__nav">
      <!-- 看板 -->
      <router-link to="/dashboard" class="vk-topnav__item" :class="{ 'vk-topnav__item--active': isActive('/dashboard') }">
        <LayoutDashboard :size="18" /><span>看板</span>
      </router-link>

      <!-- 生产制造 dropdown -->
      <div class="vk-topnav__dropdown" @mouseenter="openMenu='production'" @mouseleave="openMenu=''">
        <button :class="['vk-topnav__item', { 'vk-topnav__item--active': isMenuActive('production') }]">
          <Wrench :size="18" /><span>生产</span><ChevronDown :size="12" class="vk-topnav__chevron" />
        </button>
        <Transition name="vk-dd">
          <div v-if="openMenu==='production'" class="vk-topnav__menu">
            <router-link v-for="m in productionItems" :key="m.path" :to="m.path" class="vk-topnav__menu-item" @click="openMenu=''">
              <component :is="m.icon" :size="16" /><span>{{ m.label }}</span>
            </router-link>
          </div>
        </Transition>
      </div>

      <!-- 业务 dropdown -->
      <div class="vk-topnav__dropdown" @mouseenter="openMenu='business'" @mouseleave="openMenu=''">
        <button :class="['vk-topnav__item', { 'vk-topnav__item--active': isMenuActive('business') }]">
          <FileText :size="18" /><span>业务</span><ChevronDown :size="12" class="vk-topnav__chevron" />
        </button>
        <Transition name="vk-dd">
          <div v-if="openMenu==='business'" class="vk-topnav__menu">
            <router-link v-for="m in businessItems" :key="m.path" :to="m.path" class="vk-topnav__menu-item" @click="openMenu=''">
              <component :is="m.icon" :size="16" /><span>{{ m.label }}</span>
            </router-link>
          </div>
        </Transition>
      </div>

      <!-- 消息 -->
      <router-link to="/messages" class="vk-topnav__item" :class="{ 'vk-topnav__item--active': isActive('/messages') }">
        <MessageSquare :size="18" /><span>消息</span>
      </router-link>

      <!-- 设置 dropdown -->
      <div class="vk-topnav__dropdown" @mouseenter="openMenu='system'" @mouseleave="openMenu=''">
        <button :class="['vk-topnav__item', { 'vk-topnav__item--active': isMenuActive('system') }]">
          <Settings :size="18" /><span>设置</span><ChevronDown :size="12" class="vk-topnav__chevron" />
        </button>
        <Transition name="vk-dd">
          <div v-if="openMenu==='system'" class="vk-topnav__menu">
            <router-link v-for="m in systemItems" :key="m.path" :to="m.path" class="vk-topnav__menu-item" @click="openMenu=''">
              <component :is="m.icon" :size="16" /><span>{{ m.label }}</span>
            </router-link>
          </div>
        </Transition>
      </div>
    </nav>
    <div class="vk-topnav__user" @click="$router.push('/me')">
      <div class="vk-topnav__avatar">{{ userName.charAt(0) }}</div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import { LayoutDashboard, FileText, History, Users, ShoppingBag, MessageSquare, Settings, Layers, Package, Wrench, ShieldCheck, Truck, CheckCircle, FolderOpen, ChevronDown } from 'lucide-vue-next';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const authStore = useAuthStore();
const userName = ref(authStore.user?.name || 'User');
const openMenu = ref('');

const productionItems = [
  { path: '/bom', label: 'BOM', icon: Layers },
  { path: '/inventory', label: '库存', icon: Package },
  { path: '/production', label: '生产', icon: Wrench },
  { path: '/quality', label: '质量', icon: ShieldCheck },
  { path: '/purchases', label: '采购', icon: Truck },
];

const businessItems = [
  { path: '/quote', label: '报价', icon: FileText },
  { path: '/history', label: '历史', icon: History },
  { path: '/customers', label: '客户', icon: Users },
  { path: '/marketplace', label: '交易', icon: ShoppingBag },
  { path: '/approvals', label: '审批', icon: CheckCircle },
];

const systemItems = [
  { path: '/documents', label: '文档', icon: FolderOpen },
  { path: '/settings', label: '设置', icon: Settings },
];

const allMenuPaths: Record<string, string[]> = {
  production: productionItems.map(i => i.path),
  business: businessItems.map(i => i.path),
  system: systemItems.map(i => i.path),
};

function isActive(path: string): boolean {
  if (path === '/quote' && route.path.startsWith('/quote')) return true;
  if (path === '/marketplace' && route.path.startsWith('/marketplace')) return true;
  if (path === '/messages' && route.path.startsWith('/messages')) return true;
  if (path === '/customers' && route.path.startsWith('/customers')) return true;
  return route.path === path;
}

function isMenuActive(menu: string): boolean {
  return allMenuPaths[menu]?.some(p => {
    if (route.path.startsWith(p)) return true;
    return false;
  }) || false;
}
</script>

<style scoped>
.vk-topnav {
  display: none;
  position: sticky; top: 0; z-index: 100;
  height: 56px;
  background: rgba(255,255,255,0.82);
  backdrop-filter: blur(24px) saturate(200%);
  -webkit-backdrop-filter: blur(24px) saturate(200%);
  border-bottom: 0.5px solid rgba(0,0,0,0.08);
  padding: 0 20px; align-items: center; gap: 4px;
}
.vk-topnav__brand { display: flex; align-items: center; gap: 10px; margin-right: 8px; flex-shrink: 0; }
.vk-topnav__logo { width: 34px; height: 34px; border-radius: 9px; background: linear-gradient(135deg, var(--brand), var(--accent)); color: white; display: grid; place-items: center; font-size: 16px; font-weight: var(--fw-bold); }
.vk-topnav__brand-name { font-size: 15px; font-weight: var(--fw-bold); color: var(--text); white-space: nowrap; }
.vk-topnav__nav { display: flex; align-items: center; gap: 2px; flex: 1; }
.vk-topnav__item { display: flex; align-items: center; gap: 5px; padding: 8px 12px; border-radius: 10px; color: #8E8E93; font-size: 13px; font-weight: 500; text-decoration: none; white-space: nowrap; transition: all 0.2s ease; border: none; background: none; cursor: pointer; font-family: inherit; }
.vk-topnav__item:hover { background: rgba(0,0,0,0.04); color: var(--text); }
.vk-topnav__item--active { background: var(--brand-light); color: var(--brand); font-weight: 600; }
.vk-topnav__chevron { margin-left: 1px; transition: transform 0.2s; }
.vk-topnav__user { margin-left: auto; flex-shrink: 0; cursor: pointer; }
.vk-topnav__avatar { width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, var(--brand), var(--accent)); color: white; display: grid; place-items: center; font-size: 14px; font-weight: var(--fw-bold); }

/* Dropdown menu */
.vk-topnav__dropdown { position: relative; }
.vk-topnav__menu { position: absolute; top: 100%; left: 0; margin-top: 6px; background: rgba(255,255,255,0.96); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid var(--border); border-radius: 14px; box-shadow: 0 8px 32px rgba(0,0,0,0.08); padding: 6px; min-width: 140px; z-index: 200; display: flex; flex-direction: column; gap: 2px; }
.vk-topnav__menu-item { display: flex; align-items: center; gap: 8px; padding: 8px 12px; border-radius: 8px; color: var(--text); font-size: 13px; text-decoration: none; transition: background 0.1s; white-space: nowrap; }
.vk-topnav__menu-item:hover { background: var(--brand-light); color: var(--brand); }
.vk-topnav__menu-item .router-link-active { color: var(--brand); font-weight: 600; }

/* Dropdown transition */
.vk-dd-enter-active { transition: all 0.15s ease-out; }
.vk-dd-leave-active { transition: all 0.1s ease-in; }
.vk-dd-enter-from { opacity: 0; transform: translateY(-4px) scale(0.97); }
.vk-dd-leave-to { opacity: 0; transform: translateY(-2px) scale(0.98); }

@media (min-width: 769px) { .vk-topnav { display: flex; } }
</style>
