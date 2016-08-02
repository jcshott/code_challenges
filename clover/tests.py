import unittest
import os
import sqlalchemy
import psycopg2
import logging
from model import Base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from load import load_data, check_if_new


class TestDB(unittest.TestCase):
	def setUp(self):
		print "setup"
		url = 'postgresql://corey@localhost:5432/template1'
		self.engine = sqlalchemy.create_engine(url)
		self.connection = self.engine.connect()
		self.connection.connection.connection.set_isolation_level(0)
		self.connection.execute("CREATE DATABASE testdb")
		self.connection.connection.connection.set_isolation_level(0)
		self.db_connection = psycopg2.connect("dbname='testdb' user='corey' host='localhost'")
		Base.metadata.create_all(self.engine)
		self.db_cursor = self.db_connection.cursor()
		self.error_file = open('errortest.log', "w")
		self.error_fn = 'errortest.log'
		logging.basicConfig(filename=self.error_fn, level=logging.ERROR)

	def test_load(self):
		# create test log files instead so we can delete
		self.datelog = open('testimport.log', "w")
		self.datelog_fn = 'testimport.log'
		# run load_data
		load_data(self.db_cursor, self.db_connection, self.datelog_fn)

		# run some test queries to make sure we have what we expect
		self.db_cursor.execute("SELECT * FROM fileformat1")
		assert(len(self.db_cursor.fetchall()) == 3)
		self.db_cursor.execute("SELECT * FROM fileformat1 WHERE valid=True")
		assert(len(self.db_cursor.fetchall()) == 2 )
		self.db_cursor.execute("SELECT * FROM fileformat1 WHERE name='Corey'")
		assert(len(self.db_cursor.fetchall()) == 0)


	def tearDown(self):
		print "teardown"
		# you could remove these if you wanted to see example log output, you just need to be careful because if you run test again with same inputs for data  and not deleting the import dates, you'll get errors because the load program will think you've already loaded those files.
		os.remove('testimport.log')
		os.remove('errortest.log')
		self.db_connection.close()
		self.connection.execute("DROP DATABASE testdb")

if __name__ == '__main__':
	unittest.main()
