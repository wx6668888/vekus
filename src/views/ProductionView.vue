<template>
  <div class="prod-view">
    <Sidebar />
    <main class="prod-view__main">
      <TopBar title="生产工单" description="工单排产、工序跟踪和报工">
        <template #actions>
          <Button variant="primary" @click="openCreate"><Plus :size="16" class="mr-2" /> 新建工单</Button>
        </template>
      </TopBar>

      <!-- Filter tabs -->
      <div class="prod-view__tabs">
        <button v-for="t in tabs" :key="t.value" :class="['prod-view__tab',{'prod-view__tab--active':activeTab===t.value}]" @click="activeTab=t.value;fetchOrders()">{{ t.label }}</button>
      </div>

      <Card class="prod-view__table">
        <div v-if="loading"><div class="vk-skeleton-row" v-for="i in 3" :key="i"></div></div>
        <table v-else class="vk-table">
          <thead><tr><th>工单号</th><th>产品</th><th>数量</th><th>状态</th><th>进度</th><th>车间</th><th>负责人</th><th>计划交期</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="o in orders" :key="o.id">
              <td class="vk-font-mono vk-text-sm">{{ o.orderNo }}</td>
              <td class="inv-view__name">{{ o.productName }}</td>
              <td class="vk-font-mono">{{ o.quantity }}</td>
              <td><Badge :variant="statusVariant(o.status)" size="sm">{{ statusLabel(o.status) }}</Badge></td>
              <td>
                <div class="prod-view__progress"><div class="prod-view__progress-bar" :style="{width:o.progress+'%'}"></div><span class="vk-text-xs">{{ o.progress }}%</span></div>
              </td>
              <td class="vk-text-sm">{{ o.workshop || '-' }}</td>
              <td class="vk-text-sm">{{ o.assignedTo || '-' }}</td>
              <td class="vk-text-sm">{{ o.plannedEnd || '-' }}</td>
              <td>
                <div class="inv-view__actions">
                  <button class="bom-view__action" @click="updateStatus(o,'running')" v-if="o.status==='draft'">开工</button>
                  <button class="bom-view__action" @click="openProgress(o)" v-if="o.status==='running'">报工</button>
                  <button class="bom-view__action" @click="updateStatus(o,'done')" v-if="o.status==='running'">完工</button>
                  <button class="bom-view__action bom-view__action--danger" @click="api.delete('/production/'+o.id).then(fetchOrders)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </Card>
    </main>
    <MobileNav />

    <!-- Create Dialog -->
    <div v-if="showDialog" class="vk-overlay" @click.self="showDialog=false">
      <Card class="vk-dialog"><h3 class="vk-dialog__title">新建工单</h3>
        <div class="vk-dialog__form">
          <Input v-model="form.productName" label="产品名称 *" />
          <div class="vk-dialog__form-row"><Input v-model.number="form.quantity" type="number" label="数量" /><Input v-model="form.workshop" label="车间" /></div>
          <div class="vk-dialog__form-row"><Input v-model="form.plannedStart" label="计划开始" placeholder="2026-06-20" /><Input v-model="form.plannedEnd" label="计划完成" placeholder="2026-06-25" /></div>
          <div class="vk-dialog__form-row"><Input v-model="form.assignedTo" label="负责人" />
            <div class="post-view__select"><label class="vk-input__label">优先级</label><SelectMenu v-model="form.priority" :options="[{value:'high',label:'高'},{value:'normal',label:'中'},{value:'low',label:'低'}]" /></div>
          </div>
          <Input v-model="form.note" label="备注" />
        </div>
        <div class="vk-dialog__actions"><Button variant="ghost" @click="showDialog=false">取消</Button><Button variant="primary" :disabled="!form.productName" @click="saveOrder">保存</Button></div>
      </Card>
    </div>

    <!-- Progress Dialog -->
    <div v-if="progressItem" class="vk-overlay" @click.self="progressItem=null">
      <Card class="vk-dialog"><h3 class="vk-dialog__title">报工 — {{ progressItem.productName }}</h3>
        <p class="vk-text-sm vk-text-muted mb-4">当前进度: {{ progressItem.progress }}%</p>
        <Input v-model.number="progressVal" type="range" label="进度" :min="progressItem.progress" :max="100" />
        <div class="vk-dialog__actions mt-4"><Button variant="ghost" @click="progressItem=null">取消</Button><Button variant="primary" @click="doProgress">确认</Button></div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref,reactive,onMounted } from 'vue';
import { Plus } from 'lucide-vue-next';
import Sidebar from '@/components/layout/Sidebar.vue';import TopBar from '@/components/layout/TopBar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';import Card from '@/components/base/Card.vue';
import Button from '@/components/base/Button.vue';import Input from '@/components/base/Input.vue';
import Badge from '@/components/base/Badge.vue';import SelectMenu from '@/components/base/SelectMenu.vue';
import { api } from '@/api';
interface ProdOrder { id:string;orderNo:string;productName:string;quantity:number;status:string;priority:string;plannedStart:string;plannedEnd:string;workshop:string;assignedTo:string;progress:number;note:string; }
const orders=ref<ProdOrder[]>([]);const loading=ref(true);const activeTab=ref('all');const showDialog=ref(false);
const progressItem=ref<ProdOrder|null>(null);const progressVal=ref(0);
const tabs=[{value:'all',label:'全部'},{value:'draft',label:'草稿'},{value:'running',label:'进行中'},{value:'done',label:'已完工'}];
const form=reactive({productName:'',quantity:1,priority:'normal',plannedStart:'',plannedEnd:'',workshop:'',assignedTo:'',note:''});
function statusVariant(s:string){const m:Record<string,any>={draft:'default',scheduled:'info',running:'warn',done:'success',cancelled:'danger'};return m[s]||'default'}
function statusLabel(s:string){const m:Record<string,string>={draft:'草稿',scheduled:'已排产',running:'进行中',done:'已完工',cancelled:'已取消'};return m[s]||s}
async function fetchOrders(){const q=activeTab.value!=='all'?'?status='+activeTab.value:'';const r=await api.get<ProdOrder[]>('/production'+q);if(r.data)orders.value=r.data;loading.value=false}
onMounted(fetchOrders);
function openCreate(){Object.assign(form,{productName:'',quantity:1,priority:'normal',plannedStart:'',plannedEnd:'',workshop:'',assignedTo:'',note:''});showDialog.value=true}
async function saveOrder(){await api.post('/production',form);showDialog.value=false;fetchOrders()}
async function updateStatus(o:ProdOrder,s:string){await api.put('/production/'+o.id,{status:s});fetchOrders()}
function openProgress(o:ProdOrder){progressItem.value=o;progressVal.value=o.progress}
async function doProgress(){if(!progressItem.value)return;await api.put('/production/'+progressItem.value.id,{progress:progressVal.value});progressItem.value=null;fetchOrders()}
</script>

<style scoped>
.prod-view{display:block;min-height:100vh}.prod-view__main{padding:24px 32px 120px;max-width:1100px;margin:0 auto}
.prod-view__tabs{display:flex;gap:4px;margin-bottom:14px}
.prod-view__tab{padding:6px 14px;border-radius:var(--r-pill);border:1px solid var(--border);background:var(--surface);color:var(--text-muted);font-size:var(--fz-sm);cursor:pointer}
.prod-view__tab--active{background:var(--brand-light);border-color:var(--brand);color:var(--brand)}
.prod-view__table{padding:0;overflow:hidden}
.prod-view__progress{display:flex;align-items:center;gap:6px}
.prod-view__progress-bar{height:6px;background:var(--brand);border-radius:3px;min-width:4px;max-width:80px;transition:width .3s}
.inv-view__name{font-weight:var(--fw-semibold)}.inv-view__actions{display:flex;gap:6px}
.bom-view__action{padding:3px 8px;border-radius:4px;border:1px solid var(--border);background:transparent;color:var(--text-muted);font-size:var(--fz-xs);cursor:pointer;font-family:inherit}
.bom-view__action:hover{border-color:var(--brand);color:var(--brand)}.bom-view__action--danger:hover{border-color:var(--danger);color:var(--danger)}
.mr-2{margin-right:8px}.mt-4{margin-top:16px}.mb-4{margin-bottom:16px}
.vk-text-sm{font-size:var(--fz-sm)}.vk-text-xs{font-size:var(--fz-xs)}.vk-text-muted{color:var(--text-muted)}.vk-font-mono{font-family:var(--font-mono)}
.vk-table{width:100%;border-collapse:collapse}.vk-table th{text-align:left;padding:10px 12px;font-size:var(--fz-sm);font-weight:var(--fw-semibold);color:var(--text-muted);border-bottom:1px solid var(--border)}
.vk-table td{padding:10px 12px;font-size:var(--fz-body);border-bottom:1px solid var(--border)}.vk-table tr:last-child td{border-bottom:none}
.vk-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.4);display:grid;place-items:center;z-index:100}
.vk-dialog{width:500px;max-width:90vw;padding:24px}.vk-dialog__title{margin:0 0 20px;font-size:var(--fz-h2);font-weight:var(--fw-semibold)}
.vk-dialog__form{display:flex;flex-direction:column;gap:12px;margin-bottom:20px}.vk-dialog__form-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.vk-dialog__actions{display:flex;justify-content:flex-end;gap:8px}
.vk-input__label{font-size:var(--fz-sm);font-weight:var(--fw-medium);color:var(--text);margin-bottom:6px;display:block}.post-view__select{display:flex;flex-direction:column;gap:6px}
.vk-skeleton-row{height:40px;background:var(--surface-sunken);border-radius:var(--r-input);animation:pulse 1.5s infinite}@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
@media(max-width:768px){.prod-view__main{padding:16px 16px 100px}.vk-dialog__form-row{grid-template-columns:1fr}}
</style>
