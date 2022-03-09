from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta

from app import crud, dependencies
from app.utils import twitter
from app.routes import follows, tweets

router = APIRouter()

@router.get("/api/twitter_users")
def read_twitter_users(skip: int = 0, limit: int = 100, db: dependencies.Session = Depends(dependencies.get_db)):
    twitter_users = crud.get_twitter_users(db, skip=skip, limit=limit)
    return twitter_users

@router.post("/api/twitter_users", response_model=dependencies.schemas.TwitterUser)
def create_twitter_user_route(twitter_user: dependencies.schemas.TwitterUserCreate, db: dependencies.Session = Depends(dependencies.get_db)):
    return twitter.create_twitter_user(twitter_user=twitter_user, db=db)

@router.post("/api/twitter_users/{twitter_user_id}", response_model=dependencies.schemas.TwitterUser)
def create_twitter_user_from_id(twitter_user_id: str, db: dependencies.Session = Depends(dependencies.get_db)):
    db_twitter_user = crud.get_twitter_user(db=db, twitter_user_id=twitter_user_id)
    if db_twitter_user:
        raise HTTPException(status_code=400, detail="User already exists")
    twitter_user_create = twitter.get_twitter_user_from_twitter(twitter_user_id=twitter_user_id)
    db_twitter_user = twitter.create_twitter_user(twitter_user=twitter_user_create, db=db)
    return db_twitter_user

@router.get("/api/twitter_user/{twitter_user_id}")
def read_twitter_user_by_id(twitter_user_id: str, db: dependencies.Session = Depends(dependencies.get_db)):
    twitter_user = crud.get_twitter_user(db, twitter_user_id=twitter_user_id)
    if twitter_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return twitter_user

@router.get("/api/twitter_user/{twitter_user_id}/tweets")
def read_tweets_by_twitter_user_id(twitter_user_id: str, db: dependencies.Session = Depends(dependencies.get_db)):
    twitter_user = crud.get_twitter_user(db, twitter_user_id=twitter_user_id)
    if twitter_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return twitter_user.tweets


@router.get("/api/twitter_user/{twitter_user_id}/following_tweets")
def read_tweets_of_following_by_twitter_user_id(twitter_user_id: str, db: dependencies.Session = Depends(dependencies.get_db), time_limit: dependencies.Optional[int] = None, urls_only: dependencies.Optional[bool] = False):
    twitter_user = crud.get_twitter_user(db, twitter_user_id=twitter_user_id)
    if twitter_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    following = twitter_user.following

    tweets = []

    for follow in following:
        following = crud.get_twitter_user(db, twitter_user_id=follow.following_id)
        if time_limit:
            for tweet in following.tweets:
                if urls_only:
                    if (not tweet.url == "") and (tweet.url.find("twitter.com") == -1):
                        if (datetime.now() - tweet.time_stamp) < timedelta(hours=time_limit): #converting a time_limit in hours to seconds
                            tweet.name = following.name
                            tweet.username = following.username
                            tweets.append(tweet)
                else:
                    if (datetime.now() - tweet.time_stamp) < timedelta(hours=time_limit): #converting a time_limit in hours to seconds
                        tweet.name = following.name
                        tweet.username = following.username
                        tweets.append(tweet)
        else:
            if urls_only:
                for tweet in following.tweets:
                    if (not tweet.url == "") and (tweet.url.find("twitter.com") == -1):
                        tweet.name = following.name
                        tweet.username = following.username
                        tweets.append(tweet)
            else:
                tweets = tweets + following.tweets

    return tweets

@router.post("/api/twitter_users/{twitter_user_id}/following")
def get_following_by_user_id(twitter_user_id: str, db: dependencies.Session = Depends(dependencies.get_db), max_results: dependencies.Optional[int] = 1000):
    following = dependencies.client.get_users_following(id=twitter_user_id,user_auth=True, max_results=max_results, user_fields=['name', 'profile_image_url', 'username', 'id'])

    counter = 0
    if following.data:
        for following_user in following.data:
            twitter_user = crud.get_twitter_user(db=db, twitter_user_id=following_user.id)
            if not twitter_user:
                twitter_user_create = dependencies.schemas.TwitterUserCreate(id=following_user.id, name=following_user.name, profile_image_url=following_user.profile_image_url, username=following_user.username)
                twitter.create_twitter_user(twitter_user=twitter_user_create, db=db)
                follows.create_follows(dependencies.schemas.FollowCreate(follower_id=twitter_user_id, following_id=following_user.id), db=db)
                counter = counter + 1

    return f'{counter} users created'

@router.post("/api/twitter_user/{twitter_user_id}/tweets")
def create_tweets_of_a_twitter_user_by_id(twitter_user_id: str, db: dependencies.Session = Depends(dependencies.get_db)):

    twitter_user = crud.get_twitter_user(db=db, twitter_user_id=twitter_user_id)

    tweets_array = []
    if len(twitter_user.tweets) > 0:
        sorted_tweets = twitter_user.tweets
        sorted_tweets.sort(key=twitter.get_tweets_time_stamp, reverse=True)
        latest_id = sorted_tweets[0].id
        tweets_array = dependencies.client.get_users_tweets(id=twitter_user_id, user_auth=True, max_results=10, tweet_fields=['entities','created_at'], since_id=latest_id)
    else:
        tweets_array = dependencies.client.get_users_tweets(id=twitter_user_id, user_auth=True, max_results=10, tweet_fields=['entities','created_at'])
    counter = 0

    if tweets_array.data:

        for tweet in tweets_array.data:
            tweet_url = ""

            if tweet.entities:
                entities_data = tweet.entities
                if 'urls' in entities_data:
                    for url in entities_data['urls']:
                        tweet_url = url['expanded_url']
            
            tweet_create = dependencies.schemas.Tweet(id=tweet.id, url=tweet_url, text=tweet.text, twitter_user_id=twitter_user_id, time_stamp=tweet.created_at)

            db_tweet = crud.get_tweet(db=db, tweet_id=tweet_create.id)
            if not db_tweet:
                tweets.create_tweet(tweet=tweet_create, db=db)
                counter = counter + 1
    
    return f'{counter} tweets created'

@router.post("/api/twitter_user/{twitter_user_id}/following_tweets")
def create_tweets_of_following_by_id(twitter_user_id: str, db: dependencies.Session = Depends(dependencies.get_db)):
    twitter_user = crud.get_twitter_user(db=db, twitter_user_id=twitter_user_id)
    if not twitter_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    counter = 0
    for following in twitter_user.following:
        create_tweets_of_a_twitter_user_by_id(twitter_user_id=following.following_id, db=db)
        counter = counter + 1
    
    return f'Tweets from {counter} followings created'