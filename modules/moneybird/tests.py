from __future__ import absolute_import
import os
from unittest import TestCase
from urllib import unquote

from moneybird import TokenAuthentication, OAuthAuthentication, MoneyBird

TEST_TOKEN = os.getenv(u'MONEYBIRD_TEST_TOKEN')


class TokenAuthenticationTest(TestCase):
    u"""
    Tests the behaviour of the TokenAuthentication implementation.
    """
    def setUp(self):
        self.auth = TokenAuthentication()

    def test_initial_state(self):
        self.assertFalse(self.auth.is_ready(), u"Initially the authentication backend should not be ready.")

    def test_set_token(self):
        self.auth.set_token(u'test_token')
        self.assertEqual(self.auth.auth_token, u'test_token', u"The token was changed by the implementation.")
        self.assertTrue(self.auth.is_ready(), u"The authentication backend should be ready when a token is set.")

    def test_session(self):
        self.auth.set_token(u'test_token')
        session = self.auth.get_session().headers
        self.assertEqual(
            session[u'Authorization'],
            u'Bearer test_token',
            u"The implementation did not generate a proper HTTP Authorization header from the token.",
        )


class OAuthAuthenticationTest(TestCase):
    u"""
    Tests the behaviour of the OAuthAuthentication implementation.
    """
    def setUp(self):
        self.auth = OAuthAuthentication(
            redirect_url=u'https://example.test/login/oauth/',
            client_id=u'test_client',
            client_secret=u'test_secret',
        )

    def test_initial_state(self):
        self.assertEqual(
            self.auth.real_auth.auth_token,
            u'',
            u"The auth token should be the empty string when not explicitly set.",
        )
        self.assertFalse(self.auth.is_ready(), u"Initially the authentication backend should not be ready.")

    def test_authorize_url(self):
        url, state = self.auth.authorize_url([u'one', u'two'], u'random_string')
        path, params = url.split(u'?', 1)
        param_dict = dict((item.split(u'=', 1)[0], unquote(item.split(u'=', 1)[1])) for item in params.split(u'&'))

        self.assertEqual(state, u'random_string', u"The given state was changed by the implementation.")
        self.assertEqual(path, u'https://moneybird.com/oauth/authorize/', u"The OAuth URL is incorrect.")
        self.assertDictEqual(param_dict, {
            u'response_type': u'code',
            u'client_id': u'test_client',
            u'redirect_uri': u'https://example.test/login/oauth/',
            u'scope': u'one+two',
            u'state': u'random_string',
        }, u"The generated URL parameters for authorization are incorrect for the given input.")

    def test_generate_state(self):
        url, state = self.auth.authorize_url([u'one', u'two', u'three'])
        self.assertGreater(len(state), 16, u"The generated state string is too short.")

        states = []
        for i in xrange(10000):
            state = OAuthAuthentication._generate_state()
            self.assertGreater(len(state), 16, u"The generated state string is too short.")
            self.assertNotIn(state, states, u"The randomization of the state is not random enough (%d)." % i)
            states.append(state)


class APIConnectionTest(TestCase):
    u"""
    Tests whether a connection to the API can be made.
    """
    def setUp(self):
        self.auth = TokenAuthentication(TEST_TOKEN)
        self.api = MoneyBird(self.auth)

    def test_get_administrations(self):
        result = self.api.get(u'administrations')
        self.assertIsNotNone(result, u"The result is empty.")
        self.assertGreaterEqual(len(result), 1, u"The result does not contain any data.")

    def test_contacts_roundtrip(self):
        # Get administration ID
        adm_id = self.api.get(u'administrations')[0][u'id']

        # Build a contact
        contact = {
            u'company_name': u'MoneyBird API',
            u'firstname': u'John',
            u'lastname': u'Doe',
        }

        # Create the contact in the administration
        post_result = self.api.post(u'contacts', {u'contact': contact}, administration_id=adm_id)

        self.assertEqual(post_result[u'company_name'], u'MoneyBird API', u"The contact has not been created properly.")
        self.assertEqual(post_result[u'firstname'], u'John', u"The contact has not been created properly.")
        self.assertEqual(post_result[u'lastname'], u'Doe', u"The contact has not been created properly.")
        self.assertIsNotNone(post_result[u'id'], u"The contact has not been created properly.")

        # Set the id of the contact for further use.
        contact_id = post_result[u'id']

        contact = {
            u'firstname': u'No',
            u'lastname': u'One',
        }

        # Update the contact in the administration
        patch_result = self.api.patch(u'contacts/%s' % contact_id, {u'contact': contact}, administration_id=adm_id)

        self.assertEqual(patch_result[u'company_name'], u'MoneyBird API', u"The contact has not been updated properly.")
        self.assertEqual(patch_result[u'firstname'], u'No', u"The contact has not been updated properly.")
        self.assertEqual(patch_result[u'lastname'], u'One', u"The contact has not been updated properly.")

        # Delete the contact from the administration
        delete_result = self.api.delete(u'contacts/%s' % contact_id, administration_id=adm_id)

        self.assertEqual(delete_result[u'id'], contact_id, u"The contact has not been deleted properly.")

        # Check deletion
        try:
            self.api.get(u'contacts/%s' % contact_id, administration_id=adm_id)
        except self.api.NotFound:
            pass
        else:
            self.fail(u"The contact has not been deleted properly.")
