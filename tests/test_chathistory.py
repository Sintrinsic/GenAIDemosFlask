import unittest

from chat.chat_history import ChatHistory, Message


class TestChatHistory(unittest.TestCase):

    def setUp(self):
        self.chat_history = ChatHistory()

    def test_initialization(self):
        self.assertIsNotNone(self.chat_history.messages)
        self.assertIsNone(self.chat_history.root_message)

    def test_append_message(self):
        message = self.chat_history.append_message("user", "test_user", "Hello, world!")
        self.assertIsInstance(message, Message)
        self.assertEqual(len(self.chat_history.messages), 1)
        self.assertEqual(self.chat_history.root_message, message)

    def test_linking_messages(self):
        first_message = self.chat_history.append_message("user", "user1", "First message")
        second_message = self.chat_history.append_message("user", "user2", "Second message")
        self.assertEqual(first_message.get_child(), second_message)
        self.assertEqual(second_message.parent, first_message)

    def test_get_chat_history_as_text(self):
        self.chat_history.append_message("user", "user1", "Hello")
        self.chat_history.append_message("user", "user2", "Hi there")
        chat_history_text = self.chat_history.get_chat_history_as_text()
        self.assertIn("user1: Hello", chat_history_text)
        self.assertIn("user2: Hi there", chat_history_text)

    def test_create_and_switch_fork(self):
        original_message = self.chat_history.append_message("user", "user1", "Original")
        forked_text = "Forked message"
        self.chat_history.create_fork(original_message.uuid, forked_text)

        # Check if the fork was created
        self.assertEqual(len(original_message.versions), 2)

        # Switch to the new fork
        for version_id in original_message.versions:
            if original_message.versions[version_id]['message_text'] == forked_text:
                self.chat_history.switch_fork(original_message.uuid, version_id)
                break

        self.assertEqual(original_message.get_message_text(), forked_text)

if __name__ == '__main__':
    unittest.main()
