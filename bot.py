import telebot

from config import TOKEN
from storage.db import init_db
from handlers import start, skin, problems, budget, pager, profile, menu, focus

# состояние пользователей (в памяти)
user_data = {}

# создаём бота
bot = telebot.TeleBot(TOKEN)

# инициализируем БД
init_db()




# регистрируем хендлеры (ровно один раз)
start.register(bot, user_data)
menu.register(bot, user_data)
skin.register(bot, user_data)
budget.register(bot, user_data)
focus.register(bot, user_data)   # 👈 ВАЖНО: ДО problems
pager.register(bot, user_data)
profile.register(bot, user_data)
problems.register(bot, user_data)  # последним


if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True, timeout=20, long_polling_timeout=20)
