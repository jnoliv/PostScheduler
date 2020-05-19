#!/usr/bin/env python3

import time
import sched
#import sqlite
import configparser

from discord_webhook import DiscordWebhook

try:
	import twitter
except ImportError:
	print('Please install python-twitter:\npip3 install python-twitter\n')
	exit(-1)


def setupTwitterAPI(config):
	"""Create and return the twitter API wrapper if it is configured."""
	if 'Twitter' not in config:
		return None

	twitterConfig = config['Twitter']

	twitterAPI = twitter.Api(
			consumer_key = twitterConfig['consumer_key'],
			consumer_secret = twitterConfig['consumer_secret'],
			access_token_key = twitterConfig['access_token_key'],
			access_token_secret = twitterConfig['access_token_secret']
		)

	try:
		twitterAPI.VerifyCredentials()
	except twitter.error.TwitterError as e:
		print('Invalid Twitter credentials:\n' + e)
		return None

	return twitterAPI


def setupDiscordWebhook(config):
	""""""
	if 'Discord' not in config:
		return None

	return config['Discord']['webhook']


def post(twitterAPI, discordWebhookURL, message):
	print('[' + time.ctime() + '] Posting...')

	if twitterAPI is not None:
		twitterAPI.PostUpdate(message)

	if discordWebhookURL is not None:
		resp = DiscordWebhook(url=discordWebhookURL, content=message).execute()
		print(resp)


def main():
	scheduler = sched.scheduler(time.time, time.sleep)

	config = configparser.ConfigParser()
	config.read('postscheduler.conf')

	twitterAPI = setupTwitterAPI(config)
	discordWebhookURL = setupDiscordWebhook(config)

	message = 'Test123'

	scheduler.enterabs(time.time() + 2, 1, post, argument=(twitterAPI, discordWebhookURL, message))

	scheduler.run()


if __name__ == '__main__':
	main()
