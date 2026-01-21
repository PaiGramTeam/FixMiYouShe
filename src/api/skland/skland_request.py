from typing import Union

import hashlib
import hmac
import json
import time
from urllib.parse import urlparse

import httpx
from httpx import Response

from .device_fp import SklandDeviceFP
from ..httpxrequest import HTTPXRequest
from ...error import NetworkException, ResponseException, APIHelperTimedOut
from ...typedefs import POST_DATA, JSON_DATA

__all__ = ("HyperionRequest",)


class HyperionRequest(HTTPXRequest):
    def __init__(self, *args, headers=None, **kwargs):
        self.need_sign = kwargs.pop("need_sign", True)
        self.token = ""
        self.header_for_sign = {
            "platform": "3",
            "timestamp": "",
            "dId": "1",
            "vName": "1.0.0",
        }
        super().__init__(*args, headers=headers, **kwargs)

    async def get_headers(self, timestamp: str = None):
        if timestamp is None:
            timestamp = str(int(time.time()) - 1)
        headers = self.header_for_sign.copy()
        headers["dId"] = await SklandDeviceFP.get_cached_device_id()
        headers["timestamp"] = timestamp
        return headers

    async def request_token(self):
        headers = await self.get_headers()
        token = await self.get(
            "https://zonai.skland.com/web/v1/auth/refresh",
            headers=headers,
            need_sign=False,
        )
        self.token = token.get("token", "")

    async def generate_signature(self, path: str, body_or_query: str):
        t = str(int(time.time()) - 1)
        _token = self.token.encode("utf-8")
        header_ca = await self.get_headers(t)
        header_ca_str = json.dumps(header_ca, separators=(",", ":"))
        s = path + body_or_query + t + header_ca_str
        hex_s = hmac.new(_token, s.encode("utf-8"), hashlib.sha256).hexdigest()
        md5 = hashlib.md5(hex_s.encode("utf-8")).hexdigest()
        return md5, header_ca

    async def get_sign_header(
        self, url: str, method: str, old_header: dict, body: dict | None = None
    ):
        if not self.token:
            await self.request_token()
        h = old_header.copy()
        p = urlparse(url)
        if method.lower() == "get":
            h["sign"], header_ca = await self.generate_signature(p.path, p.query)
        else:
            h["sign"], header_ca = await self.generate_signature(
                p.path, json.dumps(body)
            )
        h.update(header_ca)
        return h

    async def get(
        self,
        url: str,
        *args,
        de_json: bool = True,
        re_json_data: bool = False,
        need_sign: bool = True,
        **kwargs,
    ) -> Union[POST_DATA, JSON_DATA, Response]:
        if self.need_sign and need_sign:
            headers = kwargs.get("headers", {})
            params = kwargs.get("params", {})
            sign_url = str(httpx.URL(url, params=params)) if params else url
            headers = await self.get_sign_header(sign_url, "get", headers)
            kwargs["headers"] = headers
        try:
            response = await self._client.get(url=url, *args, **kwargs)
        except httpx.TimeoutException as err:
            raise APIHelperTimedOut from err
        except httpx.HTTPError as exc:
            raise NetworkException(
                f"Unknown error in HTTP implementation: {repr(exc)}"
            ) from exc
        if not de_json:
            return response
        json_data = response.json()
        return_code = json_data.get("code", None)
        data = json_data.get("data", None)
        message = json_data.get("message", None)
        if return_code is None:
            return json_data
        if return_code != 0:
            if message is None:
                raise ResponseException(
                    message=f"response error in return code: {return_code}"
                )
            raise ResponseException(response=json_data)
        if not re_json_data and data is not None:
            return data
        return json_data

    async def post(
        self,
        url: str,
        *args,
        de_json: bool = True,
        re_json_data: bool = False,
        need_sign: bool = True,
        **kwargs,
    ) -> Union[POST_DATA, JSON_DATA, Response]:
        if self.need_sign and need_sign:
            headers = kwargs.get("headers", {})
            params = kwargs.get("params", {})
            data = kwargs.get("json", {})
            sign_url = str(httpx.URL(url, params=params)) if params else url
            headers = await self.get_sign_header(sign_url, "post", headers, data)
            kwargs["headers"] = headers
        try:
            response = await self._client.post(url=url, *args, **kwargs)
        except httpx.TimeoutException as err:
            raise APIHelperTimedOut from err
        except httpx.HTTPError as exc:
            raise NetworkException(
                f"Unknown error in HTTP implementation: {repr(exc)}"
            ) from exc
        if not de_json:
            return response
        json_data = response.json()
        return_code = json_data.get("code", None)
        data = json_data.get("data", None)
        message = json_data.get("message", None)
        if return_code is None:
            return json_data
        if return_code != 0:
            if message is None:
                raise ResponseException(
                    message=f"response error in return code: {return_code}"
                )
            raise ResponseException(response=json_data)
        if not re_json_data and data is not None:
            return data
        return json_data
