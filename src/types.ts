export interface Order {
  id: number;
  user_id: number;
  username?: string;
  full_name: string;
  phone: string;
  items: string;
  total_price: number;
  address: string;
  latitude: number;
  longitude: number;
  status: 'new' | 'accepted' | 'on_the_way' | 'delivered' | 'pending_payment' | 'rejected';
  payment_type: string;
  payment_check_file_id?: string;
  rejection_reason?: string;
  admin_name?: string;
  created_at: string;
}

export interface Channel {
  id: string;
  name: string;
  invite_link: string;
}

export interface Settings {
  water_price: string;
  manual_payment_status: string;
  web_site_status: string;
  terms_uz: string;
  terms_ru: string;
  warehouse_lat: string;
  warehouse_lon: string;
}
