from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

import os

# our database
DB_URI = os.environ.get("DATABASE_URL", 'postgresql://corey@localhost:5432/clover')

# map classes to base
Base = declarative_base()

### Classes to map to tables ###
class Format1(Base):
	""" schema for FileFormat1 data """

	__tablename__ = "fileformat1"

	entry_id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(10), nullable=True)
	valid = Column(Boolean, nullable=True)
	count = Column(Integer, nullable=True)

	def __repr__(self):
		return "<name=%s, valid=%s, count=%i>" % (self.name, self.valid, self.count)


class Format2(Base):
	""" schema for FileFormat1 data """

	__tablename__ = "fileformat2"

	entry_id = Column(Integer, primary_key=True, autoincrement=True)
	city = Column(String(12), nullable=True)
	state = Column(String(2), nullable=True)
	zip_code = Column(Integer, nullable=True)
	area_code = Column(Integer, nullable=True)

	def __repr__(self):
		return "<city=%s, state=%s, zip=%i>" % (self.city, self.state, self.zip_code)
