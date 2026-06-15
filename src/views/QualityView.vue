<template>
  <div class="qc-view">
    <Sidebar />
    <main class="qc-view__main">
      <TopBar title="质量管理" description="来料检 / 过程检 / 成品检">
        <template #actions><Button variant="primary" @click="openCreate"><Plus :size="16" class="mr-2" /> 新建检验</Button></template>
      </TopBar>

      <div class="qc-view__tabs">
        <button v-for="t in typeTabs" :key="t.value" :class="['prod-view__tab',{'prod-view__tab--active':activeType===t.value}]" @click="activeType=t.value;fetchItems()">{{ t.label }}</button>
      </div>

      <!-- Stats -->
      <div class="qc-view__mini">
        <div class="qc-view__mini-card"><span>总检验</span><strong>{{ items.length }}</strong></div>
        <div class="qc-view__mini-card"><span>合格率</span><strong :class="passRate>=90?'text-success':'text-danger'">{{ passRate }}%</strong></div>
        <div class="qc-view__mini-card"><span>合格</span><strong class="text-success">{{ passCount }}</strong></div>
        <div class="qc-view__mini-card"><span>不合格</span><strong class="text-danger">{{ failCount }}</strong></div>
      </div>

      <Card class="qc-view__table">
        <div v-if="loading" class="admin-view__loading"><div class="vk-skeleton-row" v-for="i in 3" :key="i"></div></div>
        <table v-else class="vk-table">
          <thead><tr><th>检验单号</th><th>物料</th><th>类型</th><th>数量</th><th>合格/不良</th><th>结果</th><th>检验员</th><th>日期</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="q in items" :key="q.id">
              <td class="vk-font-mono vk-text-sm">{{ q.checkNo }}</td>
              <td class="inv-view__name">{{ q.itemName }}</td>
              <td><Badge :variant="q.type==='incoming'?'info':q.type==='process'?'warn':'default'" size="sm">{{ typeLabel(q.type) }}</Badge></td>
              <td class="vk-font-mono">{{ q.quantity }}</td>
              <td><span class="text-success">{{ q.passQty }}</span> / <span class="text-danger">{{ q.failQty }}</span></td>
              <td><Badge :variant="q.result==='pass'?'success':q.result==='partial'?'warn':'danger'" size="sm">{{ resultLabel(q.result) }}</Badge></td>
              <td class="vk-text-sm">{{ q.inspector || '-' }}</td>
              <td class="vk-text-sm">{{ q.checkDate || '-' }}</td>
              <td>
                <div class="inv-view__actions">
                  <button class="bom-view__action" @click="openEdit(q)">详情</button>
                  <button class="bom-view__action bom-view__action--danger" @click="api.delete('/quality/'+q.id).then(fetchItems)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </Card>
    </main>
    <MobileNav />

    <div v-if="showDialog" class="vk-overlay" @click.self="showDialog=false">
      <Card class="vk-dialog vk-dialog--wide"><h3 class="vk-dialog__title">{{ editingItem ? '检验详情' : '新建检验' }}</h3>
        <div class="vk-dialog__form">
          <div class="vk-dialog__form-row"><Input v-model="form.itemName" label="物料名称 *" />
            <div class="post-view__select"><label class="vk-input__label">检验类型</label><SelectMenu v-model="form.type" :options="typeOptions" /></div></div>
          <div class="vk-dialog__form-row"><Input v-model.number="form.quantity" type="number" label="检验数量" /><Input v-model="form.inspector" label="检验员" /></div>
          <div class="vk-dialog__form-row"><Input v-model.number="form.passQty" type="number" label="合格数" /><Input v-model.number="form.failQty" type="number" label="不良数" /></div>
          <div class="vk-dialog__form-row">
            <div class="post-view__select"><label class="vk-input__label">判定结果</label><SelectMenu v-model="form.result" :options="resultOptions" /></div>
            <div class="post-view__select"><label class="vk-input__label">处理方式</label><SelectMenu v-model="form.handle" :options="handleOptions" /></div>
          </div>
          <Input v-model="form.checkDate" label="检验日期" placeholder="2026-06-15" />
          <Input v-model="form.defectDesc" label="不良描述" placeholder="描述缺陷情况" />
        </div>
        <div class="vk-dialog__actions"><Button variant="ghost" @click="showDialog=false">取消</Button><Button variant="primary" :disabled="!form.itemName" @click="saveItem">保存</Button></div>
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
interface QcItem { id:string;checkNo:string;type:string;itemName:string;quantity:number;passQty:number;failQty:number;result:string;inspector:string;checkDate:string;defectDesc:string;handle:string; }
const items=ref<QcItem[]>([]);const loading=ref(true);const activeType=ref('');const showDialog=ref(false);const editingItem=ref<QcItem|null>(null);
const form=reactive({itemName:'',type:'incoming',quantity:1,passQty:0,failQty:0,result:'pass',inspector:'',checkDate:'',defectDesc:'',handle:''});
const typeTabs=[{value:'',label:'全部'},{value:'incoming',label:'来料检'},{value:'process',label:'过程检'},{value:'final',label:'成品检'}];
const typeOptions=[{value:'incoming',label:'来料检'},{value:'process',label:'过程检'},{value:'final',label:'成品检'}];
const resultOptions=[{value:'pass',label:'合格'},{value:'partial',label:'部分合格'},{value:'fail',label:'不合格'}];
const handleOptions=[{value:'',label:'无'},{value:'rework',label:'返工'},{value:'scrap',label:'报废'},{value:'return',label:'退货'},{value:'accept',label:'特采'}];
const passCount=computed(()=>items.value.filter(i=>i.result==='pass').length);
const failCount=computed(()=>items.value.filter(i=>i.result!=='pass').length);
const passRate=computed(()=>items.value.length?Math.round(passCount.value/items.value.length*100):0);
function typeLabel(t:string){const m:Record<string,string>={incoming:'来料检',process:'过程检',final:'成品检'};return m[t]||t}
function resultLabel(r:string){const m:Record<string,string>={pass:'合格',partial:'让步',fail:'不合格'};return m[r]||r}
async function fetchItems(){const q=activeType.value?'?type='+activeType.value:'';const r=await api.get<QcItem[]>('/quality'+q);if(r.data)items.value=r.data;loading.value=false}
onMounted(fetchItems);
function openCreate(){editingItem.value=null;Object.assign(form,{itemName:'',type:'incoming',quantity:1,passQty:0,failQty:0,result:'pass',inspector:'',checkDate:'',defectDesc:'',handle:''});showDialog.value=true}
function openEdit(q:QcItem){editingItem.value=q;Object.assign(form,{itemName:q.itemName,type:q.type,quantity:q.quantity,passQty:q.passQty,failQty:q.failQty,result:q.result,inspector:q.inspector,checkDate:q.checkDate,defectDesc:q.defectDesc,handle:q.handle});showDialog.value=true}
async function saveItem(){if(editingItem.value){await api.put('/quality/'+editingItem.value.id,form)}else{await api.post('/quality',form)}showDialog.value=false;fetchItems()}
</script>

<style scoped>
.qc-view{display:block;min-height:100vh}.qc-view__main{padding:24px 32px 120px;max-width:1100px;margin:0 auto}
.qc-view__tabs{display:flex;gap:4px;margin-bottom:14px}
.prod-view__tab{padding:6px 14px;border-radius:var(--r-pill);border:1px solid var(--border);background:var(--surface);color:var(--text-muted);font-size:var(--fz-sm);cursor:pointer}
.prod-view__tab--active{background:var(--brand-light);border-color:var(--brand);color:var(--brand)}
.qc-view__mini{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:14px}
.qc-view__mini-card{display:flex;flex-direction:column;gap:4px;padding:12px 16px;background:var(--surface);border:1px solid var(--border);border-radius:10px;font-size:var(--fz-sm);color:var(--text-muted)}
.qc-view__mini-card strong{font-size:22px;font-family:var(--font-mono);color:var(--text)}
.qc-view__table{padding:0;overflow:hidden}
.inv-view__name{font-weight:var(--fw-semibold)}.inv-view__actions{display:flex;gap:6px}
.bom-view__action{padding:3px 8px;border-radius:4px;border:1px solid var(--border);background:transparent;color:var(--text-muted);font-size:var(--fz-xs);cursor:pointer;font-family:inherit}
.bom-view__action:hover{border-color:var(--brand);color:var(--brand)}.bom-view__action--danger:hover{border-color:var(--danger);color:var(--danger)}
.mr-2{margin-right:8px}.text-success{color:var(--success)!important}.text-danger{color:var(--danger)!important}
.vk-text-sm{font-size:var(--fz-sm)}.vk-font-mono{font-family:var(--font-mono)}
.admin-view__loading{padding:20px;display:flex;flex-direction:column;gap:12px}
.vk-skeleton-row{height:40px;background:var(--surface-sunken);border-radius:var(--r-input);animation:pulse 1.5s infinite}@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
.vk-table{width:100%;border-collapse:collapse}.vk-table th{text-align:left;padding:10px 12px;font-size:var(--fz-sm);font-weight:var(--fw-semibold);color:var(--text-muted);border-bottom:1px solid var(--border)}
.vk-table td{padding:10px 12px;font-size:var(--fz-body);border-bottom:1px solid var(--border)}.vk-table tr:last-child td{border-bottom:none}
.vk-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.4);display:grid;place-items:center;z-index:100}
.vk-dialog{width:560px;max-width:90vw;padding:24px}.vk-dialog__title{margin:0 0 20px;font-size:var(--fz-h2);font-weight:var(--fw-semibold)}
.vk-dialog__form{display:flex;flex-direction:column;gap:12px;margin-bottom:20px}.vk-dialog__form-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.vk-dialog__actions{display:flex;justify-content:flex-end;gap:8px}.vk-input__label{font-size:var(--fz-sm);font-weight:var(--fw-medium);color:var(--text);margin-bottom:6px;display:block}.post-view__select{display:flex;flex-direction:column;gap:6px}
@media(max-width:768px){.qc-view__main{padding:16px 16px 100px}.qc-view__mini{grid-template-columns:repeat(2,1fr)}.vk-dialog__form-row{grid-template-columns:1fr}}
</style>
