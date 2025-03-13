from translate import Translator
import paddleocr
from paddleocr import PaddleOCR
ocr = PaddleOCR(lang='en')
def getgoodtext(img):
    result = ocr.ocr(img)
    lines = []
    for n in range(len(result[0])):
        lines.append(result[0][n][1][0])
    return '\n'.join(lines)

def translate_text(text, lang):
    translator = Translator(provider='mymemory', to_lang=lang, from_lang='en')
    max_chunk_size = 500
    chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
    translated_chunks = [translator.translate(chunk) for chunk in chunks]
    translated_text = ' '.join(translated_chunks)
    return translated_text

