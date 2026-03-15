import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { 
  AuthResponse, LoginCredentials, RegisterData, User, Group, 
  Expense, GroupBalance, Payment, SimplifiedPayment 
} from '../types';

const API_URL = 'http://localhost:8000/api';

class ApiService {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: { 'Content-Type': 'application/json' },
    });

    this.client.interceptors.request.use((config: InternalAxiosRequestConfig) => {
      if (this.token && config.headers) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });
  }

  setToken(token: string) {
    this.token = token;
  }

  clearToken() {
    this.token = null;
  }

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const formData = new URLSearchParams();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);
    const { data } = await this.client.post<AuthResponse>('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return data;
  }

  async register(data: RegisterData): Promise<User> {
    const { data: user } = await this.client.post<User>('/auth/register', data);
    return user;
  }

  async getMe(): Promise<User> {
    const { data } = await this.client.get<User>('/auth/me');
    return data;
  }

  async getGroups(): Promise<Group[]> {
    const { data } = await this.client.get<Group[]>('/groups/');
    return data;
  }

  async getGroup(groupId: number): Promise<Group> {
    const { data } = await this.client.get<Group>(`/groups/${groupId}`);
    return data;
  }

  async createGroup(name: string, description?: string): Promise<Group> {
    const { data } = await this.client.post<Group>('/groups/', { name, description });
    return data;
  }

  async addMember(groupId: number, email: string): Promise<void> {
    await this.client.post(`/groups/${groupId}/members?email=${encodeURIComponent(email)}`);
  }

  async removeMember(groupId: number, userId: number): Promise<void> {
    await this.client.delete(`/groups/${groupId}/members/${userId}`);
  }

  async getGroupExpenses(groupId: number): Promise<Expense[]> {
    const { data } = await this.client.get<Expense[]>(`/expenses/group/${groupId}`);
    return data;
  }

  async createExpense(expense: Omit<Expense, 'id' | 'created_at' | 'shares'> & { shares: Array<{ user_id: number; share_amount?: number; share_percentage?: number }> }): Promise<Expense> {
    const { data } = await this.client.post<Expense>('/expenses/', expense);
    return data;
  }

  async deleteExpense(expenseId: number): Promise<void> {
    await this.client.delete(`/expenses/${expenseId}`);
  }

  async getGroupBalances(groupId: number): Promise<GroupBalance> {
    const { data } = await this.client.get<GroupBalance>(`/balances/group/${groupId}`);
    return data;
  }

  async getSimplifiedPayments(groupId: number): Promise<SimplifiedPayment[]> {
    const { data } = await this.client.get<SimplifiedPayment[]>(`/balances/group/${groupId}/simplify`);
    return data;
  }

  async createPayment(groupId: number, toUserId: number, amount: number, notes?: string): Promise<Payment> {
    const { data } = await this.client.post<Payment>('/expenses/payments', {
      group_id: groupId,
      to_user_id: toUserId,
      amount,
      notes,
    });
    return data;
  }

  async searchUsers(query: string): Promise<User[]> {
    const { data } = await this.client.get<User[]>(`/users/search?query=${encodeURIComponent(query)}`);
    return data;
  }

  async updateProfile(data: { full_name?: string; avatar_url?: string; preferred_currency?: string }): Promise<User> {
    const { data: user } = await this.client.put<User>('/users/me', data);
    return user;
  }
}

export const api = new ApiService();
