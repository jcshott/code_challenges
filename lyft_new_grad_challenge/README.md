Lyft Code Challenge
====================================
Python script to calculate the detour distance between two different rides. Given four latitude / longitude pairs, where driver one is traveling from point A to point B and driver two is traveling from point C to point D, write a function (in your language of choice) to calculate the shorter of the detour distances the drivers would need to take to pick-up and drop-off the other driver.

____

## Required Info ##

* <b> Python 2.7.1</b>
* <b>Google Maps (Distance) API Token</b>:  Obtain a token from [Google Developer Site](https://console.developers.google.com).
	+ Select "APIs" from your main dashboard
	+ If Google Maps Directions is not already in your enabled API list, find it in the Google API list
	++ You may need to associate it with a new project to retrieve the key (under 'Credentials')

____

## Set-Up ##

**Store API Token as Environment Variable**

However you prefer to store the API token as an environment variable - the script is looking for **Google_API_Key** to make the API calls.

One method is to store as as a shell script:

<kbd>secrets.sh</kbd>

```
export Google_API_Key="YOUR KEY HERE AS A STRING"
```
and then, before running program:

```sh
$ source secrets.sh
```

## Running Program ##

In your local directory for the project:

```sh
$ git clone https://github.com/jcshott/lyft_reroute.git
```

Don't forget to set your environment variable!

```sh
$ source secrets.sh
```

When you run the program, you need to supply the four latitude,longitude points in order A-B.  The individual lat/long are just as I wrote - comma seperated (no space) - and each point is space seperated, as shown below:

```sh
$ python lyft_reroute.py lat,long lat,long lat,long lat,long
```

Example with actual latitude,longitude:

```sh
$ python lyft_reroute.py 37.7839302,-122.4352607 37.7886376,-122.4136639 37.7955745,-122.3955095 37.8023991,-122.4080109
```


####Output

The program will output the driver who, if re-routed, will have the shortest re-route and how far that is by meters.  

Driver 1 is considered to be going from A -> B (1st lat/long pair to 2nd) and Driver 2 is considered to be going from point C -> D (3rd lat/long to 4th).

If there is an error with one of your lat,long points when getting the distance, script will throw and error and exit (with a try/except)