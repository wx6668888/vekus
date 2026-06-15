<template>
  <div class="bom-view">
    <Sidebar />
    <main class="bom-view__main">
      <TopBar title="BOM 物料清单" description="管理产品物料层级结构、材料定额和版本">
        <template #actions>
          <Button variant="primary" @click="openCreate(0, 0, '组件')"><Plus :size="16" class="mr-2" /> 新增顶层</Button>
        </template>
      </TopBar>

      <!-- Summary -->
      <div class="bom-view__stats">
        <span>共 {{ flatList.length }} 个物料</span>
        <span class="admin-view__stat-sep">·</span>
        <span>顶层 {{ topLevelCount }} 个</span>
        <span class="admin-view__stat-sep">·</span>
        <span>最大层级 {{ maxLevel }} 级</span>
      </div>

      <!-- Tree / Flat toggle -->
      <div class="bom-view__toolbar">
        <div class="bom-view__tabs">
          <button :class="['bom-view__tab', { 'bom-view__tab--active': viewMode === 'tree' }]" @click="viewMode = 'tree'">树形</button>
          <button :class="['bom-view__tab', { 'bom-view__tab--active': viewMode === 'flat' }]" @click="viewMode = 'flat'">列表</button>
        </div>
      </div>

      <div v-if="loading" class="admin-view__loading"><div class="vk-skeleton-row" v-for="i in 4" :key="i"></div></div>

      <!-- Tree view -->
      <Card v-else-if="viewMode === 'tree'" class="bom-view__table">
        <div v-for="item in treeItems" :key="item.id">
          <div
            :class="['bom-view__row', 'bom-view__row--l' + item.level]"
            :style="{ paddingLeft: (item.level * 24 + 12) + 'px' }"
          >
            <button v-if="item.children?.length" class="bom-view__expand" @click="toggleExpand(item.id)">{{ expanded.has(item.id) ? '▾' : '▸' }}</button>
            <span v-else class="bom-view__expand-spacer"></span>
            <Badge :variant="item.category === '组件' ? 'info' : item.category === '原材料' ? 'warn' : 'default'" size="sm">{{ item.category }}</Badge>
            <span class="bom-view__item-name">{{ item.name }}</span>
            <span class="vk-text-muted vk-text-sm">{{ item.spec || '-' }}</span>
            <span class="vk-text-muted vk-text-sm">{{ item.material || '-' }}</span>
            <span class="vk-font-mono vk-text-sm">×{{ item.quantity }}</span>
            <span class="vk-text-muted vk-text-sm">{{ item.unitWeight > 0 ? item.unitWeight + 'kg' : '-' }}</span>
            <span v-if="item.version" class="vk-text-faint vk-text-xs">v{{ item.version }}</span>
            <div class="bom-view__row-actions">
              <button class="bom-view__action" @click="openCreate(item.id, item.level + 1, '零件')">+子项</button>
              <button class="bom-view__action" @click="openEdit(item)">编辑</button>
              <button class="bom-view__action bom-view__action--danger" @click="doDelete(item)">删除</button>
            </div>
          </div>
          <!-- Children (recursive) -->
          <template v-if="expanded.has(item.id)">
            <div v-for="child in getVisibleChildren(item.id)" :key="child.id">
              <div
                :class="['bom-view__row', 'bom-view__row--l' + child.level]"
                :style="{ paddingLeft: (child.level * 24 + 12) + 'px' }"
              >
                <button v-if="child.children?.length" class="bom-view__expand" @click="toggleExpand(child.id)">{{ expanded.has(child.id) ? '▾' : '▸' }}</button>
                <span v-else class="bom-view__expand-spacer"></span>
                <Badge :variant="child.category === '组件' ? 'info' : child.category === '原材料' ? 'warn' : 'default'" size="sm">{{ child.category }}</Badge>
                <span class="bom-view__item-name">{{ child.name }}</span>
                <span class="vk-text-muted vk-text-sm">{{ child.spec || '-' }}</span>
                <span class="vk-text-muted vk-text-sm">{{ child.material || '-' }}</span>
                <span class="vk-font-mono vk-text-sm">×{{ child.quantity }}</span>
                <span class="vk-text-muted vk-text-sm">{{ child.unitWeight > 0 ? child.unitWeight + 'kg' : '-' }}</span>
                <span v-if="child.version" class="vk-text-faint vk-text-xs">v{{ child.version }}</span>
                <div class="bom-view__row-actions">
                  <button class="bom-view__action" @click="openCreate(child.id, child.level + 1, '零件')">+子项</button>
                  <button class="bom-view__action" @click="openEdit(child)">编辑</button>
                  <button class="bom-view__action bom-view__action--danger" @click="doDelete(child)">删除</button>
                </div>
              </div>
            </div>
          </template>
        </div>
      </Card>

      <!-- Flat view -->
      <Card v-else class="bom-view__table">
        <table class="vk-table">
          <thead><tr><th>编码</th><th>名称</th><th>规格</th><th>材质</th><th>类别</th><th>用量</th><th>单重</th><th>版本</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="item in flatList" :key="item.id">
              <td class="vk-font-mono vk-text-sm">{{ item.code || '-' }}</td>
              <td class="bom-view__indent" :style="{ paddingLeft: (item.level * 16 + 12) + 'px' }">{{ '└ '.repeat(item.level > 0 ? 1 : 0) }}{{ item.name }}</td>
              <td class="vk-text-sm">{{ item.spec || '-' }}</td>
              <td class="vk-text-sm">{{ item.material || '-' }}</td>
              <td><Badge :variant="item.category === '组件' ? 'info' : item.category === '原材料' ? 'warn' : 'default'" size="sm">{{ item.category }}</Badge></td>
              <td class="vk-font-mono">×{{ item.quantity }}</td>
              <td>{{ item.unitWeight > 0 ? item.unitWeight + 'kg' : '-' }}</td>
              <td class="vk-text-xs vk-text-faint">v{{ item.version }}</td>
              <td>
                <button class="bom-view__action" @click="openEdit(item)">编辑</button>
                <button class="bom-view__action bom-view__action--danger" @click="doDelete(item)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </Card>
    </main>
    <MobileNav />

    <!-- Edit Dialog -->
    <div v-if="showDialog" class="vk-overlay" @click.self="showDialog = false">
      <Card class="vk-dialog vk-dialog--wide">
        <h3 class="vk-dialog__title">{{ editingItem ? '编辑物料' : '新增物料' }}</h3>
        <div class="vk-dialog__form">
          <div class="vk-dialog__form-row">
            <Input v-model="form.name" label="物料名称 *" placeholder="如：底板" />
            <Input v-model="form.code" label="物料编码" placeholder="如：BP-001" />
          </div>
          <div class="vk-dialog__form-row">
            <Input v-model="form.spec" label="规格" placeholder="如：200×150mm" />
            <Input v-model="form.material" label="材质" placeholder="如：镀锌板" />
          </div>
          <div class="vk-dialog__form-row">
            <div class="post-view__select">
              <label class="vk-input__label">类别</label>
              <SelectMenu v-model="form.category" :options="catOptions" />
            </div>
            <Input v-model.number="form.quantity" type="number" label="用量" />
          </div>
          <div class="vk-dialog__form-row">
            <Input v-model.number="form.unitWeight" type="number" label="单重(kg)" />
            <Input v-model.number="form.price" type="number" label="参考单价(¥)" />
          </div>
          <div class="vk-dialog__form-row">
            <Input v-model="form.unit" label="单位" />
            <Input v-model="form.version" label="版本" placeholder="1.0" />
          </div>
          <Input v-model="form.note" label="备注" placeholder="选填" />
        </div>
        <div class="vk-dialog__actions">
          <Button variant="ghost" @click="showDialog = false">取消</Button>
          <Button variant="primary" :disabled="!form.name" @click="saveItem">保存</Button>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Plus } from 'lucide-vue-next';
import Sidebar from '@/components/layout/Sidebar.vue';
import TopBar from '@/components/layout/TopBar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';
import Card from '@/components/base/Card.vue';
import Button from '@/components/base/Button.vue';
import Input from '@/components/base/Input.vue';
import Badge from '@/components/base/Badge.vue';
import SelectMenu from '@/components/base/SelectMenu.vue';
import { api } from '@/api';

interface BomNode {
  id: string; code: string; name: string; spec: string; material: string;
  unit: string; unitWeight: number; price: number; category: string;
  parentId: string; quantity: number; level: number; sortOrder: number;
  note: string; version: string; status: string; createdAt: string;
  children?: BomNode[];
}

const allItems = ref<BomNode[]>([]);
const expanded = ref(new Set<string>());
const loading = ref(true);
const showDialog = ref(false);
const editingItem = ref<BomNode | null>(null);
const viewMode = ref<'tree' | 'flat'>('tree');
const newParentId = ref(0);
const newLevel = ref(0);
const newCategory = ref('零件');

const form = reactive({
  name: '', code: '', spec: '', material: '', unit: '件', unitWeight: 0,
  price: 0, category: '零件', quantity: 1, parentId: 0, level: 0,
  sortOrder: 0, note: '', version: '1.0', status: 'active',
});

const catOptions = [{value:'组件',label:'组件'},{value:'零件',label:'零件'},{value:'原材料',label:'原材料'}];

const flatList = computed(() => {
  const result: BomNode[] = [];
  function walk(items: BomNode[]) {
    for (const i of items) { result.push(i); if (i.children) walk(i.children); }
  }
  walk(treeItems.value);
  return result;
});

const treeItems = computed(() => buildTree(allItems.value));

function buildTree(items: BomNode[]): BomNode[] {
  const map = new Map<string, BomNode>();
  const roots: BomNode[] = [];
  for (const i of items) { map.set(i.id, { ...i, children: [] }); }
  for (const i of items) {
    const node = map.get(i.id)!;
    if (i.parentId && i.parentId !== '0' && map.has(i.parentId)) {
      map.get(i.parentId)!.children!.push(node);
    } else if (!i.parentId || i.parentId === '0') {
      roots.push(node);
    }
  }
  return roots;
}

const topLevelCount = computed(() => treeItems.value.length);
const maxLevel = computed(() => Math.max(0, ...flatList.value.map(i => i.level)));

function getVisibleChildren(parentId: string): BomNode[] {
  const parent = flatList.value.find(i => i.id === parentId);
  if (!parent?.children) return [];
  return parent.children.filter((c: BomNode) => expanded.value.has(parentId));
}

function toggleExpand(id: string) {
  if (expanded.value.has(id)) expanded.value.delete(id);
  else expanded.value.add(id);
  expanded.value = new Set(expanded.value); // trigger reactivity
}

function autoExpand() {
  // Expand all parent items that have children in the built tree
  const tree = buildTree(allItems.value);
  const toExpand = new Set<string>();
  function walk(nodes: BomNode[]) {
    for (const n of nodes) {
      if (n.children && n.children.length > 0) {
        toExpand.add(n.id);
        walk(n.children);
      }
    }
  }
  walk(tree);
  expanded.value = toExpand;
}

onMounted(async () => {
  const res = await api.get<BomNode[]>('/bom/tree');
  if (res.data) allItems.value = res.data;
  loading.value = false;
  autoExpand();
});

function openCreate(parentId: number, level: number, category: string) {
  editingItem.value = null;
  newParentId.value = parentId; newLevel.value = level; newCategory.value = category;
  Object.assign(form, { name: '', code: '', spec: '', material: '', unit: '件', unitWeight: 0, price: 0, category, quantity: 1, parentId, level, sortOrder: 0, note: '', version: '1.0', status: 'active' });
  showDialog.value = true;
}

function openEdit(item: BomNode) {
  editingItem.value = item;
  Object.assign(form, {
    name: item.name, code: item.code, spec: item.spec, material: item.material,
    unit: item.unit, unitWeight: item.unitWeight, price: item.price,
    category: item.category, quantity: item.quantity,
    parentId: parseInt(item.parentId) || 0, level: item.level,
    sortOrder: item.sortOrder, note: item.note, version: item.version, status: item.status,
  });
  showDialog.value = true;
}

async function saveItem() {
  const body = { ...form };
  if (editingItem.value) {
    await api.put(`/bom/${editingItem.value.id}`, body);
  } else {
    await api.post('/bom', body);
  }
  showDialog.value = false;
  const res = await api.get<BomNode[]>('/bom/tree');
  if (res.data) allItems.value = res.data;
  autoExpand();
}

async function doDelete(item: BomNode) {
  if (!confirm(`确定删除「${item.name}」及其子物料吗？`)) return;
  await api.delete(`/bom/${item.id}`);
  const res = await api.get<BomNode[]>('/bom/tree');
  if (res.data) allItems.value = res.data;
}
</script>

<style scoped>
.bom-view { display: block; min-height: 100vh; }
.bom-view__main { padding: 24px 32px 120px; max-width: 1100px; margin: 0 auto; }
.bom-view__stats { font-size: var(--fz-sm); color: var(--text-muted); margin-bottom: 12px; display: flex; gap: 4px; }
.admin-view__stat-sep { color: var(--text-faint); margin: 0 2px; }
.bom-view__toolbar { margin-bottom: 14px; }
.bom-view__tabs { display: flex; gap: 4px; }
.bom-view__tab { padding: 6px 14px; border-radius: var(--r-pill); border: 1px solid var(--border); background: var(--surface); color: var(--text-muted); font-size: var(--fz-sm); cursor: pointer; }
.bom-view__tab--active { background: var(--brand-light); border-color: var(--brand); color: var(--brand); }
.bom-view__table { padding: 0; overflow: hidden; }
.bom-view__row { display: flex; align-items: center; gap: 8px; padding: 10px 12px; border-bottom: 1px solid var(--border); font-size: var(--fz-sm); transition: background 0.1s; }
.bom-view__row:hover { background: var(--surface-sunken); }
.bom-view__row--l0 { background: var(--surface); }
.bom-view__row--l0:hover { background: var(--brand-light); }
.bom-view__expand { width: 18px; height: 18px; border: none; background: none; cursor: pointer; font-size: 12px; color: var(--text-muted); flex-shrink: 0; display: grid; place-items: center; }
.bom-view__expand-spacer { width: 18px; flex-shrink: 0; }
.bom-view__item-name { font-weight: var(--fw-semibold); min-width: 100px; }
.bom-view__row-actions { margin-left: auto; display: flex; gap: 6px; flex-shrink: 0; }
.bom-view__action { padding: 3px 8px; border-radius: 4px; border: 1px solid var(--border); background: transparent; color: var(--text-muted); font-size: var(--fz-xs); cursor: pointer; font-family: inherit; }
.bom-view__action:hover { border-color: var(--brand); color: var(--brand); }
.bom-view__action--danger:hover { border-color: var(--danger); color: var(--danger); }
.bom-view__indent { font-size: var(--fz-sm); }
.mr-2 { margin-right: 8px; }
.vk-font-mono { font-family: var(--font-mono); }
.vk-text-sm { font-size: var(--fz-sm); }
.vk-text-xs { font-size: var(--fz-xs); }
.vk-text-muted { color: var(--text-muted); }
.vk-text-faint { color: var(--text-faint); }
.admin-view__loading { padding: 20px; display: flex; flex-direction: column; gap: 12px; }
.vk-skeleton-row { height: 40px; background: var(--surface-sunken); border-radius: var(--r-input); animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }
.vk-table { width: 100%; border-collapse: collapse; }
.vk-table th { text-align: left; padding: 10px 12px; font-size: var(--fz-sm); font-weight: var(--fw-semibold); color: var(--text-muted); border-bottom: 1px solid var(--border); }
.vk-table td { padding: 10px 12px; font-size: var(--fz-body); border-bottom: 1px solid var(--border); }
.vk-table tr:last-child td { border-bottom: none; }
/* Dialog */
.vk-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: grid; place-items: center; z-index: 100; }
.vk-dialog { width: 560px; max-width: 90vw; padding: 24px; max-height: 85vh; overflow-y: auto; }
.vk-dialog__title { margin: 0 0 20px; font-size: var(--fz-h2); font-weight: var(--fw-semibold); }
.vk-dialog__form { display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px; }
.vk-dialog__form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.vk-dialog__actions { display: flex; justify-content: flex-end; gap: 8px; }
.vk-input__label { font-size: var(--fz-sm); font-weight: var(--fw-medium); color: var(--text); margin-bottom: 6px; display: block; }
.post-view__select { display: flex; flex-direction: column; gap: 6px; }
@media (max-width: 768px) {
  .bom-view__main { padding: 16px 16px 100px; }
  .vk-dialog__form-row { grid-template-columns: 1fr; }
}
</style>
