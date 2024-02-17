from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ntscraper import Nitter
import requests

app = FastAPI()
scraper = Nitter(0)
API_URL = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment"
headers = {"Authorization": "Bearer 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"}

Check_URL = 'https://status.d420.de/api/v1/instances'


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    print(response.json())
    return response.json()[0]


class ScraperRequest(BaseModel):
    text: str
    mode: str
    number: int
    language: str = "en"


@app.get("/check")
async def root():
    return "Calling Sentix Application for every 10 min..."


@app.post("/get_tweets")
async def get_tweets(request: ScraperRequest):
    
    try:
        
        response = requests.get(Check_URL)
        data = response.json()
        work = []
        tweets = []
        i = 0
        Working_URL = None
        for i in data['hosts']:
            if i['rss']:
                work += [i['url']]
                Working_URL = i['url']
        
        print(Working_URL,"Stage 1")
        print(work)
        for url in work:
            twt = scraper.get_tweets(request.text, mode=request.mode, number=request.number, language=request.language, instance=url)
            print(twt)
            if 'tweets' in twt and len(twt['tweets']) != 0:
                Working_URL = url
                tweets = twt
                break
        print(Working_URL,"Stage 2")
        print(tweets)
        # tweets = scraper.get_tweets(request.text, mode=request.mode, number=request.number, language=request.language)
        final_tweets = []
        for x in tweets['tweets']:
            if f"twitter.com/{request.text[1:]}" not in x['link']:
                data = {'twitter_link': x['link'], 'text': x['text'], 'score': query({"inputs": x['text']})}
                final_tweets.append(data)

        return final_tweets

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during scraping: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
