import json
import uuid
from datetime import datetime
from enum import Enum


class MessageType(Enum):
    Identity = 1
    Correspondence = 2
    Information = 3


class Message:
    def __init__(self,
                 role: str,
                 username: str,
                 message_text: str,
                 msg_uuid: str = None,
                 time_sent: datetime = None,
                 parent: "Message" = None,
                 child=None, message_type: MessageType = MessageType.Correspondence):
        self.message_type = message_type
        self.username = username
        self.role = role
        self.parent = parent  # Note: parent is a reference to another Message object
        version_uuid = str(uuid.uuid4())
        self.versions = {version_uuid: {"message_text": message_text,
                                        "time_sent": time_sent if time_sent is not None else datetime.now(),
                                        "child": None}}

        self.active_version = version_uuid  # The active path in the tree
        self.uuid = str(uuid.uuid4()) if msg_uuid is None else msg_uuid

    def serialize_recursive(self):
        return json.dumps(self, default=self._complex_handler_recursive)

    def serialize_individually(self):
        return json.dumps(self, default=self._complex_handler_individual)

    @staticmethod
    def _complex_handler_individual(obj):
        if isinstance(obj, datetime):
            return datetime.strftime("%m/%d/%Y-%H:%M:%S")
        elif isinstance(obj, Message):
            # Handle the serialization of the Message object
            return {
                "role": obj.role,
                "username": obj.username,
                "msg_uuid": obj.uuid,
                "parent": obj.parent.uuid if obj.parent else None,
                "versions": {version_id: {
                    "message_text": version_info["message_text"],
                    "time_sent": version_info["time_sent"].isoformat() if version_info["time_sent"] else None,
                    "child": version_info["child"].uuid if version_info["child"] else None
                } for version_id, version_info in obj.versions.items()},
                "active_version": obj.active_version
            }
        else:
            return obj.__dict__

    def _complex_handler_recursive(self):
        if isinstance(self, datetime):
            return datetime.strftime("%m/%d/%Y-%H:%M:%S")
        elif isinstance(self, Message):
            # Handle the serialization of the Message object
            return {
                "role": self.role,
                "username": self.username,
                "uid": self.uuid,
                "parent": self.parent.uuid if self.parent else None,
                "versions": {version_id: {
                    "message_text": version_info["message_text"],
                    "time_sent": version_info["time_sent"].isoformat() if version_info["time_sent"] else None,
                    "child": version_info["child"].serialize_recursive() if version_info["child"] else None
                } for version_id, version_info in self.versions.items()},
                "active_version": self.active_version
            }
        else:
            return self.__dict__

    def get_message_text(self):
        return self.versions[self.active_version]["message_text"]

    def set_message_text(self, message_text):
        self.versions[self.active_version]["message_text"] = message_text

    def get_time_sent(self):
        return self.versions[self.active_version]["time_sent"]

    def get_child(self):
        return self.versions[self.active_version]["child"]

    def add_child(self, child_message):
        self.versions[self.active_version]["child"] = child_message
        child_message.parent = self

    def can_add_child_without_circular_dependency(self, potential_child):
        pass  # Need to do this, but unsure how to handle the addition of a child to a non-active fork

    def get_active_descendant_list(self):
        output_list = [self]
        child = self.get_child()
        if child is not None:
            output_list = output_list + child.get_active_descendant_list()
        return output_list

    def add_version(self, message_text, time_sent=None, child=None):
        message_uuid = str(uuid.uuid4())
        self.versions[message_uuid] = {"message_text": message_text,
                                       "time_sent": time_sent if time_sent is not None else datetime.now(),
                                       "child": None}
        self.active_version = message_uuid

    def switch_version(self, message_uuid):
        self.active_version = message_uuid


class ChatHistory:

    def __init__(self):
        self.clear_messages()
        # TODO: Update this so the chat history is cached and only requries traversal for write operations

    def clear_messages(self):
        self.messages = {}
        self.root_message = None

    def append_message(self, role: str, username: str, message_text: str,
                       message_type: MessageType = MessageType.Correspondence):
        message_list = self.__get_active_message_list()
        last_message = message_list[-1] if len(message_list) > 0 else None
        new_message = Message(role, username, message_text, parent=last_message, message_type=message_type)
        if last_message is not None:
            last_message.add_child(new_message)
        if self.root_message is None:
            self.root_message = new_message
        self.messages[new_message.uuid] = new_message
        return new_message

    def __get_active_message_list(self):
        if self.root_message is None:
            return []
        return self.root_message.get_active_descendant_list()

    def get_openai_message_list(self):
        raw_message_list = self.__get_active_message_list()
        output_list = [{"role": message.role, "content": message.get_message_text()} for message in raw_message_list]
        return output_list

    def get_raw_message_list(self):
        return self.__get_active_message_list()

    def get_chat_history_as_text(self):
        # "Chat history:\n message username: message text \nn"
        message_list = self.__get_active_message_list()
        chat_history = "Chat history:\n"
        chat_history += "\n".join([f"{message.username}: {message.get_message_text()}"
                                   for message in message_list
                                   if message.role != "system" and message.username != "router"])
        return chat_history

    def create_fork(self, message_id, message_text: str):
        target_message = self.messages[message_id]
        target_message.add_version(message_text)

    def switch_fork(self, message_id, version_id):
        target_message = self.messages[message_id]
        target_message.switch_version(version_id)

    def to_json(self):
        message_dict = {}
        for msg_uuid, message in self.messages.items():
            message_dict[msg_uuid] = message.serialize_individually()

        out_dict = {"messages": message_dict,
                    "root_message": self.root_message.uuid}

        return json.dumps(out_dict, indent=4)

    @staticmethod
    def from_json(json_data):
        json_dict = json.loads(json_data)
        root_message_uuid = json_dict["root_message"]
        message_dict = {}
        for msg_uuid, message_str in json_dict["messages"].items():
            message = json.loads(message_str)
            json_dict["messages"][msg_uuid] = message
            role = message["role"]
            username = message["username"]
            message_uuid = message["msg_uuid"]
            version_dict = {}
            for version_id, version_info in message["versions"].items():
                message_text = version_info["message_text"]
                time_sent = datetime.fromisoformat(version_info["time_sent"]) if version_info["time_sent"] else None
                child = None
                version_dict[version_id] = {"message_text": message_text,
                                            "time_sent": time_sent,
                                            "child": child}

            new_message = Message(role, username, "", msg_uuid=message_uuid, time_sent=datetime.now())
            new_message.versions = version_dict
            new_message.active_version = message["active_version"]
            message_dict[msg_uuid] = new_message

        for msg_uuid, json_message in json_dict["messages"].items():
            target_message = message_dict[msg_uuid]

            if json_message['parent'] is not None:
                if json_message['parent'] in message_dict:
                    target_message.parent = message_dict[json_message['parent']]
                    print(f"Setting parent of {msg_uuid} to {json_message['parent']}")
            for version_id, version in json_message["versions"].items():
                if version["child"] is not None:
                    if version["child"] in message_dict:
                        target_message.versions[version_id]["child"] = message_dict[version["child"]]
                        print(f"Setting child of {msg_uuid} to {version['child']}")

        chat_history = ChatHistory()
        chat_history.messages = message_dict
        chat_history.root_message = message_dict[root_message_uuid]
        return chat_history

    def list_conversations(self):
        pass

    def delete_conversation(self, filename):
        pass

    def save_conversation(self, filename):
        pass

    def load_conversation(self, filename):
        pass


if __name__ == '__main__':
    history = ChatHistory()
    for i in range(10):
        history.append_message("user", "user1", f"Message {i}")
        history.append_message("assistant", "assistant", f"confirmed Message {i}")

    json_history = history.to_json()
    print(json_history)
    new_history = ChatHistory.from_json(json_history)

    print(new_history.get_chat_history_as_text())
