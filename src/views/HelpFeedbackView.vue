<template>
  <div class="help-view">
    <Sidebar />
    <main class="help-view__main">
      <button class="help-view__back" @click="$router.back()"><ChevronLeft :size="20" /> 返回</button>
      <h1 class="help-view__title">帮助与反馈</h1>

      <Card class="help-view__card">
        <h3 class="help-view__section-title">常见问题</h3>
        <div v-for="(faq, i) in faqs" :key="i" class="help-view__faq" @click="faq.open = !faq.open">
          <div class="help-view__faq-q">
            <span>{{ faq.q }}</span>
            <ChevronRight :size="16" :class="{ 'help-view__faq-arrow--open': faq.open }" class="help-view__faq-arrow" />
          </div>
          <div v-if="faq.open" class="help-view__faq-a">{{ faq.a }}</div>
        </div>
      </Card>

      <Card class="help-view__card">
        <h3 class="help-view__section-title">联系客服</h3>
        <div class="help-view__contact">
          <div class="help-view__contact-item">
            <Phone :size="18" /> <span>客服电话</span><strong>400-888-9999</strong>
          </div>
          <div class="help-view__contact-item">
            <Clock :size="18" /> <span>服务时间</span><strong>周一至周六 9:00-18:00</strong>
          </div>
          <div class="help-view__contact-item" @click="$router.push('/messages')">
            <MessageSquare :size="18" /> <span>在线客服</span><strong style="color:var(--brand)">立即咨询 →</strong>
          </div>
        </div>
      </Card>
    </main>
    <MobileNav />
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue';
import { ChevronLeft, ChevronRight, Phone, Clock, MessageSquare } from 'lucide-vue-next';
import Sidebar from '@/components/layout/Sidebar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';
import Card from '@/components/base/Card.vue';

const faqs = reactive([
  { q: '如何上传图纸进行报价？', a: '进入报价页面，第一步填写基础信息，第二步点击上传区域或拖拽图纸文件即可。支持DWG、DXF、STEP、PDF和图片格式，最大10MB。', open: false },
  { q: 'AI识别结果不准确怎么办？', a: '所有AI识别的参数都可以点击编辑按钮手动修改。修改过的字段会显示橙色"已校正"标签。', open: false },
  { q: '如何给客户发送报价？', a: '完成三步报价流程后点击"发送报价"，系统生成专属分享页面，复制链接发给客户即可。', open: false },
  { q: '如何充值购买点数？', a: '进入"我的"→"我的余额"→选择套餐→微信支付。点数永久有效，包月用户30天不限次。', open: false },
  { q: '交易广场怎么发布信息？', a: '进入"交易"页面→点击"发布信息"→选择类型和分类→填写参数→发布。支持AI自动识别规格表。', open: false },
  { q: '忘记密码怎么办？', a: '请联系管理员重置密码或拨打客服电话400-888-9999。后续版本将支持自助找回密码。', open: false },
]);
</script>

<style scoped>
.help-view { display: grid; display: block; min-height: 100vh; }
.help-view__main { padding: 24px 32px 120px; max-width: 640px; }
.help-view__back { display: flex; align-items: center; gap: 4px; padding: 8px 0; margin-bottom: 8px; border: none; background: none; color: var(--text-muted); font-size: var(--fz-body); cursor: pointer; }
.help-view__back:hover { color: var(--brand); }
.help-view__title { font-size: var(--fz-h1); font-weight: var(--fw-bold); margin: 0 0 24px; }
.help-view__card { padding: 20px; margin-bottom: 16px; }
.help-view__section-title { font-size: var(--fz-h3); font-weight: var(--fw-semibold); margin: 0 0 16px; }
.help-view__faq { border-bottom: 1px solid var(--border); padding: 14px 0; cursor: pointer; }
.help-view__faq:last-child { border-bottom: none; }
.help-view__faq-q { display: flex; justify-content: space-between; align-items: center; font-size: var(--fz-body); font-weight: var(--fw-medium); color: var(--text); gap: 12px; }
.help-view__faq-arrow { color: var(--text-faint); transition: transform var(--duration-fast); flex-shrink: 0; }
.help-view__faq-arrow--open { transform: rotate(90deg); }
.help-view__faq-a { margin-top: 10px; padding: 12px; background: var(--surface-sunken); border-radius: var(--r-input); font-size: var(--fz-body); color: var(--text-muted); line-height: var(--lh-loose); }
.help-view__contact { display: flex; flex-direction: column; gap: 12px; }
.help-view__contact-item { display: flex; align-items: center; gap: 10px; padding: 14px; border-radius: var(--r-input); background: var(--surface-sunken); font-size: var(--fz-body); cursor: default; }
.help-view__contact-item span { color: var(--text-muted); }
.help-view__contact-item strong { margin-left: auto; color: var(--text); }
@media (max-width: 768px) { .help-view { grid-template-columns: 1fr; } .help-view__main { padding: 16px 16px 100px; } }
</style>
