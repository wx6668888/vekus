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

          <!-- Factory name (boss only) -->
          <div
            v-if="form.role === 'boss'"
            class="auth-field"
            :class="{ 'auth-field--focused': factoryFocused || form.factory_name }"
          >
            <input
              id="reg-factory"
              v-model="form.factory_name"
              type="text"
              class="auth-field__input"
              placeholder=" "
              @focus="factoryFocused = true"
              @blur="factoryFocused = false"
            />
            <label for="reg-factory" class="auth-field__label">工厂/公司名称（选填）</label>
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
          <button class="auth-view__social-btn" aria-label="Github">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
          </button>
          <button class="auth-view__social-btn" aria-label="Twitter">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
          </button>
          <button class="auth-view__social-btn" aria-label="Linkedin">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
          </button>
        </div>

        <p class="auth-view__switch">
          已有账户？<router-link to="/login">立即登录</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue';
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
const factoryFocused = ref(false);

const form = reactive({
  name: '',
  phone: '',
  password: '',
  role: 'sales' as 'sales' | 'boss',
  factory_name: '',
});

function toggleDark() {
  isDark.value = !isDark.value;
}

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
.auth-view__social-btn:hover { background: rgba(255,255,255,0.12); border-color: rgba(255,255,255,0.25); color: #fff; transform: translateY(-2px); }
.auth-view__switch { margin: 20px 0 0; text-align: center; font-size: 14px; color: rgba(255,255,255,0.45); }
.auth-view__switch a { color: #60a5fa; text-decoration: none; font-weight: 600; transition: color 0.2s; }
.auth-view__switch a:hover { color: #93bbfd; }

@media (max-width: 480px) {
  .auth-view__container { padding: 16px; }
  .auth-view__card { padding: 28px 20px; border-radius: 16px; }
}
</style>
