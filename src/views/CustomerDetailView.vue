<template>
  <div class="cust-detail">
    <Sidebar />
    <main class="cust-detail__main">
      <button class="cust-detail__back" @click="$router.back()"><ChevronLeft :size="20" /> 返回</button>
      <div v-if="loading">加载中...</div>
      <template v-else-if="customer">
        <Card class="cust-detail__card">
          <div class="cust-detail__header">
            <div class="cust-detail__avatar">{{ customer.name.charAt(0) }}</div>
            <div>
              <h1 class="cust-detail__name">{{ customer.name }}</h1>
              <p class="cust-detail__contact">{{ customer.contactName }} · {{ customer.phone }}</p>
              <div class="cust-detail__tags">
                <Badge :variant="tierVariant">{{ customer.tier }} 级客户</Badge>
                <span v-for="tag in customer.tags" :key="tag" class="vk-tag">{{ tag }}</span>
              </div>
            </div>
          </div>
        </Card>

        <Card class="cust-detail__card">
          <h3 class="cust-detail__section-title">基本信息</h3>
          <div class="cust-detail__info-grid">
            <div><span>客户名称</span><strong>{{ customer.name }}</strong></div>
            <div><span>联系人</span><strong>{{ customer.contactName }}</strong></div>
            <div><span>电话</span><strong>{{ customer.phone }}</strong></div>
            <div v-if="customer.email"><span>邮箱</span><strong>{{ customer.email }}</strong></div>
            <div v-if="customer.address"><span>地址</span><strong>{{ customer.address }}</strong></div>
            <div><span>客户等级</span><strong>{{ customer.tier }} 级</strong></div>
            <div><span>成交状态</span><strong>{{ customer.dealStatus === 'won' ? '已成交' : '未成交' }}</strong></div>
            <div><span>创建时间</span><strong>{{ customer.createdAt }}</strong></div>
          </div>
        </Card>

        <!-- Enterprise info (from registration data) -->
        <Card v-if="customer.extInfo?.Name" class="cust-detail__card">
          <h3 class="cust-detail__section-title">企业信息</h3>
          <div class="cust-detail__info-grid">
            <div v-if="customer.extInfo.Name"><span>企业名称</span><strong>{{ customer.extInfo.Name }}</strong></div>
            <div v-if="customer.extInfo.OperName"><span>法定代表人</span><strong>{{ customer.extInfo.OperName }}</strong></div>
            <div v-if="customer.extInfo.StartDate"><span>成立日期</span><strong>{{ customer.extInfo.StartDate }}</strong></div>
            <div v-if="customer.extInfo.Status"><span>经营状态</span><strong>{{ customer.extInfo.Status }}</strong></div>
            <div v-if="customer.extInfo.CreditCode"><span>信用代码</span><strong class="vk-font-mono">{{ customer.extInfo.CreditCode }}</strong></div>
            <div v-if="customer.extInfo.No"><span>注册号</span><strong class="vk-font-mono">{{ customer.extInfo.No }}</strong></div>
            <div v-if="customer.extInfo.Address" class="cust-detail__full-width"><span>注册地址</span><strong>{{ customer.extInfo.Address }}</strong></div>
          </div>
        </Card>

        <!-- Risk scan -->
        <Card class="cust-detail__card">
          <div class="cust-detail__risk">
            <div>
              <h3 class="cust-detail__risk-title">合作风险排查</h3>
              <p class="cust-detail__risk-desc">全面整合多维度风险数据与官方公示名单，实时综合排查商业合作潜在风险</p>
              <span class="cust-detail__risk-cost">20 点/次</span>
            </div>
            <Button variant="primary" :loading="scanning" :disabled="scanning" @click="doRiskScan">
              <ShieldAlert :size="16" class="mr-2" /> 风险排查
            </Button>
          </div>
        </Card>

        <!-- Risk results -->
        <Card v-if="riskResult" class="cust-detail__card cust-detail__card--risk">
          <h3 class="cust-detail__section-title">风险排查结果 — {{ riskResult.Name || customer.name }}</h3>

          <!-- Risk summary — always show all categories -->
          <div class="cust-detail__risk-summary">
            <div class="cust-detail__risk-stat">
              <span :class="['cust-detail__risk-val', (riskResult.ShiXin?.TotalCount || 0) > 0 ? 'text-danger' : 'text-muted']">{{ riskResult.ShiXin?.TotalCount || 0 }}</span>
              <span>失信被执行</span>
            </div>
            <div class="cust-detail__risk-stat">
              <span :class="['cust-detail__risk-val', (riskResult.ZhiXing?.TotalCount || 0) > 0 ? 'text-warn' : 'text-muted']">{{ riskResult.ZhiXing?.TotalCount || 0 }}</span>
              <span>被执行</span>
            </div>
            <div class="cust-detail__risk-stat">
              <span :class="['cust-detail__risk-val', (riskResult.AdminPenalty?.TotalCount || 0) > 0 ? 'text-warn' : 'text-muted']">{{ riskResult.AdminPenalty?.TotalCount || 0 }}</span>
              <span>行政处罚</span>
            </div>
            <div class="cust-detail__risk-stat">
              <span :class="['cust-detail__risk-val', (riskResult.Exception?.TotalCount || 0) > 0 ? 'text-warn' : 'text-muted']">{{ riskResult.Exception?.TotalCount || 0 }}</span>
              <span>经营异常</span>
            </div>
            <div class="cust-detail__risk-stat">
              <span :class="['cust-detail__risk-val', (riskResult.Sumptuary?.TotalCount || 0) > 0 ? 'text-danger' : 'text-muted']">{{ riskResult.Sumptuary?.TotalCount || 0 }}</span>
              <span>限制高消费</span>
            </div>
            <div class="cust-detail__risk-stat">
              <span :class="['cust-detail__risk-val', (riskResult.EquityFreeze?.TotalCount || 0) > 0 ? 'text-warn' : 'text-muted']">{{ riskResult.EquityFreeze?.TotalCount || 0 }}</span>
              <span>股权冻结</span>
            </div>
            <div class="cust-detail__risk-stat">
              <span :class="['cust-detail__risk-val', (riskResult.Bankruptcy?.TotalCount || 0) > 0 ? 'text-warn' : 'text-muted']">{{ riskResult.Bankruptcy?.TotalCount || 0 }}</span>
              <span>破产重整</span>
            </div>
            <div class="cust-detail__risk-stat">
              <span :class="['cust-detail__risk-val', (riskResult.TaxIllegal?.TotalCount || 0) > 0 ? 'text-warn' : 'text-muted']">{{ riskResult.TaxIllegal?.TotalCount || 0 }}</span>
              <span>税收违法</span>
            </div>
            <div class="cust-detail__risk-stat">
              <span :class="['cust-detail__risk-val', (riskResult.EnvPunishment?.TotalCount || 0) > 0 ? 'text-warn' : 'text-muted']">{{ riskResult.EnvPunishment?.TotalCount || 0 }}</span>
              <span>环保处罚</span>
            </div>
            <div class="cust-detail__risk-stat">
              <span :class="['cust-detail__risk-val', (riskResult.SeriousIllegal?.TotalCount || 0) > 0 ? 'text-danger' : 'text-muted']">{{ riskResult.SeriousIllegal?.TotalCount || 0 }}</span>
              <span>严重违法</span>
            </div>
            <div class="cust-detail__risk-stat">
              <span :class="['cust-detail__risk-val', (riskResult.TaxOweNotice?.TotalCount || 0) > 0 ? 'text-warn' : 'text-muted']">{{ riskResult.TaxOweNotice?.TotalCount || 0 }}</span>
              <span>欠税公告</span>
            </div>
            <div class="cust-detail__risk-stat">
              <span :class="['cust-detail__risk-val', (riskResult.JudicialSale?.TotalCount || 0) > 0 ? 'text-warn' : 'text-muted']">{{ riskResult.JudicialSale?.TotalCount || 0 }}</span>
              <span>司法拍卖</span>
            </div>
          </div>

          <!-- Detail sections for each risk type -->
          <div v-if="riskResult.ShiXin?.DataList?.length" class="cust-detail__risk-block">
            <h4 class="cust-detail__risk-block-title">失信被执行人 ({{ riskResult.ShiXin.TotalCount }}条，涉案{{ riskResult.ShiXin.TotalAmount || 0 }}万元)</h4>
            <div v-for="(item, i) in riskResult.ShiXin.DataList.slice(0,3)" :key="'sx'+i" class="cust-detail__risk-item">
              <strong>{{ item.CaseNo }}</strong>
              <span>{{ item.ExecuteCourt }} · {{ item.Amount }}元</span>
              <span class="text-danger">{{ item.ExecuteStatus }}</span>
            </div>
          </div>

          <div v-if="riskResult.ZhiXing?.DataList?.length" class="cust-detail__risk-block">
            <h4 class="cust-detail__risk-block-title">被执行人 ({{ riskResult.ZhiXing.TotalCount }}条，{{ riskResult.ZhiXing.TotalAmount || 0 }}万元)</h4>
            <div v-for="(item, i) in riskResult.ZhiXing.DataList.slice(0,3)" :key="'zx'+i" class="cust-detail__risk-item">
              <strong>{{ item.CaseNo }}</strong>
              <span>{{ item.ExecuteCourt }} · {{ item.BiaoDi }}元</span>
            </div>
          </div>

          <div v-if="riskResult.AdminPenalty?.DataList?.length" class="cust-detail__risk-block">
            <h4 class="cust-detail__risk-block-title">行政处罚 ({{ riskResult.AdminPenalty.TotalCount }}条，罚款{{ riskResult.AdminPenalty.TotalAmount || 0 }}万元)</h4>
            <div v-for="(item, i) in riskResult.AdminPenalty.DataList.slice(0,3)" :key="'ap'+i" class="cust-detail__risk-item">
              <strong>{{ item.DocNo }}</strong>
              <span>{{ item.PunishOffice }}</span>
              <span class="text-warn">罚款{{ item.PunishAmt }}元</span>
            </div>
          </div>

          <div v-if="riskResult.Exception?.DataList?.length" class="cust-detail__risk-block">
            <h4 class="cust-detail__risk-block-title">经营异常 ({{ riskResult.Exception.TotalCount }}条)</h4>
            <div v-for="(item, i) in riskResult.Exception.DataList.slice(0,3)" :key="'ex'+i" class="cust-detail__risk-item">
              <span>{{ item.AddDate }} · {{ item.AddOffice }}</span>
              <span>{{ item.AddReason }}</span>
            </div>
          </div>

          <div v-if="riskResult.Sumptuary?.DataList?.length" class="cust-detail__risk-block">
            <h4 class="cust-detail__risk-block-title">限制高消费 ({{ riskResult.Sumptuary.TotalCount }}条，涉案{{ riskResult.Sumptuary.TotalAmount || 0 }}万元)</h4>
            <div v-for="(item, i) in riskResult.Sumptuary.DataList.slice(0,3)" :key="'sp'+i" class="cust-detail__risk-item">
              <strong>{{ item.CaseNo }}</strong>
              <span>{{ item.CompanyName }} · {{ item.Amount }}元</span>
            </div>
          </div>

          <div v-if="riskResult.EquityFreeze?.DataList?.length" class="cust-detail__risk-block">
            <h4 class="cust-detail__risk-block-title">股权冻结 ({{ riskResult.EquityFreeze.TotalCount }}条)</h4>
            <div v-for="(item, i) in riskResult.EquityFreeze.DataList.slice(0,3)" :key="'ef'+i" class="cust-detail__risk-item">
              <strong>{{ item.DocNo }}</strong>
              <span>{{ item.FreezeCompany }} · {{ item.EquityAmount }}</span>
            </div>
          </div>

          <div v-if="riskResult.Bankruptcy?.DataList?.length" class="cust-detail__risk-block">
            <h4 class="cust-detail__risk-block-title">破产重整 ({{ riskResult.Bankruptcy.TotalCount }}条)</h4>
            <div v-for="(item, i) in riskResult.Bankruptcy.DataList.slice(0,3)" :key="'br'+i" class="cust-detail__risk-item">
              <strong>{{ item.CaseNo }}</strong>
              <span>{{ item.PublicDate }}</span>
            </div>
          </div>

          <div v-if="riskResult.TaxIllegal?.DataList?.length" class="cust-detail__risk-block">
            <h4 class="cust-detail__risk-block-title">税收违法 ({{ riskResult.TaxIllegal.TotalCount }}条)</h4>
            <div v-for="(item, i) in riskResult.TaxIllegal.DataList.slice(0,3)" :key="'ti'+i" class="cust-detail__risk-item">
              <span>{{ item.CaseNature }} · {{ item.TaxGov }}</span>
            </div>
          </div>

          <div v-if="riskResult.EnvPunishment?.DataList?.length" class="cust-detail__risk-block">
            <h4 class="cust-detail__risk-block-title">环保处罚 ({{ riskResult.EnvPunishment.TotalCount }}条)</h4>
            <div v-for="(item, i) in riskResult.EnvPunishment.DataList.slice(0,3)" :key="'ep'+i" class="cust-detail__risk-item">
              <span>{{ item.PunishOffice }} · 罚款{{ item.PunishAmt }}元</span>
            </div>
          </div>
        </Card>

        <Card class="cust-detail__card">
          <h3 class="cust-detail__section-title">交易概况</h3>
          <div class="cust-detail__deal-stats">
            <div class="cust-detail__deal-stat">
              <span class="cust-detail__deal-value">¥{{ formattedNumber(customer.totalAmount || 0) }}</span>
              <span class="cust-detail__deal-label">总成交额</span>
            </div>
            <div class="cust-detail__deal-stat">
              <span class="cust-detail__deal-value">{{ customer.quoteCount || quotes.length }}</span>
              <span class="cust-detail__deal-label">报价次数</span>
            </div>
            <div class="cust-detail__deal-stat">
              <span class="cust-detail__deal-value">¥{{ formattedNumber(customer.avgDealSize || 0) }}</span>
              <span class="cust-detail__deal-label">平均客单价</span>
            </div>
            <div class="cust-detail__deal-stat">
              <span class="cust-detail__deal-value">{{ customer.dealStatus === 'won' ? customer.lastDealDate || '-' : '-' }}</span>
              <span class="cust-detail__deal-label">最近成交</span>
            </div>
          </div>
        </Card>

        <Card class="cust-detail__card">
          <h3 class="cust-detail__section-title">历史报价 ({{ quotes.length }})</h3>
          <div v-if="quotes.length === 0" class="cust-detail__empty">暂无报价记录</div>
          <div v-for="q in quotes" :key="q.id" class="cust-detail__quote" @click="$router.push('/quote/result/'+q.id)">
            <div class="cust-detail__quote-main">
              <span class="vk-font-mono">{{ q.quoteNo }}</span>
              <Badge :variant="q.status === 'won' ? 'success' : q.status === 'lost' ? 'danger' : q.status === 'sent' ? 'info' : 'default'" size="sm">{{ statusLabel(q.status) }}</Badge>
            </div>
            <div class="cust-detail__quote-info">
              <span>{{ q.material }} / {{ q.thickness }}mm / {{ q.quantity }}件</span>
              <PriceDisplay :value="q.totalPrice" size="sm" />
            </div>
          </div>
        </Card>

        <Card class="cust-detail__card">
          <h3 class="cust-detail__section-title">图纸管理 ({{ drawings.length }})</h3>
          <div v-if="drawings.length === 0" class="cust-detail__empty">暂无关联图纸</div>
          <div v-for="d in drawings" :key="d.id" class="cust-detail__drawing">
            <div class="cust-detail__drawing-icon"><FileImage :size="20" /></div>
            <div class="cust-detail__drawing-info">
              <div class="cust-detail__drawing-name">{{ d.fileName || '未命名图纸' }}</div>
              <div class="cust-detail__drawing-meta">{{ d.fileType || '未知类型' }} · {{ d.createdAt || '-' }}</div>
            </div>
            <Badge :variant="d.status === 'done' ? 'success' : d.status === 'processing' ? 'info' : 'default'" size="sm">
              {{ d.status === 'done' ? '已识别' : d.status === 'processing' ? '识别中' : '待识别' }}
            </Badge>
          </div>
        </Card>
      </template>
    </main>
    <MobileNav />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { ChevronLeft, FileImage, ShieldAlert } from 'lucide-vue-next';
import Sidebar from '@/components/layout/Sidebar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';
import Card from '@/components/base/Card.vue';
import Button from '@/components/base/Button.vue';
import Badge from '@/components/base/Badge.vue';
import PriceDisplay from '@/components/data/PriceDisplay.vue';
import { api } from '@/api';

const route = useRoute();
const customer = ref<any>(null);
const quotes = ref<any[]>([]);
const drawings = ref<any[]>([]);
const loading = ref(true);
const scanning = ref(false);
const riskResult = ref<any>(null);

const tierVariant = computed(() => {
  const v: Record<string, any> = { A: 'success', B: 'info', C: 'default' };
  return v[customer.value?.tier] || 'default';
});

function statusLabel(s: string) {
  const m: Record<string, string> = { draft: '草稿', sent: '已发送', won: '已成交', lost: '已失单' };
  return m[s] || s;
}

function formattedNumber(v: number) { return new Intl.NumberFormat('zh-CN').format(v); }

async function doRiskScan() {
  if (!customer.value) return;
  scanning.value = true;
  try {
    const name = customer.value.name;
    const res = await api.get<any>(`/qichacha/risk-scan?searchKey=${encodeURIComponent(name)}&customerId=${customer.value.id}`);
    if (res.data?.ok && res.data?.data) {
      riskResult.value = res.data.data;
    } else {
      alert(res.data?.message || '排查失败，请稍后重试');
    }
  } catch { alert('请求失败'); }
  finally { scanning.value = false; }
}

onMounted(async () => {
  const id = route.params.id as string;
  const r1 = await api.get<any>('/customers/' + id);
  if (r1.data) customer.value = r1.data;
  const r2 = await api.get<any[]>('/quotes');
  if (r2.data) quotes.value = r2.data.filter((q: any) => q.customerName === customer.value?.name);
  if (r2.data) {
    const seen = new Set<string>();
    drawings.value = r2.data
      .filter((q: any) => q.customerName === customer.value?.name && q.recognized)
      .map((q: any) => ({
        id: q.id, fileName: `${q.quoteNo}.dwg`, fileType: 'DWG Drawing',
        status: q.recognized?.thickness ? 'done' : 'processing', createdAt: q.createdAt,
      }))
      .filter((d: any) => { const k = d.fileName; if (seen.has(k)) return false; seen.add(k); return true; });
  }
  loading.value = false;
});
</script>

<style scoped>
.cust-detail { display: grid; display: block; min-height: 100vh; }
.cust-detail__main { padding: 24px 32px 120px; max-width: 800px; margin: 0 auto; }
.cust-detail__back { display: flex; align-items: center; gap: 4px; padding: 8px 0; margin-bottom: 8px; border: none; background: none; color: var(--text-muted); cursor: pointer; }
.cust-detail__back:hover { color: var(--brand); }
.cust-detail__card { padding: 20px; margin-bottom: 16px; }
.cust-detail__header { display: flex; gap: 16px; }
.cust-detail__avatar { width: 56px; height: 56px; border-radius: 50%; background: linear-gradient(135deg, var(--brand), var(--accent)); color: white; display: grid; place-items: center; font-size: 24px; font-weight: var(--fw-bold); flex-shrink: 0; }
.cust-detail__name { font-size: var(--fz-h2); font-weight: var(--fw-bold); margin: 0 0 4px; }
.cust-detail__contact { font-size: var(--fz-sm); color: var(--text-muted); margin: 0 0 6px; }
.cust-detail__tags { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
.vk-tag { font-size: 11px; padding: 2px 8px; border-radius: var(--r-tag); background: var(--brand-light); color: var(--brand); }
.cust-detail__section-title { font-size: var(--fz-h3); font-weight: var(--fw-semibold); margin: 0 0 14px; }
.cust-detail__info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
.cust-detail__info-grid > div > span { display: block; font-size: var(--fz-sm); color: var(--text-muted); margin-bottom: 2px; }
.cust-detail__info-grid > div > strong { font-size: var(--fz-body); color: var(--text); }

/* Risk scan */
.cust-detail__risk { display: flex; justify-content: space-between; align-items: center; gap: 16px; }
.cust-detail__risk-title { font-size: var(--fz-h3); font-weight: var(--fw-semibold); margin: 0 0 4px; }
.cust-detail__risk-desc { font-size: var(--fz-sm); color: var(--text-muted); margin: 0 0 6px; max-width: 440px; }
.cust-detail__risk-cost { font-size: var(--fz-xs); color: var(--accent); font-weight: var(--fw-semibold); }

/* Risk results */
.cust-detail__card--risk { border-left: 3px solid var(--danger); }
.cust-detail__risk-summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
.cust-detail__full-width { grid-column: 1 / -1; }
.text-muted { color: var(--text-muted) !important; }
.cust-detail__risk-stat { text-align: center; padding: 12px 8px; background: var(--surface-sunken); border-radius: var(--r-input); display: flex; flex-direction: column; gap: 4px; font-size: var(--fz-xs); color: var(--text-muted); }
.cust-detail__risk-val { font-size: 22px; font-weight: var(--fw-bold); font-family: var(--font-mono); }
.cust-detail__risk-block { margin-bottom: 16px; }
.cust-detail__risk-block-title { font-size: var(--fz-sm); font-weight: var(--fw-semibold); margin: 0 0 8px; color: var(--text); }
.cust-detail__risk-item { display: flex; flex-direction: column; gap: 2px; padding: 8px 12px; background: var(--surface-sunken); border-radius: var(--r-tag); margin-bottom: 6px; font-size: var(--fz-sm); }
.cust-detail__risk-item strong { color: var(--text); }
.cust-detail__risk-item span { color: var(--text-muted); }

.text-danger { color: var(--danger) !important; }
.text-warn { color: var(--warn) !important; }
.mr-2 { margin-right: 8px; }

.cust-detail__deal-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.cust-detail__deal-stat { text-align: center; padding: 12px; }
.cust-detail__deal-value { display: block; font-family: var(--font-mono); font-size: 24px; font-weight: var(--fw-bold); color: var(--brand); margin-bottom: 4px; }
.cust-detail__deal-label { font-size: var(--fz-sm); color: var(--text-muted); }
.cust-detail__quote { padding: 14px; border-radius: var(--r-input); border: 1px solid var(--border); margin-bottom: 8px; cursor: pointer; transition: border-color var(--duration-fast); }
.cust-detail__quote:hover { border-color: var(--brand); }
.cust-detail__quote-main { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.cust-detail__quote-info { display: flex; justify-content: space-between; font-size: var(--fz-sm); color: var(--text-muted); }
.cust-detail__empty { text-align: center; padding: 32px; color: var(--text-muted); }
.cust-detail__drawing { display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: var(--r-input); border: 1px solid var(--border); margin-bottom: 8px; }
.cust-detail__drawing-icon { width: 40px; height: 40px; border-radius: var(--r-tag); background: var(--brand-light); color: var(--brand); display: grid; place-items: center; flex-shrink: 0; }
.cust-detail__drawing-info { flex: 1; }
.cust-detail__drawing-name { font-size: var(--fz-body); font-weight: var(--fw-medium); color: var(--text); }
.cust-detail__drawing-meta { font-size: var(--fz-sm); color: var(--text-muted); margin-top: 2px; }

@media (max-width: 768px) {
  .cust-detail { grid-template-columns: 1fr; }
  .cust-detail__main { padding: 16px 16px 100px; }
  .cust-detail__info-grid { grid-template-columns: 1fr; }
  .cust-detail__risk { flex-direction: column; align-items: stretch; text-align: center; }
  .cust-detail__risk-desc { max-width: 100%; }
  .cust-detail__risk-summary { grid-template-columns: repeat(2, 1fr); }
  .cust-detail__deal-stats { grid-template-columns: repeat(2, 1fr); }
}
</style>
