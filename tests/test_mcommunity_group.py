import json
import logging
import unittest
from unittest.mock import patch

from mcommunity import mcommunity_mocks as mocks
from mcommunity.mcommunity_group import MCommunityGroup
from mcommunity.mcommunity_user import MCommunityUser

test_group = 'test-group'


class MCommunityGroupTestCase(unittest.TestCase):
    group = None

    @classmethod
    @patch('mcommunity.mcommunity_base.MCommunityBase.search')
    def setUpClass(cls, magic_mock) -> None:
        magic_mock.side_effect = mocks.mcomm_side_effect
        cls.group = MCommunityGroup(test_group, mocks.test_app, mocks.test_secret)

    def test_init_sets_cn(self):
        self.assertEqual(test_group, self.group.name)

    def test_init_sets_raw_group(self):
        self.assertEqual(mocks.group_mock_1, self.group.raw_result)
        self.assertEqual(list, type(self.group.raw_result))
        self.assertEqual(1, len(self.group.raw_result))  # LDAP should always return a 1-item list for a real group
        self.assertEqual(2, len(self.group.raw_result[0]))  # LDAP should always return a 2-item tuple for a real group

    def test_init_sets_members(self):
        self.assertEqual(['nemcardf', 'nemcardrs', 'nemcarda'], self.group.members)

    @patch('mcommunity.mcommunity_base.MCommunityBase.search')
    def test_populate_members_mcomm_users(self, magic_mock):
        magic_mock.side_effect = mocks.mcomm_side_effect
        self.assertEqual([], self.group.members_mcomm_users)  # Before populating, there should not be any
        self.group.populate_members_mcomm_users()
        members = [
            MCommunityUser(uniqname, self.group.mcommunity_app_cn, self.group.mcommunity_app_cn)
            for uniqname in self.group.members
        ]
        self.assertEqual(len(members), len(self.group.members_mcomm_users))  # Should be 4 members
        self.assertEqual(members[0].name, self.group.members_mcomm_users[0].name)  # Make sure first element is same

    def test_group_exists(self):
        self.assertEqual(True, self.group.exists)

    @patch('mcommunity.mcommunity_base.MCommunityBase.search')
    def test_group_not_exists(self, magic_mock):
        magic_mock.side_effect = mocks.mcomm_side_effect
        with self.assertRaises(NameError):
            self.assertEqual(False, MCommunityGroup('fake', mocks.test_app, mocks.test_secret).exists)

    @patch('mcommunity.mcommunity_base.MCommunityBase.search')
    def test_multiple_groups(self, magic_mock):
        magic_mock.side_effect = mocks.mcomm_side_effect
        group_2 = MCommunityGroup('test-group-2', mocks.test_app, mocks.test_secret)
        self.assertNotEqual(self.group.name, group_2.name)
        self.assertNotEqual(len(self.group.members), len(group_2.members))  # Should be 3 and 2
        self.assertEqual(2, len(group_2.members))
        self.assertFalse('nemcarda' in group_2.members)  # Only in first group, shouldn't be in second

    def test_to_dict_produces_json_serializable_group_object(self):
        # Just test JSON serializing the dict object; if an exception is NOT RAISED, it passes
        # If an exception is raised, it will be TypeError: Object of type [type] is not JSON serializable
        self.assertTrue(json.dumps(self.group.to_dict()))

    @patch('mcommunity.mcommunity_base.MCommunityBase.search')
    def test_to_dict_produces_json_serializable_group_object_mcomm_users(self, magic_mock):
        magic_mock.side_effect = mocks.mcomm_side_effect
        # Just test JSON serializing the dict object; if an exception is NOT RAISED, it passes
        # If an exception is raised, it will be TypeError: Object of type [type] is not JSON serializable
        self.group.populate_members_mcomm_users()
        self.assertIsInstance(self.group.members_mcomm_users[0], MCommunityUser)  # Make sure it populated properly
        self.assertTrue(json.dumps(self.group.to_dict()))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main(verbosity=3)
