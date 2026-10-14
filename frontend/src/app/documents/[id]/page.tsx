"use client";

import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { api } from "@/lib/api";
import type { InvoiceData } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { InvoiceReviewForm } from "@/components/invoice-review-form";
import { Input } from "@/components/ui/input";
import { PdfViewer } from "@/components/pdf-viewer";

export default function DocumentDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const queryClient = useQueryClient();
  const [rejectReason, setRejectReason] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  const docQuery = useQuery({
    queryKey: ["document", id],
    queryFn: () => api.getDocument(id),
    enabled: Boolean(id),
  });

  const processMutation = useMutation({
    mutationFn: () => api.processDocument(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["document", id] }),
  });

  const saveMutation = useMutation({
    mutationFn: (data: InvoiceData) => api.updateReview(id, data),
    onSuccess: () => {
      setMessage("Corrections saved.");
      queryClient.invalidateQueries({ queryKey: ["document", id] });
    },
  });

  const approveMutation = useMutation({
    mutationFn: () => api.approveDocument(id),
    onSuccess: () => {
      setMessage("Document approved.");
      queryClient.invalidateQueries({ queryKey: ["document", id] });
    },
    onError: (err: Error) => setMessage(err.message),
  });

  const rejectMutation = useMutation({
    mutationFn: () => api.rejectDocument(id, rejectReason || undefined),
    onSuccess: () => {
      setMessage("Document rejected.");
      queryClient.invalidateQueries({ queryKey: ["document", id] });
    },
    onError: (err: Error) => setMessage(err.message),
  });

  const doc = docQuery.data;
  const initialInvoice = useMemo(() => {
    if (!doc?.latest_extraction) return null;
    return doc.review?.corrected_data ?? doc.latest_extraction.extracted_data;
  }, [doc]);

  if (docQuery.isLoading) return <p>Loading document…</p>;
  if (!doc) return <p className="text-red-700">Document not found.</p>;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-2xl font-semibold">{doc.original_filename}</h2>
          <p className="text-sm text-slate-600">Uploaded {formatDate(doc.uploaded_at)}</p>
          <div className="mt-2 flex flex-wrap gap-2">
            <Badge label={doc.status} tone={doc.status} />
            {doc.review ? <Badge label={doc.review.status} tone={doc.review.status} /> : null}
            {doc.latest_extraction?.provider_name === "demo" ? (
              <span className="rounded-full bg-violet-100 px-2.5 py-0.5 text-xs font-medium text-violet-800">Demo extractor (not an LLM)</span>
            ) : null}
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          {doc.status !== "completed" ? (
            <Button type="button" onClick={() => processMutation.mutate()} disabled={processMutation.isPending}>
              {processMutation.isPending ? "Processing…" : "Process"}
            </Button>
          ) : null}
          <Button
            type="button"
            variant="outline"
            onClick={async () => {
              const payload = await api.exportDocument(id, "json");
              const blob = new Blob([payload], { type: "application/json" });
              const link = document.createElement("a");
              link.href = URL.createObjectURL(blob);
              link.download = `${doc.original_filename.replace(/\.pdf$/i, "")}.json`;
              link.click();
              URL.revokeObjectURL(link.href);
              setMessage("JSON export downloaded.");
            }}
          >
            Export JSON
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={async () => {
              const payload = await api.exportDocument(id, "csv");
              const blob = new Blob([payload], { type: "text/csv" });
              const link = document.createElement("a");
              link.href = URL.createObjectURL(blob);
              link.download = `${doc.original_filename.replace(/\.pdf$/i, "")}.csv`;
              link.click();
              URL.revokeObjectURL(link.href);
              setMessage("CSV export downloaded.");
            }}
          >
            Export CSV
          </Button>
        </div>
      </div>

      {doc.error_message ? (
        <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">{doc.error_message}</div>
      ) : null}
      {message ? (
        <p className={`text-sm ${message.toLowerCase().includes("cannot") || message.toLowerCase().includes("invalid") ? "text-red-700" : "text-emerald-700"}`}>
          {message}
        </p>
      ) : null}

      <div className="grid gap-4 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <h3 className="font-semibold">Original PDF</h3>
          </CardHeader>
          <CardContent>
            <PdfViewer documentId={id} filename={doc.original_filename} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h3 className="font-semibold">Extracted invoice data</h3>
            {doc.latest_extraction ? (
              <p className="text-xs text-slate-500">
                Provider {doc.latest_extraction.provider_name}
                {doc.latest_extraction.model_id ? ` · ${doc.latest_extraction.model_id}` : ""}
              </p>
            ) : (
              <p className="text-sm text-slate-600">Process this document to generate extraction results.</p>
            )}
          </CardHeader>
          <CardContent>
            {initialInvoice && doc.latest_extraction ? (
              <InvoiceReviewForm
                initial={initialInvoice}
                validation={doc.latest_extraction.validation_results}
                confidence={doc.latest_extraction.field_confidence}
                onSave={async (data) => {
                  await saveMutation.mutateAsync(data);
                }}
              />
            ) : null}
          </CardContent>
        </Card>
      </div>

      {doc.review?.field_changes?.length ? (
        <Card>
          <CardHeader>
            <h3 className="font-semibold">Review changes</h3>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              {doc.review.field_changes.map((change) => (
                <li key={change.field} className="rounded-md border border-slate-200 p-2">
                  <p className="font-medium">{change.field}</p>
                  <p className="text-slate-600">Before: {JSON.stringify(change.before)}</p>
                  <p className="text-slate-600">After: {JSON.stringify(change.after)}</p>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      ) : null}

      {doc.latest_extraction ? (
        <Card>
          <CardHeader>
            <h3 className="font-semibold">Approval actions</h3>
          </CardHeader>
          <CardContent className="flex flex-wrap items-end gap-3">
            <Button
              type="button"
              onClick={() => approveMutation.mutate()}
              disabled={approveMutation.isPending || doc.review?.status === "approved"}
            >
              Approve
            </Button>
            <div className="flex flex-col gap-1">
              <label className="text-xs font-medium text-slate-600">Rejection reason (optional)</label>
              <Input value={rejectReason} onChange={(event) => setRejectReason(event.target.value)} className="min-w-[280px]" />
            </div>
            <Button
              type="button"
              variant="destructive"
              onClick={() => rejectMutation.mutate()}
              disabled={rejectMutation.isPending || doc.review?.status === "rejected"}
            >
              Reject
            </Button>
            {doc.review?.status === "approved" ? (
              <p className="w-full text-xs text-slate-500">To change an approved document, edit fields and save — or use Documents to re-open workflow later.</p>
            ) : null}
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
