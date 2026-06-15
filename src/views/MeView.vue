<template>
  <div class="me-view">
    <Sidebar />
    <main class="me-view__main">
      <TopBar title="个人中心" />

      <Card class="me-view__card">
        <div class="me-view__header">
          <div class="me-view__avatar">{{ userName.charAt(0) }}</div>
          <div class="me-view__info">
            <h2 class="me-view__name">{{ userName }}</h2>
            <p class="me-view__role">{{ userRole }} · {{ factoryName }}</p>
            <p class="me-view__phone">{{ userPhone || '未绑定手机' }}</p>
          </div>
        </div>

        <div class="me-view__stats">
          <div class="me-view__stat">
            <span class="me-view__stat-value">{{ stats.quotes }}</span>
            <span class="me-view__stat-label">本月报价</span>
          </div>
          <div class="me-view__stat">
            <span class="me-view__stat-value">{{ stats.won }}</span>
            <span class="me-view__stat-label">已成交</span>
          </div>
          <div class="me-view__stat">
            <span class="me-view__stat-value">{{ stats.rate }}%</span>
            <span class="me-view__stat-label">成交率</span>
          </div>
        </div>
      </Card>

      <div class="me-view__menu">
        <div class="me-view__section-label">业务</div>
        <div class="me-view__menu-item" @click="$router.push('/history')">
          <FileText :size="20" />
          <span>我的报价</span>
          <span class="me-view__count">{{ stats.quotes }} 单</span>
          <ChevronRight :size="16" />
        </div>
        <div class="me-view__menu-item" @click="$router.push('/customers')">
          <Users :size="20" />
          <span>我的客户</span>
          <span class="me-view__count">{{ customerCount }} 位</span>
          <ChevronRight :size="16" />
        </div>
        <div class="me-view__menu-item" @click="$router.push('/marketplace')">
          <ShoppingBag :size="20" />
          <span>我的交易</span>
          <span class="me-view__count">{{ myListingCount }} 条</span>
          <ChevronRight :size="16" />
        </div>
      </div>

      <div class="me-view__menu">
        <div class="me-view__section-label">资产</div>
        <div class="me-view__menu-item" @click="$router.push('/pricing')">
          <Coins :size="20" />
          <span>我的余额</span>
          <span class="me-view__points">{{ pointsBalance }} 点</span>
          <ChevronRight :size="16" />
        </div>
        <div class="me-view__menu-item" @click="$router.push('/points')">
          <Receipt :size="20" />
          <span>点数流水</span>
          <ChevronRight :size="16" />
        </div>
      </div>

      <div class="me-view__menu">
        <div class="me-view__section-label">消息</div>
        <div class="me-view__menu-item" @click="$router.push('/messages')">
          <MessageSquare :size="20" />
          <span>消息通知</span>
          <Badge v-if="unreadCount > 0" variant="info" size="sm">{{ unreadCount }}</Badge>
          <ChevronRight :size="16" />
        </div>
      </div>

      <div class="me-view__menu">
        <div class="me-view__section-label">设置</div>
        <div class="me-view__menu-item" @click="$router.push('/settings')">
          <Settings :size="20" />
          <span>报价参数</span>
          <ChevronRight :size="16" />
        </div>
        <div class="me-view__menu-item" @click="$router.push('/account-security')">
          <Shield :size="20" />
          <span>账户安全</span>
          <ChevronRight :size="16" />
        </div>
        <div class="me-view__menu-item" @click="$router.push('/help')">
          <HelpCircle :size="20" />
          <span>帮助与反馈</span>
          <ChevronRight :size="16" />
        </div>
        <div class="me-view__menu-item" @click="$router.push('/about')">
          <Info :size="20" />
          <span>关于Vekus</span>
          <ChevronRight :size="16" />
        </div>
      </div>

      <Button variant="ghost" size="lg" block class="me-view__logout" @click="handleLogout">
        退出登录
      </Button>
    </main>
    <MobileNav />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { FileText, Users, Coins, MessageSquare, ShoppingBag, Settings, Shield, HelpCircle, Info, Receipt, ChevronRight } from 'lucide-vue-next';
import Sidebar from '@/components/layout/Sidebar.vue';
import TopBar from '@/components/layout/TopBar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';
import Card from '@/components/base/Card.vue';
import Button from '@/components/base/Button.vue';
import Badge from '@/components/base/Badge.vue';
import { useAuthStore } from '@/stores/auth';
import { clearToken, api } from '@/api';
import { getPointsBalance } from '@/api/payment';
import { getUnreadCount } from '@/api/messages';

const router = useRouter();
const authStore = useAuthStore();
const userName = ref(authStore.user?.name || '张伟');
const userRole = ref(authStore.user?.role === 'boss' ? '管理员' : '业务员');
const userPhone = ref(authStore.user?.phone || '138****1234');
const factoryName = ref(authStore.user?.factoryName || 'Vekus');
const stats = ref({ quotes: 0, won: 0, rate: 0 });
const pointsBalance = ref(0);
const unreadCount = ref(0);
const customerCount = ref(0);
const myListingCount = ref(0);
const showTransactions = ref(false);

onMounted(async () => {
  const result = await api.get<any>('/profile');
  if (result.data) {
    userName.value = result.data.name || userName.value;
    userRole.value = result.data.role === 'boss' ? '管理员' : '业务员';
    userPhone.value = result.data.phone || userPhone.value;
    factoryName.value = result.data.factory_name || factoryName.value;
  }
  const statsResult = await api.get<any>('/profile/stats');
  if (statsResult.data) {
    stats.value = {
      quotes: statsResult.data.quotes || 0,
      won: statsResult.data.won || 0,
      rate: statsResult.data.rate || 0,
    };
  }
  pointsBalance.value = await getPointsBalance(1);
  unreadCount.value = await getUnreadCount(1);

  // Fetch customer count
  try {
    const custResult = await api.get<any[]>('/customers');
    customerCount.value = (custResult.data || []).length;
  } catch { customerCount.value = 0; }

  // Fetch my listings count
  try {
    const listResult = await api.get<any[]>('/marketplace/my-listings?owner_user_id=1');
    myListingCount.value = (listResult.data || []).length;
  } catch { myListingCount.value = 0; }
});

function handleLogout() {
  authStore.logout();
  clearToken();
  router.push('/login');
}
</script>

<style scoped>
.me-view {
  display: grid;
  display: block;
  min-height: 100vh;
}

.me-view__main {
  padding: 24px 32px 120px;
  max-width: 600px;
  margin: 0 auto;
}

.me-view__card {
  padding: 24px;
  margin-bottom: 20px;
}

.me-view__header {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.me-view__avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--brand), var(--accent));
  color: white;
  display: grid;
  place-items: center;
  font-size: 28px;
  font-weight: var(--fw-bold);
}

.me-view__name {
  font-size: var(--fz-h2);
  font-weight: var(--fw-bold);
  margin: 0 0 4px;
  color: var(--text);
}

.me-view__role {
  font-size: var(--fz-body);
  color: var(--text);
  margin: 0 0 4px;
}

.me-view__phone {
  font-size: var(--fz-sm);
  color: var(--text-muted);
  margin: 0;
}

.me-view__stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
}

.me-view__stat {
  text-align: center;
}

.me-view__stat-value {
  display: block;
  font-size: 28px;
  font-weight: var(--fw-bold);
  color: var(--brand);
  font-family: var(--font-mono);
}

.me-view__stat-label {
  font-size: var(--fz-sm);
  color: var(--text-muted);
}

.me-view__menu {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 24px;
}

.me-view__menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: var(--r-input);
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text);
  font-size: var(--fz-body);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.me-view__menu-item:hover {
  border-color: var(--brand);
  background: var(--surface-sunken);
}

.me-view__menu-item span {
  flex: 1;
}

.me-view__points {
  font-family: var(--font-mono);
  font-weight: var(--fw-semibold);
  color: var(--brand);
  font-size: var(--fz-sm);
}

.me-view__section-label {
  font-size: var(--fz-sm);
  font-weight: var(--fw-semibold);
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 0 8px;
  margin-bottom: 4px;
  margin-top: 4px;
}

.me-view__count {
  font-family: var(--font-mono);
  font-size: var(--fz-sm);
  color: var(--text-muted);
  margin-left: auto;
  margin-right: 4px;
}

.me-view__version {
  font-family: var(--font-mono);
  font-size: var(--fz-xs);
  color: var(--text-faint);
  margin-left: auto;
  margin-right: 4px;
}

.me-view__logout {
  border-color: var(--border-strong);
  color: var(--danger);
  margin-top: 20px;
}

@media (max-width: 768px) {
  .me-view {
    grid-template-columns: 1fr;
  }
  .me-view__main {
    padding-bottom: 100px;
    max-width: 100%;
  }
}
</style>

