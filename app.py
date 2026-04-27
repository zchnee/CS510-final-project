"""
app.py - FastAPI Backend Server

Make sure you have pip installed fastapi, uvicorn before running the below cmd

Run with: python -m uvicorn app:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def home():
    return { "message": "Server is up" }