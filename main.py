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
approved_users = ['Pres', 379179502, 'Anton', 984055351, 'Julia', 406186116, 'Anna', 402718700]
users_16k = ['Anna', 402718700]  # users who will use 16k context model

model = "gpt-3.5-turbo"
model_16k = "gpt-3.5-turbo-16k"


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

    # If user is not in the approved_users list, writing their msg and info to console and exiting
    if user.id not in approved_users:
        print(f"[white]{dt()} - [/white][green]{user.username}: [bold]{question}[/bold][/green]")
        print(f"[bold red]{dt()} - User {user.id} is not in the allowed_users list[/bold red]")
        return
    else: # else hiding the user's question by typing the word "question"
        print(f"[white]{dt()} - [/white][green]{user.username}: [bold]question[/bold][/green]")

    # Ignoring /start command
    if message.text.lower() == "/start":
        print(f"[white]{dt()} - Ignoring /start command[/white]")
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

    # Getting an answer from OpenAI API and hiding the model's answer by typing the word "answer"
    if user.id in users_16k:  # for users who will use 16k context model
        answer = openai.ChatCompletion.create(model=model_16k, messages=user_history).choices[0].message.content
    else:  # for everybody else
        answer = openai.ChatCompletion.create(model=model, messages=user_history).choices[0].message.content
    print(f"[white]{dt()} - [/white][cyan]ChatGPT: [bold]answer[/bold][/cyan]")
    user_history.append({"role": "assistant", "content": answer})

    # Updating dialog history for the current user
    conversation_history[user.id] = user_history

    # Sending the answer to the chat with the user
    await message.answer(answer)

    # Counting dialog history in tokens, and if it is more than current limit, clearing it and letting the user know it
    if user.id in users_16k:  # for users who will use 16k context model
        max_tokens = 12000
    else:
        max_tokens = 3000
    if count_tokens(conversation_history[user.id]) > max_tokens:
        clear_message = "<b><i>Conversation history is too big, clearing...</i></b>"
        await message.answer(clear_message, parse_mode=types.ParseMode.HTML)
        print(f"[black]{dt()}[/black][gray] - Conversation history is too big, clearing...[/gray]")
        conversation_history[user.id] = conversation_history[user.id][-4:]


# Run long-polling
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
