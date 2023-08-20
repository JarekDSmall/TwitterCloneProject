"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app
import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes

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


class MessageModelTestCase(TestCase):
    """Test Message Model."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.uid = 12345
        u = User.signup("test", "test@test.com", "password", None)

        u.id = self.uid
        db.session.add(u)
        db.session.commit()

        self.u = User.query.get(self.uid)
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic user model work?"""

        # User should have no messages & no followers
        self.assertEqual(len(self.u.messages), 0)
        self.assertEqual(len(self.u.followers), 0)

    def test_message_model(self):
        """Does basic message model work"""

        m = Message(
            text="Testing 123...",
            user_id=self.uid
        )

        db.session.add(m)
        db.session.commit()

        # User should have one message
        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].text, "Testing 123...")

    def test_message_likes(self):
        """Tests when new user likes another users messages"""

        m1 = Message(
            text="Test 1",
            user_id=self.uid
        )

        m2 = Message(
            text="Test 2",
            user_id=self.uid
        )

        new_user = User.signup(
            "newtest", "new@test.com", "password", None)

        new_uid = 67890
        new_user.id = new_uid

        db.session.add_all([m1, m2, new_user])
        db.session.commit()

        # append message to new_user.likes
        new_user.likes.append(m1)
        db.session.commit()

        # Get all likes of new_user
        likes = Likes.query.filter(new_user.id == Likes.user_id).all()

        self.assertEqual(len(likes), 1)
        self.assertEqual(likes[0].message_id, m1.id)