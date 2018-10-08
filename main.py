# Last modified: October 7, 2018 4:20pm
# This script runs the @get_mimicked Twitter bot. 

import datetime as dt
import json
import operator
import sys
import time

from google.cloud import vision
import requests
import twitter

from utils import (
	get_since_id,
	update_since_id,
)


FOREVER = False  # runs while loop forever -- instead of using a scheduler like cron
VERBOSE = False  # will print logs on every run -- false will print only logs when new tweet is posted

# messages
SORRY_RESPONSE = "Sorry, it looks like the media your posted was in the wrong format. Try again with a different photo."
INFORMATION_RESPONSE = "Well, hi there! Tag me in a post with a photo and I'll do my best to find a caption for it!"

# import passwords for Twitter REST API from local text file
passwords_file = open('passwords.txt', 'r')
passwords = passwords_file.readlines()
for password in passwords:
	passwords[passwords.index(password)] = password.replace('\n', '')

twitter_consumer_key = passwords[0]
twitter_consumer_secret = passwords[1]
twitter_access_token = passwords[2]
twitter_access_secret = passwords[3]

passwords_file.close()

twitter_api = twitter.Api(consumer_key=twitter_consumer_key, consumer_secret=twitter_consumer_secret, 
					access_token_key=twitter_access_token, access_token_secret=twitter_access_secret,
					sleep_on_rate_limit=True)


def get_labels(image_url):
	"""Takes in an image url and, using Google's Vision API, returns a list of associated labels"""
	client = vision.ImageAnnotatorClient()
	image = vision.types.Image()
	image.source.image_uri = image_url
	response = client.label_detection(image=image)
	return response.label_annotations


since_id = get_since_id()
mentions = twitter_api.GetMentions(since_id=since_id, count=5)

for mention in mentions:
	print(mention.lang)
	if mention.media:
		if '.jpg' in mention.media[0].media_url or '.png' in mention.media[0].media_url:
			# analyze image with Google Vision API
			labels = get_labels(mention.media[0].media_url)
			labels = labels[:5]

			# find the most favorited tweet with one of the labels in its text content
			most_favorited = None
			most_favorites = 0
			for label in labels:
				tweets = twitter_api.GetSearch(term=label.description, result_type='popular')
				for tweet in tweets:
					if tweet.favorite_count > most_favorites and len(tweet.text) < 200:
						most_favorites = tweet.favorite_count
						most_favorited = tweet
			print("Chosen caption: ", most_favorited.text)

			# respond to the mention with the most favorited tweet's text
			if most_favorited.full_text:
				update = twitter_api.PostUpdate(
					status='@{} '.format(mention.user.screen_name) + most_favorited.full_text + ' -@{}'.format(most_favorited.user.screen_name),
					in_reply_to_status_id=mention.id,
					lang=most_favorited.lang)
				update_since_id(update.id)
			else:
				update = twitter_api.PostUpdate(
					status='@{} '.format(mention.user.screen_name) + most_favorited.text + ' -@{}'.format(most_favorited.user.screen_name),
					in_reply_to_status_id=mention.id)
				update_since_id(update.id)
		else:
			print("Media in wrong format.")
			update = twitter_api.PostUpdate(
				status='@{} '.format(mention.user.screen_name) + SORRY_RESPONSE,
				in_reply_to_status_id=mention.id)
			update_since_id(update.id)
	else:
		print("No media in mention.")
		update = twitter_api.PostUpdate(
			status='@{} '.format(mention.user.screen_name) + INFORMATION_RESPONSE,
			in_reply_to_status_id=mention.id)
		update_since_id(update.id)
