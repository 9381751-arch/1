export type RequestStatus =
  | "new"
  | "clarifying"
  | "published"
  | "collecting"
  | "negotiating"
  | "awaiting_decision"
  | "closed"
  | "cancelled";

export const STATUS_LABEL: Record<RequestStatus, string> = {
  new: "Новая",
  clarifying: "Уточнение",
  published: "Опубликована",
  collecting: "Сбор предложений",
  negotiating: "Торг",
  awaiting_decision: "Ожидает решения",
  closed: "Закрыта",
  cancelled: "Отменена",
};

export interface RequestRow {
  id: string;
  created_at: string;
  status: RequestStatus;
  grade: string | null;
  length_m: number | null;
  quantity_t: number | null;
  region: string | null;
  deadline: string | null;
  condition: number | null;
  extra_conditions: string | null;
  raw_text: string | null;
  claude_post_text: string | null;
  published_msg_id: number | null;
  published_at: string | null;
  closed_at: string | null;
  winner_offer_id: string | null;
}

export interface OfferRow {
  id: string;
  request_id: string;
  created_at: string;
  source: string;
  seller_tg_id: number;
  seller_username: string | null;
  seller_name: string | null;
  grade: string | null;
  length_m: number | null;
  condition: number | null;
  quantity_t: number | null;
  price_per_t: number | null;
  vat_type: string | null;
  location: string | null;
  ready_date: string | null;
  comment: string | null;
  distance_km: number | null;
  logistics_per_t: number | null;
  total_cost_per_t: number | null;
  rank: number | null;
  negotiation_status: string | null;
  counter_price: number | null;
  final_price: number | null;
}

export interface SettingRow {
  key: string;
  value: string | null;
  description: string | null;
  updated_at: string;
}
