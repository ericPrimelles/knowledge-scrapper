from fastapi import FastAPI
from scrapper import scrapper_routine
from pydantic import BaseModel
from typing import List
app = FastAPI()

class ScrapperBody(BaseModel):
    urls : List[str]

@app.post("/scrapper")
async def scrapper(body:ScrapperBody):
    return await scrapper_routine(dict(body), {})