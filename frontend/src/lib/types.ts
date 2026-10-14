export type ProcessingStatus = "uploaded" | "processing" | "completed" | "failed";
export type ReviewStatus = "pending" | "in_review" | "approved" | "rejected";

export interface LineItem {
  description: string;
  quantity: string;
  unit_price: string;
  line_total: string;
}

export interface InvoiceData {
  supplier_name: string;
  supplier_tax_id?: string | null;
  invoice_number: string;
  invoice_date: string;
  due_date?: string | null;
  currency: string;
  subtotal: string;
  tax_amount: string;
  total_amount: string;
  purchase_order_reference?: string | null;
  line_items: LineItem[];
}

export interface ValidationIssue {
  rule_id: string;
  severity: "error" | "warning";
  message: string;
  field?: string | null;
}

export interface ExtractionSummary {
  id: string;
  provider_name: string;
  model_id?: string | null;
  extracted_data: InvoiceData;
  field_confidence?: Record<string, string | number | null> | null;
  validation_results: ValidationIssue[];
  duration_ms?: number | null;
  created_at: string;
}

export interface ReviewSummary {
  id: string;
  status: ReviewStatus;
  corrected_data?: InvoiceData | null;
  field_changes: Array<{ field: string; before: unknown; after: unknown }>;
  rejection_reason?: string | null;
  reviewed_at?: string | null;
  updated_at: string;
}

export interface DocumentDetail {
  id: string;
  original_filename: string;
  status: ProcessingStatus;
  document_type: string;
  mime_type: string;
  file_size: number;
  uploaded_at: string;
  processing_started_at?: string | null;
  processing_ended_at?: string | null;
  error_message?: string | null;
  latest_extraction?: ExtractionSummary | null;
  review?: ReviewSummary | null;
}

export interface DocumentListItem {
  id: string;
  original_filename: string;
  status: ProcessingStatus;
  uploaded_at: string;
  supplier_name?: string | null;
  invoice_number?: string | null;
  review_status?: ReviewStatus | null;
}

export interface DashboardStats {
  total_documents: number;
  processed_documents: number;
  awaiting_review: number;
  failed_documents: number;
  average_processing_ms?: number | null;
  validation_error_rate?: number | null;
}

export interface EvaluationSummary {
  document_count: number;
  field_exact_match_accuracy?: number | null;
  normalized_field_accuracy?: number | null;
  per_field_accuracy?: Record<string, number>;
  validation_failure_rate?: number | null;
  average_processing_ms?: number | null;
  metric_definitions?: Record<string, string>;
  limitations?: string;
}
