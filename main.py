import re
import pprint
import requests

import telebot
from pytube import YouTube
from googleapiclient.discovery import build


with open('API_telegram.txt', 'r') as f:
    api_telegram = f.read()
    bot = telebot.TeleBot(token=api_telegram)

with open('API_YouTube.txt', 'r') as fn:
    api_youtube = fn.read()
    youtube = build('youtube', 'v3', developerKey=api_youtube)

@bot.message_handler(commands=['start', 'hello', 'Help', 'help'])
def main(message):
    # print(message)
    bot.send_message(
                    message.chat.id,
                    f" <b>Привіт!</b> <b>{message.from_user.first_name}</b>\n - <b>Я допоможу тобі витягти аудіо з відео на YouTube.</b>\n - <b>Просто надішли мені посилання на відео з ютубу(URL), та я відправлю тобі аудіо.</b>\n - <b>Я працюю у фоновому режимі, а значить мені можна надсилати багато посилань,і я їх все оброблю. (кидати по 1 посиланню в чат, тобі все буде працювати корректно)</b>", 
                    parse_mode='html')

def extract_video_id(urls):
    url = urls[-1]
    # Паттерны для извлечения идентификатора видео из ссылки YouTube
    pattern_pc = r'^https?://(?:www\.|m\.)?youtube\.com/watch\?v=([^\s&]+)'
    pattern_mobile = r'^https?://youtu\.be/([^\s?]+)'
    match_pc = re.match(pattern_pc, url)
    match_mobile = re.match(pattern_mobile, url)
    if match_pc:
        print('ID успешно извлечен')
        return match_pc.group(1)
    elif match_mobile:
        print('ID успешно извлечен')
        return match_mobile.group(1)
    else:
        print('ID не извлечен')
        return None

def download_music_from_video(urls, message_chat_id):
    video_id = extract_video_id(urls)
    try:
        # Находим URL на аудиодорожку из видео
        youtube_url = f'https://www.youtube.com/watch?v={video_id}'
        yt = YouTube(youtube_url)
        stream = yt.streams.filter(only_audio=True).first()
        audio_url = stream.url
        # print("Аудио-URL успешно найден:", audio_url)
        
        # Выкачиваем аудио с ссылки, и передаем его в чат бота
        response = requests.get(audio_url,)
        audio_file = response.content
        
        bot.send_audio(chat_id=message_chat_id,performer=yt.author, title=yt.title, audio=audio_file)
    except:
        bot.send_message(message_chat_id, f'<b>Щось пішло не так, повторіть спробу.</b>', parse_mode='html')
        
def check_for_url(message_url, message_chat_id):
    # Регулярное выражение для поиска URL в тексте
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+/\S+'
    # Поиск URL в сообщении
    urls = re.findall(url_pattern, message_url)
    
    # Если найдены URL, значит это ссылка
    if urls:
        bot.send_message(message_chat_id, f'<em>Почалось завантаження аудіо, це може зайняти деякий час...</em>', parse_mode='html')
        download_music_from_video(urls, message_chat_id)
        return True
        
    else:
        return False

@bot.message_handler()
def main_work(message):
    try:
        # Проверяем, сообщение этот URL или нет
        if check_for_url(message.text, message.chat.id):
            # bot.send_message(message.chat.id, f'<em>Loading, please wait</em>', parse_mode='html')
            print(f'Аудио загружено пользователем: \n "username" - {message.from_user.username} \n "first_name" - {message.from_user.first_name} \n "last_name" - {message.from_user.last_name}')
        else:
            bot.send_message(message.chat.id, f'<b>Некоректне посилання, спробуйте ще раз!</b>', parse_mode='html')
    except TypeError as e:
        print(f'Error - {e}')
        bot.send_message(message.chat.id, f'<b>Щось пішло не так, повторіть спробу.</b>', parse_mode='html')


bot.polling(none_stop=True)
