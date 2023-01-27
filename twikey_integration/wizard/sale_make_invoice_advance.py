from odoo import fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _name = "sale.advance.payment.inv"
    _inherit = "sale.advance.payment.inv"

    twikey_template_id = fields.Many2one("twikey.contract.template", string="Contract Template")

    def create_invoices(self):
        context = dict(self._context)
        context.update({"twikey_template_id": self.twikey_template_id})
        sale_orders = self.env["sale.order"].browse(self._context.get("active_ids", []))
        if self.advance_payment_method == "delivered":
            sale_orders.with_context(**context)._create_invoices()
        else:
            super(SaleAdvancePaymentInv, self).create_invoices()
        for sale_id in sale_orders:
            invoice_id = sale_id.invoice_ids[-1]
        if invoice_id:
            if context.get("open_invoices", False):
                return sale_orders.action_view_invoice()
        else:
            return super(SaleAdvancePaymentInv, self).create_invoices()
