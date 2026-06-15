<template>
  <div class="auth-view" :class="{ 'auth-view--dark': isDark }">
    <canvas ref="particlesCanvas" class="auth-view__particles"></canvas>

    <button class="auth-view__theme-btn" @click="toggleDark" :aria-label="isDark ? '亮色模式' : '暗色模式'">
      <Sun v-if="isDark" :size="20" />
      <Moon v-else :size="20" />
    </button>

    <div class="auth-view__container">
      <div class="auth-view__brand">
        <div class="auth-view__logo">V</div>
        <div>
          <div class="auth-view__brand-name">Vekus</div>
          <div class="auth-view__brand-sub">AI 智能报价工作台</div>
        </div>
      </div>

      <div class="auth-view__card">
        <div class="auth-view__header">
          <h1>创建账户</h1>
          <p>注册后即可使用 AI 报价服务</p>
        </div>

        <form class="auth-view__form" @submit.prevent="handleRegister">
          <!-- Role toggle -->
          <div class="auth-view__role-toggle">
            <button
              type="button"
              :class="['auth-view__role-btn', { 'auth-view__role-btn--active': form.role === 'sales' }]"
              @click="form.role = 'sales'"
            >
              <User :size="18" /> 业务员
            </button>
            <button
              type="button"
              :class="['auth-view__role-btn', { 'auth-view__role-btn--active': form.role === 'boss' }]"
              @click="form.role = 'boss'"
            >
              <Briefcase :size="18" /> 老板
            </button>
          </div>

          <!-- Name -->
          <div class="auth-field" :class="{ 'auth-field--focused': nameFocused || form.name }">
            <input
              id="reg-name"
              v-model="form.name"
              type="text"
              class="auth-field__input"
              placeholder=" "
              @focus="nameFocused = true"
              @blur="nameFocused = false"
            />
            <label for="reg-name" class="auth-field__label">姓名</label>
          </div>

          <!-- Phone -->
          <div
            class="auth-field"
            :class="{ 'auth-field--focused': phoneFocused || form.phone, 'auth-field--error': !!errorMsg && !form.phone }"
          >
            <input
              id="reg-phone"
              v-model="form.phone"
              type="text"
              class="auth-field__input"
              placeholder=" "
              @focus="phoneFocused = true"
              @blur="phoneFocused = false"
            />
            <label for="reg-phone" class="auth-field__label">手机号</label>
          </div>

          <!-- Password -->
          <div class="auth-field" :class="{ 'auth-field--focused': passFocused || form.password }">
            <input
              id="reg-pass"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              class="auth-field__input"
              placeholder=" "
              @focus="passFocused = true"
              @blur="passFocused = false"
            />
            <label for="reg-pass" class="auth-field__label">密码（至少6位）</label>
            <button
              type="button"
              class="auth-field__toggle-pwd"
              @click="showPassword = !showPassword"
              :aria-label="showPassword ? '隐藏密码' : '显示密码'"
            >
              <EyeOff v-if="showPassword" :size="18" />
              <Eye v-else :size="18" />
            </button>
          </div>

          <!-- Company (both roles) -->
          <div class="auth-field" :class="{ 'auth-field--focused': companyFocused || form.company }">
            <input
              id="reg-company"
              v-model="form.company"
              type="text"
              class="auth-field__input"
              placeholder=" "
              @focus="companyFocused = true"
              @blur="companyFocused = false"
            />
            <label for="reg-company" class="auth-field__label">
              {{ form.role === 'boss' ? '工厂/公司名称' : '选择或输入公司' }}
            </label>
          </div>

          <p v-if="errorMsg" class="auth-view__error">{{ errorMsg }}</p>

          <button type="submit" class="auth-view__submit" :disabled="loading">
            <span v-if="loading" class="auth-view__spinner"></span>
            <span v-else>注 册</span>
          </button>
        </form>

        <div class="auth-view__separator">
          <span>或者使用以下方式</span>
        </div>

        <div class="auth-view__social">
          <button class="auth-view__social-btn auth-view__social-btn--wechat" @click="showQr = true" aria-label="微信登录">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178A1.17 1.17 0 0 1 4.623 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178 1.17 1.17 0 0 1-1.162-1.178c0-.651.52-1.18 1.162-1.18zm3.064 2.748c-3.354 0-6.073 2.455-6.073 5.483 0 2.707 2.187 4.99 5.097 5.399l1.202.668a.361.361 0 0 0 .33-.019c.217-.138.503.023.428.266l-.228.852c-.04.148.1.29.248.204l1.612-.943a.504.504 0 0 1 .473-.04c.725.318 1.524.497 2.357.497 3.354 0 6.073-2.455 6.073-5.484 0-3.028-2.72-5.483-6.073-5.483zm-2.06 2.445c.436 0 .79.37.79.825a.808.808 0 0 1-.79.825.808.808 0 0 1-.79-.825c0-.456.353-.825.79-.825zm4.12 0c.437 0 .79.37.79.825a.808.808 0 0 1-.79.825.808.808 0 0 1-.79-.825c0-.456.354-.825.79-.825z"/></svg>
          </button>
        </div>

        <!-- QR Code Modal -->
        <teleport to="body">
          <div v-if="showQr" class="qr-overlay" @click.self="showQr = false">
            <div class="qr-modal">
              <button class="qr-modal__close" @click="showQr = false" aria-label="关闭">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
              <div class="qr-modal__icon">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="#07c160"><path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178A1.17 1.17 0 0 1 4.623 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178 1.17 1.17 0 0 1-1.162-1.178c0-.651.52-1.18 1.162-1.18zm3.064 2.748c-3.354 0-6.073 2.455-6.073 5.483 0 2.707 2.187 4.99 5.097 5.399l1.202.668a.361.361 0 0 0 .33-.019c.217-.138.503.023.428.266l-.228.852c-.04.148.1.29.248.204l1.612-.943a.504.504 0 0 1 .473-.04c.725.318 1.524.497 2.357.497 3.354 0 6.073-2.455 6.073-5.484 0-3.028-2.72-5.483-6.073-5.483zm-2.06 2.445c.436 0 .79.37.79.825a.808.808 0 0 1-.79.825.808.808 0 0 1-.79-.825c0-.456.353-.825.79-.825zm4.12 0c.437 0 .79.37.79.825a.808.808 0 0 1-.79.825.808.808 0 0 1-.79-.825c0-.456.354-.825.79-.825z"/></svg>
              </div>
              <p class="qr-modal__title">微信扫码注册</p>
              <div class="qr-modal__code">
                <canvas ref="qrCanvas" width="200" height="200"></canvas>
              </div>
              <p class="qr-modal__hint">请使用微信扫描二维码</p>
            </div>
          </div>
        </teleport>

        <p class="auth-view__switch">
          已有账户？<router-link to="/login">立即登录</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { Eye, EyeOff, Sun, Moon, User, Briefcase } from 'lucide-vue-next';
import { useAuthStore } from '@/stores/auth';
import { api, setToken } from '@/api/client';

const router = useRouter();
const authStore = useAuthStore();

const loading = ref(false);
const errorMsg = ref('');
const showPassword = ref(false);
const isDark = ref(false);
const nameFocused = ref(false);
const phoneFocused = ref(false);
const passFocused = ref(false);
const companyFocused = ref(false);
const showQr = ref(false);
const qrCanvas = ref<HTMLCanvasElement | null>(null);

const form = reactive({
  name: '',
  phone: '',
  password: '',
  role: 'sales' as 'sales' | 'boss',
  company: '',
});

function toggleDark() {
  isDark.value = !isDark.value;
}

// QR code generation
function drawQr() {
  const canvas = qrCanvas.value;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  const size = 200;
  ctx.clearRect(0, 0, size, size);
  const moduleCount = 21;
  const moduleSize = size / (moduleCount + 8);
  const offset = 4 * moduleSize;
  function drawFinder(x: number, y: number) {
    ctx!.fillStyle = '#111';
    ctx!.fillRect(x, y, 7 * moduleSize, 7 * moduleSize);
    ctx!.fillStyle = '#fff';
    ctx!.fillRect(x + moduleSize, y + moduleSize, 5 * moduleSize, 5 * moduleSize);
    ctx!.fillStyle = '#111';
    ctx!.fillRect(x + 2 * moduleSize, y + 2 * moduleSize, 3 * moduleSize, 3 * moduleSize);
  }
  drawFinder(offset, offset);
  drawFinder(offset + (moduleCount - 7) * moduleSize, offset);
  drawFinder(offset, offset + (moduleCount - 7) * moduleSize);
  ctx.fillStyle = '#111';
  for (let r = 0; r < moduleCount; r++) {
    for (let c = 0; c < moduleCount; c++) {
      if (r < 8 && c < 8) continue;
      if (r < 8 && c > moduleCount - 9) continue;
      if (r > moduleCount - 9 && c < 8) continue;
      if (Math.random() > 0.5) {
        ctx.fillRect(offset + c * moduleSize, offset + r * moduleSize, moduleSize, moduleSize);
        ctx.fillRect(offset + c * moduleSize + 1, offset + r * moduleSize + 1, moduleSize - 2, moduleSize - 2);
      }
    }
  }
  ctx.fillStyle = '#fff';
  const cx = offset + (moduleCount / 2) * moduleSize;
  const cz = 3 * moduleSize;
  ctx.fillRect(cx - cz, cx - cz, cz * 2, cz * 2);
  ctx.fillStyle = '#07c160';
  ctx.beginPath();
  ctx.arc(cx, cx, cz - 2, 0, Math.PI * 2);
  ctx.fill();
}
watch(showQr, (v) => { if (v) setTimeout(drawQr, 100); })

async function handleRegister() {
  if (!form.name || !form.phone || !form.password) {
    errorMsg.value = '请填写必填项';
    return;
  }
  if (form.password.length < 6) {
    errorMsg.value = '密码至少6位';
    return;
  }
  loading.value = true;
  errorMsg.value = '';
  try {
    const result = await api.post<{ token: string; user: any }>('/auth/register', form);
    if (result.error) {
      errorMsg.value = result.error;
      return;
    }
    setToken(result.data.token);
    authStore.setUser(result.data.user);
    authStore.setToken(result.data.token);
    router.push('/quote');
  } catch {
    errorMsg.value = '注册失败，请重试';
  } finally {
    loading.value = false;
  }
}

// Particle canvas (same as login)
const particlesCanvas = ref<HTMLCanvasElement | null>(null);
let animFrame = 0;

function initParticles() {
  const canvas = particlesCanvas.value;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const resize = () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  };
  resize();
  window.addEventListener('resize', resize);

  class Particle {
    x: number; y: number; size: number; speedX: number; speedY: number; color: string;
    constructor(w: number, h: number, dark: boolean) {
      this.x = Math.random() * w;
      this.y = Math.random() * h;
      this.size = Math.random() * 2.5 + 0.8;
      this.speedX = (Math.random() - 0.5) * 0.4;
      this.speedY = (Math.random() - 0.5) * 0.4;
      const alpha = Math.random() * 0.15;
      this.color = dark ? `rgba(255,255,255,${alpha})` : `rgba(59,130,246,${alpha})`;
    }
    update(w: number, h: number) {
      this.x += this.speedX; this.y += this.speedY;
      if (this.x > w) this.x = 0; if (this.x < 0) this.x = w;
      if (this.y > h) this.y = 0; if (this.y < 0) this.y = h;
    }
    draw(ctx: CanvasRenderingContext2D) {
      ctx.fillStyle = this.color;
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  const particles: Particle[] = [];
  const count = Math.min(80, Math.floor((canvas.width * canvas.height) / 18000));
  for (let i = 0; i < count; i++) particles.push(new Particle(canvas.width, canvas.height, isDark.value));

  function animate() {
    if (!ctx || !canvas) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (const p of particles) { p.update(canvas.width, canvas.height); p.draw(ctx); }
    animFrame = requestAnimationFrame(animate);
  }
  animate();
}

onMounted(() => {
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  isDark.value = prefersDark;
  initParticles();
});

onUnmounted(() => cancelAnimationFrame(animFrame));
</script>

<style scoped>
/* Shared styles with LoginView */
.auth-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #0b1c3a 0%, #102b5c 40%, #0f2044 100%);
  font-family: var(--font-sans);
  transition: background 0.6s;
}
.auth-view--dark { background: linear-gradient(135deg, #030712 0%, #0a0f1e 40%, #020617 100%); }
.auth-view__particles { position: absolute; inset: 0; z-index: 0; pointer-events: none; }
.auth-view__theme-btn {
  position: absolute; top: 24px; right: 24px; z-index: 10;
  width: 42px; height: 42px; border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.15); background: rgba(255,255,255,0.06);
  color: rgba(255,255,255,0.8); cursor: pointer;
  display: grid; place-items: center; backdrop-filter: blur(12px); transition: all 0.25s;
}
.auth-view__theme-btn:hover { background: rgba(255,255,255,0.14); border-color: rgba(255,255,255,0.3); color: #fff; }
.auth-view__container { position: relative; z-index: 1; width: 100%; max-width: 440px; padding: 24px; display: flex; flex-direction: column; gap: 28px; }
.auth-view__brand { display: flex; align-items: center; justify-content: center; gap: 14px; color: #fff; }
.auth-view__logo {
  width: 50px; height: 50px; border-radius: 14px;
  background: linear-gradient(135deg, #3b82f6, #f97316);
  display: grid; place-items: center; font-size: 26px; font-weight: 700;
  box-shadow: 0 12px 40px rgba(59,130,246,0.35);
}
.auth-view__brand-name { font-size: 22px; font-weight: 700; letter-spacing: 0.02em; }
.auth-view__brand-sub { font-size: 13px; opacity: 0.65; margin-top: 2px; }
.auth-view__card {
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px; padding: 36px 32px;
  backdrop-filter: blur(24px); box-shadow: 0 24px 80px rgba(0,0,0,0.25);
}
.auth-view__header { text-align: center; margin-bottom: 28px; }
.auth-view__header h1 { margin: 0; font-size: 24px; font-weight: 700; color: #fff; }
.auth-view__header p { margin: 6px 0 0; font-size: 14px; color: rgba(255,255,255,0.5); }
.auth-view__form { display: flex; flex-direction: column; gap: 18px; }

/* Role toggle */
.auth-view__role-toggle { display: flex; gap: 8px; }
.auth-view__role-btn {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 7px;
  padding: 11px; border-radius: 12px;
  border: 1.5px solid rgba(255,255,255,0.12); background: rgba(255,255,255,0.04);
  color: rgba(255,255,255,0.5); font-size: 14px; font-family: inherit;
  font-weight: 500; cursor: pointer; transition: all 0.25s;
}
.auth-view__role-btn:hover { background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.8); }
.auth-view__role-btn--active {
  border-color: #3b82f6; background: rgba(59,130,246,0.15);
  color: #60a5fa; box-shadow: 0 0 0 2px rgba(59,130,246,0.1);
}

/* Floating label fields */
.auth-field { position: relative; }
.auth-field__input {
  width: 100%; padding: 16px 14px 8px; border-radius: 12px;
  border: 1.5px solid rgba(255,255,255,0.12); background: rgba(255,255,255,0.04);
  color: #fff; font-size: 15px; font-family: inherit; outline: none;
  transition: all 0.25s; box-sizing: border-box;
}
.auth-field__input:focus { border-color: rgba(59,130,246,0.6); background: rgba(255,255,255,0.07); box-shadow: 0 0 0 3px rgba(59,130,246,0.1); }
.auth-field--focused .auth-field__input { border-color: rgba(59,130,246,0.5); }
.auth-field--error .auth-field__input { border-color: rgba(239,68,68,0.6); }
.auth-field__label {
  position: absolute; left: 14px; top: 50%; transform: translateY(-50%);
  font-size: 14px; color: rgba(255,255,255,0.4); pointer-events: none; transition: all 0.2s;
}
.auth-field__input:focus + .auth-field__label,
.auth-field__input:not(:placeholder-shown) + .auth-field__label {
  top: 8px; transform: translateY(0); font-size: 10px; color: rgba(59,130,246,0.8);
}
.auth-field--error .auth-field__label { color: rgba(239,68,68,0.8); }
.auth-field__toggle-pwd {
  position: absolute; right: 12px; top: 50%; transform: translateY(-50%);
  background: none; border: none; color: rgba(255,255,255,0.4);
  cursor: pointer; padding: 6px; display: grid; place-items: center; transition: color 0.2s;
}
.auth-field__toggle-pwd:hover { color: rgba(255,255,255,0.8); }

/* Error, Submit, Separator, Social, Switch */
.auth-view__error { margin: 0; color: #f87171; font-size: 13px; text-align: center; }
.auth-view__submit {
  width: 100%; padding: 14px; border: none; border-radius: 12px;
  background: linear-gradient(135deg, #3b82f6, #2563eb); color: #fff;
  font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.3s;
  letter-spacing: 0.04em; font-family: inherit;
}
.auth-view__submit:hover:not(:disabled) { background: linear-gradient(135deg, #60a5fa, #3b82f6); box-shadow: 0 8px 30px rgba(59,130,246,0.35); transform: translateY(-1px); }
.auth-view__submit:disabled { opacity: 0.6; cursor: not-allowed; }
.auth-view__spinner { width: 20px; height: 20px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.7s linear infinite; display: block; margin: 0 auto; }
@keyframes spin { to { transform: rotate(360deg); } }
.auth-view__separator { margin: 22px 0 16px; text-align: center; position: relative; }
.auth-view__separator::before { content: ''; position: absolute; left: 0; top: 50%; width: 100%; height: 1px; background: rgba(255,255,255,0.08); }
.auth-view__separator span { position: relative; padding: 0 14px; font-size: 12px; color: rgba(255,255,255,0.35); background: linear-gradient(135deg, #0b1c3a, #102b5c); }
.auth-view__social { display: flex; justify-content: center; gap: 14px; }
.auth-view__social-btn {
  width: 42px; height: 42px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.04); color: rgba(255,255,255,0.55);
  cursor: pointer; display: grid; place-items: center; transition: all 0.25s;
}
.auth-view__social-btn:hover { background: rgba(255,255,255,0.12); border-color: rgba(255,255,255,0.3); transform: translateY(-2px); }
.auth-view__social-btn--wechat { width: auto; padding: 0 20px; gap: 8px; font-size: 14px; font-family: inherit; font-weight: 500; border-color: rgba(7,193,96,0.3); color: #07c160; }
.auth-view__social-btn--wechat:hover { background: rgba(7,193,96,0.12); border-color: #07c160; color: #07c160; }
.auth-view__switch { margin: 20px 0 0; text-align: center; font-size: 14px; color: rgba(255,255,255,0.45); }
.auth-view__switch a { color: #60a5fa; text-decoration: none; font-weight: 600; transition: color 0.2s; }
.auth-view__switch a:hover { color: #93bbfd; }

@media (max-width: 480px) {
  .auth-view__container { padding: 16px; }
  .auth-view__card { padding: 28px 20px; border-radius: 16px; }
}

/* ===== Animated Logo ===== */
.auth-view__logo {
  position: relative;
  overflow: hidden;
  animation: logoPulse 3s ease-in-out infinite;
}
.auth-view__logo::before {
  content: '';
  position: absolute;
  inset: -2px;
  border-radius: 16px;
  background: linear-gradient(270deg, #3b82f6, #f97316, #06b6d4, #3b82f6);
  background-size: 300% 100%;
  z-index: -1;
  animation: logoGlow 4s linear infinite;
}
.auth-view__logo::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 14px;
  background: linear-gradient(135deg, #1e40af, #0b1c3a);
}
@keyframes logoPulse {
  0%, 100% { transform: scale(1); box-shadow: 0 12px 40px rgba(59,130,246,0.35); }
  50% { transform: scale(1.06); box-shadow: 0 20px 56px rgba(59,130,246,0.55), 0 0 80px rgba(6,182,212,0.25); }
}
@keyframes logoGlow {
  0% { background-position: 0% 50%; }
  100% { background-position: 300% 50%; }
}

/* ===== QR Modal ===== */
.qr-overlay {
  position: fixed;
  inset: 0;
  z-index: 10000;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.25s ease-out;
}
.qr-modal {
  background: #fff;
  border-radius: 20px;
  padding: 36px 32px 28px;
  position: relative;
  text-align: center;
  box-shadow: 0 24px 80px rgba(0,0,0,0.35);
  max-width: 320px;
  width: 90%;
  animation: modalIn 0.3s ease-out;
}
.qr-modal__close {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(0,0,0,0.06);
  color: #666;
  cursor: pointer;
  display: grid;
  place-items: center;
  transition: all 0.2s;
}
.qr-modal__close:hover { background: rgba(0,0,0,0.12); color: #111; }
.qr-modal__icon { margin-bottom: 12px; }
.qr-modal__title { margin: 0 0 16px; font-size: 18px; font-weight: 700; color: #111; }
.qr-modal__code {
  background: #f8f8f8;
  border-radius: 12px;
  padding: 16px;
  display: inline-block;
}
.qr-modal__code canvas { display: block; }
.qr-modal__hint { margin: 14px 0 0; font-size: 12px; color: #999; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes modalIn { from { opacity: 0; transform: scale(0.92) translateY(20px); } to { opacity: 1; transform: scale(1) translateY(0); } }
</style>
