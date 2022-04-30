import discord
import requests
import json
import random
import db_files.load_db as ldb
from constants import color, message_count, LOGGER_NAME
import logging

# Helper Functions ---------------------------------------------
# set up logger
kalebot_logger = logging.getLogger(LOGGER_NAME)

# get a quote from zenquotes
def get_quote():
	# send a request for some data
	response = requests.get("https://zenquotes.io/api/random")
	json_data = json.loads(response.text)
	quote = json_data[0]['q'] + " -" + json_data[0]['a']
	return(quote)

#---------------------------------------------------------------
# randomly select a gender from our array
def get_gender(gid):
	global message_count

	# get genders from database
	gender_list = ldb.load_gender_list(gid)
	if type(gender_list) != list:
		kalebot_logger.critical("FAILED TO FETCH GENDER LIST: " + gender_list)
		return "AN ERROR: SEE CONSOLE FOR OUTPUT"

	rand_num = random.randint(0, 100)
	seed = rand_num + message_count
	array_index = seed % len(gender_list)
	return gender_list[array_index][0]

#---------------------------------------------------------------
# return a formatted embed to send
def get_embed(title: str = "", body: str = "", names: list = [], 
			values: list = []):
	embed_message = discord.Embed(title=title, type="rich", description=body, 
									colour=color)
	count = 0
	for string in names:
		embed_message.add_field(name=string, value=values[count], 
		inline=True)
		count += 1
	return embed_message

#---------------------------------------------------------------
# randomly pick a meme from our meme folder on disk
def get_meme_from_disk():
	global seed
	global message_count
	global extensions
	global prefixes
	a = 7
	c = message_count
	seed = (a*seed + c) % len(prefixes)
	prefix = prefixes[seed]
	seed = (a*seed + c) % len(extensions)
	extension = extensions[seed]
	directory = "./memes/"
	filepath = directory + prefix + extension
	return filepath