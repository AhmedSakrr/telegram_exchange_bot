import telebot
import requests
import time
import os
# import matplotlib.pyplot as plt

bot = telebot.TeleBot("1879123480:AAHvsZlgb8NSvlmRqDAPCT0ZhKxXvFpWKiU", parse_mode=None)

# ссылка на апи, куда будет отправлен запрос для курсов валют /list
exchange_url = 'http://api.exchangeratesapi.io/latest'

# ссылка на апи, куда будет отправлен запрос на получение истории курсов валют /history
history_url = 'https://api.exchangeratesapi.io/history'

# дополнительные параметры, нужно вписывать access key для работы api
key = {'access_key': 'b5357d8b0b5f3ad4bad0c2f93a10d6c2',
       # 'symbols': 'USD, RUB, UAH',
       }

# файл в который будут сохранены все курсы валют из запроса
# FILE = r'C:\Users\artem\Desktop\bot'
FILE = os.path.join(os.path.abspath(__file__), 'db_dir')

# переменная для сохранения времени предведущего запроса в unix time
REQUESTS_TIME = 0.0

# переменная с названием файла, который будет передан пользователю как график
# IMG = 'graph.png'


def convert_to_usd(eur, val):
    '''конвертирует val в доллары и округляет до 2ух знаков после запятой
    eur - текущий курс евро в долларах'''
    return round(val * eur, 2)


def get_values():
    '''делает запрос и получает html с курсом всех валют к евро,
     конвертирует в курсы к евро и преобразует в строку с /n '''
    html = requests.get(exchange_url, params=key)
    if html.status_code == 200:
        values = (html.json()['rates'])
        if values is not None:
            eur = round(1 / values.get('USD'), 2)
            if eur is not None:
                # создаем строку, которая будет нашим конечным списком валют и курсов
                usd_list = 'EUR' + ': ' + str(eur) + '\n'
                # конвертируем все курсы кроме USD и EUR в курс валюты к доллару и добаляем это в наш список
                for currency in values.keys():
                    if currency != 'USD' and currency != 'EUR':
                        usd_list += str(currency) + ': ' + str(convert_to_usd(eur, values.get(currency))) + '\n'
                return usd_list
    else:
        return 1


def load_to_file(string):
    with open(FILE, 'w') as f:
        f.write(string)


def take_from_file():
    with open(FILE, 'r') as f:
        return f.read()


def converter(cur1, cur2, value):
    '''делает запрос, получает курсы валют к евро
    и переводит из cur1 в cur2 сумму value через конвертацию в евро'''
    html = requests.get(exchange_url, params=key)
    if html.status_code == 200:
        values = (html.json()['rates'])
        if values is not None:
            value_in_euro1 = values.get(cur1.upper())
            value_in_euro2 = values.get(cur2.upper())
            # также округляем до 2ух знаков после запятой
            return round(value / value_in_euro1 * value_in_euro2, 2)


# def get_content_history(cur1, cur2):
#     pass
    # params = {
    #     'base': cur1,
    #     'symbols': cur2,
    # }
    # html = requests.get(history_url, data=params)
    # if html.status_code == 200:
    #     pass
    #     values = (html.json()['rates'])
    #     if values is not None:
    #         pass
    #     else:
    #         return None
    # else:
    #     return None
    # return array


# def draw_graphic(array):
#     fig = plt.figure()
#     plt.plot(array)
#     plt.title('Exchange rate')
#     plt.grid(False)
#     fig.savefig(IMG)
#     plt.close(fig)


# приветствие, краткая информация о боте и инструкция
@bot.message_handler(commands=['start', 'help'])
def information(message):
    text = 'Вас приветствует exchange bot =)\n' \
           'используйте /help чтоб снова просмотреть это сообщение\n' \
           'используйте /list для показа всех курсов валют\n' \
           'используйте /exchange для конвертации из одной валюты в другую'
    bot.send_message(chat_id=message.chat.id, text=text)


# все курсы валют
@bot.message_handler(commands=['list'])
def exchange_list_show(message):
    '''проверяет когда был сделан последний запрос и вызывает соответствующую функцию'''
    global REQUESTS_TIME
    if time.time() > REQUESTS_TIME + 600:
        # с момента запроса прошло более 10 минут и нужно выполнить новый запрос и сохранить время этого запроса
        REQUESTS_TIME = time.time()
        bot.send_message(chat_id=message.chat.id, text='Курсы валют по отношению к USD:\n' + get_values())
        # сохраняем текущий запрос в файл
        load_to_file(get_values())
    else:
        # с момента запроса прошло менее 10 минут, просто загружаем строку из файла
        bot.send_message(chat_id=message.chat.id, text=take_from_file())


# конвертор валют
# /exchange 10 USD to CAD
@bot.message_handler(commands=['exchange'])
def exchange_currency(message):
    '''разделяет сообщение на части, проводит проверку на правильность введеных данных
     и передает в функцию конвертации'''
    # сообщение при неправильном использовании команды
    error_text = 'Используйте /exchange <число> <валюта> to <валюта>\nПример: /exchange 10 USD to EUR'
    # разбираем строку на значения и записываем их в переменные
    parse = message.text.split(' ')
    # проверяем, есть ли нужное количество
    if len(parse) == 5:
        # проверяем введено ли число, если нет, то поднимаем ошибку
        try:
            value = float(parse[1])
        except ValueError:
            bot.send_message(chat_id=message.chat.id, text=error_text)
            return None
        cur1 = parse[2]
        cur2 = parse[4]
        bot.send_message(chat_id=message.chat.id, text=str(converter(cur1, cur2, value)) + ' ' + cur2.upper())
    else:
        bot.send_message(chat_id=message.chat.id, text=error_text)


# @bot.message_handler(commands=['history'])
# def current_history(message):
#     # /history USD/CAD
#     error_text = 'Используйте /history валюта/валюта ' \
#                  '\nПример: /history USD/CAN'
#     parse = message.text.split(' ')
#     if len(parse) > 1:
#         parse2 = parse[1].split('/')
#         cur1 = parse2[0]
#         cur2 = parse2[1]
#         array = get_content_history(cur1, cur2)
#         if array is None:
#             bot.send_message(chat_id=message.chat.id,
#                              text='No exchange rate data is available for the selected currency')
#     else:
#         bot.send_message(chat_id=message.chat.id, text=error_text)
#         return None
#     draw_graphic(array)
#     with open(IMG, 'rb') as img:
#         bot.send_photo(chat_id=message.chat.id, photo=img)


if __name__ == '__main__':
    # если запускается этот файл, включаем нашего бота
    bot.polling()

