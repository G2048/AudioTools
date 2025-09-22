import json
import logging
from json import JSONDecodeError
from typing import TypeAlias

from httpx import AsyncClient, Client

from .exceptions import ClientHTTPException

Json: TypeAlias = str


class BaseApi:
    logger = logging.getLogger("app.drivers.api")

    def __init__(self, url: str):
        self.HEADERS = {"Content-Type": "application/json"}
        self.URL = url
        self._status_code = None
        self._url = ""

    @staticmethod
    def _validateJson(jsondata):
        try:
            return jsondata()
        except JSONDecodeError:
            return None

    def _concat_url(self, url: str):
        return self.URL + url

    def __handle_response(self):
        self._status_code = self._response.status_code
        self.logger.debug(self._response.status_code)

        response = self._validateJson(self._response.json)
        if not response:
            response = {"text": self._response.text}

        if self._response.status_code < 300:
            return response
        raise ClientHTTPException(self._response.status_code, response)

    def _request(self, url, query_params=None, method="GET", **kwargs) -> dict:
        url = self._concat_url(url)
        self.logger.debug(f"{url}, {query_params=}, {self.HEADERS=}")

        try:
            with Client(follow_redirects=True, verify=False) as client:
                self._response = client.request(
                    method=method,
                    url=url,
                    params=query_params,
                    headers=self.HEADERS,
                    **kwargs,
                )
        except Exception as e:
            self.logger.error(f"Error while request: {e=}")
            raise e
        finally:
            self.HEADERS.update({"Content-Type": "application/json"})
        self.__handle_response()

    async def _arequest(self, url: str, query_params=None, method="GET", **kwargs):
        url = self.URL + url
        self.logger.debug(f"Async: {url}, {query_params=}, {self.HEADERS=}")
        try:
            with AsyncClient(follow_redirects=True, verify=False) as client:
                self._response = client.request(
                    method=method,
                    url=url,
                    params=query_params,
                    headers=self.HEADERS,
                    **kwargs,
                )
        except Exception as e:
            self.logger.error(f"Error while request: {e=}")
            raise e
        finally:
            self.HEADERS.update({"Content-Type": "application/json"})

        self.__handle_response()

    @property
    def status_code(self) -> int | None:
        return self._status_code

    @status_code.setter
    def status_code(self, value) -> None:
        self._status_code = value

    @staticmethod
    def serialize(data: Json) -> dict:
        return json.loads(data)

    @staticmethod
    def dump(data: dict) -> str:
        return json.dumps(data)
