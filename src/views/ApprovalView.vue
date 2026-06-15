<template>
  <div class="apv-view">
    <Sidebar />
    <main class="apv-view__main">
      <TopBar title="审批中心" description="报价审批 / 订单审批">
        <template #actions>
          <Button variant="primary" @click="showCreate=true"><Plus :size="16" class="mr-2" /> 发起审批</Button>
        </template>
      </TopBar>

      <div class="apv-view__tabs">
        <button v-for="t in tabs" :key="t.value" :class="['prod-view__tab',{'prod-view__tab--active':activeTab===t.value}]" @click="activeTab=t.value;fetchItems()">{{ t.label }}</button>
      </div>

      <Card class="apv-view__table">
        <div v-if="loading" class="admin-view__loading"><div class="vk-skeleton-row" v-for="i in 3" :key="i"></div></div>
        <table v-else class="vk-table">
          <thead><tr><th>审批号</th><th>事项</th><th>类型</th><th>申请人</th><th>审批人</th><th>状态</th><th>时间</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="a in items" :key="a.id">
              <td class="vk-font-mono vk-text-sm">{{ a.approvalNo }}</td>
              <td class="inv-view__name">{{ a.entityTitle }}</td>
              <td><Badge :variant="typeV(a.entityType)" size="sm">{{ typeL(a.entityType) }}</Badge></td>
              <td class="vk-text-sm">{{ a.applicant || '-' }}</td>
              <td class="vk-text-sm">{{ a.approver || '-' }}</td>
              <td><Badge :variant="statusV(a.status)" size="sm">{{ statusL(a.status) }}</Badge></td>
              <td class="vk-text-sm">{{ a.createdAt?.slice(0,10) || '-' }}</td>
              <td>
                <div class="inv-view__actions">
                  <button v-if="a.status==='pending'" class="bom-view__action" @click="handleApproval(a,'approved')">通过</button>
                  <button v-if="a.status==='pending'" class="bom-view__action bom-view__action--danger" @click="handleApproval(a,'rejected')">驳回</button>
                  <button class="bom-view__action bom-view__action--danger" @click="api.delete('/approvals/'+a.id).then(fetchItems)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </Card>

      <!-- Audit logs -->
      <Card class="apv-view__card mt-4">
        <h3 class="vk-dialog__title" style="margin-bottom:6px">操作日志 (最近) <span class="vk-text-sm vk-text-muted" style="font-weight:normal">— 审计追踪</span></h3>
        <div v-for="l in logs" :key="l.id" class="apv-view__log-item">
          <span class="apv-view__log-time">{{ l.createdAt?.slice(0,16) || '-' }}</span>
          <Badge :variant="'default'" size="sm">{{ l.action }}</Badge>
          <span class="vk-text-sm">{{ l.userName }}</span>
          <span class="vk-text-sm vk-text-muted">{{ l.detail }}</span>
        </div>
      </Card>
    </main>
    <MobileNav />

    <!-- Create dialog -->
    <div v-if="showCreate" class="vk-overlay" @click.self="showCreate=false">
      <Card class="vk-dialog"><h3 class="vk-dialog__title">发起审批</h3>
        <div class="vk-dialog__form">
          <Input v-model="form.entityTitle" label="事项标题 *" placeholder="如：报价单 QT-20260615-012 审批" />
          <div class="vk-dialog__form-row">
            <div class="post-view__select"><label class="vk-input__label">类型</label><SelectMenu v-model="form.entityType" :options="[{value:'quote',label:'报价'},{value:'purchase',label:'采购'},{value:'production',label:'生产'},{value:'refund',label:'退款'}]" /></div>
            <Input v-model="form.applicant" label="申请人" />
          </div>
          <Input v-model="form.approver" label="审批人" placeholder="谁审批" />
          <Input v-model="form.comment" label="备注" />
        </div>
        <div class="vk-dialog__actions"><Button variant="ghost" @click="showCreate=false">取消</Button><Button variant="primary" :disabled="!form.entityTitle" @click="saveApproval">提交</Button></div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref,reactive,onMounted } from 'vue';import { Plus } from 'lucide-vue-next';
import Sidebar from '@/components/layout/Sidebar.vue';import TopBar from '@/components/layout/TopBar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';import Card from '@/components/base/Card.vue';
import Button from '@/components/base/Button.vue';import Input from '@/components/base/Input.vue';
import Badge from '@/components/base/Badge.vue';import SelectMenu from '@/components/base/SelectMenu.vue';import { api } from '@/api';
interface ApItem { id:string;approvalNo:string;entityType:string;entityTitle:string;applicant:string;approver:string;status:string;comment:string;createdAt:string; }
interface LogItem { id:string;userName:string;action:string;detail:string;createdAt:string; }
const items=ref<ApItem[]>([]);const logs=ref<LogItem[]>([]);const loading=ref(true);const activeTab=ref('');const showCreate=ref(false);
const form=reactive({entityTitle:'',entityType:'quote',applicant:'',approver:'',comment:''});
const tabs=[{value:'',label:'全部'},{value:'pending',label:'待审批'},{value:'approved',label:'已通过'},{value:'rejected',label:'已驳回'}];
function typeV(t:string){const m:Record<string,any>={quote:'info',purchase:'warn',production:'default',refund:'danger'};return m[t]||'default'}
function typeL(t:string){const m:Record<string,string>={quote:'报价',purchase:'采购',production:'生产',refund:'退款'};return m[t]||t}
function statusV(s:string){const m:Record<string,any>={pending:'warn',approved:'success',rejected:'danger'};return m[s]||'default'}
function statusL(s:string){const m:Record<string,string>={pending:'待审批',approved:'已通过',rejected:'已驳回'};return m[s]||s}
async function fetchItems(){const q=activeTab.value?'?status='+activeTab.value:'';const r=await api.get<ApItem[]>('/approvals'+q);if(r.data)items.value=r.data;loading.value=false}
async function fetchLogs(){const r=await api.get<LogItem[]>('/audit-logs?limit=30');if(r.data)logs.value=r.data}
onMounted(()=>{fetchItems();fetchLogs()});
async function saveApproval(){await api.post('/approvals',form);showCreate.value=false;fetchItems();fetchLogs()}
async function handleApproval(a:ApItem,status:string){await api.put('/approvals/'+a.id,{status});fetchItems();fetchLogs()}
</script>

<style scoped>
.apv-view{display:block;min-height:100vh}.apv-view__main{padding:24px 32px 120px;max-width:960px;margin:0 auto}
.apv-view__tabs{display:flex;gap:4px;margin-bottom:14px}
.prod-view__tab{padding:6px 14px;border-radius:var(--r-pill);border:1px solid var(--border);background:var(--surface);color:var(--text-muted);font-size:var(--fz-sm);cursor:pointer}
.prod-view__tab--active{background:var(--brand-light);border-color:var(--brand);color:var(--brand)}
.apv-view__table{padding:0;overflow:hidden}.apv-view__card{padding:20px;margin-top:18px}
.apv-view__log-item{display:flex;align-items:center;gap:10px;padding:6px 0;border-bottom:1px solid var(--border);font-size:var(--fz-sm)}
.apv-view__log-time{font-family:var(--font-mono);font-size:var(--fz-xs);color:var(--text-faint);min-width:130px}
.inv-view__name{font-weight:var(--fw-semibold)}.inv-view__actions{display:flex;gap:6px}
.bom-view__action{padding:3px 8px;border-radius:4px;border:1px solid var(--border);background:transparent;color:var(--text-muted);font-size:var(--fz-xs);cursor:pointer;font-family:inherit}
.bom-view__action:hover{border-color:var(--brand);color:var(--brand)}.bom-view__action--danger:hover{border-color:var(--danger);color:var(--danger)}
.mr-2{margin-right:8px}.mt-4{margin-top:16px}
.vk-text-sm{font-size:var(--fz-sm)}.vk-text-xs{font-size:var(--fz-xs)}.vk-text-muted{color:var(--text-muted)}.vk-font-mono{font-family:var(--font-mono)}
.admin-view__loading{padding:20px;display:flex;flex-direction:column;gap:12px}
.vk-skeleton-row{height:40px;background:var(--surface-sunken);border-radius:var(--r-input);animation:pulse 1.5s infinite}@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
.vk-table{width:100%;border-collapse:collapse}.vk-table th{text-align:left;padding:10px 12px;font-size:var(--fz-sm);font-weight:var(--fw-semibold);color:var(--text-muted);border-bottom:1px solid var(--border)}
.vk-table td{padding:10px 12px;font-size:var(--fz-body);border-bottom:1px solid var(--border)}.vk-table tr:last-child td{border-bottom:none}
.vk-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.4);display:grid;place-items:center;z-index:100}
.vk-dialog{width:500px;max-width:90vw;padding:24px}.vk-dialog__title{margin:0 0 20px;font-size:var(--fz-h2);font-weight:var(--fw-semibold)}
.vk-dialog__form{display:flex;flex-direction:column;gap:12px;margin-bottom:20px}.vk-dialog__form-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.vk-dialog__actions{display:flex;justify-content:flex-end;gap:8px}.vk-input__label{font-size:var(--fz-sm);font-weight:var(--fw-medium);color:var(--text);margin-bottom:6px;display:block}.post-view__select{display:flex;flex-direction:column;gap:6px}
@media(max-width:768px){.apv-view__main{padding:16px 16px 100px}.vk-dialog__form-row{grid-template-columns:1fr}}
</style>
