# utility functions for main.py (mostly string manipulation and munging)
import re


def update_since_id(since_id):
	# record latest status.id that mimic me has made (this is to search for mentions only after this status was made)
	file = open('since_id.txt', 'w')
	file.write(str(since_id))
	file.close()


def get_since_id():
	# get previous status.id of our bot's last mimic (we call it since_id)
	try:
		file = open('since_id.txt', 'r')
		since_id = int(file.readline())
		file.close()
	except IOError:
		since_id = None
	return since_id


def remove_last_word(sentence):
	# Removes the last word of a sentence (and keeps the period).
	# split sentence into a list of all the words, call it post
	post = sentence.split(' ')
	# remove the last word from post
	post = post.remove(post[-1])
	# iterate from list into string again
	new_sentence = ''
	for i in range(len(post)):
		new_sentence = new_sentence + post[i] + ' '
	# Remove extra space and add a period back onto the end of the new sentence.
	new_sentence = new_sentence[:-1] + '.'
	return new_sentence


def remove_handles(text):
	# remove handles # take out all mentions in the generated tweet. (maybe so that random friends don't get mad)
	handles = re.findall('@[^ ]*', text)
	for handle in handles:
		text = text.replace(handle, '')
	return text


def remove_bad_chars(text):
	# remove parentheses
	bad_characters = re.findall('\(', text) + re.findall('\)', text)
	for character in bad_characters:
		text = text.replace(character, '')
	return text


def get_text(statuses):
	# takes in list of statuses and returns a string of their aggregated text
	text = ""
	for status in statuses:
		if status.lang == 'en':
			text += status.text.encode('utf-8') + ' '
	return text


def capitalize_first_word(sentence):
	# takes in a sentence (an array of words) and capitalizes the first
	letter = sentence[0][0]
	rest_of_word = sentence[0][1:]
	capped_word = letter.upper() + rest_of_word
	sentence[0] = capped_word
	return sentence


def add_period_to_the_end(sentence):
	# takes in a sentence (an array of words) and adds a period at the end
	sentence[len(sentence) - 1] = sentence[len(sentence) - 1] + '.'
	return sentence


def list_of_words_to_string(sentence):
	# takes in a sentence (an array of words) and returns a string
	new_tweet = ''
	for i in range(len(sentence)):
		new_tweet = new_tweet + sentence[i] + ' '
	return new_tweet
