<template>
  <div class="mp-root">
    <div v-if="!hasModel" class="mp-empty">
      <Box :size="48" class="mp-empty-icon" />
      <p>上传 STEP/STL 文件后可在此预览 3D 模型</p>
    </div>
    <div v-else ref="containerRef" class="mp-container"></div>
    <div v-if="hasModel" class="mp-controls">
      <span class="mp-info">{{ fileName }}</span>
      <button class="mp-btn" @click="resetView">重置视角</button>
      <button class="mp-btn" @click="toggleWireframe">{{ wireframe ? '实体' : '线框' }}</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick, onBeforeUnmount } from 'vue';
import { Box } from 'lucide-vue-next';
import * as THREE from 'three';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

const props = defineProps<{ fileUrl?: string; fileName?: string }>();
const containerRef = ref<HTMLElement | null>(null);
const hasModel = ref(false);
const wireframe = ref(false);

let scene: THREE.Scene, camera: THREE.PerspectiveCamera, renderer: THREE.WebGLRenderer, controls: OrbitControls;
let model: THREE.Mesh | null = null;
let animId = 0;

function initScene() {
  if (!containerRef.value) return;
  const w = containerRef.value.clientWidth;
  const h = containerRef.value.clientHeight || 300;
  scene = new THREE.Scene();
  scene.background = new THREE.Color('#F7F8FA');
  camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 1000);
  camera.position.set(5, 4, 6);
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(w, h);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  containerRef.value.appendChild(renderer.domElement);
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  // Lights
  scene.add(new THREE.AmbientLight(0xffffff, 0.6));
  const dir = new THREE.DirectionalLight(0xffffff, 0.8);
  dir.position.set(5, 10, 5);
  scene.add(dir);
  // Grid
  const grid = new THREE.GridHelper(10, 10, '#E2E8F0', '#E2E8F0');
  scene.add(grid);
  animate();
}

function animate() {
  animId = requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}

async function loadModel(url: string) {
  if (!scene) initScene();
  if (model) { scene!.remove(model); model = null; }
  const ext = url.split('.').pop()?.toLowerCase();
  try {
    if (ext === 'stl') {
      const loader = new STLLoader();
      const geometry = await loader.loadAsync(url);
      const mat = new THREE.MeshPhongMaterial({ color: '#2563EB', specular: '#111', shininess: 30 });
      model = new THREE.Mesh(geometry, mat);
      model.rotation.x = -Math.PI / 2;
      scene!.add(model);
      hasModel.value = true;
      // Fit camera
      geometry.computeBoundingBox();
      const box = geometry.boundingBox!;
      const size = box.getSize(new THREE.Vector3()).length();
      camera.position.set(size * 0.8, size * 0.6, size * 0.8);
      controls.target.copy(box.getCenter(new THREE.Vector3()));
      controls.update();
    } else if (ext === 'step' || ext === 'stp') {
      // STEP: show a placeholder cube (full STEP support needs occ-wasm)
      const geo = new THREE.BoxGeometry(2, 0.2, 1.5);
      const mat = new THREE.MeshPhongMaterial({ color: '#F97316', specular: '#111', shininess: 30, transparent: true, opacity: 0.85 });
      model = new THREE.Mesh(geo, mat);
      scene!.add(model);
      hasModel.value = true;
    }
  } catch (e) {
    console.error('3D load error:', e);
    hasModel.value = false;
  }
}

function resetView() {
  camera.position.set(5, 4, 6);
  controls.target.set(0, 0, 0);
  controls.update();
}

function toggleWireframe() {
  wireframe.value = !wireframe.value;
  if (model && model.material) {
    const mat = model.material as THREE.MeshPhongMaterial;
    mat.wireframe = wireframe.value;
  }
}

watch(() => props.fileUrl, (url) => {
  if (url) { nextTick(() => loadModel(url)); }
});

onMounted(() => {
  if (props.fileUrl) loadModel(props.fileUrl);
  else initScene();
});

onBeforeUnmount(() => {
  cancelAnimationFrame(animId);
  if (renderer) renderer.dispose();
});
</script>

<style scoped>
.mp-root { border-radius: 12px; overflow: hidden; border: 1px solid var(--border); background: var(--surface-sunken); }
.mp-container { width: 100%; height: 320px; }
.mp-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 200px; color: var(--text-muted); gap: 8px; }
.mp-empty-icon { opacity: 0.3; }
.mp-controls { display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: var(--surface); border-top: 1px solid var(--border); }
.mp-info { font-size: var(--fz-sm); color: var(--text-muted); flex: 1; }
.mp-btn { padding: 4px 10px; border-radius: 6px; border: 1px solid var(--border); background: var(--surface); color: var(--text-muted); font-size: var(--fz-xs); cursor: pointer; font-family: inherit; }
.mp-btn:hover { border-color: var(--brand); color: var(--brand); }
</style>
