import os
import sys

import django
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bot_backend.settings")
django.setup()

try:
    from event_planner.models import Speaker, Question, User
    from event_planner.utils import get_schedule, get_user_role, remove_expired_speakers
except Exception as e:
    print(f"Error importing models: {e}")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Здесь можно поменять api и вставить свою
bot = TeleBot(TELEGRAM_BOT_TOKEN)

# словарь, чтобы чекать, если пользователь в состоянии ввода вопроса
user_states = {}


def is_asking_question(message):
    tg_id = str(message.chat.id)
    return user_states.get(tg_id) == 'asking_question'


def create_reply_keyboard(role):
    """Создаем клавиатуру для бота"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton("О программе")

    if role == 'speaker':
        btn2 = KeyboardButton("Посмотреть вопросы")
        btn3 = KeyboardButton("Донат")

        keyboard.add(btn1, btn2, btn3)
    else:
        btn2 = KeyboardButton("Задать вопрос")
        btn3 = KeyboardButton("Донат")

        keyboard.add(btn1, btn2, btn3)
    return keyboard


# начало
@bot.message_handler(commands=['start'])
def start(message):
    """Идентифицируем роль пользователя и сохрняем в бд"""
    tg_id = str(message.chat.id)
    username = message.from_user.username

    try:
        user, created = User.objects.get_or_create(
            tg_id=tg_id,
            defaults={
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name,
                'username': username,
            }
        )
        user.role = get_user_role(tg_id, username) or 'listener'
        user.save()

        keyboard = create_reply_keyboard(user.role)
        role_name = 'Докладчик' if user.role == 'speaker' else 'Слушатель'

        bot.send_message(
            message.chat.id,
            f"""Добро пожаловать, {user.first_name}!\nСейчас Вы - {role_name}
                \n ＼(＾▽＾)／\nПользуйтесь кнопками ниже))\n(Спойлер: это удобно)""",
            reply_markup=keyboard
        )

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при идентификации: {e}")
    print("Бот запущен пользователем:", user.first_name, tg_id)


def is_about_command(message):
    return message.text == "О программе"


@bot.message_handler(func=is_about_command)
def handle_about(message):
    """"
    Обработка команды "О программе"
    """
    try:
        schedule = get_schedule()
        bot.send_message(message.chat.id, schedule)
    except Exception as e:
        bot.send_message(
            message.chat.id, f"Ошибка при получении расписания: {e}")


# Чекаем, если пользователь задает вопрос
def is_ask_question_command(message):
    return message.text == "Задать вопрос"


@bot.message_handler(func=is_ask_question_command)
def ask_question(message):
    """обработка вопроса"""
    tg_id = str(message.chat.id)
    user = User.objects.filter(tg_id=tg_id).first()

    if user and user.role == 'listener':
        user_states[tg_id] = 'asking_question'
        bot.send_message(
            message.chat.id, "Пожалуйста, введите ваш вопрос 	ʕ ᵔᴥᵔ ʔ")
    else:
        bot.send_message(
            message.chat.id, "Вы не можете задать вопрос. (-_-;)・・・")

# Проверяем, если пользователь в состоянии ввода вопроса


@bot.message_handler(func=is_asking_question)
def save_question(message):
    """
    Сохранение вопроса в БД
    """
    tg_id = str(message.chat.id)
    user = User.objects.filter(tg_id=tg_id).first()

    text = message.text
    speaker = Speaker.objects.first()
    if speaker:
        Question.objects.create(user=user, speaker=speaker, text=text)
        bot.send_message(message.chat.id, "Ваш вопрос отправлен. (っ ᵔ◡ᵔ)っ")
        print(f"Пользователь {user.first_name} задал вопрос:", text)
    else:
        bot.send_message(
            message.chat.id, "В настоящий момент нет докладчиков. ʕಠᴥಠʔ")

    # Ну и очищаем состояние
    user_states.pop(tg_id, None)


# Проверяем, если пользователь нажал кнопку "Посмотреть вопросы"
def is_view_questions_command(message):
    return message.text == "Посмотреть вопросы"


@bot.message_handler(func=is_view_questions_command)
def view_questions(message):
    """
    Показывает вопросы для докладчиков
    """
    tg_id = str(message.chat.id)
    speaker = Speaker.objects.filter(
        tg_id=f"@{message.from_user.username}").first()

    questions = Question.objects.filter(
        speaker=speaker).order_by('-created_at')
    if questions.exists():
        response = "Ваши вопросы:\n\n" + "\n".join(
            [f"{q.user.first_name}: {q.text}" for q in questions]
        )
    else:
        response = "У вас пока нет вопросов."
    bot.send_message(message.chat.id, response)


def send_donat(message):
    return message.text == "Донат"


@bot.message_handler(func=send_donat)
def send_donat(message):
    """Отпраавляет донат"""
    tg_id = str(message.chat.id)
    user = User.objects.filter(tg_id=tg_id)
    # tg_id = str(message.chat.id)
    # speaker = Speaker.objects.filter(
    #     tg_id=f"@{message.from_user.username}").first()
    try:
        # speaker = Speaker.objects.get(
        #     tg_id=f"@{message.from_user.username}")
        speaker = Speaker.objects.filter(
            tg_id=message.from_user.username).first()
        print(speaker)
        if speaker.card_num:
            bot.send_message(
                message.chat.id,
                f"Спасибо за вашу поддержку!૮ ˶ᵔ ᵕ ᵔ˶ ა\nВы можете отправить донат по следующему номеру карты спикера:\n{
                    speaker.card_num}"
            )
            print(f"Пользователь {user} нажал на кнопку 'Донат'")
        else:
            bot.send_message(
                message.chat.id,
                "Извините, номер карты спикера не указан. ┐( ˘_˘ )┌"
            )
    except Exception as e:
        print(f"Error: {e}")
    except Speaker.DoesNotExist:
        bot.send_message(
            message.chat.id,
            "Извините, информация о спикере не найдена.{{ (>_<) }}"
        )


if __name__ == "__main__":
    bot.polling()
