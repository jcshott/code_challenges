import requests, os, argparse, sys

def get_leg_distance(x, y):
	""" make call to Google Distance API to get the distance between two lat/lon pairs
	Input: 2 strings that are comma seperated lat,lon
	i.e.  '43.6533103,-79.3827675', '45.5017123,-73.5672184'
	Output: distance in meters (int)
	"""

	query_params = {'key': os.environ.get("Google_API_Key"),
					'origin': x,
					'destination': y
					}
	
	endpoint = 'https://maps.googleapis.com/maps/api/directions/json?'
	response = requests.get(endpoint, params=query_params).json()
	
	try:
		distance = response['routes'][0]['legs'][0]['distance']['value']
		return distance
	except Exception, e:
		print "something went wrong with your points, please try again. you need to enter 4 valid lat,long pairs space seperated"
		sys.exit()

def setup_dictionary(a, b, c, d):
	""" create our dictionary to hold the distances between points, so we can easily access each route leg.

		Input: lat,lon of each point
		Output: dictionary of the coordinate pairs that are needed to compare with the distances between each point logged as distance_dict[key]['distance']
	"""
	route_legs = [(a,b), (a, c), (c, d), (d, b), (c, a), (b, d)]
	distance_dict =  {"ab": {"coord_pair": route_legs[0]},
						"ac": {"coord_pair": route_legs[1]},
						"cd": {"coord_pair": route_legs[2]},
						"db": {"coord_pair": route_legs[3]},
						"ca": {"coord_pair": route_legs[4]},
						"bd": {"coord_pair": route_legs[5]}
						}
	
	for key, value in distance_dict.iteritems():
		coord_tuple = value["coord_pair"]
		lat, lon = coord_tuple
		# coordinates = coord_tuple[0] + ", " + coord_tuple[1]
		distance = get_leg_distance(lat, lon)
		distance_dict[key]['distance'] = distance
	
	return distance_dict



def find_shorter_reroute(A, B, C, D):
	"""calculate the shortest reroute distance for 2 drivers starting at points A & C, travelling to B & D (respectively) if one were to pick up/drop off the other
	Input: 4 lat,lon coordinates of the 4 points for the 2 drivers

	Output: shortest re-route:
	driver 1 re-route: (AC, CD, DB) - AB
	driver 2 re-route: (CA, AB, BD) - CD
	
	"""
	# get our dictionary of distances between the 4 points
	distance_dict = setup_dictionary(A, B, C, D)

	# calculate the re-routes
	a_pickup_c = (distance_dict["ac"]["distance"] + distance_dict["cd"]["distance"] + distance_dict["db"]["distance"]) - distance_dict["ab"]["distance"]
	c_pickup_a = (distance_dict["ca"]["distance"] + distance_dict["ab"]["distance"] + distance_dict["bd"]["distance"]) - distance_dict["cd"]["distance"] 

	# evaluate differences and respond accordingly
	if a_pickup_c == c_pickup_a:
		return "It's the same distance for both re-routes!"
	elif a_pickup_c < c_pickup_a:
		return "The distance for driver 1 to re-route is shortest with a distance of %d meters" % (a_pickup_c)
	elif c_pickup_a < a_pickup_c:
		return "The distance for driver 2 to re-route is shortest with a distance of %d meters" % (c_pickup_a)


def main():
	"""parse command line arguments to get user's lat/lon combinations"""

	parser = argparse.ArgumentParser(description="Find shortest re-route for 2 drivers", usage='Add command line args, in order (points A-D), in format latitude,longitude with space between each lat/long point (no spaces around comma btwn lat,long)')
	
	parser.add_argument('A', help='enter the lat,lon of point A, start point of driver 1')
	parser.add_argument('B', help='lat,lon of point B, end point of driver 1')
	parser.add_argument('C', help='lat,lon of point C, start point of driver 2')
	parser.add_argument('D', help='lat,lon of point D, end point of driver 2')
	
	parse_results = parser.parse_args()
	
	A = parse_results.A
	B = parse_results.B
	C = parse_results.C
	D = parse_results.D

	return find_shorter_reroute(A, B, C, D)


if __name__ == '__main__':
	# use print main to print out the message of the returned shorter distance
	print main()



