# Native imports
import os
import json
import random
import sys
import time as t
import queue as qu
from csv import Sniffer, Error

# venv imports
import discord
from dotenv import load_dotenv
import requests
import pandas

# Allow access to environment variables
load_dotenv()

# local imports
import gifs.gifs as g
import plots.drawplot as myplot
import db_files.load_db as ldb

### Begin

client = discord.Client()

# make sure we have the members intent
discord.Intents.members = True
# Set the random seed for gender selection
random.seed()

# Variables
PING_ON_START = False
DEVELOPMENT_MODE = False
DEBUG_MODE = False

seed = 1

BOT_ADMIN = os.getenv("BOT_ADMIN")

color = discord.Color(0).dark_green()

help_dict = {"$hello": "KaleBot says 'Hello!'", 
			 "$inspire": "KaleBot sends a random quote", 
			 "$help": "KaleBot sends this help message",
			 "$give me the launch codes": "KaleBot hands over the launch codes",
			 "$mygender": "KaleBot predicts your gender randomly",
			 "$annoy <user>": "KaleBot pings <user>",
			 "$new gender <gender>": "Propose a new gender to add to the list",
			 "$query_gender": "Show what the current proposed gender is",
			 "$meme": "Sends a random meme that we have on disk",
			 "$graph": "Attach a .csv file to graph the data contents",
			 "$graph_help": "Shows the usage for the $graph command"}

graph_help_dict = {"-graphtype": "The type of graph you want to generate <hist, bar, scatter, line, box>",
				   "-xlabel": "The label you wish to have for your x axis (no spaces)",
				   "-ylabel": "The label you wish to have for your y axis (no spaces)",
				   "-cols": "Which columns do you want graphed? (insert column numbers, starting at 0, separated by commas)",
				   "-headers": "If a row of data in your csv has the headers for the data, put that row number here"}

# gender variables
# genders = ["non-binary", "g0rl", "boi", "femboy", 
# 			"awfuckicantbelieveyouvedonethis", "trans", "yes", "no", "sex god", 
# 			"Obama", "the Gay Agenda", "somewhere in between", 
# 			"you need therapy, not a bot", "robot", "squishmallow", "furry", 
# 			"fury", "a _mystery_", "cuck", "cis-het :("]

MAX_GENDER_LENGTH = 50
MAX_MESSAGE_COUNT = 113
message_count = 0
GENDERS_FILE = "input_gender_list.txt"

# Plotting Variables
CSV_LOCATIONS = "./plots/files/"
#OPTION_PREFIX = "-"
OPTIONS_LIST = ["graphtype", "xlabel", "ylabel", "cols", "headers"]

# meme list
extensions = [".png", ".jpg"]
prefixes = ["meme1", "meme2", "meme3"]

# launch code variables
MINUTES_TO_WIN = 15
stop_word = False
launch_code_owner = ""
t1 = 0
t2 = 0
# Helper Functions ---------------------------------------------

# get a quote from zenquotes
def get_quote():
	# send a request for some data
	response = requests.get("https://zenquotes.io/api/random")
	json_data = json.loads(response.text)
	quote = json_data[0]['q'] + " -" + json_data[0]['a']
	return(quote)

# randomly select a gender from our array
def get_gender(gid):
	global message_count

	# get genders from database
	gender_list = ldb.load_gender_list(gid)
	if type(gender_list) != list:
		print(gender_list)
		return "AN ERROR: SEE CONSOLE FOR OUTPUT"

	rand_num = random.randint(0, 100)
	seed = rand_num + message_count
	array_index = seed % len(gender_list)
	return gender_list[array_index][0]

# return a formatted embed to send
def get_embed(title: str = None, body: str = None, names: list = [], 
			values: list = []):
	embed_message = discord.Embed(title=title, type="rich", description=body, 
									colour=color)
	count = 0
	for string in names:
		embed_message.add_field(name=string, value=values[count], 
		inline=True)
		count += 1
	return embed_message

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


# Discord Functions --------------------------------------------
@client.event
async def on_ready():
	# triggers when KaleBot connects to servers
	print("We have logged in as user {0.user}".format(client))
	if PING_ON_START == True:
		text_channel_list = client.get_all_channels()
		for channel in text_channel_list:
			if channel.name == "the-lab" or channel.name == "kalebot-tomfoolery":
				await channel.send("I am now awake!")

	if DEVELOPMENT_MODE == True:
		text_channel_list = client.get_all_channels()
		for channel in text_channel_list:
			if channel.name == "the-lab" or channel.name == "kalebot-tomfoolery":
				await channel.send("KaleBot is in development. Expect interruptions")

	
@client.event
async def on_disconnect():
	# triggers if KaleBot diconnects (but not if terminated)
	# text_channel_list = client.get_all_channels()
	# for channel in text_channel_list:
	# 	if channel.name == "the-lab":
	# 		await channel.send("I am going to sleep")
	# print("Kalebot has gone to bed...")
	pass

@client.event
async def on_message(message):
	# triggers whenever a message is sent to a channel
	# declare some globals
	global stop_word
	global launch_code_owner
	global t1
	global t2
	global MAX_MESSAGE_COUNT
	global message_count
	global BOT_ADMIN

	# increment message count for gender selection
	message_count += 1
	if message_count >= MAX_MESSAGE_COUNT:
		message_count = 0

	# do nothing if KaleBot sends message
	if message.author == client.user or stop_word == True:
		return
	else:
		stop_word = False

	### RANDOM JARGON
	# KaleBot says hello
	if message.content.startswith("$hello"):
		# await message.channel.send("Hello!") 
		await message.channel.send(embed=get_embed(title=None, body="Hello!", 
													names=[], values=[]))

	# Send an inspirational quote
	elif message.content.startswith("$inspire"):
		quote = get_quote()
		await message.channel.send(embed=get_embed(title=None, body=quote))

	# print out a help message
	elif message.content.startswith("$help"):
		names = []
		values = []
		for key in help_dict:
			names.append(key + ':')
			values.append(" " + help_dict[key])
		await message.channel.send(embed=get_embed(title="Help", names=names, 
												values=values))

	# get graph help
	elif message.content.startswith("$graphhelp") or message.content.startswith("$graph_help"):
		names = []
		values = []
		for key in graph_help_dict:
			names.append(key + ':')
			values.append(" " + graph_help_dict[key])
		await message.channel.send(embed=get_embed(title="Graph Help", names=names, 
											values=values))

	# tag a user
	elif message.content.startswith("$annoy"):
		get_name = message.content.split("$annoy ")
		name = get_name[1]

		uid = -1
		# if user has been tagged, get their ID
		if name.startswith("<@!"):
			uid = name.strip("<@!>")
		member_list = message.guild.fetch_members()
		async for member in member_list:
			if member.name == name or member.display_name == name or member.id == uid:
				uid = member.id
		if uid == -1:
			await message.channel.send(embed=get_embed(body="Whatchu talkin bout, Willis??"))
		else:
			await message.channel.send(embed=get_embed(body="Sup, <@!{0}>".format(uid)))

	# Post a random meme
	elif message.content.startswith("$meme"):
		# get meme
		file_path = get_meme_from_disk()
		Dfile = discord.File(file_path, filename="meme.png")
		embed = discord.Embed(colour=color, title="Meme")
		embed.set_image(url="attachment://meme.png")
		await message.channel.send(file=Dfile, embed=embed)

	# Get a data graph
	elif message.content.startswith("$graph"):
		# check for message attachments
		if message.attachments:
			# get first attachment and download file
			file_url = message.attachments[0].url
			file_request = requests.get(file_url)
			try:
				file_str = file_request.content.decode('utf-8')
			except UnicodeDecodeError as e:
				await message.channel.send(embed=get_embed(title="Error", body="Can't decode csv file\n"+str(e)))
				return
			
			## write csv data to temporary file
			csv_file_name = myplot.generate_name()
			
			# write out csv data
			csv_file = open(CSV_LOCATIONS+csv_file_name, "x")
			csv_file.write(file_str)
			csv_file.close()

			# make sure that file is in csv format
			# try:
			# 	is_csv = Sniffer().sniff(file_str, [",", ";"])
			# except Error as e:
			# 	# delete csv file
			# 	csv_file.close()
			# 	os.remove(CSV_LOCATIONS+csv_file_name)
			# 	await message.channel.send(embed=get_embed(body=e))
			# 	return

			# Parse options from input string
			graphtype = None
			xlabel = None
			ylabel = None
			cols = None
			headers = None
			substring = message.content.split("$graph ")
			args = substring[1].split("-")
			for arg in args:
				cmd = arg.split(" ")
				if cmd[0] == OPTIONS_LIST[0]:	# graphtype
					graphtype = cmd[1]
				elif cmd[0] == OPTIONS_LIST[1]:	# xlabel
					xlabel = cmd[1]
				elif cmd[0] == OPTIONS_LIST[2]:	# ylabel
					ylabel = cmd[1]
				elif cmd[0] == OPTIONS_LIST[3]:	# cols
					cols = cmd[1].split(",")
					for i in range(len(cols)):
						cols[i] = int(cols[i])
				elif cmd[0] == OPTIONS_LIST[4]:	#headers
					headers = int(cmd[1])


			# make a dataframe from the csv. until additional options are added, default to provided header names
			data_frame = pandas.read_csv(CSV_LOCATIONS+csv_file_name, delimiter=",", header=headers)
			# try:
			# 	data_frame = pandas.read_csv(CSV_LOCATIONS+csv_file_name, delimiter=",", header=headers)
			# except:
			# 	# delete csv file
			# 	os.remove(CSV_LOCATIONS+csv_file_name)
			# 	await message.channel.send(embed=get_embed(body="Could not fetch csv data"))
			# 	return

			

			# delete csv file
			os.remove(CSV_LOCATIONS+csv_file_name)
			
			# lets graph
			pyplot_file = myplot.fetch_graph(data_frame, graphtype,xlabel,ylabel,cols)
			Dfile = discord.File(myplot.PLOT_FILE_PATH+pyplot_file, filename="graph.png")
			embed = discord.Embed(colour=color, title="Graph")
			embed.set_image(url="attachment://graph.png")
			await message.channel.send(file=Dfile, embed=embed)
			os.remove(myplot.PLOT_FILE_PATH+pyplot_file)
			#print(file_request.content.decode('utf-8'))

		# if message has no attachments, 
		else:
			await message.channel.send(embed=get_embed(body="There is no data to graph :("))


	### LAUNCH CODE GAME
	# Play the launch code game
	elif message.content == "$give me the launch codes":
		if launch_code_owner != "":
			await message.channel.send(embed=get_embed(title=None, body="Sorry, "
								"but {0} has the launch codes already!!".format(launch_code_owner)))
		launch_code_owner = message.author.display_name
		await message.channel.send(embed=get_embed(
			title="Quick! {0} has seized the lAuNcH coDEs!!".format(launch_code_owner), 
			body="Type '$stop!' to stop them!")
		)
		# maybe add a timer or something?
		t1 = t.time()

	# stop the launch code game
	elif message.content.startswith("$stop!"):
		t2 = t.time()
		if launch_code_owner == "":
			await message.channel.send(embed=get_embed(body="No one has the launch codes..."))
		elif int(t2 - t1) / 60 > MINUTES_TO_WIN:
			embed_data = get_embed(title="Uh Oh!", body="You failed to stop {0}! "\
				 					"The nukes have been LaUncHeD".format(launch_code_owner))
			await message.channel.send(embed=embed_data, file=discord.File("./gifs/stark_bombs.gif"))
			launch_code_owner = ""
			t1 = 0
			t2 = 0
		else:
			await message.channel.send(embed=get_embed(title="Congrats!", 
									body="{0} has been stopped!".format(launch_code_owner)))
			launch_code_owner = ""


	### GENDER SECTION
	# Randomly assign a gender
	elif message.content.startswith("$mygender"):
		await message.channel.send(embed=get_embed(body="**<@!{0.id}>'s gender is:** {1}".format(message.author, get_gender(message.guild.id))))
		
	# Propose a gender
	elif message.content.startswith("$new gender"):
		raw_gender = message.content.split("$new gender")
		# make sure a gender was actually proposed
		if len(raw_gender) <= 1:
			await message.channel.send(embed=get_embed(body="No gender supplied"))
		gender = (raw_gender[1].strip()).replace("  ", " ")

		if len(gender) > MAX_GENDER_LENGTH:
			await message.channel.send(embed=get_embed(body="That gender is too long"))
		else:
			gender_exists = ldb.check_if_gender_exists(gender, message.guild.id)
			if gender_exists == False:
				err = ldb.suggest_gender(gender, message.guild.id)
				# print error in discord if there is one
				if err != None:
					await message.channel.send(embed=get_embed(title="DEBUG", body=err))
				# add gender to suggestions and send message
				await message.channel.send(embed=get_embed(body=
					"Await approval from an admin"))
			else:
				# print("DEBUG:\t", gender_exists)
				await message.channel.send(embed=get_embed(title="!!!That gender already exists for this server!!!", body=""))

	elif message.content.startswith("$query_gender"):
		proposed_genders = ldb.get_gender_suggestions(message.guild.id)
		# show first element of the array 
		err = None
		gender = '*NO NEW GENDERS*'
		if len(proposed_genders) > 0:
			gender = proposed_genders[0][0]
			err = ldb.insert_gender(gender, message.guild.id)
		if err != None:
			await message.channel.send(embed=get_embed(title="DEBUG", body=err))
		else:
			await message.channel.send(embed=get_embed(body="`Gender is` {0}".format(gender)))
		#await message.channel.send(embed=get_embed(title="Feature not Implemented\n", 
		#body="Someone tell Kale to get to it"))
		#await message.channel.send(embed=get_embed(title="The proposed gender is: \n", 
		#							body="> {}".format(proposed_gender)))

	elif message.content.startswith("$approve"):
		if message.author.guild_permissions.administrator == True:
			# Access Gender database
			proposed_genders = ldb.get_gender_suggestions(message.guild.id)
			# add first element of the array to genders list
			err = None
			gender = ""
			if len(proposed_genders) > 0:
				gender = proposed_genders[0][0]
				err = ldb.insert_gender(gender, message.guild.id)
			if err != None:
				await message.channel.send(embed=get_embed(title="DEBUG", body=err))
			else:
				ldb.delete_gender_suggestion(gender, message.guild.id)
			

			await message.channel.send(embed=get_embed(body="`Gender has been approved!`"))
		else:
			await message.channel.send(embed=get_embed(body="`Nice try binch >:D`"))

	elif message.content.startswith("$disapprove"):
		if message.author.name == BOT_ADMIN:
			proposed_genders = ldb.get_gender_suggestions(message.guild.id)
			# add first element of the array to genders list
			err = None
			if len(proposed_genders) > 0:
				gender = proposed_genders[0][0]
				err = ldb.delete_gender_suggestion(gender, message.guild.id)
			if err != None:
				await message.channel.send(embed=get_embed(title="DEBUG", body=err))

			await message.channel.send(embed=get_embed(body="`Gender has not been approved :(`"))
		else:
			await message.channel.send(embed=get_embed(body="`You are not authorized to complete this action`"))

	# Maybe do something here
	elif message.content.startswith("$"):
		#print(message.content)
		pass

# run the discord bot with its private token
client.run(os.getenv("TOKEN"))
