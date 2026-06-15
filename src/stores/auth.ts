import { defineStore } from 'pinia';

export type UserRole = 'boss' | 'sales' | 'customer' | 'admin';

export interface User {
  id: string;
  name: string;
  phone: string;
  role: UserRole;
  factoryName?: string;
  avatar?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    token: localStorage.getItem('vekus_auth_token'),
    isAuthenticated: !!localStorage.getItem('vekus_auth_token'),
  }),

  getters: {
    isBoss: (state) => state.user?.role === 'boss',
    isSales: (state) => state.user?.role === 'sales',
    isAdmin: (state) => state.user?.role === 'admin',
  },

  actions: {
    setUser(user: User) {
      this.user = user;
      this.isAuthenticated = true;
      localStorage.setItem('vekus_user_role', user.role);
    },
    setToken(token: string) {
      this.token = token;
      localStorage.setItem('vekus_auth_token', token);
      this.isAuthenticated = true;
    },
    logout() {
      this.user = null;
      this.token = null;
      this.isAuthenticated = false;
      localStorage.removeItem('vekus_auth_token');
      localStorage.removeItem('vekus_user_role');
    },
  },
});
