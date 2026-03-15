import { create } from 'zustand';
import { User, Group } from '../types';
import { api } from '../services/api';

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isLoading: true,

  login: async (email: string, password: string) => {
    const response = await api.login({ email, password });
    api.setToken(response.access_token);
    const user = await api.getMe();
    set({ user, token: response.access_token });
  },

  register: async (email: string, password: string, fullName?: string) => {
    await api.register({ email, password, full_name: fullName });
    await api.login({ email, password });
    const user = await api.getMe();
    set({ user });
  },

  logout: () => {
    api.clearToken();
    set({ user: null, token: null });
  },

  checkAuth: async () => {
    const token = localStorage.getItem('token');
    if (token) {
      api.setToken(token);
      try {
        const user = await api.getMe();
        set({ user, token, isLoading: false });
      } catch {
        set({ isLoading: false });
      }
    } else {
      set({ isLoading: false });
    }
  },
}));

interface GroupState {
  groups: Group[];
  currentGroup: Group | null;
  isLoading: boolean;
  fetchGroups: () => Promise<void>;
  setCurrentGroup: (group: Group | null) => void;
  addGroup: (group: Group) => void;
}

export const useGroupStore = create<GroupState>((set) => ({
  groups: [],
  currentGroup: null,
  isLoading: false,

  fetchGroups: async () => {
    set({ isLoading: true });
    const groups = await api.getGroups();
    set({ groups, isLoading: false });
  },

  setCurrentGroup: (group) => set({ currentGroup: group }),

  addGroup: (group) => set((state) => ({ groups: [...state.groups, group] })),
}));
