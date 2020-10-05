# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с JSON и логами.
import json
import logging

# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request
import random

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

# Хранилище данных о сессиях.
sessionStorage = {}


# Задаем параметры приложения Flask.
@app.route("/", methods=['POST'])
def main():
    # Функция получает тело запроса и возвращает ответ.
    logging.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    handle_dialog(request.json, response)

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )


# Функция для непосредственной обработки диалога.
def handle_dialog(req, res):
    user_id = req['session']['user_id']

    sound = True
    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.
        list = ['сопротивления', "кпд", "силы тяжести"]
        random.shuffle(list)
        sessionStorage[user_id] = {
            'formuls': {
                "сопротивления": ['напряжение делить на силу тока', 'ю делить на и'],
                "кпд": ["а полезное делить на а затраченное"],
                "силы тяжести": ["масса умножить на ускорение свободного падения",
                                 "массу умножить на ускорение свободного падения",
                                 "масса тела умножить на ускорение свободного падения"],
            },
            "suggestions": list,
            'hp': 3,
            'money': 0,
            'result': [],
            'category': 0  # вероятно сделаю выбор тем или между формулами по математике и физике
        }
        sessionStorage[user_id]['result'] = [0, len(sessionStorage[user_id]['suggestions'])]
        res['response']['text'] = 'Приветствую вас, вы тот самый герой, кто осмелился бросить вызов фор' \
                                  'мулам по физике! Какая формула у %s?' % (
                                      sessionStorage[user_id]["suggestions"][0]
                                  )
        return

    # Обрабатываем ответ пользователя.
    if req['request']['original_utterance'].lower() in sessionStorage[user_id]['formuls'][
        sessionStorage[user_id]['suggestions'][0]]:
        sessionStorage[user_id]['suggestions'].pop(0)
        sessionStorage[user_id]["result"][0] += 1
        sound = True
        res['response']['text'] = 'Абсолютно верно!'
        if len(sessionStorage[user_id]["suggestions"]) > 0:
            res['response']['text'] += ' Теперь ответь какова формула %s?' % (sessionStorage[user_id]["suggestions"][0])

    else:
        sessionStorage[user_id]['hp'] -= 1
        res['response']['text'] = 'Неверно. Правильный ответ: %s.' % (
            sessionStorage[user_id]['formuls'][sessionStorage[user_id]['suggestions'][0]][0])
        sound = False
        if sessionStorage[user_id]['hp'] < 1:
            res['response']['text'] += ' Вы погибли, перезапустите навык...'
            res['response']["end_session"] = True
        else:
            sessionStorage[user_id]['suggestions'].pop(0)
            if len(sessionStorage[user_id]["suggestions"]) > 0:
                res['response']['text'] += ' Попробуй ещё, какова формула %s?' % (
                    sessionStorage[user_id]["suggestions"][0])

    if len(sessionStorage[user_id]["suggestions"]) < 1:
        res['response']['text'] += ' К сожалению тест подошёл к концу,' \
                                   ' пезапустите навык для новой попытки.' \
                                   ' Вы дали %s правильных ответов из %s возможных' % (
                                       sessionStorage[user_id]["result"][0], sessionStorage[user_id]["result"][1])
        res['response']['end_session'] = True
    if sound:
        res['response']['tts'] = '<speaker audio="dialogs-upload/1d991873-206a-403b-b2bc-ad5fccbff23c/' \
                                 '3d8976a6-c659-41e7-b952-93b31bcab52c.opus">' + res['response']['text']
    else:
        res['response']['tts'] = '<speaker audio="dialogs-upload/1d991873-206a-403b-b2bc-ad5fccbff23c/' \
                                 '02af3341-7103-4d66-90d7-f3f7140fdaff.opus">' + res['response']['text']
