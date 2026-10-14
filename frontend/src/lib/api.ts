import type {
  DashboardStats,
  DocumentDetail,
  DocumentListItem,
  EvaluationSummary,
  InvoiceData,
  ReviewSummary,
} from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, init);
  if (!response.ok) {
    let detail = "Request failed";
    try {
      const payload = (await response.json()) as { detail?: string };
      detail = payload.detail ?? detail;
    } catch {
      detail = await response.text();
    }
    throw new Error(detail);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    return (await response.json()) as T;
  }
  return (await response.text()) as T;
}

export const api = {
  health: () => request<{ status: string }>("/api/health"),
  dashboardStats: () => request<DashboardStats>("/api/documents/stats/dashboard"),
  listDocuments: (params?: { page?: number; search?: string; status?: string }) => {
    const query = new URLSearchParams();
    if (params?.page) query.set("page", String(params.page));
    if (params?.search) query.set("search", params.search);
    if (params?.status) query.set("status", params.status);
    const suffix = query.toString() ? `?${query.toString()}` : "";
    return request<{ items: DocumentListItem[]; total: number; page: number; page_size: number }>(
      `/api/documents${suffix}`,
    );
  },
  uploadDocument: async (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<{ id: string }>("/api/documents", { method: "POST", body: form });
  },
  getDocument: (id: string) => request<DocumentDetail>(`/api/documents/${id}`),
  processDocument: (id: string) => request<DocumentDetail>(`/api/documents/${id}/process`, { method: "POST" }),
  updateReview: (id: string, corrected_data: InvoiceData) =>
    request<ReviewSummary>(`/api/documents/${id}/review`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ corrected_data, mark_in_review: true }),
    }),
  approveDocument: (id: string) => request<ReviewSummary>(`/api/documents/${id}/approve`, { method: "POST" }),
  rejectDocument: (id: string, reason?: string) =>
    request<ReviewSummary>(`/api/documents/${id}/reject`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reason }),
    }),
  exportDocument: (id: string, format: "json" | "csv") =>
    request<string>(`/api/documents/${id}/export?format=${format}`),
  evaluationSummary: () => request<EvaluationSummary>("/api/evaluation/summary"),
  /** Same-origin proxy avoids CORS issues for PDF preview (iframe/fetch). */
  fileUrl: (id: string) => `/backend-api/documents/${id}/file`,
  fileUrlDirect: (id: string) => `${API_URL}/api/documents/${id}/file`,
};
