from datetime import datetime


class Message:
    def __init__(self, role: str, username: str, message_text: str):
        self.username = username
        self.time_sent = datetime.now()
        self.message_text = message_text
        self.role = role


class ChatHistory():
    _instance = None

    @classmethod
    def getInstance(cls):
        if not cls._instance:
            cls._instance = ChatHistory.__new__(cls)
            cls._instance.messages = []
        return cls._instance

    def append_message(self, role: str, username: str, message_text: str):
        message = Message(role, username, message_text)
        self.messages.append(message)
        if username != "router":
            self.new_message_signal.emit(message)

    def get_messages(self):
        return self.messages

    def get_message_list(self, agent_username=None):
        if agent_username is None:
            output_list = [{"role": message.role, "content": message.message_text} for message in self.messages]
        else:
            output_list = [{"role": message.role, "content": message.message_text} for message in self.messages if
                           message.username == agent_username]
        return output_list

    def get_raw_message_objects(self, agent_username=None):
        if agent_username is None:
            output_list = [message for message in self.messages]
        else:
            output_list = [message for message in self.messages if message.username == agent_username]
        return output_list

    def get_chat_history_as_text(self):
        chat_history = "Chat history:\n"
        chat_history += "\n\n".join([f"{message.username}: {message.message_text}" for message in self.messages if
                                     message.role != "system" and message.username != "router"])
        return chat_history

    def clear_messages(self, agent_username=None):
        if agent_username is None:
            self.messages.clear()
        else:
            self.messages = [message for message in self.messages if message.username != agent_username]

    # Returns the entire chat history for all actors, except for other agent's system messages.
    def get_chat_history_for_agent(self, agent_username):
        raw_messages = [message for message in self.messages if
                        not (message.role == "system" and message.username != agent_username)]
        return [{"role": message.role, "content": message.message_text} for message in raw_messages]
