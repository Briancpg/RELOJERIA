export type RepairStatus = "pending" | "in_progress" | "completed" | "delivered" | "cancelled";

export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
};

export type User = {
  id: number;
  email: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
};

export type RepairImage = {
  id: number;
  repair_id: number;
  file_name: string;
  content_type: string;
  file_size: number;
  public_url: string | null;
  created_at: string;
};

export type Repair = {
  id: number;
  repair_date: string;
  brand: string;
  model: string;
  description: string;
  repair_cost: string;
  watchmaker_percentage: string;
  profit_amount: string;
  status: RepairStatus;
  customer_name: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  images: RepairImage[];
};

export type RepairPayload = {
  repair_date: string;
  brand: string;
  model: string;
  description: string;
  repair_cost: string;
  watchmaker_percentage: string;
  status: RepairStatus;
  customer_name?: string | null;
  notes?: string | null;
};

export type RepairListResponse = {
  items: Repair[];
  total: number;
  page: number;
  page_size: number;
};

export type DashboardSummary = {
  currency: string;
  week_start: string;
  week_end: string;
  total_weekly: string;
  total_monthly: string;
  pending_repairs: number;
  delivered_repairs: number;
  accumulated_profit: string;
};

export type StatusCount = {
  status: string;
  count: number;
};

export type WeeklyProfit = {
  week_start: string;
  week_end: string;
  total_profit: string;
};

