import tweepy
import os

from app import crud, schemas, models

from sqlalchemy.orm import Session

#print(os.environ['TWITTER_ACCESS_TOKEN_SECRET'])

client = tweepy.Client(
    bearer_token=os.environ['TWITTER_TOKEN'],
    consumer_key=os.environ['TWITTER_API_KEY'],
    consumer_secret=os.environ['TWITTER_API_SECRET'],
    access_token=os.environ['TWITTER_ACCESS_TOKEN'],
    access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET']
)



def load_user(twitter_user_id: str, db: Session):
    my_user = client.get_user(id=twitter_user_id, user_auth=True, user_fields=['name', 'profile_image_url'])
    my_user_object = {}
    #print(my_user.data.id)
    my_user_object["id"] = my_user.data.id
    my_user_object["name"] = my_user.data.name
    my_user_object["profile_image_url"] = my_user.data.profile_image_url
    print(my_user_object)
    return(my_user_object)

#following = client.get_users_following(id='364355433',user_auth=True, max_results=1000)

#for following_user in following.data:
    #print(following_user)

