"use client";

import { useState } from "react";
import { api } from "@/lib/api";

export function PdfViewer({ documentId, filename }: { documentId: string; filename: string }) {
  const [loaded, setLoaded] = useState(false);
  const fileUrl = api.fileUrl(documentId);

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        <a
          href={fileUrl}
          target="_blank"
          rel="noreferrer"
          className="inline-flex h-8 items-center rounded-md border border-slate-300 bg-white px-3 text-xs font-medium hover:bg-slate-50"
        >
          Open in new tab
        </a>
        <a
          href={fileUrl}
          download={filename}
          className="inline-flex h-8 items-center rounded-md border border-slate-300 bg-white px-3 text-xs font-medium hover:bg-slate-50"
        >
          Download PDF
        </a>
      </div>
      {!loaded ? <p className="text-sm text-slate-600">Loading PDF preview…</p> : null}
      <iframe
        title={`PDF preview: ${filename}`}
        src={`${fileUrl}#view=FitH`}
        className="h-[70vh] w-full rounded-lg border border-slate-200 bg-white"
        onLoad={() => setLoaded(true)}
      />
    </div>
  );
}
