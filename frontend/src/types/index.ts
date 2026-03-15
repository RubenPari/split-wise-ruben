export type SplitType = 'equal' | 'percentage' | 'fixed';

export interface User {
  id: number;
  email: string;
  full_name?: string;
  avatar_url?: string;
  preferred_currency: string;
  is_active: boolean;
  created_at: string;
}

export interface Category {
  id: number;
  group_id: number;
  name: string;
  icon?: string;
  created_at: string;
}

export interface GroupMember {
  user_id: number;
  user: User;
  role: string;
  joined_at: string;
}

export interface Group {
  id: number;
  name: string;
  description?: string;
  created_by_id: number;
  created_at: string;
  members: GroupMember[];
  categories: Category[];
}

export interface ExpenseShare {
  id: number;
  expense_id: number;
  user_id: number;
  share_amount: number;
  share_percentage?: number;
}

export interface Expense {
  id: number;
  group_id: number;
  title: string;
  amount: number;
  date: string;
  category_id?: number;
  payer_id: number;
  receipt_url?: string;
  notes?: string;
  split_type: SplitType;
  shares: ExpenseShare[];
  created_at: string;
}

export interface Payment {
  id: number;
  group_id: number;
  from_user_id: number;
  to_user_id: number;
  from_user: User;
  to_user: User;
  amount: number;
  notes?: string;
  paid_at: string;
}

export interface Balance {
  user_id: number;
  user: User;
  amount: number;
}

export interface SimplifiedPayment {
  from_user_id: number;
  from_user: User;
  to_user_id: number;
  to_user: User;
  amount: number;
}

export interface GroupBalance {
  group_id: number;
  balances: Balance[];
  simplified_payments: SimplifiedPayment[];
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name?: string;
}
