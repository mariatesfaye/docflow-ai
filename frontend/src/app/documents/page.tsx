"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

export default function DocumentsPage() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const query = useQuery({
    queryKey: ["documents", search, status],
    queryFn: () => api.listDocuments({ search: search || undefined, status: status || undefined }),
  });

  const items = useMemo(() => query.data?.items ?? [], [query.data?.items]);

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-semibold">Document history</h2>
        <p className="text-sm text-slate-600">Search and filter uploaded invoices.</p>
      </div>
      <Card>
        <CardHeader>
          <div className="flex flex-wrap gap-3">
            <Input placeholder="Search filename…" value={search} onChange={(event) => setSearch(event.target.value)} className="max-w-xs" />
            <select
              className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
              value={status}
              onChange={(event) => setStatus(event.target.value)}
            >
              <option value="">All statuses</option>
              <option value="uploaded">Uploaded</option>
              <option value="processing">Processing</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
          </div>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-slate-200 text-slate-500">
              <tr>
                <th className="px-2 py-2 font-medium">Filename</th>
                <th className="px-2 py-2 font-medium">Supplier</th>
                <th className="px-2 py-2 font-medium">Invoice #</th>
                <th className="px-2 py-2 font-medium">Uploaded</th>
                <th className="px-2 py-2 font-medium">Processing</th>
                <th className="px-2 py-2 font-medium">Review</th>
              </tr>
            </thead>
            <tbody>
              {items.map((doc) => (
                <tr key={doc.id} className="border-b border-slate-100">
                  <td className="px-2 py-3">
                    <Link href={`/documents/${doc.id}`} className="font-medium hover:underline">
                      {doc.original_filename}
                    </Link>
                  </td>
                  <td className="px-2 py-3">{doc.supplier_name ?? "—"}</td>
                  <td className="px-2 py-3">{doc.invoice_number ?? "—"}</td>
                  <td className="px-2 py-3">{formatDate(doc.uploaded_at)}</td>
                  <td className="px-2 py-3">
                    <Badge label={doc.status} tone={doc.status} />
                  </td>
                  <td className="px-2 py-3">{doc.review_status ? <Badge label={doc.review_status} tone={doc.review_status} /> : "—"}</td>
                </tr>
              ))}
              {items.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-2 py-8 text-center text-slate-500">
                    {query.isLoading ? "Loading…" : "No documents match your filters."}
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
