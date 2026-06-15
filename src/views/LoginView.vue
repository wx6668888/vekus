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
          <h1>欢迎回来</h1>
          <p>请登录以继续使用</p>
        </div>

        <form class="auth-view__form" @submit.prevent="handleLogin">
          <div
            class="auth-field"
            :class="{ 'auth-field--focused': emailFocused || phone, 'auth-field--error': !!errorMsg && !phone }"
          >
            <input
              id="login-phone"
              v-model="phone"
              type="text"
              class="auth-field__input"
              placeholder=" "
              @focus="emailFocused = true"
              @blur="emailFocused = false"
            />
            <label for="login-phone" class="auth-field__label">手机号</label>
          </div>

          <div
            class="auth-field"
            :class="{ 'auth-field--focused': passFocused || password }"
          >
            <input
              id="login-pass"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              class="auth-field__input"
              placeholder=" "
              @focus="passFocused = true"
              @blur="passFocused = false"
            />
            <label for="login-pass" class="auth-field__label">密码</label>
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

          <div class="auth-view__options">
            <label class="auth-view__remember">
              <input type="checkbox" v-model="rememberMe" />
              <span class="auth-view__checkmark"></span>
              记住我
            </label>
            <a href="#" class="auth-view__forgot">忘记密码？</a>
          </div>

          <p v-if="errorMsg" class="auth-view__error">{{ errorMsg }}</p>

          <button type="submit" class="auth-view__submit" :disabled="loading">
            <span v-if="loading" class="auth-view__spinner"></span>
            <span v-else>登 录</span>
          </button>
        </form>

        <div class="auth-view__separator">
          <span>或者使用以下方式</span>
        </div>

        <div class="auth-view__social">
          <button class="auth-view__social-btn auth-view__social-btn--wechat" aria-label="微信">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178A1.17 1.17 0 0 1 4.623 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178 1.17 1.17 0 0 1-1.162-1.178c0-.651.52-1.18 1.162-1.18zm3.064 2.748c-3.354 0-6.073 2.455-6.073 5.483 0 2.707 2.187 4.99 5.097 5.399l1.202.668a.361.361 0 0 0 .33-.019c.217-.138.503.023.428.266l-.228.852c-.04.148.1.29.248.204l1.612-.943a.504.504 0 0 1 .473-.04c.725.318 1.524.497 2.357.497 3.354 0 6.073-2.455 6.073-5.484 0-3.028-2.72-5.483-6.073-5.483zm-2.06 2.445c.436 0 .79.37.79.825a.808.808 0 0 1-.79.825.808.808 0 0 1-.79-.825c0-.456.353-.825.79-.825zm4.12 0c.437 0 .79.37.79.825a.808.808 0 0 1-.79.825.808.808 0 0 1-.79-.825c0-.456.354-.825.79-.825z"/></svg>
            <span>微信登录</span>
          </button>
        </div>

        <p class="auth-view__switch">
          还没有账户？<router-link to="/register">立即注册</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { Eye, EyeOff, Sun, Moon } from 'lucide-vue-next';
import { useAuthStore } from '@/stores/auth';
import { api, setToken } from '@/api/client';

const router = useRouter();
const authStore = useAuthStore();

const phone = ref('');
const password = ref('');
const rememberMe = ref(false);
const showPassword = ref(false);
const loading = ref(false);
const errorMsg = ref('');
const emailFocused = ref(false);
const passFocused = ref(false);
const isDark = ref(false);

const particlesCanvas = ref<HTMLCanvasElement | null>(null);
let animFrame = 0;

function toggleDark() {
  isDark.value = !isDark.value;
}

async function handleLogin() {
  if (!phone.value || !password.value) {
    errorMsg.value = '请输入手机号和密码';
    return;
  }
  loading.value = true;
  errorMsg.value = '';
  try {
    const result = await api.post<{ token: string; user: any }>('/auth/login', {
      phone: phone.value,
      password: password.value,
    });
    if (result.error) {
      errorMsg.value = result.error;
      return;
    }
    setToken(result.data.token);
    authStore.setUser(result.data.user);
    authStore.setToken(result.data.token);
    router.push('/quote');
  } catch {
    errorMsg.value = '登录失败，请重试';
  } finally {
    loading.value = false;
  }
}

// Particle canvas animation
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
    x: number;
    y: number;
    size: number;
    speedX: number;
    speedY: number;
    color: string;
    constructor(w: number, h: number, dark: boolean) {
      this.x = Math.random() * w;
      this.y = Math.random() * h;
      this.size = Math.random() * 2.5 + 0.8;
      this.speedX = (Math.random() - 0.5) * 0.4;
      this.speedY = (Math.random() - 0.5) * 0.4;
      const alpha = Math.random() * 0.15;
      this.color = dark
        ? `rgba(255,255,255,${alpha})`
        : `rgba(59,130,246,${alpha})`;
    }
    update(w: number, h: number) {
      this.x += this.speedX;
      this.y += this.speedY;
      if (this.x > w) this.x = 0;
      if (this.x < 0) this.x = w;
      if (this.y > h) this.y = 0;
      if (this.y < 0) this.y = h;
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
    for (const p of particles) {
      p.update(canvas.width, canvas.height);
      p.draw(ctx);
    }
    animFrame = requestAnimationFrame(animate);
  }
  animate();
}

onMounted(() => {
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  isDark.value = prefersDark;
  initParticles();
});

onUnmounted(() => {
  cancelAnimationFrame(animFrame);
});
</script>

<style scoped>
/* ===== Layout ===== */
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
.auth-view--dark {
  background: linear-gradient(135deg, #030712 0%, #0a0f1e 40%, #020617 100%);
}

/* ===== Particles Canvas ===== */
.auth-view__particles {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

/* ===== Theme Toggle ===== */
.auth-view__theme-btn {
  position: absolute;
  top: 24px;
  right: 24px;
  z-index: 10;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.15);
  background: rgba(255,255,255,0.06);
  color: rgba(255,255,255,0.8);
  cursor: pointer;
  display: grid;
  place-items: center;
  backdrop-filter: blur(12px);
  transition: all 0.25s;
}
.auth-view__theme-btn:hover {
  background: rgba(255,255,255,0.14);
  border-color: rgba(255,255,255,0.3);
  color: #fff;
}

/* ===== Container ===== */
.auth-view__container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 440px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

/* ===== Brand ===== */
.auth-view__brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  color: #fff;
}
.auth-view__logo {
  width: 50px;
  height: 50px;
  border-radius: 14px;
  background: linear-gradient(135deg, #3b82f6, #f97316);
  display: grid;
  place-items: center;
  font-size: 26px;
  font-weight: 700;
  box-shadow: 0 12px 40px rgba(59,130,246,0.35);
}
.auth-view__brand-name {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 0.02em;
}
.auth-view__brand-sub {
  font-size: 13px;
  opacity: 0.65;
  margin-top: 2px;
}

/* ===== Card ===== */
.auth-view__card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  padding: 36px 32px;
  backdrop-filter: blur(24px);
  box-shadow: 0 24px 80px rgba(0,0,0,0.25);
}
.auth-view__header {
  text-align: center;
  margin-bottom: 28px;
}
.auth-view__header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #fff;
}
.auth-view__header p {
  margin: 6px 0 0;
  font-size: 14px;
  color: rgba(255,255,255,0.5);
}

/* ===== Form ===== */
.auth-view__form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* ===== Floating Label Field ===== */
.auth-field {
  position: relative;
}
.auth-field__input {
  width: 100%;
  padding: 16px 14px 8px;
  border-radius: 12px;
  border: 1.5px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.04);
  color: #fff;
  font-size: 15px;
  font-family: inherit;
  outline: none;
  transition: all 0.25s;
  box-sizing: border-box;
}
.auth-field__input:focus {
  border-color: rgba(59,130,246,0.6);
  background: rgba(255,255,255,0.07);
  box-shadow: 0 0 0 3px rgba(59,130,246,0.1);
}
.auth-field--focused .auth-field__input {
  border-color: rgba(59,130,246,0.5);
}
.auth-field--error .auth-field__input {
  border-color: rgba(239,68,68,0.6);
}
.auth-field__label {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 14px;
  color: rgba(255,255,255,0.4);
  pointer-events: none;
  transition: all 0.2s;
}
.auth-field__input:focus + .auth-field__label,
.auth-field__input:not(:placeholder-shown) + .auth-field__label {
  top: 8px;
  transform: translateY(0);
  font-size: 10px;
  color: rgba(59,130,246,0.8);
}
.auth-field--error .auth-field__label {
  color: rgba(239,68,68,0.8);
}

/* Password toggle */
.auth-field__toggle-pwd {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: rgba(255,255,255,0.4);
  cursor: pointer;
  padding: 6px;
  display: grid;
  place-items: center;
  transition: color 0.2s;
}
.auth-field__toggle-pwd:hover {
  color: rgba(255,255,255,0.8);
}

/* ===== Options ===== */
.auth-view__options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}
.auth-view__remember {
  display: flex;
  align-items: center;
  gap: 7px;
  color: rgba(255,255,255,0.6);
  cursor: pointer;
  user-select: none;
}
.auth-view__remember input {
  display: none;
}
.auth-view__checkmark {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 1.5px solid rgba(255,255,255,0.25);
  transition: all 0.2s;
  display: grid;
  place-items: center;
}
.auth-view__remember input:checked + .auth-view__checkmark {
  background: #3b82f6;
  border-color: #3b82f6;
}
.auth-view__remember input:checked + .auth-view__checkmark::after {
  content: '✓';
  color: #fff;
  font-size: 10px;
  font-weight: 700;
}
.auth-view__forgot {
  color: rgba(255,255,255,0.5);
  text-decoration: none;
  transition: color 0.2s;
}
.auth-view__forgot:hover {
  color: #60a5fa;
}

/* ===== Error ===== */
.auth-view__error {
  margin: 0;
  color: #f87171;
  font-size: 13px;
  text-align: center;
}

/* ===== Submit ===== */
.auth-view__submit {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  letter-spacing: 0.04em;
  font-family: inherit;
}
.auth-view__submit:hover:not(:disabled) {
  background: linear-gradient(135deg, #60a5fa, #3b82f6);
  box-shadow: 0 8px 30px rgba(59,130,246,0.35);
  transform: translateY(-1px);
}
.auth-view__submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.auth-view__spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: block;
  margin: 0 auto;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ===== Separator ===== */
.auth-view__separator {
  margin: 22px 0 16px;
  text-align: center;
  position: relative;
}
.auth-view__separator::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  width: 100%;
  height: 1px;
  background: rgba(255,255,255,0.08);
}
.auth-view__separator span {
  position: relative;
  background: var(--bg, #0b1c3a);
  background: linear-gradient(135deg, #0b1c3a 0%, #102b5c 100%);
  padding: 0 14px;
  font-size: 12px;
  color: rgba(255,255,255,0.35);
}

/* ===== Social ===== */
.auth-view__social {
  display: flex;
  justify-content: center;
  gap: 14px;
}
.auth-view__social-btn {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.04);
  color: rgba(255,255,255,0.55);
  cursor: pointer;
  display: grid;
  place-items: center;
  transition: all 0.25s;
}
.auth-view__social-btn:hover {
  background: rgba(255,255,255,0.12);
  border-color: rgba(255,255,255,0.3);
  transform: translateY(-2px);
}
.auth-view__social-btn--wechat {
  width: auto;
  padding: 0 20px;
  gap: 8px;
  font-size: 14px;
  font-family: inherit;
  font-weight: 500;
  border-color: rgba(7,193,96,0.3);
  color: #07c160;
}
.auth-view__social-btn--wechat:hover {
  background: rgba(7,193,96,0.12);
  border-color: #07c160;
  color: #07c160;
}

/* ===== Switch ===== */
.auth-view__switch {
  margin: 20px 0 0;
  text-align: center;
  font-size: 14px;
  color: rgba(255,255,255,0.45);
}
.auth-view__switch a {
  color: #60a5fa;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s;
}
.auth-view__switch a:hover {
  color: #93bbfd;
}

/* ===== Responsive ===== */
@media (max-width: 480px) {
  .auth-view__container {
    padding: 16px;
  }
  .auth-view__card {
    padding: 28px 20px;
    border-radius: 16px;
  }
}
</style>
