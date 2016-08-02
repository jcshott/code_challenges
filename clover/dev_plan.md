Tech Stack:
-----------
* Python
* PostgreSQL
* SQLAlchemy ORM

Features:
-----------
* Model database based on spec files
* Check types of input, does match what we expect (INT, STRING, BOOLEAN)
* Dynamically load data into variable number of columns.
	* In order for the file to work on different spec files, we can't assume number of columns, column type, column width.
* Log errors
* Log datafiles added so we only add once
* Unittests

Dev Plan:
-----
1. Set up Model based on given spec file
	* Table named by fileformat (i.e. fileformat1) since each fileformat can have different structure (i.e. number of columns) so each needs different table.
2. Establish connection to database in load file
3. Run create_all to create database tables
4. Get all filenames from data/ directory
5. Loop through the filenames and grab the filetype to find associated spec file
6. Open the spec file.
	* Parse spec file and save:
		* indices of column name, width & type
		* column names + width/type info
		* store this info in dict so that we only need to parse that info once.
7. Open data file
	* Use spec info to parse.
		* for each line, grab the indicated number of chars, based on what the spec file told us to look for and store that column name & data for inputting in database
	```
		Spec file:
		column_name, width, type

		Data file:
		row = column (of width & type) column column

		indices of col_name, width, type in spec file => indices of same in each line in data file.

		Example:

		Spec file1:
		column name [idx 0], width[idx 1], type[idx 2]
		name,10,TEXT
		valid,1,BOOLEAN
		count,3,INTEGER

		datafile1:
		entry for column=name first thing we encounter of length 10, type=text.
		at char 11 would be 1 or 0 for column=valid, type=boolean.
		at char 12 be for column=count, type integer <= 3 chars long
	```
8. Once we have a line of data and its associated column, we can load in data.
9. Need to account for unknown number of columns that need to be inserted. Need to construct a SQL insert statement that is not hardcoded for table, number of columns.
10. Need to log errors:
	* data type found != data type expected
	* error loading to db for another reason
	* associated spec file not found
11. Unittests
	* Create testdb to delete at end
	* Same model as active db
	* create test load log and error log so we don't append to active ones
	* run test queries
	* tear-down test db

	[] TODO: probably want some test load data, rather than running on all data in our data files.
