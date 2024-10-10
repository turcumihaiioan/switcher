from fastapi import FastAPI
from . import __version__

app = FastAPI(
    title="switcher",
    version=__version__,
    license_info={
        "name": "GNU General Public License v3.0 or later",
        "identifier": "GPL-3.0-or-later"
        }
    )


@app.get("/")
async def root():
    return {"message": "Hello World"}
