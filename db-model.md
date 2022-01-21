

* users
* * id (primary key)
* * twitter_user_id (foreign key to twitter_users)

* twitter_users
* * id (primary key)
* * name
* * url
* * profile_image_url

* follows
* * twitter_user_id (primary key, foreign key to twitter_users)
* * following_id (foreign key to twitter_users, represents a user followed by twitter_id)

* tweet
* * id (primary key)
* * url
* * text
* * twitter_user_id (foreign key to twitter_users)
* * time_stamp