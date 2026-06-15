import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/quote' },
  { path: '/login', component: () => import('@/views/LoginView.vue') },
  { path: '/quote', component: () => import('@/views/QuoteView.vue') },
  { path: '/quote/:id', component: () => import('@/views/QuoteView.vue') },
  { path: '/quote/result/:id', component: () => import('@/views/QuoteResultView.vue') },
  { path: '/history', component: () => import('@/views/HistoryView.vue') },
  { path: '/customers', component: () => import('@/views/CustomersView.vue') },
  { path: '/marketplace', component: () => import('@/views/MarketplaceView.vue') },
  { path: '/marketplace/:id', component: () => import('@/views/MarketplaceDetailView.vue') },
  { path: '/marketplace/post', component: () => import('@/views/MarketplacePostView.vue') },
  { path: '/messages', component: () => import('@/views/MessagesView.vue') },
  { path: '/messages/:id', component: () => import('@/views/ChatView.vue') },
  { path: '/pricing', component: () => import('@/views/PricingView.vue') },
  { path: '/settings', component: () => import('@/views/SettingsView.vue') },
  { path: '/dashboard', component: () => import('@/views/DashboardView.vue') },
  { path: '/share/:id', component: () => import('@/views/ShareView.vue'), meta: { public: true } },
  { path: '/me', component: () => import('@/views/MeView.vue') },
  { path: '/account-security', component: () => import('@/views/AccountSecurityView.vue') },
  { path: '/help', component: () => import('@/views/HelpFeedbackView.vue') },
  { path: '/about', component: () => import('@/views/AboutView.vue') },
  { path: '/register', component: () => import('@/views/RegisterView.vue'), meta: { public: true } },
  { path: '/customers/:id', component: () => import('@/views/CustomerDetailView.vue') },
  { path: '/points', component: () => import('@/views/PointsTransactionView.vue') },
  { path: '/boss/sales', component: () => import('@/views/BossSalesView.vue') },
  { path: '/admin/users', component: () => import('@/views/AdminUsersView.vue') },
  { path: '/bom', component: () => import('@/views/BomView.vue') },
  { path: '/inventory', component: () => import('@/views/InventoryView.vue') },
  { path: '/production', component: () => import('@/views/ProductionView.vue') },
  { path: '/quality', component: () => import('@/views/QualityView.vue') },
  { path: '/purchases', component: () => import('@/views/PurchaseView.vue') },
  { path: '/approvals', component: () => import('@/views/ApprovalView.vue') },
  { path: '/documents', component: () => import('@/views/DocumentsView.vue') },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  const token = localStorage.getItem('vekus_auth_token');
  const userRole = localStorage.getItem('vekus_user_role');
  const publicPaths = ['/login', '/register', '/share'];
  if (!token && !publicPaths.some(p => to.path.startsWith(p)) && !to.meta?.public) {
    return '/login';
  }
  if (token && (to.path === '/login' || to.path === '/register')) {
    return '/quote';
  }
  // Admin pages: boss only
  if (to.path.startsWith('/admin') && userRole !== 'boss') {
    return '/quote';
  }
});

export default router;
