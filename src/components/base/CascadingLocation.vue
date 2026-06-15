<template>
  <div class="vk-location" ref="rootEl">
    <!-- Trigger -->
    <div
      :class="['vk-location__trigger', { 'vk-location__trigger--open': open }]"
      @click="toggle"
    >
      <MapPin :size="15" class="vk-location__icon" />
      <span class="vk-location__label">{{ displayText }}</span>
      <button v-if="modelValue" class="vk-location__clear" @click.stop="clear" title="清除">✕</button>
      <svg :class="['vk-location__chevron', { 'vk-location__chevron--open': open }]"
        width="10" height="6" viewBox="0 0 10 6" fill="none">
        <path d="M1 1L5 5L9 1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>

    <!-- Dropdown -->
    <Teleport to="body">
      <Transition name="vk-loc-fade">
        <div v-if="open" class="vk-location__portal" :style="portalStyle">
          <div class="vk-location__panel">
            <!-- Toolbar -->
            <div class="vk-location__toolbar">
              <button class="vk-location__locate-btn" @click="autoLocate">
                <Crosshair :size="14" />
                <span>{{ locating ? '定位中...' : '自动定位' }}</span>
              </button>
              <span v-if="locateError" class="vk-location__locate-error">{{ locateError }}</span>
            </div>

            <!-- 3 columns -->
            <div class="vk-location__columns">
              <!-- Province -->
              <div class="vk-location__col">
                <div class="vk-location__col-header">省份</div>
                <div class="vk-location__col-list">
                  <button
                    v-for="p in provinces"
                    :key="p.value"
                    :class="['vk-location__item', { 'vk-location__item--active': selectedProvince?.value === p.value }]"
                    @click="selectProvince(p)"
                  >{{ p.label }}</button>
                </div>
              </div>

              <!-- City -->
              <div class="vk-location__col" v-if="selectedProvince?.children?.length">
                <div class="vk-location__col-header">城市</div>
                <div class="vk-location__col-list">
                  <button
                    v-for="c in selectedProvince.children"
                    :key="c.value"
                    :class="['vk-location__item', { 'vk-location__item--active': selectedCity?.value === c.value }]"
                    @click="selectCity(c)"
                  >{{ c.label }}</button>
                </div>
              </div>

              <!-- County -->
              <div class="vk-location__col" v-if="selectedCity?.children?.length">
                <div class="vk-location__col-header">区县</div>
                <div class="vk-location__col-list">
                  <button
                    v-for="d in selectedCity.children"
                    :key="d.value"
                    :class="['vk-location__item', { 'vk-location__item--active': selectedDistrict?.value === d.value }]"
                    @click="selectDistrict(d)"
                  >{{ d.label }}</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <div v-if="open" class="vk-location__backdrop" @click="open = false"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue';
import { MapPin, Crosshair } from 'lucide-vue-next';
import { chinaRegions, type RegionNode } from '@/data/chinaRegions';

const props = defineProps<{
  modelValue: string;    // full path like "广东-深圳-宝安"
  placeholder?: string;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
}>();

const open = ref(false);
const locating = ref(false);
const locateError = ref('');
const rootEl = ref<HTMLElement | null>(null);
const triggerRect = ref({ top: 0, left: 0, width: 0, height: 0 });

const selectedProvince = ref<RegionNode | null>(null);
const selectedCity = ref<RegionNode | null>(null);
const selectedDistrict = ref<RegionNode | null>(null);

const provinces = chinaRegions;

const displayText = computed(() => {
  if (!props.modelValue) return props.placeholder || '选择地区';
  const parts = props.modelValue.split('-');
  // Walk the tree to build readable label
  let list = chinaRegions;
  let label = '';
  for (const seg of parts) {
    const found = list.find(r => r.value === props.modelValue!.split('-').slice(0, parts.indexOf(seg) + 1).join('-'));
    if (!found) break;
    // Simpler: just use the parts themselves
  }
  // Format the path into readable text
  const labels: string[] = [];
  let nodes = chinaRegions;
  for (const p of parts) {
    const match = nodes.find(n => n.value === parts.slice(0, labels.length + 1).join('-'));
    if (match) { labels.push(match.label); nodes = match.children || []; }
  }
  return labels.join(' · ') || props.modelValue;
});

const portalStyle = computed(() => ({
  position: 'fixed' as const,
  top: (triggerRect.value.top + triggerRect.value.height + 6) + 'px',
  left: Math.min(triggerRect.value.left, window.innerWidth - 520) + 'px',
  zIndex: 10001,
}));

// Parse modelValue back into selections
function parseValue(val: string) {
  if (!val) {
    selectedProvince.value = null;
    selectedCity.value = null;
    selectedDistrict.value = null;
    return;
  }
  const parts = val.split('-');
  let list: RegionNode[] = chinaRegions;
  for (let i = 0; i < parts.length; i++) {
    const seg = parts.slice(0, i + 1).join('-');
    const match = list.find(n => n.value === seg);
    if (match) {
      if (i === 0) { selectedProvince.value = match; list = match.children || []; }
      else if (i === 1) { selectedCity.value = match; list = match.children || []; }
      else if (i === 2) { selectedDistrict.value = match; }
    }
  }
}

function toggle() {
  if (!open.value) {
    parseValue(props.modelValue);
    updateRect();
    nextTick(() => (open.value = true));
  } else {
    open.value = false;
  }
}

function updateRect() {
  if (rootEl.value) {
    const r = rootEl.value.querySelector('.vk-location__trigger')!.getBoundingClientRect();
    triggerRect.value = { top: r.top, left: r.left, width: r.width, height: r.height };
  }
}

function emitValue() {
  const parts: string[] = [];
  if (selectedProvince.value) parts.push(selectedProvince.value.value);
  if (selectedCity.value) parts.push(selectedCity.value.value);
  if (selectedDistrict.value) parts.push(selectedDistrict.value.value);
  emit('update:modelValue', parts.join('-'));
  open.value = false;
}

function selectProvince(p: RegionNode) {
  selectedProvince.value = p;
  selectedCity.value = null;
  selectedDistrict.value = null;
  if (!p.children?.length) {
    emitValue();
  }
}

function selectCity(c: RegionNode) {
  selectedCity.value = c;
  selectedDistrict.value = null;
  if (!c.children?.length) {
    emitValue();
  } else {
    // If city has children (districts), wait for district selection
    // Don't auto-close
  }
}

function selectDistrict(d: RegionNode) {
  selectedDistrict.value = d;
  emitValue();
}

function clear() {
  selectedProvince.value = null;
  selectedCity.value = null;
  selectedDistrict.value = null;
  emit('update:modelValue', '');
  open.value = false;
}

function autoLocate() {
  if (!navigator.geolocation) {
    locateError.value = '浏览器不支持定位';
    return;
  }
  locating.value = true;
  locateError.value = '';
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      // Try to reverse geocode to match a known city
      const { latitude, longitude } = pos.coords;
      // For now, use a simple heuristic based on coordinates
      // In production, you'd call a geocoding API
      // We'll just show a message that location was detected
      const coordsStr = `${latitude.toFixed(2)}, ${longitude.toFixed(2)}`;
      // Approximate matching for major manufacturing regions
      if (latitude > 22.5 && latitude < 23.8 && longitude > 113 && longitude < 114.5) {
        selectProvince(chinaRegions.find(p => p.value === '广东')!);
        const gd = chinaRegions.find(p => p.value === '广东')!;
        selectedProvince.value = gd;
        selectedCity.value = gd.children?.find(c => c.value === '广东-深圳') || null;
        selectedDistrict.value = null;
      } else if (latitude > 30 && latitude < 32 && longitude > 120 && longitude < 122) {
        const sh = chinaRegions.find(p => p.value === '上海')!;
        selectedProvince.value = sh;
        selectedCity.value = null;
      } else if (latitude > 29 && latitude < 31 && longitude > 119 && longitude < 121) {
        const zj = chinaRegions.find(p => p.value === '浙江')!;
        selectedProvince.value = zj;
        selectedCity.value = zj.children?.find(c => c.value === '浙江-杭州') || null;
      } else if (latitude > 31 && latitude < 33 && longitude > 118 && longitude < 121) {
        const js = chinaRegions.find(p => p.value === '江苏')!;
        selectedProvince.value = js;
        selectedCity.value = js.children?.find(c => c.value === '江苏-苏州') || null;
      } else {
        locateError.value = `已获取位置(${coordsStr})，请手动选择城市`;
      }
      if (!locateError.value && selectedProvince.value?.children?.length && !selectedProvince.value.children[0]?.children?.length) {
        emitValue();
      }
      locating.value = false;
    },
    (err) => {
      locateError.value = '无法获取位置，请检查浏览器定位权限';
      locating.value = false;
    },
    { timeout: 8000, enableHighAccuracy: true }
  );
}

function onScroll() { if (open.value) updateRect(); }
function onResize() { if (open.value) updateRect(); }

onMounted(() => {
  parseValue(props.modelValue);
  window.addEventListener('scroll', onScroll, true);
  window.addEventListener('resize', onResize);
});

onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScroll, true);
  window.removeEventListener('resize', onResize);
});
</script>

<style scoped>
.vk-location { position: relative; display: inline-block; }

.vk-location__trigger {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 36px;
  padding: 0 10px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  font-size: var(--fz-sm);
  font-family: inherit;
  cursor: pointer;
  user-select: none;
  transition: all 0.15s ease;
  white-space: nowrap;
  outline: none;
}

.vk-location__trigger:hover { border-color: var(--border-strong); background: var(--surface-sunken); }
.vk-location__trigger--open { border-color: var(--brand); box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.08); }

.vk-location__icon { color: var(--text-muted); flex-shrink: 0; }
.vk-location__label { flex: 1; text-align: left; }
.vk-location__clear {
  background: none; border: none; color: var(--text-faint); cursor: pointer;
  font-size: 12px; padding: 2px; line-height: 1;
}
.vk-location__clear:hover { color: var(--text); }

.vk-location__chevron {
  flex-shrink: 0; color: var(--text-muted); transition: transform 0.2s;
}
.vk-location__chevron--open { transform: rotate(180deg); color: var(--brand); }

.vk-location__portal { position: fixed; }

.vk-location__panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  box-shadow: var(--sh-lg);
  overflow: hidden;
  width: 500px;
}

.vk-location__toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-bottom: 1px solid var(--border);
  background: var(--surface-sunken);
}

.vk-location__locate-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--brand);
  font-size: var(--fz-xs);
  cursor: pointer;
  font-family: inherit;
  transition: all 0.15s;
}
.vk-location__locate-btn:hover { border-color: var(--brand); }

.vk-location__locate-error { font-size: var(--fz-xs); color: var(--danger); }

.vk-location__columns {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  max-height: 320px;
  overflow: hidden;
}

.vk-location__col {
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
}
.vk-location__col:last-child { border-right: none; }

.vk-location__col-header {
  font-size: var(--fz-xs);
  font-weight: var(--fw-semibold);
  color: var(--text-muted);
  padding: 10px 14px 6px;
  background: var(--surface);
  position: sticky;
  top: 0;
  z-index: 1;
}

.vk-location__col-list {
  flex: 1;
  overflow-y: auto;
  padding: 4px;
}

.vk-location__item {
  display: block;
  width: 100%;
  padding: 7px 14px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--text);
  font-size: var(--fz-sm);
  font-family: inherit;
  text-align: left;
  cursor: pointer;
  transition: background 0.1s;
}

.vk-location__item:hover { background: var(--surface-sunken); }
.vk-location__item--active { background: var(--brand-light); color: var(--brand); font-weight: var(--fw-semibold); }

.vk-location__backdrop { position: fixed; inset: 0; z-index: 10000; }

/* Transitions */
.vk-loc-fade-enter-active { transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1); }
.vk-loc-fade-leave-active { transition: all 0.12s ease-in; }
.vk-loc-fade-enter-from { opacity: 0; transform: translateY(-6px) scale(0.97); }
.vk-loc-fade-leave-to { opacity: 0; transform: translateY(-4px) scale(0.98); }

@media (max-width: 768px) {
  .vk-location__panel { width: calc(100vw - 32px); max-width: 500px; }
  .vk-location__columns { grid-template-columns: repeat(3, 1fr); max-height: 280px; }
}
</style>
