<template>
  <div class="pur-view">
    <Sidebar />
    <main class="pur-view__main">
      <TopBar title="采购管理" description="供应商管理 / 采购订单 / 收货入库">
        <template #actions>
          <Button variant="secondary" size="sm" @click="showSupDialog=true" class="mr-2"><Plus :size="14" class="mr-1" /> 供应商</Button>
          <Button variant="primary" @click="openCreate"><Plus :size="16" class="mr-2" /> 采购订单</Button>
        </template>
      </TopBar>

      <div class="qc-view__tabs">
        <button v-for="t in statusTabs" :key="t.value" :class="['prod-view__tab',{'prod-view__tab--active':activeStatus===t.value}]" @click="activeStatus=t.value;fetchOrders()">{{ t.label }}</button>
      </div>

      <Card class="qc-view__table">
        <div v-if="loading" class="admin-view__loading"><div class="vk-skeleton-row" v-for="i in 3" :key="i"></div></div>
        <table v-else class="vk-table">
          <thead><tr><th>订单号</th><th>供应商</th><th>物料</th><th>数量</th><th>单价</th><th>金额</th><th>状态</th><th>日期</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="po in orders" :key="po.id">
              <td class="vk-font-mono vk-text-sm">{{ po.orderNo }}</td>
              <td class="inv-view__name">{{ po.supplierName || '-' }}</td>
              <td>{{ po.itemName }}<span v-if="po.spec" class="vk-text-xs vk-text-faint ml-2">{{ po.spec }}</span></td>
              <td class="vk-font-mono">{{ po.quantity }} {{ po.unit }}</td>
              <td class="vk-font-mono">¥{{ po.price }}</td>
              <td class="vk-font-mono">¥{{ formatNum(po.totalAmount) }}</td>
              <td><Badge :variant="poStatusV(po.status)" size="sm">{{ poStatusL(po.status) }}</Badge></td>
              <td class="vk-text-sm">{{ po.orderDate || '-' }}</td>
              <td>
                <div class="inv-view__actions">
                  <button class="bom-view__action" @click="updateStatus(po,'sent')" v-if="po.status==='draft'">发送</button>
                  <button class="bom-view__action" @click="updateStatus(po,'received')" v-if="po.status==='sent'">收货</button>
                  <button class="bom-view__action bom-view__action--danger" @click="api.delete('/purchases/'+po.id).then(fetchOrders)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </Card>
    </main>
    <MobileNav />

    <!-- PO Create Dialog -->
    <div v-if="showDialog" class="vk-overlay" @click.self="showDialog=false">
      <Card class="vk-dialog"><h3 class="vk-dialog__title">新建采购订单</h3>
        <div class="vk-dialog__form">
          <div class="vk-dialog__form-row"><Input v-model="form.itemName" label="物料名称 *" />
            <div class="post-view__select"><label class="vk-input__label">供应商</label><SelectMenu v-model="form.supplierName" :options="supOptions" /></div></div>
          <div class="vk-dialog__form-row"><Input v-model="form.spec" label="规格" /><Input v-model.number="form.quantity" type="number" label="数量" /></div>
          <div class="vk-dialog__form-row"><Input v-model.number="form.price" type="number" label="单价(¥)" /><Input v-model="form.unit" label="单位" /></div>
          <Input v-model="form.orderDate" label="订单日期" placeholder="2026-06-15" />
          <Input v-model="form.receiveDate" label="预计到货" placeholder="2026-06-25" />
          <Input v-model="form.note" label="备注" />
        </div>
        <div class="vk-dialog__actions"><Button variant="ghost" @click="showDialog=false">取消</Button><Button variant="primary" :disabled="!form.itemName" @click="saveOrder">保存</Button></div>
      </Card>
    </div>

    <!-- Supplier Dialog -->
    <div v-if="showSupDialog" class="vk-overlay" @click.self="showSupDialog=false">
      <Card class="vk-dialog vk-dialog--wide"><h3 class="vk-dialog__title">供应商管理</h3>
        <div class="vk-dialog__form">
          <div class="vk-dialog__form-row"><Input v-model="supForm.name" label="供应商名称 *" /><Input v-model="supForm.contactName" label="联系人" /></div>
          <div class="vk-dialog__form-row"><Input v-model="supForm.phone" label="电话" /><Input v-model="supForm.email" label="邮箱" /></div>
          <div class="vk-dialog__form-row"><Input v-model="supForm.address" label="地址" />
            <div class="post-view__select"><label class="vk-input__label">类别</label><SelectMenu v-model="supForm.category" :options="[{value:'材料',label:'材料'},{value:'外协',label:'外协'},{value:'设备',label:'设备'},{value:'其他',label:'其他'}]" /></div></div>
        </div>
        <div class="vk-dialog__actions"><Button variant="ghost" @click="showSupDialog=false">关闭</Button><Button variant="primary" :disabled="!supForm.name" @click="saveSupplier">添加供应商</Button></div>
        <!-- Supplier list -->
        <div style="margin-top:16px;max-height:200px;overflow-y:auto">
          <div v-for="s in suppliers" :key="s.id" class="bom-view__row" style="justify-content:space-between">
            <span><strong>{{ s.name }}</strong> <span class="vk-text-sm vk-text-muted">{{ s.contactName }} {{ s.phone }}</span></span>
            <button class="bom-view__action bom-view__action--danger" @click="api.delete('/suppliers/'+s.id).then(fetchSuppliers)">删除</button>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref,reactive,computed,onMounted } from 'vue';import { Plus } from 'lucide-vue-next';
import Sidebar from '@/components/layout/Sidebar.vue';import TopBar from '@/components/layout/TopBar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';import Card from '@/components/base/Card.vue';
import Button from '@/components/base/Button.vue';import Input from '@/components/base/Input.vue';
import Badge from '@/components/base/Badge.vue';import SelectMenu from '@/components/base/SelectMenu.vue';import { api } from '@/api';
interface PO { id:string;orderNo:string;supplierName:string;itemName:string;spec:string;quantity:number;unit:string;price:number;totalAmount:number;status:string;orderDate:string;receiveDate:string; }
interface Sup { id:string;name:string;contactName:string;phone:string;email:string;address:string;category:string; }
const orders=ref<PO[]>([]);const suppliers=ref<Sup[]>([]);const loading=ref(true);const activeStatus=ref('');const showDialog=ref(false);const showSupDialog=ref(false);
const form=reactive({itemName:'',supplierName:'',spec:'',quantity:1,unit:'件',price:0,orderDate:'',receiveDate:'',note:''});
const supForm=reactive({name:'',contactName:'',phone:'',email:'',address:'',category:'材料'});
const statusTabs=[{value:'',label:'全部'},{value:'draft',label:'草稿'},{value:'sent',label:'已发送'},{value:'received',label:'已收货'},{value:'done',label:'已完成'}];
const supOptions=computed(()=>suppliers.value.map(s=>({value:s.name,label:s.name})));
function poStatusV(s:string){const m:Record<string,any>={draft:'default',sent:'info',received:'warn',done:'success',cancelled:'danger'};return m[s]||'default'}
function poStatusL(s:string){const m:Record<string,string>={draft:'草稿',sent:'已发送',received:'已收货',done:'已完成',cancelled:'已取消'};return m[s]||s}
function formatNum(v:number){return new Intl.NumberFormat('zh-CN').format(Math.round(v))}
async function fetchOrders(){const q=activeStatus.value?'?status='+activeStatus.value:'';const r=await api.get<PO[]>('/purchases'+q);if(r.data)orders.value=r.data;loading.value=false}
async function fetchSuppliers(){const r=await api.get<Sup[]>('/suppliers');if(r.data)suppliers.value=r.data}
onMounted(()=>{fetchOrders();fetchSuppliers()});
function openCreate(){Object.assign(form,{itemName:'',supplierName:'',spec:'',quantity:1,unit:'件',price:0,orderDate:'',receiveDate:'',note:''});showDialog.value=true}
async function saveOrder(){await api.post('/purchases',form);showDialog.value=false;fetchOrders()}
async function saveSupplier(){await api.post('/suppliers',{...supForm});Object.assign(supForm,{name:'',contactName:'',phone:'',email:'',address:'',category:'材料'});fetchSuppliers()}
async function updateStatus(o:PO,s:string){await api.put('/purchases/'+o.id,{status:s});fetchOrders()}
</script>

<style scoped>
.pur-view{display:block;min-height:100vh}.pur-view__main{padding:24px 32px 120px;max-width:1100px;margin:0 auto}
.qc-view__tabs{display:flex;gap:4px;margin-bottom:14px}
.prod-view__tab{padding:6px 14px;border-radius:var(--r-pill);border:1px solid var(--border);background:var(--surface);color:var(--text-muted);font-size:var(--fz-sm);cursor:pointer}
.prod-view__tab--active{background:var(--brand-light);border-color:var(--brand);color:var(--brand)}
.qc-view__table{padding:0;overflow:hidden}
.inv-view__name{font-weight:var(--fw-semibold)}.inv-view__actions{display:flex;gap:6px}
.bom-view__row{display:flex;align-items:center;gap:8px;padding:8px 12px;border-bottom:1px solid var(--border);font-size:var(--fz-sm)}
.bom-view__action{padding:3px 8px;border-radius:4px;border:1px solid var(--border);background:transparent;color:var(--text-muted);font-size:var(--fz-xs);cursor:pointer;font-family:inherit}
.bom-view__action:hover{border-color:var(--brand);color:var(--brand)}.bom-view__action--danger:hover{border-color:var(--danger);color:var(--danger)}
.mr-2{margin-right:8px}.mr-1{margin-right:4px}.ml-2{margin-left:8px}
.vk-text-sm{font-size:var(--fz-sm)}.vk-text-xs{font-size:var(--fz-xs)}.vk-text-muted{color:var(--text-muted)}.vk-text-faint{color:var(--text-faint)}.vk-font-mono{font-family:var(--font-mono)}
.admin-view__loading{padding:20px;display:flex;flex-direction:column;gap:12px}
.vk-skeleton-row{height:40px;background:var(--surface-sunken);border-radius:var(--r-input);animation:pulse 1.5s infinite}@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
.vk-table{width:100%;border-collapse:collapse}.vk-table th{text-align:left;padding:10px 12px;font-size:var(--fz-sm);font-weight:var(--fw-semibold);color:var(--text-muted);border-bottom:1px solid var(--border)}
.vk-table td{padding:10px 12px;font-size:var(--fz-body);border-bottom:1px solid var(--border)}.vk-table tr:last-child td{border-bottom:none}
.vk-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.4);display:grid;place-items:center;z-index:100}
.vk-dialog{width:540px;max-width:90vw;padding:24px}.vk-dialog--wide{width:620px}.vk-dialog__title{margin:0 0 20px;font-size:var(--fz-h2);font-weight:var(--fw-semibold)}
.vk-dialog__form{display:flex;flex-direction:column;gap:12px;margin-bottom:20px}.vk-dialog__form-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.vk-dialog__actions{display:flex;justify-content:flex-end;gap:8px}.vk-input__label{font-size:var(--fz-sm);font-weight:var(--fw-medium);color:var(--text);margin-bottom:6px;display:block}.post-view__select{display:flex;flex-direction:column;gap:6px}
@media(max-width:768px){.pur-view__main{padding:16px 16px 100px}.vk-dialog__form-row{grid-template-columns:1fr}}
</style>
