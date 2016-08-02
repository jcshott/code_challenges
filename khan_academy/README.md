# Infection
## Project Based Interview: Khan Academy

Goal of this project was to model rolling out new feature to either all or a limited number of students (aka infection).

### Overview

The file <kbd>infection.py</kbd> defines a **User** Object and **CoachingGraph** Object.

To use, simply import the classes into your program
``` python
from infection import CoachingGraph, User
```

Then you can instantiate a Graph and add some users:

``` python
ClassA = CoachingGraph()
for x in range(5):
    ClassA.add_user(version=1)

#Define some connections between users

connections = [(1,2), (2,3), (1,4), (4,5)]
for item in connections:
    ClassA.add_relation(item[0], item[1])
```

Now, if we want to infect the classroom with version 2 starting at user 1

```python
ClassA.total_infection(1,2)
```

Or, a limited infection that fails:
```python
ClassA.limited_infection(start_user_id=1, new_version=3, limit=3)
# will print an error: 'too many users would be infected, new version not implemented for this graph'
```

Or one that succeeds:
```python
ClassA.limited_infection(start_user_id=1, new_version=3, limit=5)
```

### Tests

There 2 sets of tests - Doctest and UnitTests

#### UnitTests

terminal command for unittest
```
python infection_tests.py
```
This will run the included doctests as well.

Running verbosely:
```
python infection_tests.py -v
```
will show more specifics about tests as they run.

#### DocTests
Similarly, you can run just the doctests:
```
python -m doctest -v doctest_infection.txt
```

### Infection.py Details

#### User Attributes:
* self.id: user id, automatically generated integer  when added to the graph (mimicking a primary key in a database)
* self.version: integer representing current version of the software the user is on, defaults to None unless assigned at when instantiating the instance.
* self.relations: set of ids of coaching relationships held by that user. Because this is an undirected graph, all users that are connected have the id of anyone they are directly connected to in this set.

#### CoachingGraph Attributes:
* self.users: dictionary holding the current users in the graph. Key: user.id Value: user object.
* self.total_users: count of users in graph

#### CoachingGraph Methods:
* add_user: add user (vertex) to our coaching graph. if no version is given when called, the version is considered None
* remove_user: remove specified user from graph
* add_relation: add an undirected coaching relationship (edge) to 2 specified users
* remove_relation: remove edge between two users. called when removing user.
* find_relations: find all relations of a given user.
* show_graph: show graph as JSON
* total_infection: infect all connected users in a given graph, starting at a specified user and updating all users to given version. ex. Graph1.total_infection( start_user_id=1, new_version=2)
* limited_infection:  Similar to total_infection except If number of users to receive the version change is greater than the limit, the version change doesn't happen.
