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
              <ShieldAlert :size="16" class="mr-2" /> {{ riskResult ? '重新排查' : '风险排查' }}
            </Button>
            <span v-if="lastScanTime" class="cust-detail__scan-time">上次排查: {{ lastScanTime }}</span>
          </div>
        </Card>

        <!-- Risk results — full display -->
        <template v-if="riskResult">
          <!-- Enterprise overview -->
          <Card class="cust-detail__card">
            <h3 class="cust-detail__section-title">企业概览 — {{ riskResult.Name || customer.name }}</h3>
            <div class="cust-detail__info-grid">
              <div><span>企业名称</span><strong>{{ riskResult.Name }}</strong></div>
              <div><span>法定代表人</span><strong>{{ riskResult.OperName || '-' }}</strong></div>
              <div><span>成立日期</span><strong>{{ riskResult.StartDate || '-' }}</strong></div>
              <div><span>经营状态</span><strong>{{ riskResult.Status || '-' }}</strong></div>
              <div><span>注册资本</span><strong>{{ riskResult.RegistCapi || riskResult.RegisteredCapital || '-' }}{{ riskResult.RegisteredCapitalUnit || '' }}</strong></div>
              <div v-if="riskResult.RealCapi"><span>实缴资本</span><strong>{{ riskResult.RealCapi }}</strong></div>
              <div><span>统一社会信用代码</span><strong class="vk-font-mono">{{ riskResult.CreditCode || '-' }}</strong></div>
              <div v-if="riskResult.No"><span>注册号</span><strong class="vk-font-mono">{{ riskResult.No }}</strong></div>
              <div v-if="riskResult.TaxNo"><span>纳税人识别号</span><strong class="vk-font-mono">{{ riskResult.TaxNo }}</strong></div>
              <div v-if="riskResult.OrgNo"><span>组织机构代码</span><strong class="vk-font-mono">{{ riskResult.OrgNo }}</strong></div>
              <div v-if="riskResult.EconKind"><span>企业类型</span><strong>{{ riskResult.EconKind }}</strong></div>
              <div v-if="riskResult.TermStart"><span>营业期限</span><strong>{{ riskResult.TermStart }} ~ {{ riskResult.TermEnd || '-' }}</strong></div>
              <div v-if="riskResult.TaxpayerType"><span>纳税人资质</span><strong>{{ riskResult.TaxpayerType }}</strong></div>
              <div v-if="riskResult.PersonScope"><span>人员规模</span><strong>{{ riskResult.PersonScope }}</strong></div>
              <div v-if="riskResult.InsuredCount"><span>参保人数</span><strong>{{ riskResult.InsuredCount }}</strong></div>
              <div v-if="riskResult.Scale"><span>企业规模</span><strong>{{ riskResult.Scale }}</strong></div>
              <div v-if="riskResult.IsSmall !== undefined"><span>小微企业</span><strong>{{ riskResult.IsSmall === '1' ? '是' : '否' }}</strong></div>
              <div v-if="riskResult.BelongOrg"><span>登记机关</span><strong>{{ riskResult.BelongOrg }}</strong></div>
              <div v-if="riskResult.CheckDate"><span>核准日期</span><strong>{{ riskResult.CheckDate }}</strong></div>
              <div v-if="riskResult.Area" class="cust-detail__full-width"><span>所属地区</span><strong>{{ riskResult.Area.Province || '' }} {{ riskResult.Area.City || '' }} {{ riskResult.Area.County || '' }}</strong></div>
              <div v-if="riskResult.Industry" class="cust-detail__full-width"><span>国标行业</span><strong>{{ riskResult.Industry.Industry || '' }} > {{ riskResult.Industry.SubIndustry || '' }} > {{ riskResult.Industry.MiddleCategory || '' }}</strong></div>
              <div v-if="riskResult.Address" class="cust-detail__full-width"><span>注册地址</span><strong>{{ riskResult.Address }}</strong></div>
              <div v-if="riskResult.Scope" class="cust-detail__full-width"><span>经营范围</span><strong class="cust-detail__scope-text">{{ riskResult.Scope }}</strong></div>
              <div v-if="riskResult.EnglishName"><span>英文名</span><strong>{{ riskResult.EnglishName }}</strong></div>
            </div>
          </Card>

          <!-- Contact & Bank -->
          <Card v-if="riskResult.ContactInfo || riskResult.BankInfo" class="cust-detail__card">
            <h3 class="cust-detail__section-title">联系与开票信息</h3>
            <div class="cust-detail__info-grid">
              <div v-if="riskResult.ContactInfo?.Tel"><span>联系电话</span><strong>{{ riskResult.ContactInfo.Tel }}</strong></div>
              <div v-if="riskResult.ContactInfo?.Email"><span>邮箱</span><strong>{{ riskResult.ContactInfo.Email }}</strong></div>
              <div v-if="riskResult.ContactInfo?.WebSiteList?.length" class="cust-detail__full-width"><span>网址</span><strong>{{ riskResult.ContactInfo.WebSiteList.join('、') }}</strong></div>
              <div v-if="riskResult.BankInfo?.Bank"><span>开户行</span><strong>{{ riskResult.BankInfo.Bank }}</strong></div>
              <div v-if="riskResult.BankInfo?.BankAccount"><span>银行账号</span><strong class="vk-font-mono">{{ riskResult.BankInfo.BankAccount }}</strong></div>
            </div>
          </Card>

          <!-- Shareholders -->
          <Card v-if="riskResult.PartnerList?.length" class="cust-detail__card">
            <h3 class="cust-detail__section-title">工商登记股东 (前{{ riskResult.PartnerList.length }}位)</h3>
            <div v-for="(p, i) in riskResult.PartnerList.slice(0,10)" :key="'p'+i" class="cust-detail__risk-item">
              <strong>{{ p.StockName }}</strong>
              <span>{{ p.StockType }} · 持股 {{ p.StockPercent || '-' }} · 认缴 {{ p.ShouldCapi || '-' }}{{ p.SubscribedCapitalUnit || '' }}</span>
            </div>
          </Card>

          <!-- Key Personnel -->
          <Card v-if="riskResult.EmployeeList?.length" class="cust-detail__card">
            <h3 class="cust-detail__section-title">主要人员</h3>
            <div class="cust-detail__tags">
              <span v-for="(e, i) in riskResult.EmployeeList.slice(0,15)" :key="'e'+i" class="vk-tag">{{ e.Name }} · {{ e.Job || '-' }}</span>
            </div>
          </Card>

          <!-- Branches & Investments -->
          <Card v-if="riskResult.BranchList?.length || riskResult.InvestmentList?.length" class="cust-detail__card">
            <h3 class="cust-detail__section-title">分支机构与对外投资</h3>
            <div v-if="riskResult.BranchList?.length"><span class="cust-detail__risk-block-title">分支机构 ({{ riskResult.BranchList.length }})</span>
              <div v-for="(b, i) in riskResult.BranchList.slice(0,5)" :key="'br'+i" class="cust-detail__risk-item">{{ b.Name }} · {{ b.OperName || '-' }} · {{ b.Status || '-' }}</div>
            </div>
            <div v-if="riskResult.InvestmentList?.length" style="margin-top:12px"><span class="cust-detail__risk-block-title">对外投资 ({{ riskResult.InvestmentList.length }})</span>
              <div v-for="(iv, i) in riskResult.InvestmentList.slice(0,5)" :key="'iv'+i" class="cust-detail__risk-item">{{ iv.Name }} · 持股 {{ iv.FundedRatio || '-' }} · {{ iv.Status || '-' }}</div>
            </div>
          </Card>

          <!-- Parent / Group / Controllers -->
          <Card v-if="riskResult.Parent || riskResult.GroupInfo || riskResult.ActualControllerList?.length || riskResult.BeneficiaryList?.length" class="cust-detail__card">
            <h3 class="cust-detail__section-title">控制关系</h3>
            <div class="cust-detail__info-grid">
              <div v-if="riskResult.Parent"><span>总公司</span><strong>{{ riskResult.Parent.Name }}</strong></div>
              <div v-if="riskResult.GroupInfo"><span>所属集团</span><strong>{{ riskResult.GroupInfo.Name }}</strong></div>
              <div v-if="riskResult.ActualControllerList?.length"><span>实际控制人</span><strong>{{ riskResult.ActualControllerList.map((a:any)=>a.Name+'('+a.FinalBenefitPercent+')').join('、') }}</strong></div>
              <div v-if="riskResult.BeneficiaryList?.length"><span>受益所有人</span><strong>{{ riskResult.BeneficiaryList.map((a:any)=>a.Name+'('+a.FinalBenefitPercent+')').join('、') }}</strong></div>
            </div>
          </Card>

          <!-- ====== RISK SECTION ====== -->
          <Card class="cust-detail__card cust-detail__card--risk">
            <h3 class="cust-detail__section-title">风险总览</h3>
            <div class="cust-detail__risk-summary">
              <div class="cust-detail__risk-stat" v-for="r in riskCategories" :key="r.key">
                <span :class="['cust-detail__risk-val', (riskResult[r.key]?.TotalCount || 0) > 0 ? r.cls : 'text-muted']">{{ riskResult[r.key]?.TotalCount || 0 }}</span>
                <span>{{ r.label }}</span>
              </div>
            </div>

            <!-- Each risk detail -->
            <template v-for="r in riskCategories" :key="'rd-'+r.key">
              <div v-if="riskResult[r.key]?.DataList?.length" class="cust-detail__risk-block">
                <h4 class="cust-detail__risk-block-title">{{ r.label }} ({{ riskResult[r.key].TotalCount }}条<span v-if="riskResult[r.key].TotalAmount">，涉案/罚款 {{ riskResult[r.key].TotalAmount }}万元</span>)</h4>
                <div v-for="(item, i) in riskResult[r.key].DataList.slice(0,5)" :key="'ri-'+i" class="cust-detail__risk-item">
                  <template v-for="(v, k) in item" :key="k">
                    <span v-if="v && k !== 'Id' && k !== 'KeyNo' && typeof v === 'string'">{{ k === 'CaseNo' || k === 'DocNo' || k === 'RegisterNo' ? '['+v+']' : v }}</span>
                  </template>
                </div>
              </div>
            </template>
          </Card>

          <!-- Other info -->
          <Card v-if="riskResult.ChangeList?.length || riskResult.TagList?.length || riskResult.ProductList?.length" class="cust-detail__card">
            <h3 class="cust-detail__section-title">其他信息</h3>
            <div v-if="riskResult.ChangeList?.length"><span class="cust-detail__risk-block-title">变更记录 ({{ riskResult.ChangeList.length }})</span>
              <div v-for="(c, i) in riskResult.ChangeList.slice(0,5)" :key="'ch'+i" class="cust-detail__risk-item"><strong>{{ c.ChangeDate }} {{ c.ProjectName }}</strong><span>{{ c.ChangeSubject || '' }}</span></div>
            </div>
            <div v-if="riskResult.TagList?.length" style="margin-top:8px">
              <span v-for="t in riskResult.TagList" :key="t.Name" class="vk-tag" style="margin:2px">{{ t.Name }}</span>
            </div>
            <div v-if="riskResult.ProductList?.length" style="margin-top:8px"><span class="cust-detail__risk-block-title">主营产品</span>
              <span>{{ riskResult.ProductList.map((p:any)=>p.Name).join('、') }}</span>
            </div>
            <div v-if="riskResult.MainProductList?.length" style="margin-top:4px">
              <span v-for="mp in riskResult.MainProductList" :key="mp" class="vk-tag" style="margin:2px">{{ mp }}</span>
            </div>
          </Card>
        </template>

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
const lastScanTime = ref('');

const riskCategories = [
  { key: 'ShiXin', label: '失信被执行', cls: 'text-danger' },
  { key: 'ZhiXing', label: '被执行人', cls: 'text-warn' },
  { key: 'AdminPenalty', label: '行政处罚', cls: 'text-warn' },
  { key: 'Exception', label: '经营异常', cls: 'text-warn' },
  { key: 'Sumptuary', label: '限制高消费', cls: 'text-danger' },
  { key: 'EquityFreeze', label: '股权冻结', cls: 'text-warn' },
  { key: 'Bankruptcy', label: '破产重整', cls: 'text-warn' },
  { key: 'TaxIllegal', label: '税收违法', cls: 'text-warn' },
  { key: 'EnvPunishment', label: '环保处罚', cls: 'text-warn' },
  { key: 'SeriousIllegal', label: '严重违法', cls: 'text-danger' },
  { key: 'TaxOweNotice', label: '欠税公告', cls: 'text-warn' },
  { key: 'JudicialSale', label: '司法拍卖', cls: 'text-warn' },
  { key: 'ChattelMortgage', label: '动产抵押', cls: 'text-warn' },
  { key: 'EquityPledge', label: '股权出质', cls: 'text-warn' },
  { key: 'TaxAbnormal', label: '税务非正常户', cls: 'text-warn' },
  { key: 'TaxHurry', label: '税务催缴', cls: 'text-warn' },
  { key: 'TaxReminder', label: '税务催报', cls: 'text-warn' },
  { key: 'PublicSecurityNotice', label: '公安通告', cls: 'text-danger' },
];

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
      lastScanTime.value = res.data.scanTime ? formatScanTime(res.data.scanTime) : formatScanTime(new Date().toISOString());
    } else {
      alert(res.data?.message || '排查失败，请稍后重试');
    }
  } catch { alert('请求失败'); }
  finally { scanning.value = false; }
}

function formatScanTime(t: string) {
  if (!t) return '';
  return t.slice(0, 16).replace('T', ' ');
}

onMounted(async () => {
  const id = route.params.id as string;
  const r1 = await api.get<any>('/customers/' + id);
  if (r1.data) {
    customer.value = r1.data;
    // Load cached risk scan result
    if (r1.data.extInfo?.riskResult) {
      riskResult.value = r1.data.extInfo.riskResult;
      lastScanTime.value = formatScanTime(r1.data.extInfo.riskScanTime || '');
    }
  }
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
.cust-detail__scan-time { font-size: var(--fz-xs); color: var(--text-faint); margin-left: 12px; }

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
.cust-detail__scope-text { font-size: var(--fz-sm); line-height: 1.6; max-height: 120px; overflow-y: auto; display: block; }

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
