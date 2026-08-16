import asyncio
import hashlib
import os

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


def burn_cpu(iterations: int) -> None:
    data = os.urandom(2048)
    for _ in range(iterations):
        hashlib.sha256(data).hexdigest()


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <body>
            <h1>cpu-api</h1>
            <p><a href="/health">/health</a></p>
            <p><a href="/work">/work</a></p>
            <p><a href="/docs">/docs</a></p>
        </body>
    </html>
    """


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/work")
async def work(iterations: int = 150_000):
    await asyncio.to_thread(burn_cpu, iterations)
    return {"status": "done", "iterations": iterations}
