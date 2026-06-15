<template>
  <header class="vk-topnav">
    <div class="vk-topnav__inner">
      <!-- Brand -->
      <div class="vk-topnav__brand">
        <div class="vk-topnav__logo">V</div>
        <span class="vk-topnav__brand-name">Vekus</span>
      </div>

      <!-- Centered nav -->
      <nav class="vk-topnav__nav">
        <router-link to="/dashboard" class="vk-topnav__item" :class="{ active: isActive('/dashboard') }">
          <LayoutDashboard :size="17" /><span>看板</span>
        </router-link>

        <!-- 生产 dropdown -->
        <div class="vk-dd" @mouseenter="open='production'" @mouseleave="open=''">
          <button :class="['vk-topnav__item', { active: isMenuActive('production') }]">
            <Wrench :size="17" /><span>生产</span><ChevronDown :size="11" class="vk-dd-arrow" />
          </button>
          <Transition name="vk-dd-fade">
            <div v-if="open==='production'" class="vk-dd__panel vk-dd__panel--wide">
              <div class="vk-dd__grid">
                <router-link v-for="m in productionBig" :key="m.path" :to="m.path" class="vk-dd__card" @click="open=''">
                  <div class="vk-dd__card-icon" :style="{ background: m.bg }">
                    <component :is="m.icon" :size="22" />
                  </div>
                  <div class="vk-dd__card-text">
                    <span class="vk-dd__card-title">{{ m.label }}</span>
                    <span class="vk-dd__card-desc">{{ m.desc }}</span>
                  </div>
                </router-link>
              </div>
              <div class="vk-dd__footer">
                <router-link v-for="m in productionSmall" :key="m.path" :to="m.path" class="vk-dd__link" @click="open=''">{{ m.label }}</router-link>
              </div>
            </div>
          </Transition>
        </div>

        <!-- 业务 dropdown -->
        <div class="vk-dd" @mouseenter="open='business'" @mouseleave="open=''">
          <button :class="['vk-topnav__item', { active: isMenuActive('business') }]">
            <FileText :size="17" /><span>业务</span><ChevronDown :size="11" class="vk-dd-arrow" />
          </button>
          <Transition name="vk-dd-fade">
            <div v-if="open==='business'" class="vk-dd__panel vk-dd__panel--wide">
              <div class="vk-dd__grid">
                <router-link v-for="m in businessBig" :key="m.path" :to="m.path" class="vk-dd__card" @click="open=''">
                  <div class="vk-dd__card-icon" :style="{ background: m.bg }">
                    <component :is="m.icon" :size="22" />
                  </div>
                  <div class="vk-dd__card-text">
                    <span class="vk-dd__card-title">{{ m.label }}</span>
                    <span class="vk-dd__card-desc">{{ m.desc }}</span>
                  </div>
                </router-link>
              </div>
              <div class="vk-dd__footer">
                <router-link v-for="m in businessSmall" :key="m.path" :to="m.path" class="vk-dd__link" @click="open=''">{{ m.label }}</router-link>
              </div>
            </div>
          </Transition>
        </div>

        <router-link to="/messages" class="vk-topnav__item" :class="{ active: isActive('/messages') }">
          <MessageSquare :size="17" /><span>消息</span>
        </router-link>

        <router-link to="/settings" class="vk-topnav__item" :class="{ active: isActive('/settings') }">
          <Settings :size="17" /><span>设置</span>
        </router-link>
      </nav>

      <!-- User -->
      <div class="vk-topnav__user" @click="$router.push('/me')">
        <div class="vk-topnav__avatar">{{ userName.charAt(0) }}</div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import {
  LayoutDashboard, FileText, History, Users, ShoppingBag,
  MessageSquare, Settings, Layers, Package, Wrench, ShieldCheck, Truck, CheckCircle, FolderOpen, ChevronDown,
} from 'lucide-vue-next';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const open = ref('');
const userName = ref(useAuthStore().user?.name || 'User');

const productionBig = [
  { path: '/bom', label: 'BOM 物料', desc: '产品结构·版本管理', icon: Layers, bg: 'linear-gradient(135deg,#2563EB,#1D4ED8)' },
  { path: '/inventory', label: '库存管理', desc: '出入库·安全预警', icon: Package, bg: 'linear-gradient(135deg,#059669,#047857)' },
  { path: '/production', label: '生产工单', desc: '排产·报工·流转', icon: Wrench, bg: 'linear-gradient(135deg,#D97706,#B45309)' },
];
const productionSmall = [
  { path: '/quality', label: '质量管理' },
  { path: '/purchases', label: '采购管理' },
];

const businessBig = [
  { path: '/quote', label: '智能报价', desc: 'AI识图·自动计算·PDF导出', icon: FileText, bg: 'linear-gradient(135deg,#2563EB,#1D4ED8)' },
  { path: '/customers', label: '客户管理', desc: '企查查·风险排查·等级', icon: Users, bg: 'linear-gradient(135deg,#7C3AED,#6D28D9)' },
];
const businessSmall = [
  { path: '/history', label: '历史报价' },
  { path: '/marketplace', label: '交易广场' },
  { path: '/approvals', label: '审批中心' },
  { path: '/documents', label: '文档管理' },
];

const menuPaths: Record<string, string[]> = {
  production: [...productionBig, ...productionSmall].map(i => i.path),
  business: [...businessBig, ...businessSmall].map(i => i.path),
};

function isActive(path: string) {
  if (path === '/quote' && route.path.startsWith('/quote')) return true;
  if (path === '/marketplace' && route.path.startsWith('/marketplace')) return true;
  if (path === '/messages' && route.path.startsWith('/messages')) return true;
  if (path === '/customers' && route.path.startsWith('/customers')) return true;
  return route.path === path;
}
function isMenuActive(menu: string) {
  return menuPaths[menu]?.some(p => route.path.startsWith(p)) || false;
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
}

.vk-topnav__inner {
  display: flex; align-items: center;
  max-width: 960px; margin: 0 auto;
  height: 100%; padding: 0 16px;
}

.vk-topnav__brand { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
.vk-topnav__logo { width: 34px; height: 34px; border-radius: 9px; background: linear-gradient(135deg, var(--brand), var(--accent)); color: white; display: grid; place-items: center; font-size: 16px; font-weight: var(--fw-bold); }
.vk-topnav__brand-name { font-size: 15px; font-weight: var(--fw-bold); color: var(--text); }

.vk-topnav__nav { display: flex; align-items: center; justify-content: center; gap: 2px; flex: 1; }

.vk-topnav__item {
  display: flex; align-items: center; gap: 5px;
  padding: 7px 13px; border-radius: 9px;
  color: #6B7280; font-size: 13px; font-weight: 500;
  text-decoration: none; white-space: nowrap;
  transition: all 0.15s ease; border: none; background: none; cursor: pointer; font-family: inherit;
}
.vk-topnav__item:hover { background: rgba(0,0,0,0.04); color: #1F2937; }
.vk-topnav__item.active { background: var(--brand-light); color: var(--brand); font-weight: 600; }

.vk-dd-arrow { transition: transform 0.2s; margin-left: 1px; }

.vk-topnav__user { flex-shrink: 0; cursor: pointer; }
.vk-topnav__avatar { width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, var(--brand), var(--accent)); color: white; display: grid; place-items: center; font-size: 14px; font-weight: var(--fw-bold); }

/* ====== Dropdown Panel ====== */
.vk-dd { position: relative; }
.vk-dd__panel {
  position: absolute; top: calc(100% + 8px); left: 50%; transform: translateX(-50%);
  background: rgba(255,255,255,0.97);
  backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 18px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.02), 0 12px 40px rgba(0,0,0,0.08), 0 0 0 0.5px rgba(0,0,0,0.04);
  padding: 16px;
  z-index: 200;
  min-width: 180px;
}
.vk-dd__panel--wide { width: 520px; padding: 20px; }

/* Grid cards */
.vk-dd__grid { display: grid; gap: 12px; margin-bottom: 14px; }
.vk-dd__panel--wide .vk-dd__grid { grid-template-columns: repeat(3, 1fr); }

.vk-dd__card {
  display: flex; gap: 12px; padding: 14px;
  border-radius: 14px; background: var(--surface-sunken);
  text-decoration: none; cursor: pointer;
  transition: all 0.15s; border: 1px solid transparent;
}
.vk-dd__card:hover { background: #fff; border-color: var(--border); box-shadow: 0 2px 12px rgba(0,0,0,0.06); transform: translateY(-1px); }

.vk-dd__card-icon {
  width: 40px; height: 40px; border-radius: 11px;
  display: grid; place-items: center; color: #fff; flex-shrink: 0;
}
.vk-dd__card-text { display: flex; flex-direction: column; gap: 3px; justify-content: center; }
.vk-dd__card-title { font-size: 14px; font-weight: 600; color: var(--text); }
.vk-dd__card-desc { font-size: 11px; color: var(--text-muted); line-height: 1.3; }

/* Footer links */
.vk-dd__footer { display: flex; gap: 8px; padding-top: 12px; border-top: 1px solid var(--border); flex-wrap: wrap; }
.vk-dd__link {
  padding: 5px 12px; border-radius: 8px; font-size: 12px; color: var(--text-muted);
  text-decoration: none; transition: all 0.1s;
}
.vk-dd__link:hover { background: var(--brand-light); color: var(--brand); }

/* Dropdown small panel */
.vk-dd__panel:not(.vk-dd__panel--wide) {
  padding: 6px; min-width: 140px;
}
.vk-dd__panel:not(.vk-dd__panel--wide) .vk-dd__link {
  display: block; padding: 8px 12px; border-radius: 8px; font-size: 13px;
}

/* Transition */
.vk-dd-fade-enter-active { transition: all 0.18s cubic-bezier(0.16,1,0.3,1); }
.vk-dd-fade-leave-active { transition: all 0.1s ease-in; }
.vk-dd-fade-enter-from { opacity: 0; transform: translateX(-50%) translateY(-6px) scale(0.96); }
.vk-dd-fade-leave-to { opacity: 0; transform: translateX(-50%) translateY(-3px) scale(0.98); }

@media (min-width: 769px) { .vk-topnav { display: block; } }
@media (max-width: 900px) { .vk-dd__panel--wide { width: 420px; } }
</style>
