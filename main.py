# Telegram Bot ChatGPT with history (context)
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from openai import OpenAI

from datetime import datetime
from rich import print
from os import getenv
import asyncio
import logging
import sys
import re

DEBUG = 1  # In DEBUG mode all messages will be written into the console
logging.basicConfig(level=logging.ERROR)  # Set up logging to avoid unnecessary Tracebacks

client = OpenAI()  # init openai client
client.api_key = getenv('OPENAI_API_KEY')
model = "gpt-3.5-turbo-1106"
max_tokens = 12000
conversation_history = {}  # dialog history

dp = Dispatcher()  # telegram dispatcher bot
escape_pattern = r'([\\\`\*\_\}\{\]\[\)\(\~\>\<\#\+\-\=\|\.\!])'  # telegram parsemode MARKDOWN_V2 requires many characters to be escaped by \
approved_users = ['Pres', 379179502, 'Anton', 984055351, 'Julia', 406186116, 'Anna', 402718700]  # telegram users which questions will be processed by OpenAI


def dt():
    return datetime.now().isoformat(timespec='milliseconds', sep=' ')


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(re.sub(escape_pattern, r'\\\1', f"Hello, {message.from_user.full_name}!"))
    print(f"[white]{dt()} - Sending 'Hello {message.from_user.full_name}' to the /start command[/white]")


@dp.message()
async def gpt_answer(message: types.Message) -> None:
    global conversation_history

    # Getting the user data from received message
    user = message.from_user

    # If there is no dialog history with the user, writing their data into to console
    if user.id not in conversation_history:
        print(f"[bold magenta]{dt()} - {user}[/bold magenta]")

    # Getting the user's question
    question = message.text

    # If user is not in the approved_users list, writing their msg and info to console and exiting
    if user.id not in approved_users:
        print(f"[white]{dt()} - [/white][green]{user.username}: [bold]{question}[/bold][/green]")
        print(f"[bold red]{dt()} - User {user.id} is not in the allowed_users list[/bold red]")
        return
    elif DEBUG:  # elseif DEBUG mode, printing a question
        print(f"[white]{dt()} - [/white][green]{user.username}: [bold]{question}[/bold][/green]")
    else: # else (by default) hiding the user's question by typing the word "question"
        print(f"[white]{dt()} - [/white][green]{user.username}: [bold]question[/bold][/green]")

    # Getting a dialog history for the current user or creating a new one
    user_history = conversation_history.get(user.id, [])

    # Resetting dialog history for the user if they ask for it and exiting
    if question.lower() in ["сброс", "reset", "clear", "cls", "restart"]:
        conversation_history[user.id] = []
        print(f"[white]{dt()} - Context for {user.username} has been cleared[/white]")
        await message.answer(re.sub(escape_pattern, r'\\\1', f"Context for {user.username} has been cleared"))
        return

    user_history.append({"role": "user", "content": question})

    # Getting an answer from OpenAI API and writing or masking the model's answer into the console
    response = client.chat.completions.create(model=model, messages=user_history)
    answer = response.choices[0].message.content
    if DEBUG:  # if DEBUG mode, printing an answer into the console
        print(f"[white]{dt()} - [/white][cyan]ChatGPT: [bold]{answer}[/bold][/cyan]")
    else:  # else (by default) masking an answer
        print(f"[white]{dt()} - [/white][cyan]ChatGPT: [bold]answer[/bold][/cyan]")
    user_history.append({"role": "assistant", "content": answer})

    # Updating dialog history for the current user
    conversation_history[user.id] = user_history

    # Sending the answer to the chat with the user
    await message.answer(re.sub(escape_pattern, r'\\\1', answer))

    # Getting the entire request in tokens, and if it is more than current limit, clearing it and letting the user know it
    if response.usage.total_tokens > max_tokens:
        await message.answer("_*Conversation history is too big, clearing\.\.\.*_")
        print(f"[black]{dt()}[/black][gray] - Conversation history is too big, clearing...[/gray]")
        conversation_history[user.id] = conversation_history[user.id][-4:]


async def main() -> None:
    try:
        # Initialize Bot instance with a default parse mode which will be passed to all API calls
        bot = Bot(token=getenv('ChatGPT_Galk_Bot'), parse_mode=ParseMode.MARKDOWN_V2)
        # And the run events dispatching
        await dp.start_polling(bot)
    except Exception as e:
        # Catch any exception and log only the error message
        logging.error(f"[black]{dt()}[/black][gray]Error occurred: {e}[/gray]")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
