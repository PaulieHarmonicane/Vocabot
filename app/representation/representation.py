from PIL import Image, ImageDraw, ImageFont, features
import PIL
from io import BytesIO
from aiogram.types import BufferedInputFile

lang_font = {'中文':'Deng.otf'}

answer_colours = {'known':[(41, 182, 246), (255, 255, 255)], 'unknown':[(255, 102, 102), (255, 255, 255)], 'correct':[(41, 171, 135), (255, 255, 255)], 'wrong':[(139, 0, 0), (255, 255, 255)]}

async def create_flashcard_question(question, need_transcription, c_lang, padding=10):
    img_size = (300, 500)
    image = Image.new(mode='RGB', size=img_size ,color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    if need_transcription == 't':
        font_size = 100
        fnt = ImageFont.truetype(font=f"app/representation/{lang_font[c_lang]}", size=font_size)
        while font_size > 10:
            max_line_width = img_size[0] - 2*padding
            lines = []
            words = question.split()
            current_line = []
            longest_word = ''
            for word in words:
                if len(word) > len(longest_word):
                    longest_word = word

            bbox = draw.textbbox((0,0), longest_word, font=fnt)
            max_word_width = bbox[2] - bbox[0]
            while max_word_width > max_line_width:
                font_size -= 2
                fnt = ImageFont.truetype(font=f"app/representation/{lang_font[c_lang]}", size=font_size)
                bbox = draw.textbbox((0,0), longest_word, font=fnt)
                max_word_width = bbox[2] - bbox[0]


            for word in words:
                test_line = " ".join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=fnt)
                test_width = bbox[2] - bbox[0]
                if test_width <= max_line_width:
                    current_line.append(word)
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(" ".join(current_line))
            line_height = fnt.getbbox("A")[3] - fnt.getbbox("A")[1]
            total_text_height = len(lines) * line_height + padding
            if total_text_height <= img_size[1] - 2 * padding:
                break


            font_size -= 2
            fnt = ImageFont.truetype(font_path, font_size)
        y = (img_size[1] - total_text_height) // 2
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=fnt)
            line_width = bbox[2] - bbox[0]
            x = (img_size[0] - line_width) // 2
            draw.text((x, y), line, font=fnt, fill=(0, 0, 0))
            y += line_height
    elif need_transcription == 'nt':
        font_size = 50
        fnt = ImageFont.truetype(font=f"app/representation/Faberge-Regular.otf", size=font_size)
        while font_size > 10:
            max_line_width = img_size[0] - 2*padding
            lines = []
            words = question.split()
            current_line = []
            longest_word = ''
            for word in words:
                if len(word) > len(longest_word):
                    longest_word = word

            bbox = draw.textbbox((0,0), longest_word, font=fnt)
            max_word_width = bbox[2] - bbox[0]
            while max_word_width > max_line_width:
                font_size -= 2
                fnt = ImageFont.truetype(font=f"app/representation/Faberge-Regular.otf", size=font_size)
                bbox = draw.textbbox((0,0), longest_word, font=fnt)
                max_word_width = bbox[2] - bbox[0]

            for word in words:
                test_line = " ".join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=fnt)
                test_width = bbox[2] - bbox[0]
                if test_width <= max_line_width:
                    current_line.append(word)
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(" ".join(current_line))
            line_height = fnt.getbbox("A")[3] - fnt.getbbox("A")[1]
            total_text_height = len(lines) * line_height + padding
            if total_text_height <= img_size[1] - 2 * padding:
                break


            font_size -= 2
            fnt = ImageFont.truetype(font_path, font_size)
        y = (img_size[1] - total_text_height) // 2
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=fnt)
            line_width = bbox[2] - bbox[0]
            x = (img_size[0] - line_width) // 2
            draw.text((x, y), line, font=fnt, fill=(0, 0, 0))
            y += line_height


    buffer = BytesIO()
    image.save(buffer, format="png")
    img_f = buffer.tell()
    print(img_f)
    buffer.seek(0)
    print(buffer.tell())
    
    return buffer.getvalue()



async def create_flashcard_t_answer(word, translation, need_transcription, c_config, c_lang, padding=20, transcription=None):
    img_size = (300, 500)
    image = Image.new(mode='RGB', size=img_size ,color=answer_colours[c_config][0])
    draw = ImageDraw.Draw(image)
    font_size = 100
    if need_transcription == 't':
        word_font_path = f"app/representation/{lang_font[c_lang]}"
        transcription_font_path = f"app/representation/{lang_font[c_lang]}"
        translation_font_path = "app/representation/Faberge-Regular.otf"
    elif need_transcription == 'nt':
        word_font_path = "app/representation/Faberge-Regular.otf"
        translation_font_path = "app/representation/Faberge-Regular.otf"


    def fit_text_to_box(text, font_path, max_width, max_height, max_font_size=70, min_font_size=10):
        font_size = max_font_size
        font = ImageFont.truetype(font_path, font_size)
        lines = []
        
        while font_size >= min_font_size:
            # Wrap text
            words = text.split()
            current_line = []
            lines = []
            longest_word = ''
            for word in words:
                if len(word) > len(longest_word):
                    longest_word = word
            bbox = draw.textbbox((0,0), longest_word, font=font)
            max_word_width = bbox[2] - bbox[0]
            while max_word_width > img_size[0]-padding:
                font_size -= 2
                font = ImageFont.truetype(font=font_path, size=font_size)
                bbox = draw.textbbox((0,0), longest_word, font=font)
                max_word_width = bbox[2] - bbox[0]

            for word in words:
                test_line = " ".join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] <= max_width:
                    current_line.append(word)
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(" ".join(current_line))
            
            # Check height
            line_height = font.getbbox("A")[3] - font.getbbox("A")[1]
            total_height = len(lines) * line_height
            if total_height <= max_height:
                break
            
            # Reduce font size
            font_size -= 2
            font = ImageFont.truetype(font_path, font_size)
        
        return font, lines

    
    # Word (top section)
    word_height = int(img_size[1] * 0.25)
    word_font, word_lines = fit_text_to_box(word, word_font_path, img_size[0] - 2 * padding, word_height)
    
    # Transcription (middle section, below word if provided)
    if transcription:
        transcription_height = int(img_size[1] * 0.05)
        transcription_font, transcription_lines = fit_text_to_box(transcription, transcription_font_path, img_size[0] - 2 * padding, transcription_height)
    else:
        transcription_lines = []
    
    # Translation (lower section)
    translation_box_y = img_size[1] - int(img_size[1] * 0.2)
    translation_font, translation_lines_translation = fit_text_to_box(translation, translation_font_path, img_size[0] - 2 * padding, img_size[1] - translation_box_y)
    
    # Draw the text
    current_y = padding
    
    # Draw word
    for line in word_lines:
        bbox = draw.textbbox((0, 0), line, font=word_font)
        line_width = bbox[2] - bbox[0]
        x = (img_size[0] - line_width) // 2
        draw.text((x, current_y), line, font=word_font, fill=answer_colours[c_config][1])
        current_y += word_font.getbbox("A")[3] - word_font.getbbox("A")[1] + padding

    # Draw transcription
    if transcription:
        for line in transcription_lines:
            bbox = draw.textbbox((0, 0), line, font=transcription_font)
            line_width = bbox[2] - bbox[0]
            x = (img_size[0] - line_width) // 2
            draw.text((x, current_y), line, font=transcription_font, fill=answer_colours[c_config][1])
            current_y += transcription_font.getbbox("A")[3] - transcription_font.getbbox("A")[1] + padding
    
    # Draw translation
    #current_y = translation_box_y
    for line in translation_lines_translation:
        bbox = draw.textbbox((0, 0), line, font=translation_font)
        line_width = bbox[2] - bbox[0]
        x = (img_size[0] - line_width) // 2
        draw.text((x, current_y), line, font=translation_font, fill=answer_colours[c_config][1])
        current_y += translation_font.getbbox("A")[3] - translation_font.getbbox("A")[1] + padding
    

    buffer = BytesIO()
    image.save(buffer, format="png")
    img_f = buffer.tell()
    buffer.seek(0)
    
    return buffer.getvalue()


