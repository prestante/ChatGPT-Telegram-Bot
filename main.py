# Telegram Bot ChatGPT with history (context)
from aiogram import Bot, Dispatcher, executor, types
from rich import print
import config
import openai

openai.api_key = config.OPENAI_TOKEN  # init openai
bot = Bot(token=config.TOKEN)  # init aiogram
dp = Dispatcher(bot)  # dispatcher bot
conversation_history = {}  # dialog history


@dp.message_handler()
async def gpt_answer(message: types.Message):
    global conversation_history

    # Вычленяем пользователя из сообщения и печатаем в консоль инфу о юзере, если он новый
    user = message.from_user
    if user.id not in conversation_history:
        print(user)

    # Получаем историю диалога для текущего пользователя или создаем новую
    user_history = conversation_history.get(user.id, [])

    # Формируем запрос к API OpenAI с использованием истории диалога текущего пользователя
    question = message.text
    print(f"[bold white]{user.username}: {question}[/bold white]")
    if question.lower() in ["сброс", "reset", "clear", "cls", "restart"]:
        conversation_history[user.id] = []
        answer = f"Context for {user.username} has been cleared"
        print(answer)
        await message.answer(answer)
        return
    user_history.append({"role": "user", "content": question})
    answer = openai.ChatCompletion.create(
        model="gpt-4", messages=user_history
    ).choices[0].message.content

    # Обновляем историю диалога для текущего пользователя
    print(f"[bold yellow]ChatGPT: {answer}[/bold yellow]")
    user_history.append({"role": "assistant", "content": answer})
    conversation_history[user.id] = user_history
    await message.answer(answer)

# run long-polling
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
