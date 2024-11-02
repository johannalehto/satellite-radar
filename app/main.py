from fastapi import FastAPI
from dotenv import load_dotenv
import requests
import os

from models import SatellitesNowResponse
from service import api_response_to_satellites_now_response

load_dotenv()
api_key = os.getenv("N2YO_API_KEY")

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello Johanna"}

@app.get("/satellites/{lat}/{lon}")
def get_satellites(lat: float, lon: float) -> SatellitesNowResponse:
    api_key = os.getenv("N2YO_API_KEY")
    url = f"https://api.n2yo.com/rest/v1/satellite/above/{lat}/{lon}/0/45/0/?apiKey={api_key}"
    response = requests.get(url).json()
    return api_response_to_satellites_now_response(response, lat, lon)
