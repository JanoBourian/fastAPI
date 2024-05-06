from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting app...")
    yield
    print("Finishing app...")


@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Look ma! HTML!</h1>
        </body>
    </html>
    """
