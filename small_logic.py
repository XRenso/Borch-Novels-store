import docx
import re
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
    ready = len(sentences)//5
    result = []
    for i in range(ready):
        text = '. '.join(sentences[:5])
        result.append(text)
        sentences = sentences[5:]
    result.extend(sentences)
    return result


