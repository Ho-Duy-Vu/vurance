export interface User {
  id: string;
  email: string;
  full_name: string | null;
  role: 'user' | 'reviewer' | 'admin';
  province: string | null;
  region: string | null;
  is_active: boolean;
}

export interface DocumentRecord {
  document_id: string;
  file_name: string;
  file_type: string;
  doc_type: string;
  file_size_kb: number;
  processing_status: 'pending' | 'processing' | 'done' | 'failed';
  ocr_confidence: number | null;
  needs_manual_review: boolean;
  is_merged: boolean;
  created_at: string;
  updated_at: string;
}

export interface Claim {
  id: string;
  user_id: string;
  status: 'pending' | 'processing' | 'approved' | 'rejected' | 'manual_review';
  claim_type: string;
  amount_claimed: number;
  amount_approved: number | null;
  ai_decision: string | null;
  ai_reasoning: string | null;
  ai_fraud_score: number | null;
  ai_fraud_flags: string[];
  province: string | null;
  disaster_type: string | null;
  created_at: string;
}

export interface GeoRisk {
  province_name: string;
  province_code: string;
  region: 'north' | 'central' | 'south';
  overall_risk_score: number;
  is_high_risk: boolean;
  risk_factors: string[];
  disaster_risks: Array<{
    type: string;
    risk_score: number;
    frequency: string;
  }>;
  recommendations: Array<{
    insurance_type: string;
    priority_score: number;
    reason: string;
  }>;
}
