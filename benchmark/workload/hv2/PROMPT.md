# Hostile Milestone 2 — pricing & checkout on the ledger

Extend the split-payment ledger from Hostile Milestone 1 with a **pricing and
checkout** layer. An **invoice** prices a cart, then SETTLES by creating a
ledger transfer from the customer to the merchant. Money stays integer cents;
every Hostile Milestone 1 behavior (accounts, split transfers, reconciliation,
insufficient→409, idempotency, conservation) must keep working unchanged.

## Coupons

`POST /coupons` `{ "code": str, "kind": "percent"|"fixed", "value": int>0,
"once_per_customer": bool }` → `201`. A `percent` coupon takes `value` **percent**
off (e.g. `10` = 10%); a `fixed` coupon takes `value` **cents** off. A duplicate
`code` → `409`. Unknown `kind` or non-positive `value` → `400`.

## Invoices

`POST /invoices`
```json
{ "customer_account_id": str, "merchant_account_id": str,
  "line_items": [ { "sku": str, "unit_price_cents": int>0, "qty": int>0 }, ... ],
  "coupons": [ "CODE", ... ] }
```

Price it with this **fixed pipeline**, in this exact order, all integer cents:

1. `subtotal = sum(unit_price_cents * qty)` over the line items.
2. **Discounts, percent BEFORE fixed.** Apply every `percent` coupon first, then
   every `fixed` coupon, each to the running amount:
   - percent: `running -= running * pct // 100` (floor).
   - fixed: `running = max(0, running - value)` — a discount can NEVER drive the
     goods amount below `0`.
   Call the result `discounted_subtotal`; `discount_cents = subtotal - discounted_subtotal`.
3. **Tax on the DISCOUNTED subtotal**, never the gross: `tax_cents =
   round_half_even(discounted_subtotal * 875, 10000)` — an **8.75%** rate,
   rounded half-to-even to whole cents.
4. **Shipping on the DISCOUNTED subtotal:** `0` if `discounted_subtotal >= 5000`
   (free-shipping threshold, **$50.00**), else `500` ($5.00 flat).
5. `total_cents = discounted_subtotal + tax_cents + shipping_cents`.

**Settlement.** On success, create a ledger transfer of `total_cents` from
`customer_account_id` to `merchant_account_id` (a single-payee split). If the
customer cannot afford `total_cents` → `409` and NO invoice, NO transfer, no
balance change. The customer's balance drops by `total_cents`; the merchant's
rises by `total_cents`.

Response `201`:
```json
{ "id", "customer_account_id", "merchant_account_id",
  "subtotal_cents", "discount_cents", "tax_cents", "shipping_cents",
  "total_cents", "transfer_id" }
```

## Rules

- **Coupon `once_per_customer`.** A `once_per_customer` coupon may be used at most
  once per customer; a second invoice by the SAME customer using it → `400`
  (`coupon_exhausted`). A different customer may still use it once.
- **Input hardening.** Unknown account → `404`; unknown coupon code, empty
  `line_items`, non-positive `unit_price_cents`/`qty` → `400` with a JSON error
  body — never a `500`, never a partial mutation.

Entry contract (unchanged): the app runs as `python -m app` serving HTTP on
`$PORT`, standard library only.
