"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { formatDate, formatPercent } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

export default function DashboardPage() {
  const statsQuery = useQuery({ queryKey: ["dashboard-stats"], queryFn: api.dashboardStats });
  const docsQuery = useQuery({ queryKey: ["recent-documents"], queryFn: () => api.listDocuments({ page: 1 }) });

  const stats = statsQuery.data;
  const recent = docsQuery.data?.items.slice(0, 6) ?? [];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-semibold">Operations dashboard</h2>
          <p className="text-sm text-slate-600">Track uploads, processing health, and review backlog.</p>
        </div>
        <Link
          href="/upload"
          className="inline-flex h-10 items-center rounded-md bg-slate-900 px-4 text-sm font-medium text-white hover:bg-slate-800"
        >
          Upload invoice
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {[
          ["Total documents", stats?.total_documents],
          ["Processed", stats?.processed_documents],
          ["Awaiting review", stats?.awaiting_review],
          ["Failed", stats?.failed_documents],
        ].map(([label, value]) => (
          <Card key={label as string}>
            <CardContent className="pt-5">
              <p className="text-sm text-slate-500">{label}</p>
              <p className="mt-1 text-3xl font-semibold">{value ?? (statsQuery.isLoading ? "…" : 0)}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <h3 className="font-semibold">Extraction quality (stored data)</h3>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-slate-700">
            <p>Average processing time: {stats?.average_processing_ms ? `${Math.round(stats.average_processing_ms)} ms` : "—"}</p>
            <p>Validation error rate: {formatPercent(stats?.validation_error_rate)}</p>
            <p className="text-slate-500">Metrics reflect documents processed in this workspace, not external production traffic.</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <h3 className="font-semibold">Recent documents</h3>
          </CardHeader>
          <CardContent>
            {recent.length === 0 ? (
              <p className="text-sm text-slate-600">No documents yet. Upload a synthetic invoice to begin.</p>
            ) : (
              <ul className="space-y-3">
                {recent.map((doc) => (
                  <li key={doc.id} className="flex items-center justify-between gap-3 text-sm">
                    <div>
                      <Link href={`/documents/${doc.id}`} className="font-medium text-slate-900 hover:underline">
                        {doc.original_filename}
                      </Link>
                      <p className="text-slate-500">{formatDate(doc.uploaded_at)}</p>
                    </div>
                    <div className="flex gap-2">
                      <Badge label={doc.status} tone={doc.status} />
                      {doc.review_status ? <Badge label={doc.review_status} tone={doc.review_status} /> : null}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
