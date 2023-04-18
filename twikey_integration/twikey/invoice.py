import json
import logging

import requests


class Invoice(object):
    def __init__(self, client) -> None:
        super().__init__()
        self.client = client
        self.logger = logging.getLogger(__name__)

    def create(self, data):  # pylint: disable=W8106
        url = self.client.instance_url("/invoice")
        data = data or {}
        self.client.refreshTokenIfRequired()
        headers = self.client.headers("application/json")
        headers["X-PARTNER"] = "Odoo"
        response = requests.post(
            url=url,
            json=data,
            headers=headers,
            timeout=15,
        )
        json_response = response.json()
        response_text = json.loads(response.text)
        if "code" in response_text:
            if "err" in response_text["code"]:
                raise self.client.raise_error("Create invoice", response)
        self.logger.debug("Added invoice : %s" % json_response["url"])
        return json_response

    def update(self, id, data):  # pylint: disable=W0622
        url = self.client.instance_url("/invoice/" + id)
        data = data or {}
        self.client.refreshTokenIfRequired()
        headers = self.client.headers("application/json")
        response = requests.put(url=url, json=data, headers=headers, timeout=15)
        json_response = response.json()
        if "ApiErrorCode" in response.headers:
            error = json_response
            raise Exception("Error updating : %s" % error)
        self.logger.debug("Updated invoice : %s" % json_response["url"])
        return json_response

    def feed(self, invoiceFeed):
        url = self.client.instance_url("/invoice?include=customer&include=meta&include=lastpayment")

        self.client.refreshTokenIfRequired()
        initheaders = self.client.headers()
        response = requests.get(
            url=url,
            headers=initheaders,
            timeout=15,
        )
        response.raise_for_status()
        response_text = json.loads(response.text)
        if "code" in response_text:
            if "err" in response_text["code"]:
                raise self.client.raise_error("Feed invoice", response)
        feed_response = response.json()
        while len(feed_response["Invoices"]) > 0:
            self.logger.debug(
                "Feed handling %d invoices from seq=%s"
                % (len(feed_response["Invoices"]), response.headers["X-LAST"])
            )
            for invoice in feed_response["Invoices"]:
                self.logger.debug("Feed handling : %s" % invoice)
                invoiceFeed.invoice(invoice)
            response = requests.get(
                url=url,
                headers=self.client.headers(),
                timeout=15,
            )
            response_text = json.loads(response.text)
            if "code" in response_text:
                if "err" in response_text["code"]:
                    raise self.client.raise_error("Feed invoice", response)
            feed_response = response.json()

    def geturl(self, invoice_id):
        return "%s/%s/%s" % (
            self.client.api_base.replace("api", "app"),
            self.client.merchant_id,
            invoice_id,
        )


class InvoiceFeed:
    def invoice(self, invoice):
        pass
