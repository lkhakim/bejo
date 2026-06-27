import logging

logger = logging.getLogger("bejo.conversation")


class ConversationManager:
    def __init__(self):
        self._message_count = 0

    def on_user_message(self, user_input: str):
        self._message_count += 1

    def on_assistant_response(self, user_input: str, response_text: str):
        pass
