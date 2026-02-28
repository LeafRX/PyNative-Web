import asyncio
import re
import json

class NanoWeb:
    def __init__(self):
        # list (regex_c, handler_h)
        self.routes = []
    def route(self, path):
        """
        decorator that converts simple paths like '/user/<id>' 
        in regular expression capture
        """
        def wrapper(handler):
            # turn syntax <var> to regex groups named (?P<var>[^/]+)
            regex_path = re.sub(r'<(\w+)>', r'(?P<\1>[^/]+)', path)
            regex_path = f"^{regex_path}$"
            self.routes.append((re.compile(regex_path), handler))
            return handler
        return wrapper
    async def handle_request(self, reader, writer):
        data = await reader.read(2048)
        request_text = data.decode('utf-8')
        if not request_text:
            writer.close()
            return
        lines = request_text.splitlines()
        method, full_path, _ = lines[0].split()
        response_body = "404 Not Found"
        status_code = "404 NOT FOUND"
        content_type = "text/plain"
        for pattern, handler in self.routes:
            match = pattern.match(full_path)
            if match:
                kwargs = match.groupdict()
                try:
                    result = await handler(**kwargs)
                    if isinstance(result, dict):
                        response_body = json.dumps(result)
                        content_type = "application/json"
                    else:
                        response_body = str(result)
                        content_type = "text/html"
                    status_code = "200 OK"
                except Exception as e:
                    response_body = f"Error 500: {str(e)}"
                    status_code = "500 INTERNAL SERVER ERROR"
                break
        response = (
            f"HTTP/1.1 {status_code}\r\n"
            f"Content-Type: {content_type}; charset=UTF-8\r\n"
            f"Content-Length: {len(response_body.encode('utf-8'))}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
            f"{response_body}"
        )
        writer.write(response.encode('utf-8'))
        await writer.drain()
        writer.close()
    def run(self, host="127.0.0.1", port=5000):
        loop = asyncio.get_event_loop()
        server_coro = asyncio.start_server(self.handle_request, host, port)
        server = loop.run_until_complete(server_coro)

        print(f"server on http://{host}:{port}")
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.close()
            loop.run_until_complete(server.wait_closed())
