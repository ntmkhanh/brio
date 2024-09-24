import os
import glob
import pandas as pd

folder = './script/'
joined_files = os.path.join(folder, '*.csv') #Get all file csv in folder
list_file = glob.glob(joined_files)
print(list_file)
def merge_csv(list_file):
	df = pd.concat(map(pd.read_csv, list_file))
	# df = df.drop([''], axis=1)
	df.reset_index(drop=True, inplace=True)
	df.to_csv("recipe-dataset.csv".format(len(list_file)))
	print("Done, merged {} links!" .format(len(df.index)))

if __name__ == '__main__':
	merge_csv(list_file)
