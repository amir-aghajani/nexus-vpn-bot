import os

import uvicorn

from api import web_app
from bot import start_bot_in_background

if __name__ == "__main__":
    start_bot_in_background()
    port = int(os.getenv("API_PORT", "21312"))
    uvicorn.run(web_app, port=port, workers=1)
