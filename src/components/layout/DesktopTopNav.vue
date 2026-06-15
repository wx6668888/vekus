<template>
  <header class="vk-topnav">
    <div class="vk-topnav__inner">
      <div class="vk-topnav__brand">
        <div class="vk-topnav__logo">V</div>
        <span class="vk-topnav__brand-name">Vekus</span>
      </div>

      <nav class="vk-topnav__nav">
        <router-link to="/dashboard" class="vk-topnav__item" :class="{ active: isActive('/dashboard') }">
          <LayoutDashboard :size="17" /><span>看板</span>
        </router-link>

        <!-- 生产 -->
        <div class="vk-dd" @mouseenter="open='production'" @mouseleave="open=''">
          <button :class="['vk-topnav__item', { active: isMenuActive('production') }]">
            <Wrench :size="17" /><span>生产</span><ChevronDown :size="11" class="vk-dd-arrow" />
          </button>
          <Transition name="vk-dd-fade">
            <div v-if="open==='production'" class="vk-dd__panel">
              <div class="vk-dd__split">
                <!-- Left: cards grid -->
                <div class="vk-dd__left">
                  <div class="vk-dd__grid">
                    <router-link v-for="m in productionBig" :key="m.path" :to="m.path" class="vk-dd__card" @click="open=''">
                      <div class="vk-dd__card-pattern"></div>
                      <div class="vk-dd__card-glow"></div>
                      <component :is="m.icon" class="vk-dd__card-icon" :size="22" />
                      <span class="vk-dd__card-title">{{ m.label }}</span>
                    </router-link>
                  </div>
                </div>
                <!-- Right: link list -->
                <div class="vk-dd__right">
                  <router-link v-for="m in productionSmall" :key="m.path" :to="m.path" class="vk-dd__right-link" @click="open=''">
                    <component :is="m.icon" :size="15" /><span>{{ m.label }}</span>
                    <ChevronRight :size="13" class="vk-dd__right-arrow" />
                  </router-link>
                </div>
              </div>
            </div>
          </Transition>
        </div>

        <!-- 业务 -->
        <div class="vk-dd" @mouseenter="open='business'" @mouseleave="open=''">
          <button :class="['vk-topnav__item', { active: isMenuActive('business') }]">
            <FileText :size="17" /><span>业务</span><ChevronDown :size="11" class="vk-dd-arrow" />
          </button>
          <Transition name="vk-dd-fade">
            <div v-if="open==='business'" class="vk-dd__panel">
              <div class="vk-dd__split">
                <!-- Left: big feature cards -->
                <div class="vk-dd__left">
                  <div class="vk-dd__grid vk-dd__grid--2col">
                    <router-link v-for="m in businessBig" :key="m.path" :to="m.path" class="vk-dd__card" @click="open=''">
                      <div class="vk-dd__card-pattern"></div>
                      <div class="vk-dd__card-glow"></div>
                      <component :is="m.icon" class="vk-dd__card-icon" :size="22" />
                      <span class="vk-dd__card-title">{{ m.label }}</span>
                    </router-link>
                  </div>
                </div>
                <!-- Right: link list -->
                <div class="vk-dd__right">
                  <router-link v-for="m in businessSmall" :key="m.path" :to="m.path" class="vk-dd__right-link" @click="open=''">
                    <component :is="m.icon" :size="15" /><span>{{ m.label }}</span>
                    <ChevronRight :size="13" class="vk-dd__right-arrow" />
                  </router-link>
                </div>
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
  MessageSquare, Settings, Layers, Package, Wrench, ShieldCheck, Truck, CheckCircle, FolderOpen, ChevronDown, ChevronRight,
} from 'lucide-vue-next';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const open = ref('');
const userName = ref(useAuthStore().user?.name || 'User');

const productionBig = [
  { path: '/bom', label: 'BOM 物料清单', desc: '产品层级结构、材料定额与版本管理', icon: Layers },
  { path: '/inventory', label: '库存管理', desc: '出入库操作、安全库存预警与盘点', icon: Package },
  { path: '/production', label: '生产工单', desc: '排产调度、工序流转与报工跟踪', icon: Wrench },
];
const productionSmall = [
  { path: '/quality', label: '质量管理', icon: ShieldCheck },
  { path: '/purchases', label: '采购管理', icon: Truck },
];

const businessBig = [
  { path: '/quote', label: '智能报价', desc: 'AI 识图自动提取参数，实时计算报价总价，支持 PDF 导出', icon: FileText },
  { path: '/customers', label: '客户管理', desc: '企业工商查询、风险排查、客户等级与跟进记录', icon: Users },
];
const businessSmall = [
  { path: '/history', label: '历史报价', icon: History },
  { path: '/marketplace', label: '交易广场', icon: ShoppingBag },
  { path: '/approvals', label: '审批中心', icon: CheckCircle },
  { path: '/documents', label: '文档管理', icon: FolderOpen },
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
  box-shadow: 0 4px 6px rgba(0,0,0,0.02), 0 16px 48px rgba(0,0,0,0.1);
  z-index: 200;
}

/* Split layout */
.vk-dd__split { display: flex; }
.vk-dd__left { flex: 1; padding: 14px; min-width: 0; }
.vk-dd__right {
  width: 160px; flex-shrink: 0;
  padding: 14px 12px 14px 6px;
  border-left: 1px solid var(--border);
  background: var(--surface-sunken);
  border-radius: 0 18px 18px 0;
}

.vk-dd__right-link {
  display: flex; align-items: center; gap: 6px;
  padding: 7px 10px; border-radius: 8px;
  font-size: 13px; color: var(--text); white-space: nowrap;
  text-decoration: none; transition: all 0.1s;
}
.vk-dd__right-link:hover { background: var(--brand-light); color: var(--brand); }
.vk-dd__right-link span { flex: 1; }
.vk-dd__right-arrow { opacity: 0; transition: all 0.15s; color: var(--text-faint); flex-shrink: 0; }
.vk-dd__right-link:hover .vk-dd__right-arrow { opacity: 1; transform: translateX(2px); color: var(--brand); }

/* Square grid cards */
.vk-dd__grid { display: grid; gap: 8px; grid-template-columns: repeat(3, 1fr); }
.vk-dd__grid--2col { grid-template-columns: repeat(2, 1fr); }

.vk-dd__card {
  position: relative; isolation: isolate; overflow: hidden;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px;
  aspect-ratio: 1;
  padding: 12px; border-radius: 10px;
  background: var(--surface-sunken);
  border: 1px solid transparent;
  text-decoration: none; cursor: pointer;
  transition: all 0.2s ease;
}
.vk-dd__card:hover {
  background: #fff; border-color: var(--border);
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  transform: translateY(-1px);
}

.vk-dd__card-pattern {
  position: absolute; inset: 0; z-index: -1; opacity: 0.35;
  background-image: radial-gradient(circle, var(--border) 0.7px, transparent 0.7px);
  background-size: 12px 12px;
  mask-image: linear-gradient(135deg, black 35%, transparent 100%);
  -webkit-mask-image: linear-gradient(135deg, black 35%, transparent 100%);
}

.vk-dd__card-glow {
  position: absolute; inset: -20%; z-index: -1; opacity: 0;
  transition: opacity 0.3s ease;
  background: conic-gradient(from 0deg, rgba(37,99,235,0.06), rgba(124,58,237,0.04), rgba(37,99,235,0.03), rgba(37,99,235,0.06));
  border-radius: 50%; filter: blur(40px);
}
.vk-dd__card:hover .vk-dd__card-glow { opacity: 1; }

.vk-dd__card-icon { color: var(--text-muted); opacity: 0.65; flex-shrink: 0; }

.vk-dd__card-title { font-size: 13px; font-weight: 600; color: var(--text); white-space: nowrap; }

/* Transitions */
.vk-dd-fade-enter-active { transition: all 0.18s cubic-bezier(0.16,1,0.3,1); }
.vk-dd-fade-leave-active { transition: all 0.1s ease-in; }
.vk-dd-fade-enter-from { opacity: 0; transform: translateX(-50%) translateY(-6px) scale(0.96); }
.vk-dd-fade-leave-to { opacity: 0; transform: translateX(-50%) translateY(-3px) scale(0.98); }

@media (min-width: 769px) { .vk-topnav { display: block; } }
@media (max-width: 860px) { .vk-dd__right { width: 140px; } .vk-dd__panel { width: 480px; } }
</style>
