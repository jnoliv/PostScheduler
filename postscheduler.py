#!/usr/bin/env python3

import time
import sched
import sqlite3
import os.path
import configparser

try:
	import twitter
except ImportError:
	print('Please install python-twitter:\npip3 install python-twitter\n')
	exit(-1)

try:
	from discord_webhook import DiscordWebhook
except:
	print('Please install discord-webhook:\npip3 install discord-webhook')
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
	"""Fetch and return the Discord Webhook URL if it is configured."""
	if 'Discord' not in config:
		return None

	return config['Discord']['webhook']


def schedule(twitterAPI, discordWebhookURL, scheduler, dbName, scheduledTime, twitterMessage, discordMessage):
	id = 0
	with sqlite3.connect(dbName) as dbConn:
		id = scheduleDB(dbConn.cursor(), scheduledTime, twitterMessage, discordMessage)

	scheduler.enterabs(scheduledTime, 1, post, argument=(twitterAPI, twitterMessage, discordWebhookURL, discordMessage, dbName, id))


def post(twitterAPI, twitterMessage, discordWebhookURL, discordMessage, dbName, dbId):
	"""Post the given message to Twitter and Discord using the given Twitter API wrapper and Discord Webhook URL."""
	print('[' + time.ctime() + '] Posting...')

	if twitterMessage and twitterAPI is not None:
		twitterAPI.PostUpdate(message)

	if discordMessage and discordWebhookURL is not None:
		DiscordWebhook(url=discordWebhookURL, content=message).execute()

	with sqlite3.connect(dbName) as dbConn:
		deleteFromDB(dbConn.cursor(), dbId)


def createDB(cursor):
	"""Create the database schema in the current database connection."""
	schema = """CREATE TABLE ScheduledPosts(
				id INTEGER PRIMARY KEY ASC,
				scheduledTime INTEGER CHECK(scheduledTime NOT NULL AND scheduledTime > 0),
				twitterPost TEXT NOT NULL DEFAULT "",
				discordPost TEXT NOT NULL DEFAULT ""
			  )"""

	cursor.execute(schema)


def scheduleDB(cursor, scheduledTime, twitterMessage, discordMessage):
	query = "INSERT INTO ScheduledPosts(scheduledTime, twitterPost, discordPost) VALUES (?,?,?)"
	return cursor.execute(query, (scheduledTime, twitterMessage, discordMessage)).lastrowid


def deleteFromDB(cursor, dbId):
	query = "DELETE FROM ScheduledPosts WHERE id = ?"
	print(type(dbId))
	cursor.execute(query, (dbId,))


def scheduleAllInDB(twitterAPI, discordWebhookURL, scheduler, dbName):
	query = "SELECT id,scheduledTime, twitterPost, discordPost FROM ScheduledPosts"

	with sqlite3.connect(dbName) as dbConn:
		for row in dbConn.cursor().execute(query):
			scheduler.enterabs(row[1], 1, post, argument=(twitterAPI, row[2], discordWebhookURL, row[3], dbName, row[0]))


def main():
	# Create the scheduled posts database if it doesn't exist
	dbName = 'scheduledposts.db'
	if not os.path.isfile(dbName):
		with sqlite3.connect(dbName) as dbConn:
			createDB(dbConn.cursor())

	# Create the scheduler
	scheduler = sched.scheduler(time.time, time.sleep)

	# Configure
	config = configparser.ConfigParser()
	config.read('postscheduler.conf')

	twitterAPI = setupTwitterAPI(config)
	discordWebhookURL = setupDiscordWebhook(config)

	#scheduler.enterabs(time.time() + 2, 1, post, argument=(twitterAPI, "", discordWebhookURL, ""))

	# Run the scheduler
	scheduler.run()


if __name__ == '__main__':
	main()
