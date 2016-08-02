from model import DB_URI, Base
from sqlalchemy import create_engine
from psycopg2.extensions import AsIs

import os, psycopg2, logging

def load_data(db_cursor, db_connection, datelog):
	"""
	parse & load new data into database
	"""
	spec_path = "./specs/"
	# get list of files in data/
	data_path = "./data/"
	file_list = os.listdir(data_path)
	# sorted by fileformat and then date w/in that format
	file_list = sorted(file_list)
	specs_seen = {}

	for filename in file_list:
		# parse filename for spec to use
		idx_end_fn = filename.index("_")
		# f_format will be our table name
		f_format = filename[:idx_end_fn]
		f_date = filename[idx_end_fn+1:-4]
		# check last item in our import log to only get new data
		new_file = check_if_new(format_name=f_format, filename=filename, date=f_date, idx_end_fn=idx_end_fn, datelog=datelog)

		if new_file:
			### CAPTURE SPECS ####
			try:
				specs = open(spec_path+f_format+".csv")
			#if we don't have a matching spec file, skip this data file, log error & move on
			except IOError:
				logging.error('Spec Not Found for {}, data file: {}'.format(f_format, filename))
				continue

			# check our specs_seen so if we have multiple data files of same type, we don't parse same specs file more than once
			if f_format in specs_seen:
				name_idx = specs_seen[f_format]["name_idx"]
				type_idx = specs_seen[f_format]["type_idx"]
				width_idx = specs_seen[f_format]["width_idx"]
				col_info = specs_seen[f_format]["col_info"]
			else:
				name_idx = None
				type_idx = None
				width_idx = None
				col_info = []
				for idx, line in enumerate(specs):
					# header row contains where our col name, datatype & width will be found.
					if idx == 0:
						descriptors = line.rstrip().split(",")
						# grab index in line where we will find the col name, type & width
						name_idx = descriptors.index('\"column name\"')
						type_idx = descriptors.index("datatype")
						width_idx = descriptors.index("width")
					else:
						# for each line in our spec file, use known idx create list of col information
						data_list = line.rstrip().split(",")

						# want to store our spec info in the same order that we know will appear in our data file so we store sublists of each column where the name, etc. is stored at same idx we found in the header.
						info = [False]*3
						# ex. in format1: col_name=idx 0, width=idx 1, type=idx 2
						# ea. sublist = [col_name, width, type]
						info[name_idx] = data_list[name_idx]
						info[width_idx] = data_list[width_idx]
						info[type_idx] = data_list[type_idx].lower()
						col_info.append(info)
				specs_seen[f_format] = {"name_idx": name_idx, "type_idx": type_idx, "width_idx": width_idx, "col_info": col_info}
			specs.close()

			## PARSE FILE INFO ##
			file_info = open(data_path+filename)
			for line in file_info:
				# raw data
				data = line.rstrip()
				# raw data lined up with appropriate column
				data_to_load = []
				idx_counter = 0
				# go through our columns we pulled from spec
				for column in col_info:
					# need the column name to map to column in db
					cname = column[name_idx]
					# width to parse data file
					cwidth = int(column[width_idx])
					# type to make sure correct type in db
					ctype = column[type_idx]
					# error handling. if we get data type other than expected skip entry.
					bad_type = False
					# in postgresql, need to convert 1 & 0 to True/False
					if ctype == "boolean":
						if int(data[idx_counter:idx_counter+cwidth]) == 1:
							data_tuple = (cname, True)
						elif int(data[idx_counter:idx_counter+cwidth]) == 0:
							data_tuple = (cname, False)
						else:
							# found a non 1/0
							logging.error('bad boolean {}, data: {} not loaded from {} file'.format(data[idx_counter:idx_counter+cwidth], data, filename))
							bad_type = True
							break
					elif ctype == "integer":
						try:
							int(data[idx_counter:idx_counter+cwidth])
							data_tuple = (cname, data[idx_counter:idx_counter+cwidth].strip())
						except ValueError as e:
							#log error & skip entry
							logging.error('bad int type {}, data: {} not loaded from {} file'.format(data[idx_counter:idx_counter+cwidth], data, filename))
							bad_type = True
							break
					else:
						data_tuple = (cname, data[idx_counter:idx_counter+cwidth].strip())
					# print data_to_load
					data_to_load.append(data_tuple)
					idx_counter = idx_counter + cwidth

				# we've created a list of tuples (column_name, data)
				# ex. [(name, rocky),(valid, True),(number, 654)]
				if bad_type:
					continue
				### load the info for that line into db
				# format string with all columns
				columns = "(" + ",".join([tup[0] for tup in data_to_load]) + ")"
				# format your values-param string to have right num of %s for inserting vals.
				params = "(" + ",".join(["%s" for i in data_to_load]) + ")"
				QUERY = """
							INSERT INTO {} {}
							VALUES {}
						""".format(f_format, columns, params)
				values = tuple([tup[1] for tup in data_to_load])

				try:
					db_cursor.execute(QUERY, values)
					db_connection.commit()
					logging.info('Data Loaded for {}'.format(f_format))
				except Exception as e:
					logging.warning('unable to load data {}, error {}'.format(" ".join(str(values)), e))
			file_info.close()

def check_if_new(format_name, filename, date, idx_end_fn, datelog):
	""" Checks the import log file for most recently uploaded data file of particular filetype.

	Returns True or False depending on if its a newer file
	"""
	with open(datelog, "r+") as current:
		load_dates = current.readlines()
		# empty file
		if not load_dates:
			# write record of data load
			current.write(filename[:-4] + '\n')
			return True
		else:
			# go through data records from end
			for line_idx in range(len(load_dates)-1, -1, -1):
				# if we find a matching filetype. check the date.
				if load_dates[line_idx][:idx_end_fn].strip() == format_name:
					if load_dates[line_idx][idx_end_fn+1:].strip() < date:
						# if our current date is less than last date, load it up & write record to end of file.
						current.seek(0,2)
						current.write(filename[:-4] + '\n')
						return True
					else:
						return False
			# if we get through all records and don't find filetype. ok to upload
			current.seek(0,2)
			current.write(filename[:-4] + '\n')
			return True

def create_tables():
	# connect to db
	engine = create_engine(DB_URI)
	# run create_all in case new table model added
	Base.metadata.create_all(engine)

def main():
	""" set up logging
	create tables if model changed
	run load data
	"""
	# connect to db to run sql load
	try:
		DB = os.environ.get("DATABASE_URL","dbname='clover' user='corey' host='localhost'")
		db_connection = psycopg2.connect(DB)

	except Exception as e:
		print "unable to connect to database"
	# cursor for querying, etc.
	db_cursor = db_connection.cursor()
	# logging set up
	error_fn = 'error.log'
	logging.basicConfig(filename=error_fn, level=logging.DEBUG)
	# create tables if new model found
	create_tables()
	#load data using connection and import.log as fn for date capture
	load_data(db_cursor, db_connection,'import.log')
	db_connection.close()

if __name__ == '__main__':
	main()
