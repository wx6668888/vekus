<template>
  <div class="doc-view">
    <Sidebar />
    <main class="doc-view__main">
      <TopBar title="文档管理" description="图纸文件归档和版本管理">
        <template #actions>
          <label class="bom-view__action" style="cursor:pointer;display:inline-flex;align-items:center;gap:4px;margin-right:8px;padding:8px 14px;border-radius:8px">
            <Upload :size="14" /> 上传文件
            <input type="file" multiple accept=".dwg,.dxf,.step,.stp,.pdf,.png,.jpg" style="display:none" @change="uploadFiles" />
          </label>
          <Button variant="primary" @click="fetchDocs"><RefreshCw :size="14" class="mr-1" /> 刷新</Button>
        </template>
      </TopBar>

      <div class="doc-view__mini">
        <div class="doc-view__mini-card"><span>文件总数</span><strong>{{ docs.length }}</strong></div>
        <div class="doc-view__mini-card"><span>DWG/DXF</span><strong>{{ typeCount('dwg')+typeCount('dxf') }}</strong></div>
        <div class="doc-view__mini-card"><span>STEP/STP</span><strong>{{ typeCount('step')+typeCount('stp') }}</strong></div>
        <div class="doc-view__mini-card"><span>PDF/图片</span><strong>{{ typeCount('pdf')+typeCount('png')+typeCount('jpg') }}</strong></div>
      </div>

      <Card class="doc-view__table">
        <div v-if="loading" class="admin-view__loading"><div class="vk-skeleton-row" v-for="i in 3" :key="i"></div></div>
        <table v-else class="vk-table">
          <thead><tr><th>文件名</th><th>类型</th><th>关联客户</th><th>大小</th><th>版本</th><th>上传时间</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="d in docs" :key="d.id">
              <td class="inv-view__name">{{ d.fileName }}</td>
              <td><Badge size="sm" :variant="'default'">{{ d.fileType?.toUpperCase() }}</Badge></td>
              <td class="vk-text-sm">{{ d.customerName || '-' }}</td>
              <td class="vk-font-mono vk-text-sm">{{ formatSize(d.fileSize) }}</td>
              <td class="vk-text-sm">v{{ d.version || '1.0' }}</td>
              <td class="vk-text-sm">{{ d.createdAt?.slice(0,10) }}</td>
              <td>
                <button class="bom-view__action" @click="window.open('/api/files/'+d.id+'/download')">下载</button>
                <button class="bom-view__action bom-view__action--danger" @click="api.delete('/docs/'+d.id).then(fetchDocs)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </Card>
    </main>
    <MobileNav />
  </div>
</template>

<script setup lang="ts">
import { ref,onMounted } from 'vue';import { Upload,RefreshCw } from 'lucide-vue-next';
import Sidebar from '@/components/layout/Sidebar.vue';import TopBar from '@/components/layout/TopBar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';import Card from '@/components/base/Card.vue';
import Button from '@/components/base/Button.vue';import Badge from '@/components/base/Badge.vue';import { api } from '@/api';
interface DocItem { id:string;fileName:string;fileType:string;fileSize:number;customerName:string;version:string;createdAt:string; }
const docs=ref<DocItem[]>([]);const loading=ref(true);
function typeCount(ext:string){return docs.value.filter(d=>d.fileType?.toLowerCase()===ext).length}
function formatSize(b:number){return b>1e6?(b/1e6).toFixed(1)+'MB':b>1e3?(b/1e3).toFixed(1)+'KB':b+'B'}
async function fetchDocs(){const r=await api.get<DocItem[]>('/docs');if(r.data)docs.value=r.data;loading.value=false}
onMounted(fetchDocs);
async function uploadFiles(e:Event){
  const files=(e.target as HTMLInputElement).files;if(!files)return;
  for(let i=0;i<files.length;i++){
    const f=files[i];const fd=new FormData();fd.append('file',f);
    await fetch('/api/docs/upload',{method:'POST',body:fd});
  }
  fetchDocs();(e.target as HTMLInputElement).value='';
}
</script>

<style scoped>
.doc-view{display:block;min-height:100vh}.doc-view__main{padding:24px 32px 120px;max-width:1000px;margin:0 auto}
.doc-view__mini{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:14px}
.doc-view__mini-card{display:flex;flex-direction:column;gap:4px;padding:12px 16px;background:var(--surface);border:1px solid var(--border);border-radius:10px;font-size:var(--fz-sm);color:var(--text-muted)}
.doc-view__mini-card strong{font-size:22px;font-family:var(--font-mono);color:var(--text)}
.doc-view__table{padding:0;overflow:hidden}.inv-view__name{font-weight:var(--fw-semibold)}
.bom-view__action{padding:3px 8px;border-radius:4px;border:1px solid var(--border);background:transparent;color:var(--text-muted);font-size:var(--fz-xs);cursor:pointer;font-family:inherit}
.bom-view__action:hover{border-color:var(--brand);color:var(--brand)}.bom-view__action--danger:hover{border-color:var(--danger);color:var(--danger)}
.mr-1{margin-right:4px}.vk-text-sm{font-size:var(--fz-sm)}.vk-font-mono{font-family:var(--font-mono)}
.admin-view__loading{padding:20px;display:flex;flex-direction:column;gap:12px}
.vk-skeleton-row{height:40px;background:var(--surface-sunken);border-radius:var(--r-input);animation:pulse 1.5s infinite}@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
.vk-table{width:100%;border-collapse:collapse}.vk-table th{text-align:left;padding:10px 12px;font-size:var(--fz-sm);font-weight:var(--fw-semibold);color:var(--text-muted);border-bottom:1px solid var(--border)}
.vk-table td{padding:10px 12px;font-size:var(--fz-body);border-bottom:1px solid var(--border)}.vk-table tr:last-child td{border-bottom:none}
@media(max-width:768px){.doc-view__main{padding:16px 16px 100px}.doc-view__mini{grid-template-columns:repeat(2,1fr)}}
</style>
