import matplotlib.pyplot as plt
import random
import string
import pandas

### Contains functions used in generating graphs
# Constants
PLOT_FILE_PATH = "./plots/plots/"

# Seed rand
random.seed()

# generate a file name
def generate_name(ext = ".csv"):
	file_name = ""
	for i in range(0,5):
		char = random.choice(string.ascii_lowercase)
		file_name += char
	return file_name + ext


def fetch_graph(df: pandas.DataFrame, graphtype, xlabel, ylabel, cols):
	plt.figure()

	# set graph type
	if graphtype == None or graphtype == "plot":
		if cols != None:
			df[df.columns[cols]].plot()
		else:
			df.plot()
	else:
		if cols != None:
			df[df.columns[cols]].plot(kind=graphtype)
		else:
			df.plot(kind=graphtype)

	# set labels : DOESNT WORK
	if xlabel != None:
		plt.xlabel(xlabel) 
	if ylabel != None:
		plt.ylabel(ylabel) 

	


	plot_file_name = generate_name(".png")
	plt.savefig(fname=PLOT_FILE_PATH+plot_file_name)
	return plot_file_name