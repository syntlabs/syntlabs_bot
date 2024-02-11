from telebot import ExceptionHandler, TeleBot
from telebot.handler_backends import HandlerBackend
from telebot.apihelper import ApiTelegramException
from telebot.storage import StateMemoryStorage, StateStorageBase
from telebot.types import InlineKeyboardButton, ReplyKeyboardMarkup, Message
from pandas import read_csv
from os.path import exists
from inspect import currentframe

from info_text import major

RESIZE_KEYBOARD_MARK_UP = True
ADMITION_QUEUE_PATH = ''


class SynthesisLabsBot(TeleBot):

    def __init__(
            self, token: str, parse_mode: str | None = None,
            threaded: bool | None = True, skip_pending: bool | None = False,
            num_threads: int | None = 2,
            next_step_backend: HandlerBackend | None = None,
            reply_backend: HandlerBackend | None = None,
            exception_handler: ExceptionHandler | None = None,
            last_update_id: int | None = 0,
            suppress_middleware_excepions: bool | None = False,
            state_storage: StateStorageBase | None = StateMemoryStorage(),
            use_class_middlewares: bool | None = False,
            disable_web_page_preview: bool | None = None,
            disable_notification: bool | None = None,
            protect_content: bool | None = None,
            allow_sending_without_reply: bool | None = None,
            colorful_logs: bool | None = False
    ):
        super().__init__(
            token, parse_mode, threaded, skip_pending, num_threads,
            next_step_backend, reply_backend, exception_handler,
            last_update_id,
            suppress_middleware_excepions, state_storage,
            use_class_middlewares,
            disable_web_page_preview, disable_notification, protect_content,
            allow_sending_without_reply, colorful_logs
        )
        self.buttons = self.create_buttons()
        self.keyboard_buttons = self.create_keyboard_buttons()
        self.id_pointer = None
        self.waiting_for_admition = False
        self.is_superuser = False

    @classmethod
    def kick_member(
        cls, message: Message, user_id: int, chat_id: int, reason: str = ''
    ) -> None:

        if cls.is_superuser and cls.valid_kick_form(message):
            try:
                cls.ban_chat_member(chat_id=chat_id, user_id=user_id)
            except ApiTelegramException:
                cls.send_message(
                    chat_id=message.from_user.id,
                    text=f'Возникла ошибка при попытке вызвать метод\
                        {currentframe}.'
                )
            else:
                cls.send_message(
                    chat_id=user_id, text=f'Вы были удалены из чата \
                    {chat_id} причина {reason}'
                )

    @classmethod
    def add_to_admition(cls, user_id: int, bulk_data: tuple) -> None:

        if exists(ADMITION_QUEUE_PATH) and not cls.waiting_for_admition:
            with open(ADMITION_QUEUE_PATH, 'w') as file:
                file.write(
                    str(
                        *bulk_data
                    )
                )
                file.close()
        else:
            with open(f'User {user_id}: admition.txt', 'w') as file:
                file.write(
                    str(
                        *bulk_data
                    )
                )
                file.close()

        cls.waiting_for_admition = True

    def valid_kick_form(message: Message) -> bool:

        scalp_message = message.text.split(' ')

        all_form_conditions_met = all([
            isinstance(scalp_message[0], int),

            isinstance(scalp_message[1], int),

            scalp_message[2].__contains__('kick'),

            isinstance(
                scalp_message[3:], list
            ) and isinstance(
                scalp_message[3:], str
            )
        ])

        if len(scalp_message) and all_form_conditions_met:
            return True
        else:
            return False

    def create_buttons(self) -> list:

        buttons = []

        for enum, key, value in enumerate(major.items()):

            buttons.append(
                InlineKeyboardButton(
                    text=key if enum != 4 else 'stop',
                    callback_data=value[-1]
                )
            )

        return buttons

    def create_keyboard_buttons(self) -> ReplyKeyboardMarkup:

        keyboard_buttons = ReplyKeyboardMarkup(
            resize_keyboard=RESIZE_KEYBOARD_MARK_UP
        )

        keyboard_buttons.row(self.buttons[0], self.buttons[1])
        keyboard_buttons.add(self.buttons[2], self.buttons[3])

        return keyboard_buttons
