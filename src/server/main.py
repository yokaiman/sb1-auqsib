from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
from rss_parser import Parser
import requests
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BlogPost(Base):
    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    source_url = Column(String)

Base.metadata.create_all(bind=engine)

# Pydantic models
class RSSFeed(BaseModel):
    url: str

class LLMConfig(BaseModel):
    name: str
    type: str

class BlogPostPrompt(BaseModel):
    prompt: str

class Automation(BaseModel):
    name: str
    schedule: str

# API routes
@app.post("/rss-feeds")
async def add_rss_feed(feed: RSSFeed):
    # Logic to add RSS feed
    return {"message": "RSS feed added successfully"}

@app.get("/rss-feeds")
async def get_rss_feeds():
    # Logic to retrieve RSS feeds
    return {"feeds": []}

@app.post("/llm-config")
async def add_llm_config(config: LLMConfig):
    # Logic to add LLM configuration
    return {"message": "LLM configuration added successfully"}

@app.get("/llm-config")
async def get_llm_configs():
    # Logic to retrieve LLM configurations
    return {"configs": []}

@app.post("/generate-post")
async def generate_blog_post(prompt: BlogPostPrompt):
    # Logic to generate blog post using LLM
    llm = OpenAI(temperature=0.7)
    prompt_template = PromptTemplate(
        input_variables=["topic"],
        template="Write a blog post about {topic}."
    )
    chain = LLMChain(llm=llm, prompt=prompt_template)
    generated_post = chain.run(topic=prompt.prompt)
    
    # Save generated post to database
    db = SessionLocal()
    new_post = BlogPost(title=prompt.prompt, content=generated_post)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    db.close()
    
    return {"generated_post": generated_post}

@app.post("/automations")
async def add_automation(automation: Automation):
    # Logic to add automation
    return {"message": "Automation added successfully"}

@app.get("/automations")
async def get_automations():
    # Logic to retrieve automations
    return {"automations": []}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)