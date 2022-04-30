# Defines the interface for interacting with our database
import psycopg2 as pg
import os
import logging
from src.constants import LOGGER_NAME

# set db connection variables
db_host = os.environ['DB_HOST']
db_name = os.environ['DB_NAME']
db_user = os.environ['DB_USER']
db_pword = os.environ['DB_PWORD']

kalebot_logger = logging.getLogger(LOGGER_NAME)

def get_db():
	conn = pg.connect(host=db_host, database=db_name, user=db_user, password=db_pword)
	return conn


#----------------------------------
def load_gender_list(gid):
	""" gets whole gender list accessible to the requesting server/guild
	:param gid: the id of the reqeusting guild
	:return error string if problem, full list of genders made by server and default genders otherwise
	"""
	query = """SELECT gender FROM gender_table 
	WHERE gid IS NULL 
	OR gid = %s;"""
	conn = get_db()
	cur = conn.cursor()
	try:
		cur.execute(query, (str(gid),))
		results_array = cur.fetchall()
	except pg.DatabaseError as e:
		conn.rollback()
		conn.close()
		return str(e)
	conn.close()
	return results_array

#----------------------------------
def insert_gender(gender, gid):
	""" adds a gender into database with guild id key
	:param gender: the gender string to be added 
	:param gid: the guild id used as a key to store 
	"""
	query = """INSERT INTO gender_table (gid, gender) 
	VALUES (%s, %s);"""
	conn = get_db()
	cur = conn.cursor()
	try:
		cur.execute(query, (str(gid), gender))
	except pg.DatabaseError as e:
		conn.rollback()
		conn.close()
		return str(e)
	conn.commit()
	conn.close()
	return None

#----------------------------------
def check_if_gender_exists(gender, gid) -> bool:
	"""checks if a gender already exists for the given guild
	:param gender: the gender being checked
	:param gid: the querying guild
	:return True if gender is found, False otherwise
	"""
	gender_exists = False
	# check if gender has been 
	query = """SELECT gender FROM gender_table 
	WHERE gender = %s 
	AND (gid IS NULL 
	OR gid = %s);"""
	conn = get_db()
	cur = conn.cursor()
	try:
		cur.execute(query, (str(gender), str(gid)))
	except pg.DatabaseError as e:
		conn.rollback()
		conn.close()
		return str(e)
	result = cur.fetchall()
	if len(result) > 0:
		kalebot_logger.info(f"Suggested gender '{gender}' was found in the gender table")
		gender_exists = True

	query = """SELECT gender_suggestion FROM gender_inputs 
	WHERE gender_suggestion = %s 
	AND gid = %s;"""
	try:
		cur.execute(query, (str(gender), str(gid)))
	except pg.DatabaseError as e:
		conn.rollback()
		conn.close()
		return str(e)
	if len(cur.fetchall()) > 0:
		gender_exists = True
		kalebot_logger.info(f"Suggested gender '{gender}' was found in the gender suggestions")
	conn.close()
	return gender_exists

#----------------------------------
def suggest_gender(gender, gid):
	""" inserts a suggested gender into the suggestions table
	:param gender: the proposed gender
	:param gid: the proposing guild
	:return None if success, otherwise an error string
	"""
	query = """INSERT INTO gender_inputs (gid, gender_suggestion) 
	VALUES (%s, %s);"""
	conn = get_db()
	cur = conn.cursor()
	try:
		cur.execute(query, (str(gid), gender))
	except pg.DatabaseError as e:
		conn.rollback()
		conn.close()
		return str(e)
	conn.commit()
	conn.close()
	return None

#----------------------------------
def get_gender_suggestions(gid):
	query = """SELECT gender_suggestion FROM gender_inputs
	WHERE gid = %s;"""
	conn = get_db()
	cur = conn.cursor()
	try:
		cur.execute(query, (str(gid),))
		results_array = cur.fetchall()
	except pg.DatabaseError as e:
		conn.rollback()
		conn.close()
		return str(e)
	conn.close()
	return results_array

#----------------------------------
def delete_gender_suggestion(gender, gid):
	""" deletes the first one of the suggested genders
	:param gender: the gender to be deleted
	:param gid: the guild id requesting the delete
	:return None if success, otherwise returns the error
	"""
	query = """DELETE FROM gender_inputs 
	WHERE gender_suggestion = %s 
	AND gid = %s;"""
	conn = get_db()
	cur = conn.cursor()
	try:
		cur.execute(query, (gender, str(gid)))
	except pg.DatabaseError as e:
		conn.rollback()
		conn.close()
		return str(e)
	conn.commit()
	conn.close()
	return None