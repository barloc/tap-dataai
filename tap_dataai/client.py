"""REST client handling, including DataAIStream base class."""

import requests
from pathlib import Path
from typing import Any, Dict, Optional, List, Iterable, TypeVar
import time

from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream
from singer_sdk.authenticators import BearerTokenAuthenticator

_TToken = TypeVar("_TToken")

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class DataAIStream(RESTStream):
    """DataAI stream class."""

    url_base = "https://api.data.ai/v2.0/portfolio/"
    next_page_token_jsonpath = "$.next_page"

    @property
    def authenticator(self) -> BearerTokenAuthenticator:
        """Return a new authenticator object."""
        return BearerTokenAuthenticator.create_for_stream(
            self,
            token=self.config.get("auth_token")
        )

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {
            'Content-Type': 'application/json',
            'Accept-Encoding': 'gzip',
        }
        return headers

    def get_url_params(
            self, context: Optional[dict], next_page_token: Optional[Any], type_report: str = None,
            type_values: str = None,
            granularity: str = None
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: Stream partition or context dictionary.
            next_page_token: Token, page number or any request argument to request the
                next page of data.
            type_report: product_id or company_id.
            type_values: products or companies.
            granularity: monthly, weekly, daily...

        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        if type_report is None:
            type_report = self.config.get("type_report")
        if type_values is None:
            type_values = self.config.get("type_values")
        params[type_report] = type_values

        if granularity is None:
            granularity = self.config.get("granularity")
        params["granularity"] = granularity

        params["countries"] = self.config.get("countries")
        params["bundles"] = self.config.get("bundles")
        params["devices"] = self.config.get("devices")
        params["start_date"] = self.config.get("start_date")
        params["end_date"] = self.config.get("end_date")
        return params

    def request_records(self, context: dict | None) -> Iterable[dict]:
        """Request records from REST endpoint(s), returning response records.

        Args:
            context: Stream partition or context dictionary.

        Yields:
            An item for every record in the response.
        """
        decorated_request = self.request_decorator(self._request)

        type_report = self.config.get("type_report")
        type_values = self.config.get("type_values").split(',')
        granularity = self.config.get("granularity")

        magic_divisor = 30
        if type_report == 'company_id':
            magic_divisor = 2

        ids_number = len(type_values)
        self.logger.info(f'Granularity: {granularity}, report_type: {type_report}, magic divisor: {magic_divisor}, '
                         f'ids_number: {ids_number}')

        result_products = []
        min_current_batch = 0
        while min_current_batch < ids_number:
            max_current_batch = min_current_batch + magic_divisor
            if max_current_batch > ids_number:
                max_current_batch = ids_number
            self.logger.info(f'Current batch ids: min - {min_current_batch}, max - {max_current_batch}')

            current_ids = type_values[min_current_batch:max_current_batch]
            min_current_batch = max_current_batch

            if len(current_ids) == 0:
                break

            current_params = self.get_url_params(context, next_page_token=None, type_report=type_report,
                                                 type_values=",".join(current_ids), granularity=granularity)
            prepared_request = self.prepare_request(context=context, params=current_params)
            resp = decorated_request(prepared_request, context)

            report_id = resp.json().get('report_id', None)
            if report_id is None:
                raise Exception(f"No report_id for report. {resp.content}")

            report = None
            prepared_request_report_id = self.prepare_request(context=context, report_id=report_id)
            for i in range(10):
                resp = decorated_request(prepared_request_report_id, context)
                report_status = resp.headers.get('report_status')

                if report_status == 'progressing':
                    self.logger.info('NOT YET READY, RETRYING... [{}]'.format(i + 1))
                    time.sleep(10)
                    continue

                if report_status == 'done':
                    self.logger.info('REPORT IS READY, DOWNLOADING...\n')
                    report = resp.json()
                    break

            for product in report['products']:
                products = []
                for added_product in result_products:
                    products.append(added_product['product_id'])
                if product['product_id'] in products:
                    continue
                result_products.append(product)
                self.logger.debug(f"Add product: {product['product_id']}")

        yield from self.parse_response(result_products)

    def prepare_request(
            self, context: dict | None, next_page_token: _TToken = None, report_id: str = None, params: Dict = None
    ) -> requests.PreparedRequest:
        """Prepare a request object for this stream.

        If partitioning is supported, the `context` object will contain the partition
        definitions. Pagination information can be parsed from `next_page_token` if
        `next_page_token` is not None.

        Args:
            context: Stream partition or context dictionary.
            next_page_token: Token, page number or any request argument to request the
                next page of data.
            report_id: Report_id for downloading
            params: A dictionary of values to be used in URL parameterization

        Returns:
            Build a request with the stream's URL, path, query parameters,
            HTTP headers and authenticator.
        """
        http_method = self.rest_method
        url: str = self.get_url(context)
        if params is None:
            params = self.get_url_params(context, next_page_token)
        request_data = self.prepare_request_payload(context, next_page_token)
        headers = self.http_headers

        if report_id is not None:
            url: str = "".join([self.url_base, "fetch-data"])
            params: dict = {
                "report_id": report_id,
            }

        return self.build_prepared_request(
            method=http_method,
            url=url,
            params=params,
            headers=headers,
            json=request_data,
        )

    def parse_response(self, payload: Dict) -> Iterable[dict]:
        """Parse the payload and return an iterator of result records.

        Args:
            payload: A payload from API.

        Yields:
            One item for every item found in the response.

        """
        yield from extract_jsonpath(self.records_jsonpath, input=payload)
