from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LineItem(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    description: str = Field(min_length=1)
    quantity: Decimal = Field(ge=0)
    unit_price: Decimal
    line_total: Decimal


class InvoiceData(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    supplier_name: str = Field(min_length=1)
    supplier_tax_id: str | None = None
    invoice_number: str = Field(min_length=1)
    invoice_date: date
    due_date: date | None = None
    currency: str = Field(min_length=3, max_length=3)
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    purchase_order_reference: str | None = None
    line_items: list[LineItem] = Field(min_length=1)

    @field_validator("currency")
    @classmethod
    def uppercase_currency(cls, value: str) -> str:
        return value.upper()


DecimalStr = Annotated[Decimal, Field(max_digits=18, decimal_places=4)]
