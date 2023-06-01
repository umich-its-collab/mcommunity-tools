from copy import deepcopy


def change_uniqname_on_mock(mock: list, new_uniqname: str):
    copy = deepcopy(mock)
    copy[0] = (f'uid={new_uniqname},ou=People,dc=umich,dc=edu', copy[0][1])
    copy[0][1]['mail'] = f'{new_uniqname}@umich.edu'
    copy[0][1]['uid'] = new_uniqname
    return copy


def mcomm_side_effect(*args):
    query = args[1].split('=')[1]
    if args[0] == 'ou=People,dc=umich,dc=edu':
        if query == 'nemcardf':
            return faculty_mock
        elif query == 'nemcardrs':
            return regstaff_mock
        elif query == 'nemcards':
            return student_mock
        elif query == 'nemcardts':
            return tempstaff_mock
        elif query == 'nemcardsa1':
            return t1sponsored_mock
        elif query == 'nemcardsa2':
            return t2sponsored_mock
        elif query == 'um999999':
            return t3sponsored_mock
        elif query == 'nemcardr':
            return retiree_mock
        elif query == 'nemcarda':
            return alumni_mock
        elif query == 'nemcardferr':
            return faculty_missing_use_mock
        elif query == 'nemcardaerr':
            return alumni_with_use_mock
        elif query == 'nemcardfnouse':
            return faculty_empty_use_mock
        elif query == 'nemcardna':
            return na_no_roles_mock
        else:
            return []
    elif args[0] == 'ou=User Groups,ou=Groups,dc=umich,dc=edu':
        if query in ['test-group', 'collab-iam-admins']:
            return group_mock_1
        elif query == 'test-group-2':
            return group_mock_2
        elif query == 'something-iam-primary':
            return something_iam_primary_mock
        else:
            return []
    else:
        return []


test_app = 'ITS-FakeTestApp-McDirApp001'
test_secret = 'test123'

eligible_use_str = [
    '{"system":"papercut","changeDate":"20141201050814Z","foreignKey":"","eligibility":"yesDelay","status":"role",'
    '"action":""}',
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
    '{"system":"adobecc","changeDate":"20201017144315Z","foreignKey":"","eligibility":"cc","status":"","action":""}',
    '{"system":"enterprise","changeDate":"20210721193419Z","eligibility":"yes","status":"active","action":""}'
]

ineligible_use_str = [
    '{"system":"box","changeDate":"20220727160206Z","foreignKey":"","eligibility":"yesImmed","status":"",'
    '"action":"add"}',
    '{"system":"tdx","changeDate":"20220727160206Z","foreignKey":"","eligibility":"yes","status":"","action":"add"}',
    '{"system":"dropbox","changeDate":"20220727160206Z","foreignKey":"","eligibility":"yesImmed","status":"",'
    '"action":""}',
    '{"system":"adobecc","changeDate":"20220727160206Z","foreignKey":"","eligibility":"acct","status":"","action":""}',
    '{"system":"canvas","changeDate":"20220727160208Z","foreignKey":"746786","eligibility":"yesImmed",'
    '"status":"active","action":""}',
    '{"system":"papercut","changeDate":"20220727160210Z","foreignKey":"","eligibility":"yesImmed","status":"role",'
    '"action":""} '
]

eligible_use_bytes = []
for s in eligible_use_str:
    eligible_use_bytes.append(bytes(s, 'UTF-8'))

ineligible_use_bytes = []
for s in ineligible_use_str:
    ineligible_use_bytes.append(bytes(s, 'UTF-8'))

faculty_mock = [(
    'uid=nemcardf,ou=People,dc=umich,dc=edu',
    {
        'umichServiceEntitlement': eligible_use_bytes,
        'umichInstRoles': [
            b'FacultyAA', b'RegularStaffDBRN', b'StudentFLNT', b'TemporaryStaffFLNT',
            b'SponsoredAffiliateAA', b'Retiree', b'AlumniAA'
        ],
        'entityid': [b'00000000'],
        'displayName': [b'Natalie Emcard'],
        'mail': [b'nemcardf@umich.edu'],
        'uid': [b'nemcardf'],
        'cn': [b'Natalie Emcard'],
        'test_str': b'test_decoding_str'
    }
)]

regstaff_mock = change_uniqname_on_mock(faculty_mock, 'nemcardrs')
regstaff_mock[0][1]['umichInstRoles'] = regstaff_mock[0][1]['umichInstRoles'][1:]

student_mock = change_uniqname_on_mock(regstaff_mock, 'nemcards')
student_mock[0][1]['umichInstRoles'] = student_mock[0][1]['umichInstRoles'][1:]

tempstaff_mock = change_uniqname_on_mock(student_mock, 'nemcardts')
tempstaff_mock[0][1]['umichInstRoles'] = tempstaff_mock[0][1]['umichInstRoles'][1:]

t1sponsored_mock = change_uniqname_on_mock(tempstaff_mock, 'nemcardsa1')
t1sponsored_mock[0][1]['umichInstRoles'] = t1sponsored_mock[0][1]['umichInstRoles'][1:]

t2sponsored_mock = change_uniqname_on_mock(t1sponsored_mock, 'nemcardsa2')
t2sponsored_mock[0][1]['entityid'] = [b'99000000']
t2sponsored_mock[0][1]['umichServiceEntitlement'] = ineligible_use_bytes

t3sponsored_mock = change_uniqname_on_mock(t2sponsored_mock, 'um999999')

retiree_mock = change_uniqname_on_mock(faculty_mock, 'nemcardr')
retiree_mock[0][1]['umichInstRoles'] = retiree_mock[0][1]['umichInstRoles'][-2:]
retiree_mock[0][1]['umichServiceEntitlement'] = ineligible_use_bytes

alumni_mock = change_uniqname_on_mock(retiree_mock, 'nemcarda')
alumni_mock[0][1]['umichInstRoles'] = alumni_mock[0][1]['umichInstRoles'][1:]

faculty_missing_use_mock = change_uniqname_on_mock(faculty_mock, 'nemcardferr')
faculty_missing_use_mock[0][1]['umichServiceEntitlement'] = ineligible_use_bytes

alumni_with_use_mock = change_uniqname_on_mock(alumni_mock, 'nemcardaerr')
alumni_with_use_mock[0][1]['umichServiceEntitlement'] = faculty_mock[0][1]['umichServiceEntitlement'].copy()

faculty_empty_use_mock = change_uniqname_on_mock(faculty_mock, 'nemcardfnouse')
faculty_empty_use_mock[0][1].pop('umichServiceEntitlement')

na_no_roles_mock = change_uniqname_on_mock(alumni_mock, 'nemcardna')
na_no_roles_mock[0][1].pop('umichInstRoles')

group_mock_1 = [
    ('cn=test-group,ou=User Groups,ou=Groups,dc=umich,dc=edu', {
        'umichGroupEmail': [b'test.group'],
        'owner': [b'uid=nemcardf,ou=People,dc=umich,dc=edu', b'uid=nemcardrs,ou=People,dc=umich,dc=edu'],
        'member': [b'uid=nemcardf,ou=People,dc=umich,dc=edu', b'uid=nemcardrs,ou=People,dc=umich,dc=edu',
                   b'uid=nemcarda,ou=People,dc=umich,dc=edu'],
        'cn': [b'test-group']})
]

group_mock_2 = [
    ('cn=test-group-2,ou=User Groups,ou=Groups,dc=umich,dc=edu', {
        'umichGroupEmail': [b'test.group.2'],
        'owner': [b'uid=nemcardf,ou=People,dc=umich,dc=edu'],
        'member': [b'uid=nemcardf,ou=People,dc=umich,dc=edu', b'uid=nemcardrs,ou=People,dc=umich,dc=edu'],
        'cn': [b'test-group-2']})
]

something_iam_primary_mock = [
    ('cn=something-iam-primary,ou=User Groups,ou=Groups,dc=umich,dc=edu', {
        'umichGroupEmail': [b'something.iam.primary'],
        'owner': [b'uid=nemcardts,ou=People,dc=umich,dc=edu'],
        'member': [b'uid=nemcardts,ou=People,dc=umich,dc=edu', b'uid=nemcarda,ou=People,dc=umich,dc=edu'],
        'cn': [b'something-iam-primary']})
]
