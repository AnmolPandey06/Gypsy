from fastapi import FastAPI
from datetime import datetime, time, timedelta
from pydantic import BaseModel
from typing import List
import boto3
from fastapi.middleware.cors import CORSMiddleware



class RouteRequest(BaseModel):
    DeparturePosition: List[float]
    DestinationPosition: List[float]
    DepartureTime: str = datetime.now().isoformat()


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = boto3.client('location', region_name='ap-south-1')


@app.get("/api/search/")
async def search(text: str, maxResults: int = 5):
    """
    Autocompletion Support
    """
    response = client.search_place_index_for_text(
        IndexName='GypsyPlaceIndex',
        Text=text,
        MaxResults=maxResults
    )

    return response


@app.post("/api/getRoute/")
async def getRoute(route: RouteRequest):
    """
    Get the Route Info Based on src and dest (in Lat & Long)
    """

    response = client.calculate_route(
        CalculatorName='GypsyRouteCalculator',
        DepartureTime=route.DepartureTime,
        DeparturePosition=route.DeparturePosition,
        DestinationPosition=route.DestinationPosition
    )

    return response


@app.post("/api/getRoutes")
async def getRoutes(route: RouteRequest):
    """
    Get multiple routes for different times.
    """
    todays_date = datetime.today() + timedelta(days=1)
    times = [
        time(hour=1, minute=00, second=00), 
        time(hour=9, minute=00, second=00), 
        time(hour=12, minute=00, second=00),
        time(hour=17, minute=15, second=00) 
    ]

    diff_times = [datetime.combine(todays_date, time_) for time_ in times]
    responses = []

    for time_ in diff_times:
        route.DepartureTime = time_.isoformat()
        response = client.calculate_route(
            CalculatorName='GypsyRouteCalculator',
            DepartureTime=route.DepartureTime,
            DeparturePosition=route.DeparturePosition,
            DestinationPosition=route.DestinationPosition
        )

        responses.append(response)
    
    return {
        "data": responses
    }
