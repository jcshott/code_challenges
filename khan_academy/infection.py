import json

class User(object):
    """
    Model users.

    Intended to be a helper class. The CoachingGraph is where all the fun happens.

    Attributes:
        -user_id
        -version of the site they see (int)
        -coaching relations between them.
        a relation is added via method in the graph class because when you add a relation, you need a way to ensure it is added to both users in that connection so its a graph-class level method

        A user can coach any number of other users. No self-coaching relationships.

    """
    def __init__(self, version=None):
        # user_ids are auto-generated ints, like a primary key might be in a db.
        # version initiates to "None" unless given one
        # relations are non-directed
        self.id = None
        self.version = version
        self.relations = set()

class CoachingGraph(object):
    """
    Graph object for any given classroom/coaching system

    >>> ClassA = CoachingGraph()
    >>> for x in range(5):
    ...     ClassA.add_user(version=1)

    """

    def __init__(self):
        """
        users is a dict of {user_id: User()-object}
        """
        self.users = {}
        self.total_users = 0
        self.total_relations = 0

    def __repr__(self):
        """
        print out readable output if accessing the graph object
        """
        user_ids = [str(u_id) for u_id in sorted(self.users.keys())]

        return "total users: {}, user_ids: {}".format(self.total_users, ", ".join(user_ids))

    def add_user(self, version=None):
        """
        add user to our coaching graph. if no version is given when called, the version is considered None

        Input: version the new user is using (optional)
        Output: nothing

        """
        # since id is auto-generated, need to grab the most recent added and simply increment
        # if this is the first user added, start at 1
        if not self.users:
            u_id = 1
        else:
            # otherwise, get the length of the dict (num of keys) & our new user_id is +1
            u_id = len(self.users) + 1

        new_user = User(version)
        new_user.id = u_id
        # user_id as key and obj as val in graph's users dict
        self.users[u_id] = new_user
        self.total_users += 1

    def remove_user(self, u_id):
        """
        Method that takes an id as its input, and removes the user with the matching id & removes connection/edges to that user from others in graph
        """
        if u_id in self.users:
            # set of edges
            edges_to_rem = list(self.find_relations(u_id))
            for edge in edges_to_rem:
                self.remove_relation(u_id, edge)
            self.total_users -= 1
            del self.users[u_id]
        else:
            print "user not found"
        return

    def add_relation(self, id_val1, id_val2):
        """
        accepts 2 user_ids as inputs and adds a connection (aka edge) between them.
        """
        try:
            # get the vertex object that corresponds to two given vals
            user_obj1 = self.users[id_val1]
            user_obj2 = self.users[id_val2]
            # add relation to both users since undirected graph
            user_obj1.relations.add(user_obj2.id)
            user_obj2.relations.add(user_obj1.id)
            self.total_relations += 1

        except KeyError as e:
            raise e
            return "need two valid ids to add relation"

    def remove_relation(self, id_val1, id_val2):
        """
        Method that accepts two different id's as its input, and removes the relation/edge between the two users if it exists.
        """
        try:
            user_obj1 = self.users.get(id_val1)
            user_obj2 = self.users.get(id_val2)
            user_obj1.relations.remove(user_obj2.id)
            user_obj2.relations.remove(user_obj1.id)
            self.total_relations -= 1

        except KeyError as e:
            return "need two valid users to delete relation"

    def find_relations(self, id_val):
        """
        Input: id of user
        Output/Return: Set of all connections/edges of that user
        """
        try:
            target_user = self.users.get(id_val)
            # return set of user_id-values given user is connected to
            return target_user.relations
        except KeyError as e:
            raise e
            return

    def show_graph(self):
        """
        return a dict/JSON for D3?
        [{user_id: 1, version: 1, coaching_relations: [u_ids]}]
        """
        output = []

        for u_id, u_object in sorted(self.users.items()):
            output.append({"user_id": u_id, "version": u_object.version, "user_relations": list(u_object.relations)})

        return json.dumps(output, sort_keys=True, indent=4, separators=(',', ': '))


    def total_infection(self, start_user_id, new_version):
        """
        implement the infection algorithm. Starting from any given user (as represented by their id), the entire connected component of the coaching graph containing that user should become infected.

        uses a list to represent a Stack data structure then performs a breadth-first search through the graph to change the version to the new version.

        I used this method (rather than breadth first search using a queue (first-in, first-out)) because we don't care about order that things are changed.   A stack-like data structure (last-in, first-out) is more effecient when using a python list as your base-structure - pop() from end and append() to end are O(1) operations. whereas when you use a queue, you pop() from the beginning, which is a O(N) operation each time.
        """
        # 1. starting at the given user, do a search for all relations
        # 2. update those relations' versions to the new one
        stack = [start_user_id]
        seen = set()

        while stack:
            # grab an id from stack
            curr_id = stack.pop()
            # we only need to change things if we haven't seen this id before.
            if curr_id not in seen:
                seen.add(curr_id)
                # change the current user's version to new one
                curr_obj = self.users.get(curr_id)
                curr_obj.version = new_version
                # find all their relations & add to stack, if we haven't seen that user yet
                relations = self.find_relations(curr_id)
                if relations:
                    for rel in relations:
                        if rel not in seen:
                            stack.append(self.users[rel].id)

    def limited_infection(self, start_user_id, new_version, limit):
        """
        We would like to be able to infect close to a given number of users.

        If more users than limit will be infected, version change doesn't happen

        Input: start user id, new version, limit of infection
        Output: None.
        """
        # 1. starting at the given user, do a search for all relations
        # 2. add user to the seen set
        # 3. check the length of seen, if it is bigger than our limit, we don't change the versions of this graph, otherwise, change them
        stack = [start_user_id]
        seen = set()

        while stack:
            # grab an id from stack
            curr_id = stack.pop()
            # we only need to change things if we haven't seen this id before.
            if curr_id not in seen:
                seen.add(curr_id)
                relations = self.find_relations(curr_id)
                if relations:
                    for rel in relations:
                        if rel not in seen:
                            stack.append(self.users[rel].id)

        if len(seen) <= limit:
            update_lst = list(seen)
            for u_id in update_lst:
                # change the current user's version to new one
                curr_obj = self.users.get(u_id)
                curr_obj.version = new_version
        else:
            return "too many users would be infected, new version not implemented for this graph"
