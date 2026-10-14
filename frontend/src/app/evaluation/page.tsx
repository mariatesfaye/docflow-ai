"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { formatPercent } from "@/lib/utils";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

export default function EvaluationPage() {
  const evaluationQuery = useQuery({ queryKey: ["evaluation"], queryFn: api.evaluationSummary });
  const report = evaluationQuery.data;

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-semibold">Evaluation</h2>
        <p className="text-sm text-slate-600">
          Benchmark metrics from labeled synthetic fixtures (demo extractor). Not mixed with unlabeled production uploads.
        </p>
      </div>

      {evaluationQuery.isLoading ? <p>Loading evaluation report…</p> : null}

      {report ? (
        <>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {[
              ["Documents evaluated", report.document_count],
              ["Exact-match accuracy", formatPercent(report.field_exact_match_accuracy)],
              ["Normalized field accuracy", formatPercent(report.normalized_field_accuracy)],
              ["Validation failure rate", formatPercent(report.validation_failure_rate)],
            ].map(([label, value]) => (
              <Card key={label as string}>
                <CardContent className="pt-5">
                  <p className="text-sm text-slate-500">{label}</p>
                  <p className="mt-1 text-2xl font-semibold">{value}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card>
            <CardHeader>
              <h3 className="font-semibold">Per-field accuracy</h3>
            </CardHeader>
            <CardContent>
              <ul className="grid gap-2 text-sm md:grid-cols-2">
                {Object.entries(report.per_field_accuracy ?? {}).map(([field, accuracy]) => (
                  <li key={field} className="flex justify-between rounded-md border border-slate-200 px-3 py-2">
                    <span>{field}</span>
                    <span>{formatPercent(accuracy)}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <h3 className="font-semibold">Metric definitions</h3>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-slate-700">
              {Object.entries(report.metric_definitions ?? {}).map(([key, definition]) => (
                <p key={key}>
                  <span className="font-medium">{key}:</span> {definition}
                </p>
              ))}
              <p className="text-slate-500">{report.limitations}</p>
              <p>Average processing duration: {report.average_processing_ms ? `${Math.round(report.average_processing_ms)} ms` : "—"}</p>
            </CardContent>
          </Card>
        </>
      ) : null}
    </div>
  );
}
