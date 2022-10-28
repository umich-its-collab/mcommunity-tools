import json
import logging
import unittest
from unittest.mock import patch

from mcommunity import mcommunity_mocks as mocks
from mcommunity.mcommunity_user import MCommunityUser

test_user = 'nemcardf'


class MCommunityUserTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.patcher = patch('mcommunity.mcommunity_base.MCommunityBase.search')
        self.mock = self.patcher.start()
        self.mock.side_effect = mocks.mcomm_side_effect
        self.user = MCommunityUser(test_user, mocks.test_app, mocks.test_secret)
        self.nemcardf_dict = {
            'affiliations': [],
            'display_name': 'Natalie Emcard',
            'email': 'nemcardf@umich.edu',
            'entityid': '00000000',
            'errors': None,
            'exists': True,
            'highest_affiliation': '',
            'mcommunity_app_cn': 'ITS-FakeTestApp-McDirApp001',
            'name': 'nemcardf',
            'query_object': 'uid=nemcardf',
            'service_entitlements': []
        }
        self.nemcardf_dict_populated = self.nemcardf_dict.copy()
        self.nemcardf_dict_populated['affiliations'] = [
            'FacultyAA', 'RegularStaffDBRN', 'StudentFLNT', 'TemporaryStaffFLNT',
            'SponsoredAffiliateAA', 'Retiree', 'AlumniAA'
        ]
        self.nemcardf_dict_populated['highest_affiliation'] = 'Faculty'
        self.nemcardf_dict_populated['service_entitlements'] = [
            '{"system":"papercut","changeDate":"20141201050814Z","foreignKey":"",'
            '"eligibility":"yesDelay","status":"role","action":""}',
            '{"system":"tdx","changeDate":"20200520160600Z","foreignKey":"5fd61fa7-035f-ea11-a81b-000d3a8e391e",'
            '"eligibility":"yes","status":"active","action":""}',
            '{"system":"box","changeDate":"20200815082046Z","foreignKey":"229315957","eligibility":"yesDelay",'
            '"status":"active","action":""}',
            '{"system":"canvas","changeDate":"20200821155033Z","foreignKey":"327664","eligibility":"yesImmed",'
            '"status":"active","action":""}',
            '{"system":"dropbox","changeDate":"20200929151240Z","foreignKey":"dbmid:x","eligibility":"yesDelay",'
            '"status":"active","action":""}',
            '{"system":"linkedinlearning","changeDate":"20201017144315Z","foreignKey":"","eligibility":"yesDelay",'
            '"status":"","action":""}',
            '{"system":"adobecc","changeDate":"20201017144315Z","foreignKey":"","eligibility":"cc","status":"",'
            '"action":""}',
            '{"system":"enterprise","changeDate":"20210721193419Z","eligibility":"yes","status":"active","action":""}'
        ]

    def test_init_sets_name(self):
        self.assertEqual(test_user, self.user.name)

    def test_init_sets_email(self):
        self.assertEqual(f'{test_user}@umich.edu', self.user.email)

    def test_user_not_exists(self):
        user = MCommunityUser('fake', mocks.test_app, mocks.test_secret)
        self.assertIsInstance(user.errors, NameError)
        self.assertEqual(False, user.exists)
        self.assertEqual('', user.entityid)

    def test_user_exists(self):
        self.assertEqual(True, self.user.exists)

    def test_init_sets_entityid(self):
        self.assertEqual('00000000', self.user.entityid)

    def test_init_sets_display_name(self):
        self.assertEqual('Natalie Emcard', self.user.display_name)

    def test_init_sets_raw_result(self):
        self.assertEqual(mocks.faculty_mock, self.user.raw_result)
        self.assertEqual(list, type(self.user.raw_result))
        self.assertEqual(1, len(self.user.raw_result))  # LDAP should always return a 1-item list for a real person
        self.assertEqual(2, len(self.user.raw_result[0]))  # LDAP should always return a 2-item tuple for a real person

    def test_check_service_entitlements_eligible(self):
        self.assertEqual(True, self.user.check_service_entitlement('enterprise'))

    def test_check_service_entitlements_not_eligible(self):
        user = MCommunityUser('nemcardr', mocks.test_app, mocks.test_secret)  # Retiree uniqname
        self.assertEqual(False, user.check_service_entitlement('enterprise'))

    def test_check_sponsorship_type_sa1(self):
        user = MCommunityUser('nemcardsa1', mocks.test_app, mocks.test_secret)
        self.assertEqual(1, user.check_sponsorship_type())

    def test_check_sponsorship_type_sa2(self):
        user = MCommunityUser('nemcardsa2', mocks.test_app, mocks.test_secret)
        self.assertEqual(2, user.check_sponsorship_type())

    def test_check_sponsorship_type_sa3(self):
        user = MCommunityUser('um999999', mocks.test_app, mocks.test_secret)
        self.assertEqual(3, user.check_sponsorship_type())

    def test_check_sponsorship_type_not_sponsored(self):
        self.assertEqual(0, self.user.check_sponsorship_type())

    def test_populate_affiliations(self):
        self.assertEqual([], self.user.affiliations)  # Before populating, there should not be any
        self.user.populate_affiliations()
        self.assertEqual([
            'FacultyAA', 'RegularStaffDBRN', 'StudentFLNT', 'TemporaryStaffFLNT', 'SponsoredAffiliateAA',
            'Retiree', 'AlumniAA'
        ], self.user.affiliations)

    def test_populate_affiliations_no_roles(self):
        user = MCommunityUser('nemcardna', mocks.test_app, mocks.test_secret)
        self.assertEqual([], user.affiliations)  # Before populating, there should not be any
        user.populate_affiliations()
        self.assertEqual([], user.affiliations)

    def test_populate_highest_affiliation_faculty(self):
        self.assertEqual('', self.user.highest_affiliation)
        self.user.populate_highest_affiliation()
        self.assertEqual('Faculty', self.user.highest_affiliation)

    def test_populate_highest_affiliation_regstaff(self):
        user = MCommunityUser('nemcardrs', mocks.test_app, mocks.test_secret)
        self.assertEqual('', user.highest_affiliation)
        user.populate_highest_affiliation()
        self.assertEqual('RegularStaff', user.highest_affiliation)

    def test_populate_highest_affiliation_student(self):
        user = MCommunityUser('nemcards', mocks.test_app, mocks.test_secret)
        self.assertEqual('', user.highest_affiliation)
        user.populate_highest_affiliation()
        self.assertEqual('Student', user.highest_affiliation)

    def test_populate_highest_affiliation_tempstaff(self):
        user = MCommunityUser('nemcardts', mocks.test_app, mocks.test_secret)
        self.assertEqual('', user.highest_affiliation)
        user.populate_highest_affiliation()
        self.assertEqual('TemporaryStaff', user.highest_affiliation)

    def test_populate_highest_affiliation_sa1(self):
        user = MCommunityUser('nemcardsa1', mocks.test_app, mocks.test_secret)
        self.assertEqual('', user.highest_affiliation)
        user.populate_highest_affiliation()
        self.assertEqual('SponsoredAffiliate', user.highest_affiliation)

    def test_populate_highest_affiliation_retiree(self):
        user = MCommunityUser('nemcardr', mocks.test_app, mocks.test_secret)
        self.assertEqual('', user.highest_affiliation)
        user.populate_highest_affiliation()
        self.assertEqual('Retiree', user.highest_affiliation)

    def test_populate_highest_affiliation_alumni(self):
        user = MCommunityUser('nemcarda', mocks.test_app, mocks.test_secret)
        self.assertEqual('', user.highest_affiliation)
        user.populate_highest_affiliation()
        self.assertEqual('Alumni', user.highest_affiliation)

    def test_populate_highest_affiliation_na_no_user(self):
        user = MCommunityUser('fake', mocks.test_app, mocks.test_secret)
        self.assertIsInstance(user.errors, NameError)
        self.assertEqual('', user.highest_affiliation)
        user.populate_highest_affiliation()
        self.assertEqual('NA', user.highest_affiliation)

    def test_populate_highest_affiliation_na_no_roles(self):
        user = MCommunityUser('nemcardna', mocks.test_app, mocks.test_secret)
        self.assertEqual('', user.highest_affiliation)
        user.populate_highest_affiliation()
        self.assertEqual('NA', user.highest_affiliation)

    def test_populate_service_entitlements(self):
        self.assertEqual([], self.user.service_entitlements)  # Before populating, there should not be any
        self.user.populate_service_entitlements()
        self.assertEqual(mocks.eligible_use_str, self.user.service_entitlements)

    def test_populate_service_entitlements_warn_if_empty(self):
        user = MCommunityUser('nemcardfnouse', mocks.test_app, mocks.test_secret)
        self.assertEqual([], user.service_entitlements)  # Before populating, there should not be any
        with self.assertWarns(UserWarning):
            user.populate_service_entitlements()

    def test_to_dict_returns_dict_of_user_attributes_no_populating(self):
        user = MCommunityUser('nemcardf', mocks.test_app, mocks.test_secret)
        self.assertEqual(self.nemcardf_dict, user.to_dict())

    def test_to_dict_returns_dict_of_user_attributes_with_populating(self):
        user = MCommunityUser('nemcardf', mocks.test_app, mocks.test_secret)
        user.populate_highest_affiliation()
        user.populate_service_entitlements()
        self.assertEqual(self.nemcardf_dict_populated, user.to_dict())

    def test_to_dict_converts_error_to_str(self):
        user = MCommunityUser('fake', mocks.test_app, mocks.test_secret)
        self.assertEqual("NameError('No user found in MCommunity for fake')", user.to_dict().get('errors'))

    def test_to_dict_produces_json_serializable_user_object(self):
        user = MCommunityUser('nemcardf', mocks.test_app, mocks.test_secret)
        user.populate_highest_affiliation()
        user.populate_service_entitlements()
        # Just test JSON serializing the dict object; if an exception is NOT RAISED, it passes
        # If an exception is raised, it will be TypeError: Object of type [type] is not JSON serializable
        self.assertTrue(json.dumps(user.to_dict()))

    def test_to_dict_produces_json_serializable_user_object_not_found(self):
        user = MCommunityUser('fake', mocks.test_app, mocks.test_secret)
        # Just test JSON serializing the dict object; if an exception is NOT RAISED, it passes
        # If an exception is raised, it will be TypeError: Object of type [type] is not JSON serializable
        self.assertTrue(json.dumps(user.to_dict()))

    def tearDown(self) -> None:
        self.patcher.stop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main(verbosity=3)
