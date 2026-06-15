<template>
  <div class="pricing-page">
    <main class="pricing-page__main">
      <!-- Header -->
      <div class="pricing-page__header">
        <h2 class="pricing-page__title">方案与定价</h2>
        <p class="pricing-page__subtitle">
          从个人试用到大企业定制，找到最适合您的钣金 AI 报价方案
        </p>

        <!-- Monthly/Yearly Switch -->
        <div class="pricing-page__switch">
          <div class="pricing-page__switch-track">
            <button
              :class="['pricing-page__switch-btn', { active: !isYearly }]"
              @click="isYearly = false"
            >
              <span class="pricing-page__switch-label">月付</span>
            </button>
            <button
              :class="['pricing-page__switch-btn', { active: isYearly }]"
              @click="isYearly = true"
            >
              <span class="pricing-page__switch-label">
                年付
                <span class="pricing-page__switch-save">省 20%</span>
              </span>
            </button>
          </div>
        </div>
      </div>

      <!-- Plans Grid -->
      <div class="pricing-page__grid">
        <div
          v-for="plan in displayPlans"
          :key="plan.id"
          :class="['pricing-card', { 'pricing-card--popular': plan.popular }]"
        >
          <!-- Popular badge -->
          <div v-if="plan.popular" class="pricing-card__badge">最受欢迎</div>

          <!-- Name & Description -->
          <div class="pricing-card__header">
            <h3 class="pricing-card__name">{{ plan.name }}</h3>
            <p class="pricing-card__desc">{{ plan.description }}</p>
          </div>

          <!-- Price -->
          <div class="pricing-card__price-row">
            <span class="pricing-card__currency">¥</span>
            <span class="pricing-card__price">{{ plan.displayPrice }}</span>
            <span class="pricing-card__period">/月</span>
          </div>
          <div v-if="isYearly && plan.price > 0" class="pricing-card__yearly-info">
            <span class="pricing-card__original">原价 ¥{{ plan.price }}/月</span>
            <span class="pricing-card__yearly-total">年付共计 ¥{{ plan.yearlyTotal }}</span>
          </div>

          <div class="pricing-card__points" v-if="plan.points">
            <span>或 {{ plan.points }} 点一次性购买</span>
          </div>

          <!-- Feature list -->
          <div class="pricing-card__features">
            <h4 class="pricing-card__features-title">{{ plan.includesTitle }}</h4>
            <ul class="pricing-card__features-list">
              <li v-for="(feat, fi) in plan.features" :key="fi" class="pricing-card__feature">
                <span class="pricing-card__check">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                </span>
                <span>{{ feat }}</span>
              </li>
            </ul>
          </div>

          <!-- CTA Button -->
          <button
            :class="['pricing-card__btn', plan.popular ? 'pricing-card__btn--primary' : 'pricing-card__btn--outline']"
            :disabled="loadingPlan === plan.id"
            @click="handleBuy(plan)"
          >
            <span v-if="loadingPlan === plan.id" class="pricing-card__spinner"></span>
            <span v-else>{{ plan.price === 0 ? '免费试用' : '立即开通' }}</span>
          </button>
        </div>
      </div>

      <!-- Balance bar -->
      <div class="pricing-page__balance" v-if="balance >= 0">
        <span class="pricing-page__balance-label">当前余额</span>
        <span class="pricing-page__balance-value">{{ balance }} 点</span>
        <router-link to="/me" class="pricing-page__balance-link">查看流水 →</router-link>
      </div>
    </main>

    <MobileNav />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import MobileNav from '@/components/layout/MobileNav.vue';
import { getPricing, createOrder, completePayment, getPointsBalance, type PricingPlan } from '@/api/payment';

const plans = ref<PricingPlan[]>([]);
const balance = ref(0);
const loadingPlan = ref('');
const isYearly = ref(false);

onMounted(async () => {
  plans.value = await getPricing();
  balance.value = await getPointsBalance(1);
});

const featureMap: Record<string, string[]> = {
  free: ['每日 3 次 AI 识图', '基础报价计算', 'PDF 报价单导出', '手机号登录'],
  pro: ['无限 AI 识图', '高级报价引擎', '3D 模型预览', '客户管理', '交易广场', '微信扫码登录', '发票对账', '报价历史记录'],
  enterprise: ['Pro 版全部功能', '专属服务器部署', 'API 接口对接', '自定义报价参数', '多人团队协作', '数据看板定制', '7×24 技术支持', '私有化部署可选'],
};

const displayPlans = computed(() => {
  return plans.value.map(p => {
    const features = featureMap[p.id] || [];
    const monthlyPrice = p.price;
    const yearlyPerMonth = p.price > 0 ? Math.round(p.price * 12 * 0.8 / 12) : 0;
    const displayPrice = isYearly.value ? yearlyPerMonth : monthlyPrice;
    const yearlyTotal = p.price > 0 ? Math.round(p.price * 12 * 0.8) : 0;
    return {
      ...p,
      features,
      displayPrice,
      yearlyTotal,
      includesTitle: '包含功能',
      popular: p.id === 'pro',
      description: p.description || (p.id === 'free' ? '适合个人和小团队试用 AI 报价' : p.id === 'pro' ? '适合大多数钣金加工企业日常使用' : '适合大型企业和有定制需求的客户'),
    };
  });
});

async function handleBuy(plan: PricingPlan & { displayPrice: number }) {
  if (plan.price === 0) {
    try {
      const order = await createOrder(plan.id, 1);
      await completePayment(order.orderNo);
      balance.value = await getPointsBalance(1);
      alert('开通成功！');
    } catch { alert('开通失败'); }
    return;
  }
  loadingPlan.value = plan.id;
  try {
    const order = await createOrder(plan.id, 1);
    const confirmed = confirm(`订单金额：¥${order.amount}\n订单号：${order.orderNo}\n\n（演示模式）点击确定模拟支付成功`);
    if (confirmed) {
      await completePayment(order.orderNo);
      balance.value = await getPointsBalance(1);
      alert('支付成功！');
    }
  } catch { alert('支付失败，请重试'); }
  finally { loadingPlan.value = ''; }
}
</script>

<style scoped>
.pricing-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8fafc, #f1f5f9);
}
.pricing-page__main {
  max-width: 1060px;
  margin: 0 auto;
  padding: 48px 32px 120px;
}

/* Header */
.pricing-page__header {
  text-align: center;
  margin-bottom: 40px;
}
.pricing-page__title {
  font-size: 36px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 12px;
  letter-spacing: -0.02em;
}
.pricing-page__subtitle {
  font-size: 16px;
  color: #64748b;
  margin: 0 0 28px;
}

/* Switch */
.pricing-page__switch { display: flex; justify-content: center; }
.pricing-page__switch-track {
  display: inline-flex;
  background: #e2e8f0;
  border-radius: 100px;
  padding: 4px;
  gap: 2px;
}
.pricing-page__switch-btn {
  border: none;
  background: transparent;
  padding: 10px 24px;
  border-radius: 100px;
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  transition: all 0.25s;
  font-family: inherit;
}
.pricing-page__switch-btn.active {
  background: #fff;
  color: #0f172a;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  font-weight: 600;
}
.pricing-page__switch-label { display: flex; align-items: center; gap: 8px; }
.pricing-page__switch-save {
  font-size: 11px;
  background: #dbeafe;
  color: #2563eb;
  padding: 2px 8px;
  border-radius: 100px;
  font-weight: 600;
}

/* Grid */
.pricing-page__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  align-items: start;
}

/* Card */
.pricing-card {
  background: #fff;
  border-radius: 20px;
  padding: 32px 28px;
  position: relative;
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}
.pricing-card:hover {
  box-shadow: 0 8px 40px rgba(0,0,0,0.06);
  transform: translateY(-2px);
}
.pricing-card--popular {
  border: 2px solid #0f172a;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
  transform: scale(1.04);
  z-index: 1;
  background: linear-gradient(180deg, #fff 0%, #fafafa 100%);
}
.pricing-card--popular:hover { transform: scale(1.04) translateY(-2px); }
.pricing-card__badge {
  position: absolute;
  top: -14px;
  left: 50%;
  transform: translateX(-50%);
  background: #0f172a;
  color: #fff;
  padding: 4px 18px;
  border-radius: 100px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.02em;
}

/* Card header */
.pricing-card__header { margin-bottom: 20px; }
.pricing-card__name {
  font-size: 22px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 6px;
}
.pricing-card__desc {
  font-size: 13px;
  color: #94a3b8;
  margin: 0;
  line-height: 1.5;
}

/* Price */
.pricing-card__price-row {
  display: flex;
  align-items: baseline;
  margin-bottom: 4px;
}
.pricing-card__currency { font-size: 24px; font-weight: 600; color: #0f172a; }
.pricing-card__price {
  font-size: 48px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.02em;
  line-height: 1;
}
.pricing-card__period { font-size: 14px; color: #94a3b8; margin-left: 2px; }
.pricing-card__yearly-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: 8px;
}
.pricing-card__original {
  font-size: 13px;
  color: #94a3b8;
  text-decoration: line-through;
}
.pricing-card__yearly-total {
  font-size: 12px;
  color: #16a34a;
  font-weight: 600;
}
.pricing-card__points {
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 20px;
}

/* Features */
.pricing-card__features {
  border-top: 1px solid #f1f5f9;
  padding-top: 20px;
  flex: 1;
}
.pricing-card__features-title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  margin: 0 0 14px;
}
.pricing-card__features-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.pricing-card__feature {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 13px;
  color: #475569;
  line-height: 1.4;
}
.pricing-card__check {
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #f0fdf4;
  color: #16a34a;
  display: grid;
  place-items: center;
  margin-top: 1px;
}

/* Button */
.pricing-card__btn {
  margin-top: 24px;
  width: 100%;
  padding: 14px;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.25s;
}
.pricing-card__btn--primary {
  background: #0f172a;
  color: #fff;
}
.pricing-card__btn--primary:hover { background: #1e293b; box-shadow: 0 8px 24px rgba(0,0,0,0.15); }
.pricing-card__btn--outline {
  background: #fff;
  color: #0f172a;
  border: 2px solid #e2e8f0;
}
.pricing-card__btn--outline:hover { border-color: #0f172a; background: #f8fafc; }
.pricing-card__btn:disabled { opacity: 0.6; cursor: not-allowed; }
.pricing-card__spinner {
  width: 20px; height: 20px;
  border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff;
  border-radius: 50%; animation: spin 0.7s linear infinite;
  display: block; margin: 0 auto;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Balance */
.pricing-page__balance {
  margin-top: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 16px 24px;
  background: #fff;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
}
.pricing-page__balance-label { font-size: 14px; color: #64748b; }
.pricing-page__balance-value { font-size: 24px; font-weight: 700; color: #2563eb; font-family: var(--font-mono); }
.pricing-page__balance-link { font-size: 14px; color: #2563eb; text-decoration: none; font-weight: 500; }

@media (max-width: 860px) {
  .pricing-page__grid { grid-template-columns: 1fr; max-width: 400px; margin: 0 auto; }
  .pricing-card--popular { transform: none; }
  .pricing-card--popular:hover { transform: translateY(-2px); }
  .pricing-page__title { font-size: 28px; }
  .pricing-page__main { padding: 32px 16px 120px; }
}
</style>
