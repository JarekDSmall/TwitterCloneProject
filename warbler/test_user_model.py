"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app
import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        uid1 = 1111
        u1 = User.signup("test1", "test1@test.com", "password", None)
        u1.id = uid1

        uid2 = 2222
        u2 = User.signup("test2", "test2@test.com", "password", None)
        u2.id = uid2

        db.session.add_all([u1, u2])
        db.session.commit()

        self.u1 = User.query.get(uid1)
        self.u2 = User.query.get(uid2)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    ####
    #
    # Following tests
    #
    ####
    def test_user_follows(self):
        """Tests if users can follow each other"""
        self.u1.following.append(self.u2)
        db.session.commit()

        # test followers
        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u1.followers), 0)

        # test following
        self.assertEqual(len(self.u1.following), 1)
        self.assertEqual(len(self.u2.following), 0)

        # test followers id
        self.assertEqual(self.u1.following[0].id, self.u2.id)
        self.assertEqual(self.u2.followers[0].id, self.u1.id)

    def test_is_following(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_is_followed_by(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))

    ####
    #
    # Signup tests
    #
    ####
    def test_valid_signup(self):
        test_user = User.signup(
            "test_user",
            "test_user@test.com",
            "password",
            None
        )

        test_user_id = 9999
        test_user.id = test_user_id
        db.session.add(test_user)
        db.session.commit()

        user = User.query.get(test_user_id)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "test_user")
        self.assertEqual(user.email, "test_user@test.com")
        # Default image if None
        self.assertEqual(user.image_url, "/static/images/default-pic.png")
        # Password should be hashed
        self.assertNotEqual(user.password, "password")
        # Bcrypt strings should start with $2b$
        self.assertTrue(user.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        invalid = User.signup(None, "test_user@test.com", "password", None)
        u_id = 9999
        invalid.id = u_id

        # Raises Integrity Error if submitted
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid = User.signup("test_user", None, "password", None)
        u_id = 9999
        invalid.id = u_id

        # Raises Integrity Error if submitted
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            invalid = User.signup("test_user", "test_user@test.com", "", None)

        with self.assertRaises(ValueError) as context:
            User.signup("test_user", "test_user@test.com", None, None)

    ####
    #
    # Authentication tests
    #
    ####
    def test_valid_authentication(self):
        """User data should be returned if User.authenticate"""
        user = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.u1.id)

    def test_invalid_username(self):
        """Should return False if incorrect username"""
        self.assertFalse(User.authenticate("wrong_username", "password"))

    def test_wrong_password(self):
        """Should return False if incorrect password"""
        self.assertFalse(User.authenticate(self.u1.username, "wrong_password"))