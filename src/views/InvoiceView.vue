<template>
  <div class="inv-page">
    <Sidebar />
    <main class="inv-page__main">
      <TopBar title="发票对账" description="管理发票、跟踪收款">
        <template #actions><Button variant="primary" @click="openCreate"><Plus :size="16" class="mr-2" /> 新建发票</Button></template>
      </TopBar>

      <div class="qc-view__mini">
        <div class="qc-view__mini-card"><span>总金额</span><strong>¥{{ fmt(stats.totalAmount) }}</strong></div>
        <div class="qc-view__mini-card"><span>已收款</span><strong class="text-success">¥{{ fmt(stats.paidAmount) }}</strong></div>
        <div class="qc-view__mini-card"><span>逾期</span><strong class="text-danger">¥{{ fmt(stats.overdueAmount) }}</strong></div>
        <div class="qc-view__mini-card"><span>待处理</span><strong>{{ stats.pendingCount }}</strong></div>
      </div>

      <div class="apv-view__tabs">
        <button v-for="t in tabs" :key="t.value" :class="['prod-view__tab',{'prod-view__tab--active':activeTab===t.value}]" @click="activeTab=t.value;fetchItems()">{{ t.label }}</button>
      </div>

      <Card class="apv-view__table">
        <table class="vk-table">
          <thead><tr><th>发票号</th><th>客户</th><th>金额</th><th>税额</th><th>总额</th><th>状态</th><th>日期</th><th>到期</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="inv in items" :key="inv.id" :class="{ 'inv-row--overdue': inv.status === 'overdue' }">
              <td class="vk-font-mono vk-text-sm">{{ inv.invoiceNo }}</td>
              <td class="inv-view__name">{{ inv.customerName }}</td>
              <td class="vk-font-mono">¥{{ fmt(inv.amount) }}</td>
              <td class="vk-font-mono">¥{{ fmt(inv.taxAmount) }}</td>
              <td class="vk-font-mono fw-bold">¥{{ fmt(inv.totalAmount) }}</td>
              <td><Badge :variant="invStatusV(inv.status)" size="sm">{{ invStatusL(inv.status) }}</Badge></td>
              <td class="vk-text-sm">{{ inv.invoiceDate?.slice(0,10) }}</td>
              <td class="vk-text-sm">{{ inv.dueDate?.slice(0,10) || '-' }}</td>
              <td>
                <div class="inv-view__actions">
                  <button v-if="inv.status==='draft'" class="bom-view__action" @click="updateStatus(inv,'sent')">发送</button>
                  <button v-if="inv.status==='sent'" class="bom-view__action" @click="updateStatus(inv,'paid')">收款</button>
                  <button class="bom-view__action bom-view__action--danger" @click="api.delete('/invoices/'+inv.id).then(fetchItems)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </Card>
    </main>
    <MobileNav />

    <div v-if="showDialog" class="vk-overlay" @click.self="showDialog=false">
      <Card class="vk-dialog"><h3 class="vk-dialog__title">新建发票</h3>
        <div class="vk-dialog__form">
          <Input v-model="form.customerName" label="客户名称 *" />
          <div class="vk-dialog__form-row"><Input v-model.number="form.amount" type="number" label="金额(不含税¥)" /><Input v-model="form.dueDate" label="到期日" placeholder="2026-07-15" /></div>
          <Input v-model="form.note" label="备注" />
          <p class="vk-text-sm vk-text-muted">税额自动按13%计算: ¥{{ (form.amount * 0.13).toFixed(2) }}，总额: ¥{{ (form.amount * 1.13).toFixed(2) }}</p>
        </div>
        <div class="vk-dialog__actions"><Button variant="ghost" @click="showDialog=false">取消</Button><Button variant="primary" :disabled="!form.customerName" @click="saveItem">保存</Button></div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref,reactive,onMounted } from 'vue';import { Plus } from 'lucide-vue-next';
import Sidebar from '@/components/layout/Sidebar.vue';import TopBar from '@/components/layout/TopBar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';import Card from '@/components/base/Card.vue';
import Button from '@/components/base/Button.vue';import Input from '@/components/base/Input.vue';
import Badge from '@/components/base/Badge.vue';import { api } from '@/api';
interface Inv { id:string;invoiceNo:string;customerName:string;amount:number;taxAmount:number;totalAmount:number;status:string;invoiceDate:string;dueDate:string; }
const items=ref<Inv[]>([]);const loading=ref(true);const activeTab=ref('');const showDialog=ref(false);
const stats=ref({totalAmount:0,paidAmount:0,overdueAmount:0,totalCount:0,paidCount:0,pendingCount:0});
const form=reactive({customerName:'',amount:0,dueDate:'',note:''});
const tabs=[{value:'',label:'全部'},{value:'draft',label:'草稿'},{value:'sent',label:'已发送'},{value:'paid',label:'已收款'},{value:'overdue',label:'逾期'}];
function invStatusV(s:string){const m:Record<string,any>={draft:'default',sent:'info',paid:'success',overdue:'danger',cancelled:'danger'};return m[s]||'default'}
function invStatusL(s:string){const m:Record<string,string>={draft:'草稿',sent:'已发送',paid:'已收款',overdue:'逾期',cancelled:'已取消'};return m[s]||s}
function fmt(v:number){return new Intl.NumberFormat('zh-CN').format(Math.round(v||0))}
async function fetchItems(){const q=activeTab.value?'?status='+activeTab.value:'';const r=await api.get<Inv[]>('/invoices'+q);if(r.data)items.value=r.data;loading.value=false;const s=await api.get<any>('/invoices/stats');if(s.data)stats.value=s.data}
onMounted(fetchItems);
function openCreate(){Object.assign(form,{customerName:'',amount:0,dueDate:'',note:''});showDialog.value=true}
async function saveItem(){await api.post('/invoices',form);showDialog.value=false;fetchItems()}
async function updateStatus(inv:Inv,s:string){await api.put('/invoices/'+inv.id,{status:s});fetchItems()}
</script>

<style scoped>
.inv-page{display:block;min-height:100vh}.inv-page__main{padding:24px 32px 120px;max-width:1000px;margin:0 auto}
.qc-view__mini{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:14px}
.qc-view__mini-card{display:flex;flex-direction:column;gap:4px;padding:12px 16px;background:var(--surface);border:1px solid var(--border);border-radius:10px;font-size:var(--fz-sm);color:var(--text-muted)}
.qc-view__mini-card strong{font-size:22px;font-family:var(--font-mono);color:var(--text)}
.apv-view__tabs{display:flex;gap:4px;margin-bottom:14px}
.prod-view__tab{padding:6px 14px;border-radius:var(--r-pill);border:1px solid var(--border);background:var(--surface);color:var(--text-muted);font-size:var(--fz-sm);cursor:pointer}
.prod-view__tab--active{background:var(--brand-light);border-color:var(--brand);color:var(--brand)}
.apv-view__table{padding:0;overflow:hidden}.inv-view__name{font-weight:var(--fw-semibold)}.inv-view__actions{display:flex;gap:6px}
.bom-view__action{padding:3px 8px;border-radius:4px;border:1px solid var(--border);background:transparent;color:var(--text-muted);font-size:var(--fz-xs);cursor:pointer;font-family:inherit}
.bom-view__action:hover{border-color:var(--brand);color:var(--brand)}.bom-view__action--danger:hover{border-color:var(--danger);color:var(--danger)}
.mr-2{margin-right:8px}.fw-bold{font-weight:var(--fw-bold)}.text-success{color:var(--success)!important}.text-danger{color:var(--danger)!important}
.inv-row--overdue{background:#FFF5F5}
.vk-text-sm{font-size:var(--fz-sm)}.vk-text-muted{color:var(--text-muted)}.vk-font-mono{font-family:var(--font-mono)}
.vk-table{width:100%;border-collapse:collapse}.vk-table th{text-align:left;padding:10px 12px;font-size:var(--fz-sm);font-weight:var(--fw-semibold);color:var(--text-muted);border-bottom:1px solid var(--border)}
.vk-table td{padding:10px 12px;font-size:var(--fz-body);border-bottom:1px solid var(--border)}.vk-table tr:last-child td{border-bottom:none}.vk-table tr:hover td{background:var(--surface-sunken)}
.vk-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.4);display:grid;place-items:center;z-index:100}
.vk-dialog{width:500px;max-width:90vw;padding:24px}.vk-dialog__title{margin:0 0 20px;font-size:var(--fz-h2);font-weight:var(--fw-semibold)}
.vk-dialog__form{display:flex;flex-direction:column;gap:12px;margin-bottom:20px}.vk-dialog__form-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.vk-dialog__actions{display:flex;justify-content:flex-end;gap:8px}
@media(max-width:768px){.inv-page__main{padding:16px 16px 100px}.qc-view__mini{grid-template-columns:repeat(2,1fr)}}
</style>
