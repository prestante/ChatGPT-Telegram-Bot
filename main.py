# Telegram Bot ChatGPT with history (context)
from rich import print
import config
import openai
from aiogram import Bot, Dispatcher, executor, types

openai.api_key = config.OPENAI_TOKEN  # init openai
bot = Bot(token=config.TOKEN)  # init aiogram
dp = Dispatcher(bot)  # dispatcher bot
conversation_history = []  # dialog history


@dp.message_handler()
async def gpt_answer(message: types.Message):
    global conversation_history

    # Соединяем предыдущие сообщения в истории диалога в одну строку
    conversation_text = "\n".join(conversation_history)

    # Формируем запрос к API OpenAI с использованием истории диалога
    question = message.text
    print(f"[bold white]Q: {question}[/bold white]")
    if question.lower() in ["сброс", "reset", "clear", "cls", "restart"]:
        conversation_history = []
        answer = "Context has been cleared"
        print(answer)
        await message.answer(answer)
        return
    prompt = f"{conversation_text}\nQ: {question}\nA: "
    response = openai.Completion.create(
        engine="text-davinci-003", prompt=prompt, max_tokens=2048, n=1, stop=None, temperature=0.5
    )

    # Обновляем историю диалога
    answer = response.choices[0].text.strip()
    print(f"[bold yellow]A: {answer}[/bold yellow]")
    conversation_history.append(f"Q: {question}\nA: {answer}")
    await message.answer(answer)

# run long-polling
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
