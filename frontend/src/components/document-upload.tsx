"use client";

import { useCallback, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

export function DocumentUpload() {
  const router = useRouter();
  const [dragging, setDragging] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const handleFile = useCallback(
    async (file: File) => {
      setError(null);
      setBusy(true);
      setStatus("Uploading PDF…");
      try {
        if (file.type !== "application/pdf") {
          throw new Error("Only PDF files are supported.");
        }
        if (file.size === 0) {
          throw new Error("File is empty.");
        }
        const uploaded = await api.uploadDocument(file);
        setStatus("Processing extraction…");
        const processed = await api.processDocument(uploaded.id);
        if (processed.status === "failed") {
          throw new Error(processed.error_message ?? "Processing failed.");
        }
        router.push(`/documents/${uploaded.id}`);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Upload failed.");
        setStatus(null);
      } finally {
        setBusy(false);
      }
    },
    [router],
  );

  return (
    <Card>
      <CardHeader>
        <h2 className="text-base font-semibold">Upload invoice PDF</h2>
        <p className="text-sm text-slate-600">Drag and drop a synthetic demo invoice or choose a file (max 10 MB).</p>
      </CardHeader>
      <CardContent>
        <div
          className={`rounded-xl border-2 border-dashed p-10 text-center transition-colors ${
            dragging ? "border-slate-900 bg-slate-100" : "border-slate-300 bg-slate-50"
          }`}
          onDragOver={(event) => {
            event.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(event) => {
            event.preventDefault();
            setDragging(false);
            const file = event.dataTransfer.files?.[0];
            if (file) void handleFile(file);
          }}
        >
          <p className="mb-4 text-sm text-slate-600">Drop PDF here</p>
          <label className="inline-flex cursor-pointer items-center rounded-md border border-slate-300 bg-white px-3 py-2 text-sm font-medium hover:bg-slate-50">
            Choose file
            <input
              type="file"
              accept="application/pdf"
              className="hidden"
              disabled={busy}
              onChange={(event) => {
                const file = event.target.files?.[0];
                if (file) void handleFile(file);
              }}
            />
          </label>
        </div>
        {status ? <p className="mt-3 text-sm text-slate-700">{status}</p> : null}
        {error ? (
          <div className="mt-3 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            {error}
            <div className="mt-2">
              <Button type="button" size="sm" variant="outline" onClick={() => setError(null)}>
                Retry
              </Button>
            </div>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
