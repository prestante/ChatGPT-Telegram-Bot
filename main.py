# Telegram Bot ChatGPT with history (context)
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime
from rich import print
import config
import openai
import tiktoken
import traceback
from rich.traceback import install
install()

openai.api_key = config.OPENAI_TOKEN  # init openai
bot = Bot(token=config.TOKEN)  # init aiogram
dp = Dispatcher(bot)  # dispatcher bot
conversation_history = {}  # dialog history
approved_users = ['pres', 379179502, 'anton', 984055351]
model = "gpt-3.5-turbo"


def dt():
    return datetime.now().isoformat(timespec='milliseconds', sep=' ')


def count_tokens(conversation_history) -> int:
    encoding = tiktoken.encoding_for_model(model)
    token_count = 0
    for message in conversation_history:
        content = message['content']
        token_count += len(encoding.encode(content))
    return token_count


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
    print(f"[white]{dt()} - [/white][green]{user.username}: [bold]{question}[/bold][/green]")

    # Обнуляем контекст если пришло сообщение о сбросе
    if question.lower() in ["сброс", "reset", "clear", "cls", "restart"]:
        conversation_history[user.id] = []
        answer = f"Context for {user.username} has been cleared"
        print(f"[white]{dt()} - {answer}[/white]")
        await message.answer(answer)
        return

    user_history.append({"role": "user", "content": question})

    # Получаем ответ от API OpenAI
    #answer = openai.ChatCompletion.create(model=model, messages=user_history).choices[0].message.content
    answer = openai.ChatCompletion.create(model=model, messages=user_history, timeout=30).choices[0].message.content
    print(f"[white]{dt()} - [/white][cyan]ChatGPT: [bold]{answer}[/bold][/cyan]")

    user_history.append({"role": "assistant", "content": answer})

    # Обновляем историю диалога для текущего пользователя
    conversation_history[user.id] = user_history

    # Отправляем ответ в чат пользователю
    await message.answer(answer)

    if count_tokens(conversation_history[user.id]) > 3000:
        clear_message = "<b><i>Conversation history is too big, clearing...</i></b>"
        await message.answer(clear_message, parse_mode=types.ParseMode.HTML)
        print(f"[black]{dt()}[/black][gray] - Conversation history is too big, clearing...[/gray]")
        conversation_history[user.id] = conversation_history[user.id][-4:]

# run long-polling
if __name__ == "__main__":
    try:
        executor.start_polling(dp, skip_updates=True)
    except Exception as e:
        print("[red]An error occurred: {}".format(e.__class__.__name__))
