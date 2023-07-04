# Telegram Bot ChatGPT with history (context)
from aiogram import Bot, Dispatcher, executor, types
from rich import print
from datetime import datetime
import config
import openai

openai.api_key = config.OPENAI_TOKEN  # init openai
bot = Bot(token=config.TOKEN)  # init aiogram
dp = Dispatcher(bot)  # dispatcher bot
conversation_history = {}  # dialog history
approved_users = ['pres',379179502,'anton',984055351]


def dt():
    return datetime.now().isoformat(timespec='milliseconds', sep=' ')


@dp.message_handler()
async def gpt_answer(message: types.Message):
    global conversation_history

    # Вычленяем пользователя из сообщения
    user = message.from_user

    # Если с юзером еще не было истории сообщений, пишем в консоли его данные
    if user.id not in conversation_history:
        print(f"[bold magenta]{dt()} - {user}[/bold magenta]")

    # Проверяем есть ли юзер в списке allowed_users
    if user.id not in approved_users:
        print(f"[bold red]{dt()} - User {user.id} is not in the allowed_users list[/bold red]")
        return

    # Игнорируем команду /start
    if message.text.lower() == "/start":
        return

    # Получаем историю диалога для текущего пользователя или создаем новую
    user_history = conversation_history.get(user.id, [])

    # Получаем и пишем в консоль вопрос от пользователя
    question = message.text
    print(f"[white]{dt()} - [/white][green]{user.username}: [bold]{question}[/bold][green]")

    # Обнуляем контекст если пришло сообщение о сбросе
    if question.lower() in ["сброс", "reset", "clear", "cls", "restart"]:
        conversation_history[user.id] = []
        answer = f"Context for {user.username} has been cleared"
        print(f"[white]{dt()} - {answer}[/white]")
        await message.answer(answer)
        return

    user_history.append({"role": "user", "content": question})

    # Получаем ответ от API OpenAI
    answer = openai.ChatCompletion.create(
        #model="gpt-4", messages=user_history
        model="gpt-3.5-turbo", messages=user_history
    ).choices[0].message.content
    print(f"[white]{dt()} - [/white][cyan]ChatGPT: [bold]{answer}[/bold][cyan]")
    user_history.append({"role": "assistant", "content": answer})

    # Обновляем историю диалога для текущего пользователя
    conversation_history[user.id] = user_history

    # Отправляем ответ в чат пользователю
    await message.answer(answer)

# run long-polling
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
