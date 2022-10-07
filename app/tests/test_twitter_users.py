from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from itsdangerous import json

from app.main import app as meow
from app.models import Follow, Tweet, TwitterUser

client = TestClient(meow)


def mocked_get_twitter_user(*args, **kwargs):

    user = TwitterUser()

    if kwargs.get("twitter_user_id") == "12345":
        user.id = "12345"
        user.name = "Cool Name"
        user.profile_image_url = "https://meow.org"
        user.username = "TheCoolestName"

        follow = Follow()
        follow.id = "1"
        follow.follower_id = "12345"
        follow.following_id = "22222"
        user.following = [follow]
        user.tweets = []

        return user

    elif kwargs.get("twitter_user_id") == "22222":

        user.id = "22222"
        user.name = "Joe Awesome"
        user.profile_image_url = "https://cool.net"
        user.username = "Wheeeeeee"
        user.following = []

        tweet1 = Tweet()
        tweet2 = Tweet()
        tweet3 = Tweet()

        tweet1.twitter_user_id = "22222"
        tweet2.twitter_user_id = "22222"
        tweet3.twitter_user_id = "22222"
        tweet1.url = ""
        tweet3.url = ""
        tweet2.url = "https://thebestwebsite.com"
        tweet1.id = "1"
        tweet2.id = "2"
        tweet3.id = "3"
        tweet1.text = "Fun tweet"
        tweet2.text = "Yay"
        tweet3.text = "The best tweet to ever tweet"
        # TODO make programmatic date stuff
        tweet1.time_stamp = "2022-05-28T14:40:06"
        tweet2.time_stamp = "2022-05-28T08:36:59"
        tweet3.time_stamp = "2022-05-31T14:44:59"

        user.tweets = [tweet2]

        return user
    else:
        return None


@patch("app.routes.users.crud.get_twitter_user", side_effect=mocked_get_twitter_user)
def test_get_following_tweets(mocked_get_twitter_user):
    request_url = f"/api/twitter_users/{12345}/following_tweets?urls_only=true"
    response = client.get(url=request_url)

    assert response.status_code == 200


@patch("app.routes.users.crud.get_twitter_user", side_effect=mocked_get_twitter_user)
def test_get_following_tweets_user_not_found(mocked_get_twitter_user):
    request_url = f"/api/twitter_users/{55555}/following_tweets"
    response = client.get(url=request_url)

    assert response.status_code == 404
