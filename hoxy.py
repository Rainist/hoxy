import os
from dataclasses import dataclass
from http import HTTPStatus
from typing import Optional, Tuple

import aiohttp.client_exceptions as exc
from aiohttp.client import ClientSession
from aiohttp_ultrajson import get_json
from sanic import Sanic, response
from sanic_cors import CORS

__version__ = '{0}.{1}.{2}'.format(*(0, 0, 1))

HTTPResponse = Tuple[int, Optional[dict]]


@dataclass(frozen=True)
class ProxyConfiguration:
    base_url: str


app = Sanic(__name__)  # pylint: disable=invalid-name
app.config.proxy = ProxyConfiguration(os.environ['HOXY_PROXY_BASE_URL'])

CORS(app, automatic_options=True)


@app.listener('before_server_start')
async def init(app_, loop):
    app_.session = ClientSession(loop=loop)


@app.listener('after_server_stop')
async def cleanup(app_, _):
    await app_.session.close()


async def fetch(request) -> HTTPResponse:
    try:
        async with request as r:
            try:
                data = await get_json(r)
            except ValueError:
                data = None

            return r.status, data
    except exc.ClientConnectorError:
        return HTTPStatus.BAD_GATEWAY, None


@app.get('/')
@app.get('/<p:path>')
async def get(r, p=''):
    url = f'{r.app.config.proxy.base_url}/{p}?{r.query_string}'
    status, resp = await fetch(r.app.session.get(url))
    return response.json(resp, status=status)


if __name__ == '__main__':
    app.go_fast(
        host=os.environ.get('HOXY_HTTP_HOST', '0.0.0.0'),
        port=int(os.environ.get('HOXY_HTTP_PORT', 8282)),
        auto_reload=False,
    )
