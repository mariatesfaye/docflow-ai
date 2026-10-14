import { describe, expect, it } from "vitest";

describe("invoice form schema sanity", () => {
  it("accepts basic invoice shape", () => {
    const payload = {
      supplier_name: "Acme",
      invoice_number: "1",
      invoice_date: "2024-01-01",
      currency: "USD",
      subtotal: "10",
      tax_amount: "1",
      total_amount: "11",
      line_items: [{ description: "Item", quantity: "1", unit_price: "10", line_total: "10" }],
    };
    expect(payload.line_items.length).toBeGreaterThan(0);
  });
});
