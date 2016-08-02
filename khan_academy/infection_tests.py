import unittest
import doctest
import infection

def load_tests(loader, tests, ignore):
    """Also run our doctests and file-based doctests."""

    tests.addTests(doctest.DocFileSuite("doctest_infection.txt"))
    return tests

class GraphTestCase(unittest.TestCase):
    def setUp(self):
        """
        create a test graph/classroom with 5 users and some connections between all of them.
        """
        self.testGraph = infection.CoachingGraph()
        # add five users with version 1
        for x in range(5):
            self.testGraph.add_user(version=1)
        # define some coaching relations between the users
        connections = [(1,2), (2,3), (1,4), (4,5)]
        for item in connections:
            self.testGraph.add_relation(item[0], item[1])

    def test_user_count(self):
        """
        make sure we have the number of users we expect
        """
        self.assertEqual(self.testGraph.total_users, 5)
        self.assertEqual(self.testGraph.total_users, len(self.testGraph.users))

    def test_getting_relations(self):
        user1_relations = self.testGraph.users[1].relations
        self.assertEqual(len(user1_relations), 2)

    def test_add_bad_relation(self):
        """
        add a relation where one user doesn't exist
        """
        self.assertRaises(KeyError, self.testGraph.add_relation, 1, 6)

    def test_add_new_user(self):
        """
        add a single user. but don't add a version.
        """
        self.testGraph.add_user()
        self.assertEqual(self.testGraph.total_users, 6)
        self.assertEqual(self.testGraph.users[6].version, None)

    def test_total_infection(self):
        # infect all users starting from user 1 with version 2
        self.testGraph.total_infection(1,2)

        self.assertEqual(self.testGraph.users[3].version, 2)
        self.assertNotEqual(self.testGraph.users[5].version, 1)

        # get all users on version 2
        ver2_users = [user for user in self.testGraph.users if self.testGraph.users[user].version == 2]

        # make sure everyone in our graph is infected
        assert len(ver2_users) == self.testGraph.total_users

    def test_limited_infection(self):

        # check a limited infection on graph with more users than limit
        self.assertEqual(self.testGraph.limited_infection(start_user_id=1, new_version=3, limit=3),"too many users would be infected, new version not implemented for this graph")

        # # check a limited infection on graph that is within limit
        self.testGraph.limited_infection(start_user_id=1, new_version=3, limit=10)
        #
        ver3_users = [user for user in self.testGraph.users if self.testGraph.users[user].version == 3]
        assert len(ver3_users) == self.testGraph.total_users


if __name__ == '__main__':
    # If called like a script, run our tests
    unittest.main()
