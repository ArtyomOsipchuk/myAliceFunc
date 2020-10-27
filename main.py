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
    if req['session']['new']:
        res['response']['text'] = 'Приветствую вас, вы тот самый герой, кто осмелился бросить вызов фор' \
                                  'мулам по физике! Всегда помните, что у вас всего 3 права на ошибку' \
                                  ' и можно попросить меня повторить вопрос.' \
                                  ' Какой режим игры вы выбираете, сложность 1 - ' \
                                  'с выбором вариантов ответа или режим 2 - без вариантов ответа?'
        sessionStorage[request.json['session']['user_id']] = {'mode': 0}
        return
    if sessionStorage[user_id]['mode']:
        if sessionStorage[user_id]['mode'] == 1:
            easy(req, res)
            return
        else:
            hard(req, res)
            return
    if '1' in req['request']['nlu']["tokens"] or \
            'с вариантами' in req['request']['original_utterance'].lower():
        req['session']['new'] = True
        sessionStorage[user_id]['mode'] = 1
        easy(req, res)
    elif '2' in req['request']['nlu']["tokens"] or \
            'без вариантов' in req['request']['original_utterance'].lower():
        req['session']['new'] = True
        sessionStorage[user_id]['mode'] = 2
        hard(req, res)
    else:
        res['response']['text'] = 'Простите, но я вас не расслышала, повторите пожалуйста, режим 1 или 2?'
        req['session']['new'] = True


# далее описывается код разных игровых режимов (по функции на каждый;
# код не разделён по разным файлам, т.к. задеплоен на pythonanywhere и пока что удобнее так)

def hard(req, res):
    user_id = req['session']['user_id']

    sound = True
    if req['session']['new']:
        req['session']['new'] = False
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.
        sessionStorage[user_id] = {
            'formuls': {
                "сопротивления": ['напряжение делить на силу тока', 'ю делить на и'],
                "кпд": ["а полезное делить на а затраченное"],
                "силы тяжести": ["масса умножить на ускорение свободного падения",
                                 "массу умножить на ускорение свободного падения",
                                 "масса тела умножить на ускорение свободного падения"],
                "центростремительного ускорения": ["скорость в квадрате делить на радиус", "в квадрат делить на р"],
                "угловой скорости": ["скорость делить на радиус", "в делить на р"],
                "плотности, выраженной через массу и объём": ["масса делить на объём", "м делить на в"],
                "средней скорости": ["путь делить на время", "расстояние делить на время", "с делить на т"],
                "второго закона ньютона": ["сила равно ускорению умноженному на ускорение",
                                           "ф равно м умножить на а", "ф равно м а"],
                "модуля силы трения скольжения": ["коэффициэнт трения умножить на силу реакции опоры",
                                                  "мю умножить на н"],
                "импульса тела": ["масса умножить на скорость", "м умножить на в", "м в"],
                "для вычисления работы силы": ["силу умножить на расстояние и косинус направления работы",
                                               "ф умножить на с и косинус альфа", "ф с кос альфа"],
                "механической мощности": ["работа делить на время", "а делить на т"],
                "кинетической энергии": ["полупроизведение массы и квадрата скорости", "м в квадрат делить на два"],
                "потенциальной энергии": ["масса умножить на ускорение свободного падения умножить на высоту",
                                          "произведение массы, ускорения свободного падения и высоты", "м г аш"],
                "силы Архимеда": ["плотность жидкости умножить на ускорения свободного падения умножить на объём",
                                  "произведение плотности жидкости, ускорения свободного падения и объёма", "п г аш"],
            },
            "suggestions": [],
            'hp': 3,
            'money': 0,
            'result': [],
            'mode': 2,
            'hints': 0,
            'category': 0  # вероятно сделаю выбор тем или между формулами по математике и физике
        }
        suggs = [i for i in sessionStorage[user_id]["formuls"].keys()]
        random.shuffle(suggs)
        sessionStorage[user_id]['suggestions'] = suggs
        sessionStorage[user_id]['result'] = [0, len(sessionStorage[user_id]['suggestions'])]
        res['response']['text'] = 'Вы выбрали сложность 2, отличный выбор! Какая формула у %s?' % (
            sessionStorage[user_id]["suggestions"][0]
        )
        return
    if 'повтор' in req['request']['original_utterance'].lower():
        res['response']['text'] = 'Повторяю, какая формула у %s?' % (
            sessionStorage[user_id]["suggestions"][0]
        )
        return
    # Обрабатываем ответ пользователя.
    if sessionStorage[user_id]["hints"] > 0 and 'подсказка' in any(req['request']['original_utterance'].lower() or
                                                                   "подсказку" in req['request'][
                                                                       'original_utterance'].lower()):
        sessionStorage[user_id]['suggestions'].pop(0)
        sessionStorage[user_id]["result"][0] += 1
        sessionStorage[user_id]["hints"] -= 1
        sound = True
        res['response']['text'] = 'Ответ %s. Мои подсказки как всегда верны!' % \
                                  (sessionStorage[user_id]['formuls'][sessionStorage[user_id]['suggestions'][0]][0])
        if len(sessionStorage[user_id]["suggestions"]) > 0:
            res['response']['text'] += ' Теперь ответь какова формула %s?' % (sessionStorage[user_id]["suggestions"][0])

    if req['request']['original_utterance'].lower() in sessionStorage[user_id]['formuls'][
        sessionStorage[user_id]['suggestions'][0]]:
        sessionStorage[user_id]['suggestions'].pop(0)
        sessionStorage[user_id]["result"][0] += 1
        if sessionStorage[user_id]['result'][0] % 5 == 0 and sessionStorage[user_id]['result'][0] != 0:
            sessionStorage[user_id]['hints'] += 1
            res['response']['text'] += ' Вы были благославлены богами за 5 правильных ответов,' \
                                       ' теперь вы можете попросить подсказку для автоматической' \
                                       ' победы над формулой. Текущий баланс подсказок %s.' \
                                       % (sessionStorage[user_id]['hints'])
        sound = True
        res['response']['text'] = ' Абсолютно верно!'
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


def easy(req, res):
    user_id = req['session']['user_id']

    sound = True
    if req['session']['new']:
        req['session']['new'] = False
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.
        list = ['сопротивления', "кпд", "силы тяжести", "центростремительного ускорения",
                "угловой скорости", "плотности, выраженной через массу и объём"]
        random.shuffle(list)
        sessionStorage[user_id] = {
            'formuls': {
                "сопротивления": ['напряжение делить на силу тока', 'напряжение умножить на силу тока',
                                  "напряжение в квадрате делить на силу тока",
                                  "напряжение умножить на силу тока в квадрате"],
                "кпд": ["а полезное делить на а затраченное",
                        "а затраченное делить на а полезное"],
                "силы тяжести": ["масса умножить на ускорение свободного падения",
                                 "массу делить на ускорение свободного падения",
                                 "масса тела плюс на ускорение свободного падения"],
                "центростремительного ускорения": ["скорость в квадрате делить на радиус",
                                                   "скорость в квадрате умножить на радиус",
                                                   "скорость делить на радиус в квадрате",
                                                   "скорость в квадрате умножить на радиус в квадрате"],
                "угловой скорости": ["скорость делить на радиус", "скорость умножить на радиус",
                                     "скорость делить на радиус в квадрате", "скорость умножить на удвоенный радиус"],
                "плотности, выраженной через массу и объём": ["масса делить на объём", "масса умножить на объём",
                                                              "масса делить на удвоенный объём",
                                                              "масса умножить на объём в квадрате"],
            },
            "suggestions": list,
            'hp': 3,
            'money': 0,
            'result': [],
            'mode': 1,
            'right': 0,
            'hints': 0,
            'category': 0  # вероятно сделаю выбор тем или между формулами по математике и физике
        }
        sessionStorage[user_id]['result'] = [0, len(sessionStorage[user_id]['suggestions'])]
        variants = sessionStorage[user_id]["formuls"][sessionStorage[user_id]["suggestions"][0]][:]
        random.shuffle(variants)
        res['response'][
            'text'] = 'Вы выбрали сложность 1, хороший выбор! Какая формула у %s? Озвучьте только номер варианта. ' \
                      'Варианты ответов: %s.' % (
                          sessionStorage[user_id]["suggestions"][0],
                          '; '.join([f'Вариант {i + 1}: {variants[i]}' for i in range(len(variants))])
                      )
        sessionStorage[user_id]["right"] = variants.index(
            sessionStorage[user_id]["formuls"][sessionStorage[user_id]["suggestions"][0]][0]) + 1
        return
    if 'повтор' in req['request']['original_utterance'].lower():
        variants = sessionStorage[user_id]["formuls"][sessionStorage[user_id]["suggestions"][0]][:]
        random.shuffle(variants)
        res['response'][
            'text'] = 'Повторяю, какая формула у %s? Озвучьте только номер варианта. ' \
                      'Варианты ответов: %s.' % (
                          sessionStorage[user_id]["suggestions"][0],
                          '; '.join([f'Вариант {i + 1}: {variants[i]}' for i in range(len(variants))])
                      )
        return
    if str(sessionStorage[user_id]["right"]) in req['request']['nlu']["tokens"]:
        sessionStorage[user_id]['suggestions'].pop(0)
        sessionStorage[user_id]["result"][0] += 1
        sound = True
        res['response']['text'] = 'Абсолютно верно!'
        if len(sessionStorage[user_id]["suggestions"]) > 0:
            variants = sessionStorage[user_id]["formuls"][sessionStorage[user_id]["suggestions"][0]][:]
            random.shuffle(variants)
            res['response']['text'] += ' Теперь ответь какова формула %s? Озвучьте только номер варианта.' \
                                       ' Варианты ответов: %s.' % (
                                           sessionStorage[user_id]["suggestions"][0],
                                           '; '.join([f'Вариант {i + 1}: {variants[i]}' for i in range(len(variants))])
                                       )
            sessionStorage[user_id]["right"] = variants.index(
                sessionStorage[user_id]["formuls"][sessionStorage[user_id]["suggestions"][0]][0]) + 1

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
                variants = sessionStorage[user_id]["formuls"][sessionStorage[user_id]["suggestions"][0]][:]
                random.shuffle(variants)
                res['response']['text'] += ' Попробуйте ещё раз, какова формула %s? Озвучьте только номер варианта.' \
                                           ' Варианты ответов: %s.' % (
                                               sessionStorage[user_id]["suggestions"][0],
                                               '; '.join(
                                                   [f'Вариант {i + 1}: {variants[i]}' for i in range(len(variants))])
                                           )
                sessionStorage[user_id]["right"] = variants.index(
                    sessionStorage[user_id]["formuls"][sessionStorage[user_id]["suggestions"][0]][0]) + 1

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
