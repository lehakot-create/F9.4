import json
import os

from aiohttp import web, ClientSession

WS_FILE = os.path.join(os.path.dirname(__file__), "websocket.html")

routes = web.RouteTableDef()


@routes.post('/news/')
async def post_handler(request: web.Request):
    res = await request.json()

    async with ClientSession().ws_connect('http://localhost:8080/') as ws:
        await ws.send_str(res['news'])
        await ws.close()

    data = {"status": "ok"}

    return web.json_response(data)


@routes.get('/')
async def wshandler(request: web.Request):
    resp = web.WebSocketResponse()
    available = resp.can_prepare(request)
    if not available:
        with open(WS_FILE, "rb") as fp:
            return web.Response(body=fp.read(), content_type="text/html")

    await resp.prepare(request)

    await resp.send_str("Welcome!!!")

    try:
        print("Someone joined.")
        for ws in request.app["sockets"]:
            await ws.send_str("Someone joined")
        request.app["sockets"].append(resp)

        async for msg in resp:
            if msg.type == web.WSMsgType.TEXT:
                for ws in request.app["sockets"]:
                    if ws is not resp:
                        await ws.send_str(msg.data)
            else:
                return resp
        return resp

    finally:
        request.app["sockets"].remove(resp)
        print("Someone disconnected.")
        for ws in request.app["sockets"]:
            await ws.send_str("Someone disconnected.")


async def on_shutdown(app: web.Application):
    for ws in app["sockets"]:
        await ws.close()


def init():
    app = web.Application()
    app["sockets"] = []
    # app.router.add_get("/", wshandler) # wshandler опишем позже
    # app.router.add_post('/news', posthandler)
    app.add_routes(routes)
    app.on_shutdown.append(on_shutdown)  # on_shutdown опишем позже
    return app


web.run_app(init())
