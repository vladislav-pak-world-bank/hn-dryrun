"""Everything a judge reads on screen lives here. Change this file first after picking a brief."""

PRODUCT_NAME = "Clearpay"
TAGLINE = "Decides whether a supplier invoice should be paid, held, or disputed, and shows why."
USER = "Accounts-payable analyst at a mid-size distributor"
SPONSOR_TOOL = "OpenAI Responses API"

# The only outcomes the model is allowed to return. The UI colours them in this order.
OUTCOMES = ["PAY", "HOLD", "DISPUTE"]

INPUT_LABEL = "Invoice and contract terms"
INPUT_PLACEHOLDER = "Paste the invoice lines and the relevant contract clauses."

SYSTEM_PROMPT = f"""You review supplier invoices for an {USER}.
Return exactly one outcome from {OUTCOMES}.
PAY: every line matches the contract and the PO.
HOLD: something is missing or ambiguous and a human must check it.
DISPUTE: a line contradicts the contract (price, quantity, terms, or a fee not in the contract).
Cite evidence only from the text you are given. Quote the exact figures. Never invent a figure.
Give 2 to 4 evidence items, most important first."""
