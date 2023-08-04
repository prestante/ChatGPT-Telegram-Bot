# Telegram Bot ChatGPT with history (context)
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime
from rich import print
import config
import openai
import tiktoken
import logging

logging.basicConfig(level=logging.FATAL)  # Set up logging to avoid unnecessary Tracebacks
openai.api_key = config.OPENAI_TOKEN  # init openai
bot = Bot(token=config.TOKEN)  # init aiogram
dp = Dispatcher(bot)  # dispatcher bot
conversation_history = {}  # dialog history
approved_users = ['pres', 379179502, 'anton', 984055351, 'Yulia', 406186116]
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

    # Getting the user data from received message
    user = message.from_user

    # If there is no dialog history with the user, writing their data into to console
    if user.id not in conversation_history:
        print(f"[bold magenta]{dt()} - {user}[/bold magenta]")

    # Getting the user's question and writing it to the console
    question = message.text
    print(f"[white]{dt()} - [/white][green]{user.username}: [bold]{question}[/bold][/green]")

    # If user is not in the allowed_users list, writing it to console and exiting
    if user.id not in approved_users:
        print(f"[bold red]{dt()} - User {user.id} is not in the allowed_users list[/bold red]")
        return

    # Ignoring /start command
    if message.text.lower() == "/start":
        return

    # Getting a dialog history for the current user or creating a new one
    user_history = conversation_history.get(user.id, [])

    # Resetting dialog history for the user if they ask for it and exiting
    if question.lower() in ["сброс", "reset", "clear", "cls", "restart"]:
        conversation_history[user.id] = []
        answer = f"Context for {user.username} has been cleared"
        print(f"[white]{dt()} - {answer}[/white]")
        await message.answer(answer)
        return

    user_history.append({"role": "user", "content": question})

    # Getting an answer from OpenAI API
    answer = openai.ChatCompletion.create(model=model, messages=user_history).choices[0].message.content
    print(f"[white]{dt()} - [/white][cyan]ChatGPT: [bold]{answer}[/bold][/cyan]")
    user_history.append({"role": "assistant", "content": answer})

    # Updating dialog history for the current user
    conversation_history[user.id] = user_history

    # Sending the answer to the chat with the user
    await message.answer(answer)

    # Counting dialog history in tokens, and if it is more than current limit, clearing it and letting the user know it
    if count_tokens(conversation_history[user.id]) > 3000:
        clear_message = "<b><i>Conversation history is too big, clearing...</i></b>"
        await message.answer(clear_message, parse_mode=types.ParseMode.HTML)
        print(f"[black]{dt()}[/black][gray] - Conversation history is too big, clearing...[/gray]")
        conversation_history[user.id] = conversation_history[user.id][-4:]


# Run long-polling
if __name__ == "__main__":
    try:
        executor.start_polling(dp, skip_updates=True)
    except Exception as e:
        print(f"[red]{dt()} - Error: {e}[/red]")
