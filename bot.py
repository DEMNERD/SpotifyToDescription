import requests
import json


class Bot:

    def __init__(self, token):
        """
        Initialises telegram bot object
        :param token: Telegram bot token given by @botfather
        """
        self.token = token
        self.link = f'https://api.telegram.org/bot{self.token}'

    def delete_message(self, chat_id, message_id):
        """
        Deletes message by given id
        :param chat_id: ID of the chat with messages one of which needs to be deleted
        :param message_id: ID of message that needs to be deleted
        :return: response object
        """
        response = requests.post(f'{self.link}/DeleteMessage?',
                                 data={'chat_id': chat_id, 'message_id': message_id})
        return response

    def send_message(self, chat_id, message, parse_mode="", reply_markup=None):
        """
        Sends message
        :param chat_id: Unique identifier for the target chat or username of the target channel
        :param message: Text of the message to be sent, 1-4096 characters after entities parsing
        :param parse_mode: Mode for parsing entities in the message text. See https://core.telegram.org/bots/api#formatting-options for more details.
        :param reply_markup: Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
        :return: response object
        """
        if reply_markup:
            reply_markup = [reply_markup, ]
            reply_markup = json.dumps({"inline_keyboard": reply_markup})
            print(reply_markup)
            response = requests.post(f'{self.link}/SendMessage?',
                                     data={'chat_id': chat_id, 'text': message, 'parse_mode': parse_mode,
                                           'reply_markup': reply_markup})
        else:
            response = requests.post(f'{self.link}/SendMessage?',
                                     data={'chat_id': chat_id, 'text': message, 'parse_mode': parse_mode})
        print(response.content)
        return response

    def send_photo_by_id(self, chat_id, parse_mode='', caption='', photo_id='', photo=None, reply_markup=None):
        """

        :param chat_id: Unique identifier for the target chat or username of the target channel
        :param parse_mode: Mode for parsing entities in the message text. See https://core.telegram.org/bots/api#formatting-options for more details.
        :param caption: Photo caption (may also be used when resending photos by file_id), 0-1024 characters after entities parsing
        :param photo_id: file_id as String to send a photo that exists on the Telegram servers (recommended)
        :param photo: Photo to send
        :param reply_markup: Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
        :return: response object
        """
        data = {'chat_id': chat_id, 'caption': caption, 'parse_mode': parse_mode}
        if reply_markup:
            data.update({'reply_markup': json.dumps({'inline_keyboard': [reply_markup,]})})
        print(data)
        if photo_id:
            data.update({'photo': photo_id})
            response = requests.post(f'{self.link}/SendPhoto',
                                     data=data)
        else:
            response = requests.post(f'{self.link}/SendPhoto',
                                     data=data,
                                     files={'photo': photo})
        return response
