import tweepy
import os

#from app import crud, schemas, models

#from sqlalchemy.orm import Session

#print(os.environ['TWITTER_ACCESS_TOKEN_SECRET'])

client = tweepy.Client(
    bearer_token=os.environ['TWITTER_TOKEN'],
    consumer_key=os.environ['TWITTER_API_KEY'],
    consumer_secret=os.environ['TWITTER_API_SECRET'],
    access_token=os.environ['TWITTER_ACCESS_TOKEN'],
    access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET']
)



#following = client.get_users_following(id='364355433',user_auth=True, max_results=1000)

#for following_user in following.data:
    #print(following_user.profile_image_url)

