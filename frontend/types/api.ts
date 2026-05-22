export type RepairStatus = "pending" | "in_progress" | "delivered" | "cancelled";
export type RepairImageType = "watch" | "envelope";

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
  image_type: RepairImageType;
  file_name: string;
  content_type: string;
  file_size: number;
  public_url: string | null;
  created_at: string;
};

export type Repair = {
  id: number;
  repair_date: string;
  envelope_date: string | null;
  envelope_raw_transcription: string | null;
  brand: string;
  model: string;
  watch_color: string | null;
  watch_specifications: string | null;
  description: string;
  repair_cost: string;
  deposit_amount: string | null;
  watchmaker_percentage: string;
  profit_amount: string;
  status: RepairStatus;
  customer_name: string | null;
  customer_phone: string | null;
  customer_document_id: string | null;
  invoice_number: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  images: RepairImage[];
};

export type RepairPayload = {
  repair_date: string;
  envelope_date?: string | null;
  envelope_raw_transcription?: string | null;
  brand: string;
  model: string;
  watch_color?: string | null;
  watch_specifications?: string | null;
  description: string;
  repair_cost: string;
  deposit_amount?: string | null;
  watchmaker_percentage: string;
  status: RepairStatus;
  customer_name?: string | null;
  customer_phone?: string | null;
  customer_document_id?: string | null;
  invoice_number?: string | null;
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
  floating_weekly: string;
  floating_monthly: string;
  floating_profit: string;
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

export type ExtractedRepairFields = Partial<{
  repair_date: string;
  envelope_date: string;
  brand: string;
  model: string;
  watch_color: string;
  watch_specifications: string;
  description: string;
  repair_cost: string;
  deposit_amount: string;
  watchmaker_percentage: string;
  customer_name: string;
  customer_phone: string;
  customer_document_id: string;
  invoice_number: string;
  notes: string;
}>;

export type EnvelopeExtractionResponse = {
  extracted: boolean;
  message: string;
  fields: ExtractedRepairFields;
  confidence: number | null;
  raw_text: string | null;
  raw_transcription: string | null;
  raw_text_candidates: string[];
  envelope_number: string | null;
  phone_numbers: string[];
  field_confidences: Record<string, number>;
  warnings: string[];
};
