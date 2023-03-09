# Telegram Bot ChatGPT with history
import config
#import logging
import openai
#from gpytranslate import Translator
from aiogram import Bot, Dispatcher, executor, types

# log
#logging.basicConfig(level=logging.INFO)

openai.api_key = config.OPENAI_TOKEN  # init openai
bot = Bot(token=config.TOKEN)  # init aiogram
dp = Dispatcher(bot)  # dispatcher bot
conversation_history = []  # dialog history
#t = Translator()  # init translator


@dp.message_handler()
async def gpt_answer(message: types.Message):
    global conversation_history

    # Соединяем предыдущие сообщения в истории диалога в одну строку
    conversation_text = "\n".join(conversation_history)

    # Формируем запрос к API OpenAI с использованием истории диалога
    #prompt = await t.translate(message.text, targetlang="en")
    question = message.text
    prompt = f"{conversation_text}\nQ: {question}\nA: "
    response = openai.Completion.create(
        engine="text-davinci-003", prompt=prompt, max_tokens=2048, n=1, stop=None, temperature=0.5
    )

    # Обновляем историю диалога
    answer = response.choices[0].text.strip()
    conversation_history.append(f"Q: {question}\nA: {answer}")
    #print('------------history-------------')
    #print(conversation_history)

    #translated_result = await t.translate(completion.choices[0].text, targetlang="ru")
    #await message.answer(translated_result.text)
    await message.answer(answer)

# run long-polling
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
