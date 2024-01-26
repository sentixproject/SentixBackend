from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from ntscraper import Nitter
import requests

app = FastAPI()
scraper = Nitter(0)
API_URL = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment"
headers = {"Authorization": "Bearer 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"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	print(response.json())
	return response.json()[0]

class ScraperRequest(BaseModel):
    text: str
    mode: str
    number: int
    language: str = "en"
    

@app.post("/get_tweets")
async def get_tweets(request: ScraperRequest):
    try:
        
        tweets = scraper.get_tweets(request.text, mode=request.mode, number=request.number, language=request.language)

        final_tweets = []
        for x in tweets['tweets']:
            if f"twitter.com/{request.text[1:]}" not in x['link']:
                data = {'twitter_link': x['link'], 'text': x['text'],'score':query({"inputs":x['text']})}
                final_tweets.append(data)

        return final_tweets

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during scraping: {str(e)}")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)