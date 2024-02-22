import json

from fastapi import FastAPI, responses
from fastapi.middleware.cors import CORSMiddleware

import service

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def root():
    res = service.root()
    err = {"status": "error"}
    err = json.dumps(err, indent=4, sort_keys=True, default=str)
    if res:
        return responses.Response(
            content=res,
            status_code=200,
            media_type='application/json'
        )

    else:
        return responses.Response(
            content=err,
            status_code=500,
            media_type='application/json'
        )


@app.get("/parseToLocal")
async def parse_to_local():
    res = service.parse_to_local()
    err = {"status": "error"}
    err = json.dumps(err, indent=4, sort_keys=True, default=str)
    if res:
        return responses.Response(
            content=res,
            status_code=200,
            media_type='application/json'
        )

    else:
        return responses.Response(
            content=err,
            status_code=500,
            media_type='application/json'
        )


@app.get("/parse")
async def parse():
    res = service.parse()
    err = {"status": "error"}
    err = json.dumps(err, indent=4, sort_keys=True, default=str)
    if res:
        return responses.Response(
            content=res,
            status_code=200,
            media_type='application/json'
        )

    else:
        return responses.Response(
            content=err,
            status_code=500,
            media_type='application/json'
        )