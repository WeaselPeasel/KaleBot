import discord
#--------------
import os
import json

# define command prefix and names here
command_prefix = "$"
help_command = "help"
hello_command = "hello"
patch_note_command = "patch_notes"
inspire_command = "inspire"
graph_command = "graph"
graph_help_command = "graph_help"
annoy_command = "annoy"
meme_command = "meme"
launch_code_command = "give me the launch codes"
launch_code_stop_command = "stop!"
gender_command = "mygender"
new_gender_command = "new_gender"
query_gender_command = "query_gender"
approve_gender_command = "approve"
disapprove_gender_command = "disapprove"

# Variables
PING_ON_START = False
DEVELOPMENT_MODE = False
DEBUG_MODE = False
LOGGER_NAME = "kalebotlogger"

seed = 1

BOT_ADMIN = os.getenv("BOT_ADMIN")

color = discord.Color(0).dark_green()

help_dict = {command_prefix + hello_command: "KaleBot says 'Hello!'", 
			 command_prefix + patch_note_command: "Shows the most recent patch notes for Kalebot",
			 command_prefix + inspire_command: "KaleBot sends a random quote", 
			 command_prefix + help_command: "KaleBot sends this help message",
			 command_prefix + launch_code_command: "KaleBot hands over the launch codes",
			 command_prefix + gender_command: "KaleBot predicts your gender randomly",
			 command_prefix + annoy_command + " <user>": "KaleBot pings <user>",
			 command_prefix + new_gender_command + " <gender>": "Propose a new gender to add to the list",
			 command_prefix + query_gender_command: "Show what the current proposed gender is",
			 command_prefix + meme_command: "Sends a random meme that we have on disk",
			 command_prefix + graph_command: "Attach a .csv file to graph the data contents",
			 command_prefix + graph_help_command: "Shows the usage for the $graph command"}

graph_help_dict = {"-graphtype": "The type of graph you want to generate <hist, bar, scatter, line, box>",
				   "-xlabel": "The label you wish to have for your x axis (no spaces)",
				   "-ylabel": "The label you wish to have for your y axis (no spaces)",
				   "-cols": "Which columns do you want graphed? (insert column numbers, starting at 0, separated by commas)",
				   "-headers": "If a row of data in your csv has the headers for the data, put that row number here"}

CURRENT_VERSION = "2.0"


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