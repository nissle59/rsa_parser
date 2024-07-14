import json
import logging
from fastapi import FastAPI, responses, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

import config
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
    LOGGER = logging.getLogger(__name__ + ".root")
    res = json.dumps(service.root(), ensure_ascii=False, indent=4, sort_keys=True, default=str)
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
    LOGGER = logging.getLogger(__name__ + ".parseToLocal")
    res = json.dumps(service.parse_to_local(), ensure_ascii=False, indent=4, sort_keys=True, default=str)
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
async def parse(background_tasks: BackgroundTasks):
    LOGGER = logging.getLogger(__name__ + ".parse")
    try:
        background_tasks.add_task(service.parse)
        #res = json.dumps(await service.parse(), ensure_ascii=False, indent=4, sort_keys=True, default=str)
        res = {"status": "success"}
        err = {"status": "error"}
        err = json.dumps(err, indent=4, sort_keys=True, default=str)
    except Exception as e:
        LOGGER.critical(e, config.name, exc_info=True)
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