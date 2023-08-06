from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import secrets
import string
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse  # Import RedirectResponse

# Database setup
# Replace with your PostgreSQL connection URL
SQLALCHEMY_DATABASE_URL = "postgresql://ryhhukph:irLaoNAMHn10ZDXdklu1qp-CrtRPjLGs@surus.db.elephantsql.com/ryhhukph"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Model for URL mapping


class URLMapping(Base):
    __tablename__ = "url_mappings"
    id = Column(Integer, primary_key=True, index=True)
    long_url = Column(String, index=True)
    short_url = Column(String, unique=True, index=True)


app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:3000",  # Replace with the actual frontend URL if different
    "http://localhost:3000/",  # Add the trailing slash variant as well
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the database
Base.metadata.create_all(bind=engine)

# Create URL mapping


def create_short_url(long_url: str) -> str:
    short_url = "".join(secrets.choice(
        string.ascii_letters + string.digits) for _ in range(6))
    db = SessionLocal()
    db_url = URLMapping(long_url=long_url, short_url=short_url)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    db.close()
    return short_url

# API endpoint to create a short URL


class LongURL(BaseModel):
    url: str


@app.post("/shorten/")
def shorten_url(long_url: LongURL):
    short_url = create_short_url(long_url.url)
    # Construct full URL
    full_shortened_url = f"http://localhost:8000/{short_url}"
    return {"short_url": full_shortened_url}  # Return full URL

# API endpoint to get all URLs in a paginated format


@app.get("/urls/")
def get_urls(skip: int = 0, limit: int = 10):
    db = SessionLocal()
    urls = db.query(URLMapping).offset(skip).limit(limit).all()
    db.close()
    return urls

# OPTIONS route to handle preflight requests


@app.options("/shorten/")
def options_shorten(request: Request):
    return {}

# Endpoint for handling redirection


@app.get("/{short_url}")
def redirect_to_long_url(short_url: str):
    db = SessionLocal()
    url_mapping = db.query(URLMapping).filter_by(short_url=short_url).first()
    db.close()
    if url_mapping is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return RedirectResponse(url=url_mapping.long_url)  # Redirect to long URL
