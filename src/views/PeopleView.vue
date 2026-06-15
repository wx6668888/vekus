<template>
  <div class="peo-view"><Sidebar /><main class="peo-view__main">
    <TopBar title="人员管理" description="员工档案与部门管理">
      <template #actions><Button variant="primary" @click="openCreate"><Plus :size="16" class="mr-2"/> 新增员工</Button></template>
    </TopBar>
    <div class="qc-view__mini">
      <div class="qc-view__mini-card"><span>总人数</span><strong>{{ items.length }}</strong></div>
      <div class="qc-view__mini-card"><span>生产部</span><strong>{{ deptCount('生产') }}</strong></div>
      <div class="qc-view__mini-card"><span>质量部</span><strong>{{ deptCount('质量') }}</strong></div>
      <div class="qc-view__mini-card"><span>管理部</span><strong>{{ deptCount('管理') }}</strong></div>
    </div>
    <Card class="apv-view__table">
      <table class="vk-table"><thead><tr><th>工号</th><th>姓名</th><th>部门</th><th>职位</th><th>电话</th><th>入职</th><th>操作</th></tr></thead>
        <tbody><tr v-for="e in items" :key="e.id">
          <td class="vk-font-mono vk-text-sm">{{ e.code || '-' }}</td>
          <td class="inv-view__name">{{ e.name }}</td><td class="vk-text-sm">{{ e.department }}</td>
          <td class="vk-text-sm">{{ e.position }}</td><td class="vk-text-sm">{{ e.phone }}</td>
          <td class="vk-text-sm">{{ e.hireDate?.slice(0,10) || '-' }}</td>
          <td><div class="inv-view__actions"><button class="bom-view__action" @click="openEdit(e)">编辑</button><button class="bom-view__action bom-view__action--danger" @click="api.delete('/employees/'+e.id).then(fetchItems)">删除</button></div></td>
        </tr></tbody>
      </table>
    </Card>
  </main><MobileNav />
  <div v-if="showDialog" class="vk-overlay" @click.self="showDialog=false"><Card class="vk-dialog"><h3 class="vk-dialog__title">{{editing?'编辑':'新增'}}员工</h3>
    <div class="vk-dialog__form">
      <div class="vk-dialog__form-row"><Input v-model="form.name" label="姓名 *"/><Input v-model="form.code" label="工号"/></div>
      <div class="vk-dialog__form-row">
        <div class="post-view__select"><label class="vk-input__label">部门</label><SelectMenu v-model="form.department" :options="deptOptions"/></div>
        <Input v-model="form.position" label="职位"/>
      </div>
      <div class="vk-dialog__form-row"><Input v-model="form.phone" label="电话"/><Input v-model="form.email" label="邮箱"/></div>
      <Input v-model="form.hireDate" label="入职日期" placeholder="2026-01-01"/>
    </div>
    <div class="vk-dialog__actions"><Button variant="ghost" @click="showDialog=false">取消</Button><Button variant="primary" :disabled="!form.name" @click="saveItem">保存</Button></div>
  </Card></div>
  </div>
</template>

<script setup lang="ts">
import { ref,reactive,onMounted } from 'vue';import { Plus } from 'lucide-vue-next';
import Sidebar from '@/components/layout/Sidebar.vue';import TopBar from '@/components/layout/TopBar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';import Card from '@/components/base/Card.vue';
import Button from '@/components/base/Button.vue';import Input from '@/components/base/Input.vue';
import SelectMenu from '@/components/base/SelectMenu.vue';import { api } from '@/api';
interface Emp { id:string;code:string;name:string;department:string;position:string;phone:string;hireDate:string; }
const items=ref<Emp[]>([]);const showDialog=ref(false);const editing=ref(false);const editId=ref('');
const form=reactive({name:'',code:'',department:'生产',position:'',phone:'',email:'',hireDate:''});
const deptOptions=[{value:'管理',label:'管理'},{value:'生产',label:'生产'},{value:'质量',label:'质量'},{value:'采购',label:'采购'},{value:'销售',label:'销售'}];
function deptCount(d:string){return items.value.filter(e=>e.department===d).length}
async function fetchItems(){const r=await api.get<Emp[]>('/employees');if(r.data)items.value=r.data}
onMounted(fetchItems);
function openCreate(){Object.assign(form,{name:'',code:'',department:'生产',position:'',phone:'',email:'',hireDate:''});editing.value=false;showDialog.value=true}
function openEdit(e:Emp){Object.assign(form,{name:e.name,code:e.code,department:e.department,position:e.position,phone:e.phone,email:e.email||'',hireDate:e.hireDate||''});editing.value=true;editId.value=e.id;showDialog.value=true}
async function saveItem(){if(editing.value){await api.put('/employees/'+editId.value,form)}else{await api.post('/employees',form)}showDialog.value=false;fetchItems()}
</script>

<style scoped>
.peo-view{display:block;min-height:100vh}.peo-view__main{padding:24px 32px 120px;max-width:960px;margin:0 auto}
.qc-view__mini{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:14px}
.qc-view__mini-card{display:flex;flex-direction:column;gap:4px;padding:12px 16px;background:var(--surface);border:1px solid var(--border);border-radius:10px;font-size:var(--fz-sm);color:var(--text-muted)}
.qc-view__mini-card strong{font-size:22px;font-family:var(--font-mono);color:var(--text)}
.apv-view__table{padding:0;overflow:hidden}.inv-view__name{font-weight:var(--fw-semibold)}.inv-view__actions{display:flex;gap:6px}
.bom-view__action{padding:3px 8px;border-radius:4px;border:1px solid var(--border);background:transparent;color:var(--text-muted);font-size:var(--fz-xs);cursor:pointer;font-family:inherit}
.bom-view__action:hover{border-color:var(--brand);color:var(--brand)}.bom-view__action--danger:hover{border-color:var(--danger);color:var(--danger)}
.mr-2{margin-right:8px}.vk-text-sm{font-size:var(--fz-sm)}.vk-font-mono{font-family:var(--font-mono)}
.vk-table{width:100%;border-collapse:collapse}.vk-table th{text-align:left;padding:10px 12px;font-size:var(--fz-sm);font-weight:var(--fw-semibold);color:var(--text-muted);border-bottom:1px solid var(--border)}
.vk-table td{padding:10px 12px;font-size:var(--fz-body);border-bottom:1px solid var(--border)}.vk-table tr:last-child td{border-bottom:none}
.vk-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.4);display:grid;place-items:center;z-index:100}
.vk-dialog{width:500px;max-width:90vw;padding:24px}.vk-dialog__title{margin:0 0 20px;font-size:var(--fz-h2);font-weight:var(--fw-semibold)}
.vk-dialog__form{display:flex;flex-direction:column;gap:12px;margin-bottom:20px}.vk-dialog__form-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.vk-dialog__actions{display:flex;justify-content:flex-end;gap:8px}.vk-input__label{font-size:var(--fz-sm);font-weight:var(--fw-medium);color:var(--text);margin-bottom:6px;display:block}.post-view__select{display:flex;flex-direction:column;gap:6px}
@media(max-width:768px){.peo-view__main{padding:16px 16px 100px}.qc-view__mini{grid-template-columns:repeat(2,1fr)}}
</style>
