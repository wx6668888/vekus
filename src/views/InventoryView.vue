<template>
  <div class="inv-view">
    <Sidebar />
    <main class="inv-view__main">
      <TopBar title="库存管理" description="出入库、盘点、安全库存预警">
        <template #actions>
          <Button variant="primary" @click="openCreate"><Plus :size="16" class="mr-2" /> 新增物料</Button>
        </template>
      </TopBar>

      <!-- Alerts -->
      <div v-if="lowStockItems.length" class="inv-view__alerts">
        <AlertTriangle :size="16" /> <span>{{ lowStockItems.length }} 个物料低于安全库存</span>
      </div>

      <!-- Stats -->
      <div class="inv-view__mini">
        <div class="inv-view__mini-card"><span>总品类</span><strong>{{ items.length }}</strong></div>
        <div class="inv-view__mini-card"><span>总库存量</span><strong>{{ totalQty.toFixed(1) }}</strong></div>
        <div class="inv-view__mini-card"><span>紧缺</span><strong class="text-danger">{{ lowStockItems.length }}</strong></div>
        <div class="inv-view__mini-card"><span>正常</span><strong class="text-success">{{ items.length - lowStockItems.length }}</strong></div>
      </div>

      <Card class="inv-view__table">
        <div v-if="loading" class="admin-view__loading"><div class="vk-skeleton-row" v-for="i in 4" :key="i"></div></div>
        <table v-else class="vk-table">
          <thead><tr><th>物料名称</th><th>规格</th><th>材质</th><th>库存</th><th>安全库存</th><th>库位</th><th>状态</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="item in items" :key="item.id" :class="{ 'inv-view__row--warn': item.quantity <= item.safetyStock && item.safetyStock > 0 }">
              <td class="inv-view__name">{{ item.name }}<span v-if="item.code" class="vk-text-xs vk-text-faint ml-2">{{ item.code }}</span></td>
              <td class="vk-text-sm">{{ item.spec || '-' }}</td>
              <td class="vk-text-sm">{{ item.material || '-' }}</td>
              <td class="vk-font-mono">{{ item.quantity }} {{ item.unit }}</td>
              <td class="vk-font-mono">{{ item.safetyStock || '-' }}</td>
              <td class="vk-text-sm">{{ item.location || '-' }}</td>
              <td><Badge :variant="item.quantity <= item.safetyStock && item.safetyStock > 0 ? 'danger' : 'success'" size="sm">{{ item.status }}</Badge></td>
              <td>
                <div class="inv-view__actions">
                  <button class="bom-view__action" @click="openTransact(item, 'in')">入库</button>
                  <button class="bom-view__action" @click="openTransact(item, 'out')">出库</button>
                  <button class="bom-view__action bom-view__action--danger" @click="api.delete('/inventory/'+item.id).then(fetchItems)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </Card>
    </main>
    <MobileNav />

    <!-- Create Dialog -->
    <div v-if="showDialog" class="vk-overlay" @click.self="showDialog = false">
      <Card class="vk-dialog"><h3 class="vk-dialog__title">新增物料</h3>
        <div class="vk-dialog__form">
          <div class="vk-dialog__form-row"><Input v-model="form.name" label="物料名称 *" /><Input v-model="form.code" label="编码" /></div>
          <div class="vk-dialog__form-row"><Input v-model="form.spec" label="规格" /><Input v-model="form.material" label="材质" /></div>
          <div class="vk-dialog__form-row"><Input v-model.number="form.quantity" type="number" label="初始数量" /><Input v-model.number="form.safetyStock" type="number" label="安全库存" /></div>
          <div class="vk-dialog__form-row"><Input v-model="form.unit" label="单位" /><Input v-model="form.location" label="库位" /></div>
        </div>
        <div class="vk-dialog__actions"><Button variant="ghost" @click="showDialog=false">取消</Button><Button variant="primary" :disabled="!form.name" @click="saveItem">保存</Button></div>
      </Card>
    </div>

    <!-- Transact Dialog -->
    <div v-if="transactItem" class="vk-overlay" @click.self="transactItem=null">
      <Card class="vk-dialog"><h3 class="vk-dialog__title">{{ transactType === 'in' ? '入库' : '出库' }} — {{ transactItem.name }}</h3>
        <p class="vk-text-sm vk-text-muted mb-4">当前库存: {{ transactItem.quantity }} {{ transactItem.unit }}</p>
        <div class="vk-dialog__form">
          <Input v-model.number="transactQty" type="number" :label="transactType === 'in' ? '入库数量' : '出库数量'" />
          <Input v-model="transactNote" label="备注" placeholder="选填" />
        </div>
        <div class="vk-dialog__actions"><Button variant="ghost" @click="transactItem=null">取消</Button><Button variant="primary" @click="doTransact">确认</Button></div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref,computed,onMounted,reactive } from 'vue';
import { Plus,AlertTriangle } from 'lucide-vue-next';
import Sidebar from '@/components/layout/Sidebar.vue';import TopBar from '@/components/layout/TopBar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';import Card from '@/components/base/Card.vue';
import Button from '@/components/base/Button.vue';import Input from '@/components/base/Input.vue';
import Badge from '@/components/base/Badge.vue';import { api } from '@/api';
interface InvItem { id:string;name:string;code:string;spec:string;material:string;unit:string;quantity:number;safetyStock:number;location:string;status:string; }
const items=ref<InvItem[]>([]);const loading=ref(true);const showDialog=ref(false);
const transactItem=ref<InvItem|null>(null);const transactType=ref('in');const transactQty=ref(1);const transactNote=ref('');
const form=reactive({name:'',code:'',spec:'',material:'',unit:'件',quantity:0,safetyStock:0,location:''});
const lowStockItems=computed(()=>items.value.filter(i=>i.quantity<=i.safetyStock&&i.safetyStock>0));
const totalQty=computed(()=>items.value.reduce((s,i)=>s+i.quantity,0));
async function fetchItems(){const r=await api.get<InvItem[]>('/inventory');if(r.data)items.value=r.data;loading.value=false;}
onMounted(fetchItems);
function openCreate(){Object.assign(form,{name:'',code:'',spec:'',material:'',unit:'件',quantity:0,safetyStock:0,location:''});showDialog.value=true;}
async function saveItem(){await api.post('/inventory',form);showDialog.value=false;fetchItems();}
function openTransact(item:InvItem,type:string){transactItem.value=item;transactType.value=type;transactQty.value=1;transactNote.value='';}
async function doTransact(){if(!transactItem.value)return;await api.post('/inventory/'+transactItem.value.id+'/transact',{type:transactType.value,quantity:transactQty.value,note:transactNote.value});transactItem.value=null;fetchItems();}
</script>

<style scoped>
.inv-view{display:block;min-height:100vh}.inv-view__main{padding:24px 32px 120px;max-width:1100px;margin:0 auto}
.inv-view__alerts{display:flex;align-items:center;gap:8px;padding:10px 16px;background:#FEF2F2;border:1px solid #FECACA;border-radius:10px;color:#DC2626;font-size:var(--fz-sm);font-weight:var(--fw-medium);margin-bottom:14px}
.inv-view__mini{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:14px}
.inv-view__mini-card{display:flex;flex-direction:column;gap:4px;padding:12px 16px;background:var(--surface);border:1px solid var(--border);border-radius:10px;font-size:var(--fz-sm);color:var(--text-muted)}
.inv-view__mini-card strong{font-size:22px;font-family:var(--font-mono);color:var(--text)}
.inv-view__table{padding:0;overflow:hidden}.inv-view__name{font-weight:var(--fw-semibold)}
.inv-view__row--warn{background:#FFFBF0}.inv-view__actions{display:flex;gap:6px}
.bom-view__action{padding:3px 8px;border-radius:4px;border:1px solid var(--border);background:transparent;color:var(--text-muted);font-size:var(--fz-xs);cursor:pointer;font-family:inherit}
.bom-view__action:hover{border-color:var(--brand);color:var(--brand)}
.bom-view__action--danger:hover{border-color:var(--danger);color:var(--danger)}
.mr-2{margin-right:8px}.ml-2{margin-left:8px}.mb-4{margin-bottom:16px}
.text-danger{color:var(--danger)!important}.text-success{color:var(--success)!important}
.vk-text-sm{font-size:var(--fz-sm)}.vk-text-xs{font-size:var(--fz-xs)}.vk-text-muted{color:var(--text-muted)}.vk-text-faint{color:var(--text-faint)}.vk-font-mono{font-family:var(--font-mono)}
.admin-view__loading{padding:20px;display:flex;flex-direction:column;gap:12px}
.vk-skeleton-row{height:40px;background:var(--surface-sunken);border-radius:var(--r-input);animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
.vk-table{width:100%;border-collapse:collapse}.vk-table th{text-align:left;padding:10px 12px;font-size:var(--fz-sm);font-weight:var(--fw-semibold);color:var(--text-muted);border-bottom:1px solid var(--border)}
.vk-table td{padding:10px 12px;font-size:var(--fz-body);border-bottom:1px solid var(--border)}.vk-table tr:last-child td{border-bottom:none}
.vk-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.4);display:grid;place-items:center;z-index:100}
.vk-dialog{width:500px;max-width:90vw;padding:24px}.vk-dialog__title{margin:0 0 20px;font-size:var(--fz-h2);font-weight:var(--fw-semibold)}
.vk-dialog__form{display:flex;flex-direction:column;gap:12px;margin-bottom:20px}.vk-dialog__form-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.vk-dialog__actions{display:flex;justify-content:flex-end;gap:8px}
@media(max-width:768px){.inv-view__main{padding:16px 16px 100px}.inv-view__mini{grid-template-columns:repeat(2,1fr)}.vk-dialog__form-row{grid-template-columns:1fr}}
</style>
