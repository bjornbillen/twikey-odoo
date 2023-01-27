import requests

from odoo import _, exceptions, fields, models
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    twikey_api_key = fields.Char(
        related="company_id.twikey_api_key", help="Add Api Key from Twikey", readonly=False
    )
    twikey_base_url = fields.Char(related="company_id.twikey_base_url", readonly=False)

    def twikey_authenticate(self):
        twikey_client = self.env["ir.config_parameter"].get_twikey_client(company=self.env.company)

        if self.twikey_api_key:
            self.set_values()
            try:
                twikey_client.refreshTokenIfRequired()
                return self.connection_succesful_message()
            except (ValueError, requests.exceptions.RequestException) as e:
                raise exceptions.AccessError from e
        else:
            raise UserError(_("API key not set!"))

    def connection_succesful_message(self):
        view = self.env.ref("twikey_integration.success_message_wizard")
        context = dict(self._context or {})
        context["message"] = "Connection succesful!"
        return {
            "name": "Test OK",
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "success.message.wizard",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "context": context,
        }

    def test_twikey_connection(self):
        try:
            self.twikey_authenticate()
            self.set_values()
            self.env["ir.config_parameter"].get_twikey_client(company=self.env.company)
            return self.connection_succesful_message()

        except (ValueError, requests.exceptions.RequestException) as e:
            raise exceptions.AccessError from e

    def twikey_sync_contract_template(self):
        self.env["twikey.sync.contract.templates"].twikey_sync_contract_templates()
