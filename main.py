import os

import uvicorn

from web import web_app
from bot import start_bot_in_background

if __name__ == '__main__':
    start_bot_in_background()
    host = str(os.getenv('NEXUS_API_IP', '127.0.0.1'))
    port = int(os.getenv('NEXUS_API_PORT', '22222'))
    uvicorn.run(web_app, host=host, port=port, workers=1)
