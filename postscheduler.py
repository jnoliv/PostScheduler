#!/usr/bin/env python3

import configparser


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
		print('Could not verify twitter credentials:\n' + e)
		return None

	return twitterAPI



def main():
	config = configparser.ConfigParser()
	config.read('postscheduler.conf')

	twitterAPI = setupTwitterAPI(config)

	twitterAPI.PostUpdate('Hello, I am a test tweet!')


if __name__ == '__main__':
	main()
