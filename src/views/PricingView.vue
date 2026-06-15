<template>
  <div class="pricing-view">
    <Sidebar />
    <main class="pricing-view__main">
      <TopBar title="充值中心" description="购买点数或开通包月，畅享无限报价" />

      <div class="pricing-view__balance" v-if="balance >= 0">
        <Card class="pricing-view__balance-card">
          <div class="pricing-view__balance-content">
            <div>
              <div class="pricing-view__balance-label">当前余额</div>
              <div class="pricing-view__balance-value">{{ balance }} 点</div>
            </div>
            <Button variant="secondary" @click="$router.push('/me')">查看流水</Button>
          </div>
        </Card>
      </div>

      <div class="pricing-view__grid">
        <Card
          v-for="plan in plans"
          :key="plan.id"
          class="pricing-view__plan"
          :class="{ 'pricing-view__plan--featured': plan.id === 'pro' }"
        >
          <div v-if="plan.id === 'pro'" class="pricing-view__ribbon">推荐</div>
          <h3 class="pricing-view__plan-name">{{ plan.name }}</h3>
          <div class="pricing-view__plan-price">
            <span class="pricing-view__plan-currency">¥</span>
            {{ plan.price }}
          </div>
          <p class="pricing-view__plan-desc">{{ plan.description }}</p>
          <Button
            :variant="plan.id === 'pro' ? 'primary' : 'secondary'"
            size="lg"
            block
            :loading="loadingPlan === plan.id"
            @click="handleBuy(plan)"
          >
            {{ plan.price === 0 ? '免费试用' : '立即开通' }}
          </Button>
        </Card>
      </div>
    </main>
    <MobileNav />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import Sidebar from '@/components/layout/Sidebar.vue';
import TopBar from '@/components/layout/TopBar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';
import Card from '@/components/base/Card.vue';
import Button from '@/components/base/Button.vue';
import { getPricing, createOrder, completePayment, getPointsBalance, type PricingPlan } from '@/api/payment';

const plans = ref<PricingPlan[]>([]);
const balance = ref(0);
const loadingPlan = ref('');

onMounted(async () => {
  plans.value = await getPricing();
  balance.value = await getPointsBalance(1);
});

async function handleBuy(plan: PricingPlan) {
  if (plan.price === 0) {
    // Free trial
    try {
      const order = await createOrder(plan.id, 1);
      await completePayment(order.orderNo);
      balance.value = await getPointsBalance(1);
      alert('开通成功！已获得 ' + (plan.points > 0 ? plan.points + ' 点' : '包月权益'));
    } catch {
      alert('开通失败');
    }
    return;
  }

  loadingPlan.value = plan.id;
  try {
    const order = await createOrder(plan.id, 1);
    // Simulate payment flow - in production this would open WeChat Pay
    const confirmed = confirm(`订单金额：¥${order.amount}\n订单号：${order.orderNo}\n\n（演示模式）点击确定模拟支付成功`);
    if (confirmed) {
      await completePayment(order.orderNo);
      balance.value = await getPointsBalance(1);
      alert('支付成功！');
    }
  } catch {
    alert('支付失败，请重试');
  } finally {
    loadingPlan.value = '';
  }
}
</script>

<style scoped>
.pricing-view {
  display: grid;
  display: block;
  min-height: 100vh;
}

.pricing-view__main {
  padding: 24px 32px 120px;
}

.pricing-view__balance-card {
  padding: 20px;
  margin-bottom: 24px;
}

.pricing-view__balance-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pricing-view__balance-label {
  font-size: var(--fz-sm);
  color: var(--text-muted);
  margin-bottom: 4px;
}

.pricing-view__balance-value {
  font-size: 28px;
  font-weight: var(--fw-bold);
  color: var(--brand);
  font-family: var(--font-mono);
}

.pricing-view__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}

.pricing-view__plan {
  padding: 28px 24px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.pricing-view__plan--featured {
  border: 2px solid var(--brand);
  box-shadow: var(--sh-md);
}

.pricing-view__ribbon {
  position: absolute;
  top: 12px;
  right: -28px;
  padding: 4px 32px;
  background: var(--accent);
  color: white;
  font-size: 11px;
  font-weight: var(--fw-bold);
  transform: rotate(45deg);
}

.pricing-view__plan-name {
  font-size: var(--fz-h2);
  font-weight: var(--fw-semibold);
  margin: 0 0 12px;
}

.pricing-view__plan-price {
  font-size: 42px;
  font-weight: var(--fw-bold);
  font-family: var(--font-mono);
  color: var(--text);
  margin-bottom: 8px;
}

.pricing-view__plan-currency {
  font-size: 24px;
  font-weight: var(--fw-medium);
}

.pricing-view__plan-desc {
  font-size: var(--fz-sm);
  color: var(--text-muted);
  margin: 0 0 20px;
}

@media (max-width: 768px) {
  .pricing-view { grid-template-columns: 1fr; }
  .pricing-view__main { padding: 16px 16px 100px; }
  .pricing-view__grid { grid-template-columns: 1fr; }
}
</style>
