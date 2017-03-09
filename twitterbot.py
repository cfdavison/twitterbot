"""
Twitter Bot by Creston Davison
Feb. 22, 2017
For Karen Neicy
Task: Follow users that use hashtags contained in predetermined list
	  and unfollow users that do not follow back.
"""

import twitter_info
import tweepy
import time
import sys
from hashtags import hashtags
searches_per_day = 2
days_to_follow_back = 3

target_users = []
followed_this_cycle = []

class Bot:
	def __init__(self):
		self.CONSUMER_KEY = twitter_info.CONSUMER_KEY
		self.CONSUMER_KEY_SECRET = twitter_info.CONSUMER_KEY_SECRET
		self.ACCESS_TOKEN = twitter_info.ACCESS_TOKEN
		self.ACCESS_TOKEN_SECRET = twitter_info.ACCESS_TOKEN_SECRET
		self.TWITTER_HANDLE = twitter_info.TWITTER_HANDLE
		self.api = self.authen()
		
	def authen(self):
	#authenticate bot to twitter API via Oauth.
		auth = tweepy.OAuthHandler(self.CONSUMER_KEY, self.CONSUMER_KEY_SECRET)
		auth.set_access_token(self.ACCESS_TOKEN, self.ACCESS_TOKEN_SECRET)
		api = tweepy.API(auth)
		try:
			api.verify_credentials()
		except:
			print("The bot was unable to authenticate. Please verify credentials, keys and tokens")
		else:
			print("The bot has been authenticated.")
			return api
	def search_tweets(self, hashtag):
		"""searches twitter API for tweets containing the given hashtag
		   and returns a list of the users' screen names"""
		users = []
		for tweet in tweepy.Cursor(self.api.search, q = hashtag).items(30):
			users.append(tweet.user.screen_name)
			target_users.append("@"+ tweet.user.screen_name)
		print('%s users found using %s:\n' % (len(users), hashtag))
	
	def get_friends(self):
		numfriends = self.api.friends_ids(self.TWITTER_HANDLE)
		friends = []
		for f in numfriends:
			a = self.api.get_user(f).screen_name
			friends.append("@" + a)
		return friends

	def get_followers(self):
		numfollowers = self.api.followers_ids(self.TWITTER_HANDLE)
		followers = []
		for f in numfollowers:
			a = self.api.get_user(f).screen_name
			followers.append("@" + a)
		return followers
		


	def filter_list(self):
		#removes friends from target_users list
		friends = self.get_friends()
		i = 0
		while (i < len(target_users)):
			if target_users[i] in friends:
				del target_users[i]
			else:
				i += 1
		return target_users

	def mass_follow(self):
	#Follows all users in the given list then clears the list
		print("---starting follow process---")
		to_follow = 0
		for user in target_users:
			try:
				self.api.create_friendship(user)
				to_follow += 1
				print("%s) You are now following user: %s" % (to_follow, user))
				followed_this_cycle.append(user)
				time.sleep(5)
			except Exception:
				print("user: %s cannot be followed" % (user))
				pass
		print("---all targets followed---")

	def unfollow(self):
		#unfollows all users that are not following back
		print("---starting unfollow process---")
		followers = self.get_followers()
		friends = followed_this_cycle
		unfollow_count = 0
		for user in friends:
			if user not in followers:
				self.api.destroy_friendship(self.api.get_user(user).screen_name)
				print("You are no longer following user: " + self.api.get_user(user).screen_name)
				unfollow_count += 1
				time.sleep(5)
			print('%s users unfollowed' % (unfollow_count))
		print("---all targets unfollowed---")


#start bot
twitter_bot = Bot()
# who is using this  
print("twitter handle is " + twitter_bot.TWITTER_HANDLE)
# what are the hashtags
print("Hashtags.txt contains %s hashtags" % (len(hashtags)))

#loop
while True:
	tweet_searches = 0
	while tweet_searches < searches_per_day * days_to_follow_back:	
		#searches for tweets containing each hashtag
		for i in hashtags:
			twitter_bot.search_tweets(i)
			time.sleep(5)
		print("There are %s unsortted users" % (len(target_users)))
		#filters out duplicates
		for user in target_users:
			count = 0
			for x in target_users:
				if user == x:
					count += 1
				if count >= 2:
					target_users.remove(x)
					count -= 1
		#remove people already followed from target_users
		target_users = twitter_bot.filter_list()
		print("people already followed removed, %s users remaining" % (len(target_users)))
		#sorts the list in alphabetical order
		target_users.sort()
		#shows how many targeted users were found
		print("There are %s targeted users before mass_follow" % (len(target_users)))
		#follow all targeted users
		twitter_bot.mass_follow()
		tweet_searches += 1
		target_users = []
		#change wait time back to 86400 = 1 day
		time.sleep(85400/searches_per_day)
	#wait 3 days and unfollow
	twitter_bot.unfollow()
	followed_this_cycle = []
	time.sleep(900)




