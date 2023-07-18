import os

import docx
import re
import openai
from dotenv import load_dotenv
from asyncify import asyncify
load_dotenv()

openai.api_key = os.getenv('API_KEY')

def rating(rating_as_num):
    pure_rating = int(rating_as_num)
    decimal_part = rating_as_num - pure_rating
    final_score = "●" * pure_rating
    if decimal_part >= 0.75:
        final_score += "●"
    elif decimal_part >= 0.25:
        final_score += "◐"
    need_to_five = 5 - len(final_score)
    final_score += '○' * need_to_five
    return final_score

def integer_modificator(expresion):
    return eval(expresion)

def get_book_text(fname):
    text = []
    doc = docx.Document(fname)
    for para in doc.paragraphs:
            text.append(para.text)
    text = ' '.join(text)
    split_regex = re.compile("""
    (?:
        (?:
            (?<!\\d(?:р|г|к))
            (?<!и\\.т\\.(?:д|п))
            (?<!и(?=\\.т\\.(?:д|п)\\.))
            (?<!т\\.(?:д|п))
            (?<!т(?=\\.(?:д|п)\\.))
            (?<!и\\.т(?=\\.(?:д|п)\\.))
            (?<!руб|коп)
        \\.) |
        [!?\\n]
    )+
    """, re.X)
    sentences = list(filter(lambda t: t, [t.strip() for t in split_regex.split(text)]))
    ready = len(sentences)//10
    result = []
    for i in range(ready):
        text = '. '.join(sentences[:10])
        result.append(text)
        sentences = sentences[10:]
    result.extend(sentences)
    return result

async def generate_image(prompt, game_name):
    text =f'Картинка на основе произведения {game_name}\nОписание картинки: {prompt}'
    try:
        response = await asyncify(openai.Image.create)(
            prompt=text,
            n=1,
            size='256x256'
        )
        image_url = response['data'][0]['url']
        return image_url
    except openai.error.InvalidRequestError:
        return 0

