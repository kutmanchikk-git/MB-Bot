import os, requests, logging
from aiogram import F, Router, Bot, types
from aiogram.filters import CommandStart, Command
import app.keyboards as kb
from app.keyboards import search_music
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, BufferedInputFile, InputFile
from app.keyboards import user_links
from app.database.request import set_user
from aiogram.utils.keyboard import InlineKeyboardBuilder
from collections import defaultdict

user_ranges = defaultdict(lambda: (0, 10))


router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await set_user(message.from_user.id, message.from_user.first_name or "Unnamed", message.from_user.last_name or "Unlastnamed")

    await message.answer("Привет отправь мне название музыки. Hi send me the title of music")

@router.message()
async def search_handler(message: types.Message):
    user_id = message.from_user.id
    query = message.text
    await message.answer(f"{query}...")

    user_ranges[user_id] = (0, 10)

    try:
        low_line, high_line = user_ranges[user_id]
        keyboard_builder = await search_music(user_id, query, low_line, high_line)
        main_keyboard = keyboard_builder.as_markup()

        additional_buttons = [
            InlineKeyboardButton(text="➡️", callback_data=f"forward_{query}")
        ]
        main_keyboard.inline_keyboard.append(additional_buttons)

        if keyboard_builder.buttons:
            await message.answer("Вот что я нашёл:", reply_markup=main_keyboard)
        else:
            await message.answer("К сожалению, ничего не найдено. Unfortunattely, i coudnt find anything")
    except Exception as e:
        await message.answer(f"По вашему запросу ничего нет.Проверьте, нет ли опечаток, или попробуйте ввести другой запрос")
        error_message = str(e)
        await message.answer(error_message)
    


@router.callback_query()
async def main_handler(callback: CallbackQuery):
    await callback.answer("")
    user_id = callback.from_user.id
    data = callback.data
    
    if data.startswith("forward_") or data.startswith("backward_"):
        query = data.split("_")[1]
        low_line, high_line = user_ranges[user_id]

        if data.startswith("forward_"):
            low_line += 10
            high_line += 10
        elif data.startswith("backward_"):
            low_line = max(0, low_line - 10)
            high_line = max(10, high_line - 10)

        user_ranges[user_id] = (low_line, high_line)

        try:
            if low_line == 0 and high_line == 10:
                try:
                    keyboard_builder = await search_music(user_id, query, low_line, high_line)
                    main_keyboard = keyboard_builder.as_markup()

                        
                    additional_buttons = [
                            InlineKeyboardButton(text="➡️", callback_data=f"forward_{query}")
                        ]
                    main_keyboard.inline_keyboard.append(additional_buttons)

                    await callback.message.edit_reply_markup(reply_markup=main_keyboard)
                except ValueError:
                        await callback.message.answer("Больше результатов нет. There is no more results")
                except Exception as e:
                    await callback.message.answer(f"Попробуйте нажать на другую кнопку.  Try to click another button")
           
            else:
                keyboard_builder = await search_music(user_id, query, low_line, high_line)
                main_keyboard = keyboard_builder.as_markup()

        
                additional_buttons = [
                    InlineKeyboardButton(text="⬅️", callback_data=f"backward_{query}"),
                    InlineKeyboardButton(text="➡️", callback_data=f"forward_{query}")
                ]
                main_keyboard.inline_keyboard.append(additional_buttons)
                await callback.message.edit_reply_markup(reply_markup=main_keyboard)
        except ValueError:
            await callback.message.answer("Больше результатов нет. There is no more results")
        except Exception as e:
            await callback.message.answer(f"Попробуйте нажать на другую кнопку. Try to click another button")
    elif data:
        try:
            index = int(callback.data)
            if index < len(user_links[user_id]):
                url = user_links[user_id][index]
                await callback.message.answer_audio(audio=url, caption="@MusMBbot Bot to download the music")
            else:
                await callback.message.answer("Некорректный выбор песни. You have chosen the incorrect song")
        except Exception as e:
            await callback.message.answer(f"Очень длинная музыка, попробуйте другую. This music is too long, try another one")