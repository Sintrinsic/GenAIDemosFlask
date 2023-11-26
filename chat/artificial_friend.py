import enum
import threading

from chat.chat_history import ChatHistory
from chat.openAI_client import OpenAIClient


class ArtificialFriend:
    def __init__(self, identity_message, model_name='gpt-4-1106-preview',
                 agent_name="assistant", talking_speed=1, chat_mode="group"):
        self.agent_name = agent_name
        self.chat_mode = chat_mode
        self.talking_speed = talking_speed
        self.openai_client = OpenAIClient.getInstance()
        self.model_name = model_name
        self.messageHistory = ChatHistory.getInstance()
        self.identity_message = identity_message
        self.set_identity(identity_message)

    def __add_message(self, message, role="assistant"):
        self.messageHistory.append_message(role, self.agent_name, message)

    def set_identity(self, identity_message):
        self.identity_message = identity_message
        history = self.messageHistory.get_raw_message_objects(self.agent_name)
        system_message = None
        for message in history:
            if message.role == "system":
                system_message = message
                break
        if system_message is not None:
            system_message.message_text = identity_message
        else:
            self.__add_message(identity_message, "system")

    def clear_messages(self):
        self.messageHistory.clear_messages(self.agent_name)
        self.set_identity(self.identity_message)

    def send_message(self, message):
        if self.chat_mode == "solo":
            return self.send_message_solo(message)
        elif self.chat_mode == "group":
            return self.send_group_message(message)
        else:
            raise Exception("Chat mode not recognized. Pick 'solo' or 'group'.")

    def send_message_solo(self, message):
        self.__add_message(message, "user")
        message_list = self.messageHistory.get_message_list(self.agent_name)
        response = self.openai_client.call_chat_completion(self.model_name, message_list)
        self.__add_message(response)
        return response

    def send_group_message(self, message):
        self.__add_message(message, "user")
        message_list = self.messageHistory.get_message_list(self.agent_name)
        system_message = {"role": "system", "content": self.messageHistory.get_chat_history_as_text()}
        message_list = [system_message] + message_list
        response = self.openai_client.call_chat_completion(self.model_name, message_list)
        self.__add_message(response)
        return response

    def insert_fake_agent_message(self, message):
        self.__add_message(message)

    def insert_fake_user_message(self, message):
        self.__add_message(message, "user")
