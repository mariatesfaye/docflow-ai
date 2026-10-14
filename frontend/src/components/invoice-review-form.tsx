"use client";

import { useFieldArray, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { InvoiceData, ValidationIssue } from "@/lib/types";

const lineItemSchema = z.object({
  description: z.string().min(1),
  quantity: z.string().min(1),
  unit_price: z.string().min(1),
  line_total: z.string().min(1),
});

const invoiceSchema = z.object({
  supplier_name: z.string().min(1),
  supplier_tax_id: z.string().optional().nullable(),
  invoice_number: z.string().min(1),
  invoice_date: z.string().min(1),
  due_date: z.string().optional().nullable(),
  currency: z.string().length(3),
  subtotal: z.string().min(1),
  tax_amount: z.string().min(1),
  total_amount: z.string().min(1),
  purchase_order_reference: z.string().optional().nullable(),
  line_items: z.array(lineItemSchema).min(1),
});

export function InvoiceReviewForm({
  initial,
  validation,
  confidence,
  onSave,
}: {
  initial: InvoiceData;
  validation: ValidationIssue[];
  confidence?: Record<string, string | number | null> | null;
  onSave: (data: InvoiceData) => Promise<void>;
}) {
  const form = useForm<InvoiceData>({
    resolver: zodResolver(invoiceSchema),
    defaultValues: initial,
  });
  const { fields, append, remove } = useFieldArray({ control: form.control, name: "line_items" });

  const confidenceLabel = (field: string) => {
    const value = confidence?.[field];
    if (value === undefined || value === null) return "Not provided";
    if (value === "demo_heuristic") return "Demo heuristic (not model confidence)";
    return String(value);
  };

  return (
    <form
      className="space-y-4"
      onSubmit={form.handleSubmit(async (values) => {
        await onSave(values);
      })}
    >
      <div className="grid gap-3 md:grid-cols-2">
        {(
          [
            ["supplier_name", "Supplier name"],
            ["supplier_tax_id", "Tax ID"],
            ["invoice_number", "Invoice number"],
            ["invoice_date", "Invoice date"],
            ["due_date", "Due date"],
            ["currency", "Currency"],
            ["subtotal", "Subtotal"],
            ["tax_amount", "Tax amount"],
            ["total_amount", "Total amount"],
            ["purchase_order_reference", "PO reference"],
          ] as const
        ).map(([name, label]) => (
          <label key={name} className="space-y-1 text-sm">
            <span className="font-medium text-slate-700">{label}</span>
            <Input {...form.register(name)} />
            <span className="text-xs text-slate-500">Confidence: {confidenceLabel(name)}</span>
          </label>
        ))}
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-800">Line items</h3>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => append({ description: "", quantity: "1", unit_price: "0", line_total: "0" })}
          >
            Add line
          </Button>
        </div>
        {fields.map((field, index) => (
          <div key={field.id} className="grid gap-2 rounded-lg border border-slate-200 p-3 md:grid-cols-4">
            <Input placeholder="Description" {...form.register(`line_items.${index}.description`)} />
            <Input placeholder="Qty" {...form.register(`line_items.${index}.quantity`)} />
            <Input placeholder="Unit price" {...form.register(`line_items.${index}.unit_price`)} />
            <div className="flex gap-2">
              <Input placeholder="Line total" {...form.register(`line_items.${index}.line_total`)} />
              <Button type="button" variant="outline" size="sm" onClick={() => remove(index)}>
                Remove
              </Button>
            </div>
          </div>
        ))}
      </div>

      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-slate-800">Validation</h3>
        {validation.length === 0 ? (
          <p className="text-sm text-emerald-700">No validation issues detected.</p>
        ) : (
          <ul className="space-y-1 text-sm">
            {validation.map((issue) => (
              <li
                key={`${issue.rule_id}-${issue.field}`}
                className={issue.severity === "error" ? "text-red-700" : "text-amber-700"}
              >
                [{issue.severity}] {issue.message}
              </li>
            ))}
          </ul>
        )}
      </div>

      <Button type="submit">Save corrections</Button>
    </form>
  );
}
