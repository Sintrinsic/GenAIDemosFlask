import unittest
from datetime import datetime

from chat.chat_history import Message


class TestMessage(unittest.TestCase):

    def setUp(self):
        self.username = "test_user"
        self.role = "user"
        self.message_text = "Hello, world!"
        self.message = Message(self.role, self.username, self.message_text)

    def test_initialization(self):
        self.assertEqual(self.message.username, self.username)
        self.assertEqual(self.message.role, self.role)
        self.assertIsNotNone(self.message.uuid)
        self.assertEqual(len(self.message.versions), 1)

    def test_add_version(self):
        new_message_text = "Updated message"
        self.message.add_version(new_message_text)
        self.assertEqual(len(self.message.versions), 2)
        self.assertEqual(self.message.get_message_text(), new_message_text)

    def test_switch_version(self):
        original_version_id = self.message.active_version
        new_message_text = "Another version"
        self.message.add_version(new_message_text)
        new_version_id = self.message.active_version

        self.message.switch_version(original_version_id)
        self.assertEqual(self.message.active_version, original_version_id)
        self.assertNotEqual(self.message.get_message_text(), new_message_text)

        self.message.switch_version(new_version_id)
        self.assertEqual(self.message.active_version, new_version_id)
        self.assertEqual(self.message.get_message_text(), new_message_text)

    def test_add_child(self):
        child_message = Message(self.role, self.username, "Child message")
        self.message.add_child(child_message)
        self.assertEqual(self.message.get_child(), child_message)
        self.assertEqual(child_message.parent, self.message)

    def test_get_active_descendant_list(self):
        child_message = Message(self.role, self.username, "Child message")
        self.message.add_child(child_message)
        descendant_list = self.message.get_active_descendant_list()
        self.assertIn(self.message, descendant_list)
        self.assertIn(child_message, descendant_list)

if __name__ == '__main__':
    unittest.main()