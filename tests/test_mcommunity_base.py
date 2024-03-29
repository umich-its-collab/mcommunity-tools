import json
import logging
import unittest
from unittest.mock import patch

import ldap

from mcommunity import mcommunity_mocks as mocks
from mcommunity.mcommunity_base import MCommunityBase


class MCommunityBaseTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.patcher = patch('mcommunity.mcommunity_base.MCommunityBase.search')
        self.mock = self.patcher.start()
        self.mock.side_effect = mocks.mcomm_side_effect
        self.base = MCommunityBase(mocks.test_app, mocks.test_secret)

    def test_init_sets_app_secret(self):
        self.assertEqual(mocks.test_app, self.base.mcommunity_app_cn)
        self.assertEqual(mocks.test_secret, self.base.mcommunity_secret)

    def test_connect_error_invalid_credentials(self):
        with self.assertRaises(ldap.INVALID_CREDENTIALS):
            self.base.connect()

    @patch('mcommunity.mcommunity_base.MCommunityBase.connect')
    def test_search_retry(self, magic_mock):
        self.patcher.stop()  # Suppress the search patcher on this test only to test the retry
        magic_mock.side_effect = ldap.UNAVAILABLE()
        with self.assertRaises(ldap.UNAVAILABLE):
            self.base.search('ou=People,dc=umich,dc=edu', 'uid=nemcardf', ['*'])
            self.assertEqual(3, magic_mock.call_count)

    def test_search_person_valid(self):
        self.assertEqual(mocks.faculty_mock, self.base.search('ou=People,dc=umich,dc=edu', 'uid=nemcardf', ['*']))

    def test_search_person_invalid(self):
        self.assertEqual([], self.base.search('ou=People,dc=umich,dc=edu', 'uid=fake', ['*']))

    def test_search_group_valid(self):
        self.assertEqual(
            mocks.group_mock_1, self.base.search('ou=User Groups,ou=Groups,dc=umich,dc=edu', 'cn=test-group', ['*']))

    def test_search_group_invalid(self):
        self.assertEqual([], self.base.search('ou=User Groups,ou=Groups,dc=umich,dc=edu', 'uid=fake', ['*']))

    def test_decode_str(self):
        self.base.raw_result = self.base.search('ou=People,dc=umich,dc=edu', 'uid=nemcardf', ['*'])
        self.assertEqual('test_decoding_str', self.base._decode('test_str'))

    def test_decode_empty_list_as_list(self):
        self.base.raw_result = self.base.search('ou=People,dc=umich,dc=edu', 'uid=nemcardna', ['*'])
        self.assertEqual([], self.base._decode('umichServiceEntitlements', return_str=False))

    def test_decode_empty_list_as_str(self):
        self.base.raw_result = self.base.search('ou=People,dc=umich,dc=edu', 'uid=nemcardna', ['*'])
        self.assertEqual('', self.base._decode('umichServiceEntitlements'))

    def test_decode_single_item_list_as_list(self):
        self.base.raw_result = self.base.search('ou=People,dc=umich,dc=edu', 'uid=nemcardf', ['*'])
        self.assertEqual(['Natalie Emcard'], self.base._decode('cn', return_str=False))

    def test_decode_single_item_list_as_str(self):
        self.base.raw_result = self.base.search('ou=People,dc=umich,dc=edu', 'uid=nemcardf', ['*'])
        self.assertEqual('Natalie Emcard', self.base._decode('cn'))

    def test_decode_list(self):
        self.base.raw_result = self.base.search('ou=People,dc=umich,dc=edu', 'uid=nemcardf', ['*'])
        self.assertEqual([
            'FacultyAA', 'RegularStaffDBRN', 'StudentFLNT', 'TemporaryStaffFLNT', 'SponsoredAffiliateAA',
            'Retiree', 'AlumniAA'
        ], self.base._decode('umichInstRoles', return_str=False))

    def test_to_dict_returns_dict_of_attributes(self):
        self.base.raw_result = self.base.search('ou=People,dc=umich,dc=edu', 'uid=nemcardf', ['*'])
        self.assertDictEqual({'mcommunity_app_cn': 'ITS-FakeTestApp-McDirApp001'}, self.base.to_dict())

    def test_to_dict_removes_mcommunity_secret(self):
        self.base.raw_result = self.base.search('ou=People,dc=umich,dc=edu', 'uid=nemcardf', ['*'])
        self.assertIsNone(self.base.to_dict().get('mcommunity_secret'))

    def test_to_dict_removes_raw_result(self):
        self.base.raw_result = self.base.search('ou=People,dc=umich,dc=edu', 'uid=nemcardf', ['*'])
        self.assertIsNone(self.base.to_dict().get('raw_result'))

    def test_to_dict_produces_json_serializable_object(self):
        self.base.raw_result = self.base.search('ou=People,dc=umich,dc=edu', 'uid=nemcardf', ['*'])
        self.assertEqual('{"mcommunity_app_cn": "ITS-FakeTestApp-McDirApp001"}', json.dumps(self.base.to_dict()))

    def tearDown(self) -> None:
        self.patcher.stop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main(verbosity=3)
