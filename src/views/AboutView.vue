<template>
  <div class="about-view">
    <Sidebar />
    <main class="about-view__main">
      <button class="about-view__back" @click="$router.back()"><ChevronLeft :size="20" /> 返回</button>
      <div class="about-view__hero">
        <div class="about-view__logo">V</div>
        <h1 class="about-view__name">Vekus 智能报价平台</h1>
        <p class="about-view__version">版本 1.0.0</p>
      </div>
      <Card class="about-view__card">
        <h3 class="about-view__section-title">关于Vekus</h3>
        <p class="about-view__desc">Vekus 是专为钣金加工行业打造的AI智能报价平台。通过AI图纸识别技术，将传统报价流程缩短至90秒以内。</p>
        <div class="about-view__features">
          <div class="about-view__feature">AI图纸智能识别</div>
          <div class="about-view__feature">实时自动报价计算</div>
          <div class="about-view__feature">交易广场材料买卖</div>
          <div class="about-view__feature">AI智能客服助手</div>
        </div>
      </Card>
      <Card class="about-view__card">
        <h3 class="about-view__section-title">技术栈</h3>
        <div class="about-view__tech"><span>前端</span><strong>Vue 3 + Vite + TypeScript</strong></div>
        <div class="about-view__tech"><span>后端</span><strong>Python FastAPI</strong></div>
        <div class="about-view__tech"><span>AI引擎</span><strong>DeepSeek</strong></div>
      </Card>
      <p class="about-view__copyright">2026 Vekus</p>
    </main>
    <MobileNav />
  </div>
</template>

<script setup lang="ts">
import { ChevronLeft } from 'lucide-vue-next';
import Sidebar from '@/components/layout/Sidebar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';
import Card from '@/components/base/Card.vue';
</script>

<style scoped>
.about-view { display: grid; display: block; min-height: 100vh; }
.about-view__main { padding: 24px 32px 120px; max-width: 640px; }
.about-view__back { display: flex; align-items: center; gap: 4px; padding: 8px 0; margin-bottom: 8px; border: none; background: none; color: var(--text-muted); font-size: var(--fz-body); cursor: pointer; }
.about-view__hero { text-align: center; padding: 40px 0; }
.about-view__logo { width: 72px; height: 72px; border-radius: 20px; background: linear-gradient(135deg, var(--brand), var(--accent)); color: white; display: grid; place-items: center; font-size: 36px; font-weight: var(--fw-bold); margin: 0 auto 16px; }
.about-view__name { font-size: var(--fz-h1); font-weight: var(--fw-bold); margin: 0 0 4px; }
.about-view__version { font-size: var(--fz-sm); color: var(--text-muted); margin: 0; font-family: var(--font-mono); }
.about-view__card { padding: 20px; margin-bottom: 16px; }
.about-view__section-title { font-size: var(--fz-h3); font-weight: var(--fw-semibold); margin: 0 0 12px; }
.about-view__desc { font-size: var(--fz-body); color: var(--text-muted); line-height: var(--lh-loose); margin: 0 0 16px; }
.about-view__features { display: flex; flex-wrap: wrap; gap: 8px; }
.about-view__feature { padding: 6px 14px; border-radius: var(--r-pill); background: var(--brand-light); color: var(--brand); font-size: var(--fz-sm); }
.about-view__tech { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid var(--border); font-size: var(--fz-body); }
.about-view__tech:last-child { border-bottom: none; }
.about-view__tech span { color: var(--text-muted); }
.about-view__tech strong { color: var(--text); font-family: var(--font-mono); font-size: var(--fz-sm); }
.about-view__copyright { text-align: center; font-size: var(--fz-sm); color: var(--text-faint); padding: 20px 0; }
@media (max-width: 768px) { .about-view { grid-template-columns: 1fr; } .about-view__main { padding: 16px 16px 100px; } }
</style>
