from __future__ import unicode_literals

import json
import logging
from flask import Flask, request
import random

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
sessionStorage = {}


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


def handle_dialog(req, res):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'Приветствую вас, вы тот самый герой, кто осмелился бросить вызов фор' \
                                  'мулам по физике! Всегда помните, что у вас всего 3 права на ошибку' \
                                  ' и можно попросить меня повторить вопрос.' \
                                  ' Какой режим игры вы выбираете, сложность 1 - ' \
                                  'с выбором вариантов ответа или режим 2 - без вариантов ответа?'
        # ещё эпическая и экспериментальная, но со временем они все сольются
        sessionStorage[request.json['session']['user_id']] = {'mode': 0}
        return
    if sessionStorage[user_id]['mode']:
        if sessionStorage[user_id]['mode'] == 3:
            experimental(req, res)
            return
        elif sessionStorage[user_id]['mode'] == 1:
            easy(req, res)
            return
        elif sessionStorage[user_id]['mode'] == 4:
            epic(req, res)
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
    elif '0' in req['request']['nlu']["tokens"] or \
            'экспериментальный' in req['request']['original_utterance'].lower():
        req['session']['new'] = True
        sessionStorage[user_id]['mode'] = 3
        experimental(req, res)
    elif '4' in req['request']['nlu']["tokens"] or \
            'эпич' in req['request']['original_utterance'].lower():
        req['session']['new'] = True
        sessionStorage[user_id]['mode'] = 4
        epic(req, res)
    else:
        res['response']['text'] = 'Простите, но я вас не расслышала, повторите пожалуйста, режим 1 или 2?'
        req['session']['new'] = True


def experimental(req, res):
    user_id = req['session']['user_id']
    sound = True
    if req['session']['new']:
        req['session']['new'] = False
        sessionStorage[user_id] = {
            'formuls': {
                "сопротивления": ["напряжение", "делить", "силу", "ток"],
                "кпд": ["работ", "полезн", "дели", "работ", "затрачен"],
                "силы тяжести": ["масс", "умнож", "ускорен"],
                "угловой скорости": ["скорост", "дели", "радиус"],
            },
            'answers': {
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
            'mode': 3,
            'hints': 0,
            'category': 0
        }
        suggs = [i for i in sessionStorage[user_id]["formuls"].keys()]
        random.shuffle(suggs)
        sessionStorage[user_id]['suggestions'] = suggs
        sessionStorage[user_id]['result'] = [0, len(sessionStorage[user_id]['suggestions'])]
        res['response']['text'] = 'Вы выбрали экспериментальную сложность, отличный выбор! Какая формула у %s?' % (
            sessionStorage[user_id]["suggestions"][0]
        )
        return
    if 'повтор' in req['request']['original_utterance'].lower():
        res['response']['text'] = 'Повторяю, какая формула у %s?' % (
            sessionStorage[user_id]["suggestions"][0]
        )
        return
    if sessionStorage[user_id]["hints"] > 0 and 'подсказка' in any(req['request']['original_utterance'].lower() or
                                                                   "подсказку" in req['request'][
                                                                       'original_utterance'].lower()):
        sessionStorage[user_id]['suggestions'].pop(0)
        sessionStorage[user_id]["result"][0] += 1
        sessionStorage[user_id]["hints"] -= 1
        sound = True
        res['response']['text'] = 'Ответ %s. Мои подсказки как всегда верны!' % \
                                  (sessionStorage[user_id]['answers'][sessionStorage[user_id]['suggestions'][0]][0])
        if len(sessionStorage[user_id]["suggestions"]) > 0:
            res['response']['text'] += ' Теперь ответь какова формула %s?' % (sessionStorage[user_id]["suggestions"][0])

    count = 0
    parts = sessionStorage[user_id]['formuls'][sessionStorage[user_id]['suggestions'][0]]
    for word in req['request']['original_utterance'].lower().split():
        if count < len(parts):
            if parts[count] in word:
                count += 1
    if count != len(parts):
        correct = False
    else:
        correct = True
    if correct:
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
            sessionStorage[user_id]['answers'][sessionStorage[user_id]['suggestions'][0]][0])
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


def hard(req, res):
    user_id = req['session']['user_id']
    sound = True
    if req['session']['new']:
        req['session']['new'] = False
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
                "второго закона ньютона": ["сила равно ускорению умноженному на массу",
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
                                  "произведение плотности жидкости, ускорения свободного падения и объёма", "п г аш"]
            },
            "suggestions": [],
            'hp': 3,
            'money': 0,
            'result': [],
            'mode': 2,
            'hints': 0,
            'category': 0
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
            'category': 0
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
    if str(sessionStorage[user_id]["right"]) == req['request']['nlu']["tokens"][0]:
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


def epic(req, res):
    res['response']['text'] = ''
    res['response']['tts'] = ''
    user_id = req['session']['user_id']
    if req['session']['new']:
        req['session']['new'] = False
        sessionStorage[user_id] = {
            'formuls': {
                "сопротивления": ["напряжение", "делить", "силу", "ток"],
                "кпд": ["работ", "полезн", "дели", "работ", "затрачен"],
                "силы тяжести": ["масс", "умнож", "ускорен", "свободн", "паден"],
                "угловой скорости": ["скорост", "дели", "радиус"],
                "центростремительного ускорения": ["скор", "квадр", "дел", "рад"],
                "плотности, выраженной через массу и объём": ["мас", "дел", "объём"],
                "средней скорости": ["пут", "дел", "врем"],
                "второго закона ньютона": ["сил", "равн", "мас", "умнож", "ускор"],
                "модуля силы трения скольжения": ["коэфф", "тре", "умнож", "сил", "реакции опоры"],
                "импульса тела": ["мас", "умнож", "скор"],
                "для вычисления работы силы": ["сил", "умнож", "расстоян", "кос", "направ", "работ"],
                "механической мощности": ["работ", "дел", "врем"],
                "кинетической энергии": ["полупроизвед", "мас", "квадр", "скор"],
                "потенциальной энергии": ["мас", "умнож", "ускор", "свободн", "паден", "умнож", "высот"],
                "силы Архимеда": ["плотность жидкости", "умнож", "ускор", "свободн", "паден", "умнож", "объём"]
            },
            'answers': {
                "сопротивления": ['напряжение делить на силу тока', 'ю делить на и'],
                "кпд": ["а полезное делить на а затраченное"],
                "силы тяжести": ["масса умножить на ускорение свободного падения",
                                 "массу умножить на ускорение свободного падения",
                                 "масса тела умножить на ускорение свободного падения"],
                "центростремительного ускорения": ["скорость в квадрате делить на радиус", "в квадрат делить на р"],
                "угловой скорости": ["скорость делить на радиус", "в делить на р"],
                "плотности, выраженной через массу и объём": ["масса делить на объём", "м делить на в"],
                "средней скорости": ["путь делить на время", "расстояние делить на время", "с делить на т"],
                "второго закона ньютона": ["равнодействующая сила равна массе умноженной на ускорение",
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
                "силы Архимеда": ["плотность жидкости умножить на уск   орения свободного падения умножить на объём",
                                  "произведение плотности жидкости, ускорения свободного падения и объёма", "п г аш"],
            },
            "suggestions": [],
            'hp': 3,
            'money': 0,
            'result': [],
            'mode': 4,
            'hints': 0,
            'warpath': 0,
            'category': 0,
            'encounters': 0
        }
        suggs = [i for i in sessionStorage[user_id]["formuls"].keys()]
        random.shuffle(suggs)
        sessionStorage[user_id]['suggestions'] = suggs
        sessionStorage[user_id]['result'] = [0, len(sessionStorage[user_id]['suggestions'])]
        res['response'][
            'text'] = 'Добро пожаловать в ту самую "эпическую" сложность игры,' \
                      ' она отличается крайней гротескностью и невозможностью всё' \
                      ' это пропустить! Чтобы начать своё путешествие, тебе нужно пройти испытание и ответить на вопрос: какая формула у %s?' % (
                          sessionStorage[user_id]["suggestions"][0]
                      )
        res['response']['tts'] = res['response'][
                                     'text'] + '<speaker audio="dialogs-upload/1d991873-206a-403b-b2bc-ad5fccbff23c/' \
                                               '3d8976a6-c659-41e7-b952-93b31bcab52c.opus">' + 'Какая формула у %s?' % (
                                     sessionStorage[user_id]["suggestions"][0]
                                 )
        return
    if 'повтор' in req['request']['original_utterance'].lower():
        res['response']['text'] = 'Повторяю, какая формула у %s?' % (
            sessionStorage[user_id]["suggestions"][0]
        )
        return
    if sessionStorage[user_id]["hints"] > 0 and 'подсказка' in any(req['request']['original_utterance'].lower() or
                                                                   "подсказку" in req['request'][
                                                                       'original_utterance'].lower()):
        sessionStorage[user_id]['suggestions'].pop(0)
        sessionStorage[user_id]["result"][0] += 1
        sessionStorage[user_id]["hints"] -= 1
        sessionStorage[user_id]['warpath'] += 1
        res['response'][
            'text'] = 'Эпика не будет, слабак! Ответ %s. Благославение богов перенесло вас на следущую стадию путешествия...' % \
                      (sessionStorage[user_id]['answers'][sessionStorage[user_id]['suggestions'][0]][0])
        if len(sessionStorage[user_id]["suggestions"]) > 0:
            txt = warpath(sessionStorage[user_id]["warpath"], 0).replace('*', sessionStorage[user_id]["suggestions"][0])
            res['response']['text'] += txt[:txt.find('<')] + txt[txt.find('>') + 1:]
            res['response']['tts'] += txt

    count = 0
    parts = sessionStorage[user_id]['formuls'][sessionStorage[user_id]['suggestions'][0]]
    for word in req['request']['original_utterance'].lower().split():
        if count > len(parts):
            break
        if parts[count] in word:
            count += 1
    if count != len(parts):
        correct = False
    else:
        correct = True
    if correct:
        sessionStorage[user_id]['suggestions'].pop(0)
        sessionStorage[user_id]["result"][0] += 1
        txt = warpath(sessionStorage[user_id]["warpath"], 1).replace('*', sessionStorage[user_id]["suggestions"][0])
        res['response']['text'] += txt[:txt.find('<')] + txt[txt.find('>') + 1:]
        res['response']['tts'] += txt
        if sessionStorage[user_id]['result'][0] % 5 == 0 and sessionStorage[user_id]['result'][0] != 0:
            sessionStorage[user_id]['hints'] += 1
            res['response']['text'] += ' Вы были благославлены богами за 5 правильных ответов,' \
                                       ' теперь вы можете попросить подсказку для автоматической' \
                                       ' победы над формулой. Текущий баланс подсказок %s.' \
                                       % (sessionStorage[user_id]['hints'])
            res['response']['tts'] += '<speaker audio="dialogs-upload/1d991873-206a-403b-b2bc-ad5fccbff23c/' \
                                      '3d8976a6-c659-41e7-b952-93b31bcab52c.opus">' + res['response']['text']
        sessionStorage[user_id]['warpath'] += 1
        # if len(sessionStorage[user_id]["suggestions"]) > 0:
    else:
        sessionStorage[user_id]['suggestions'].pop(0)
        sessionStorage[user_id]['hp'] -= 1
        if sessionStorage[user_id]['hp'] < 1:
            txt = warpath(sessionStorage[user_id]["warpath"], 0).replace('*', sessionStorage[user_id]["suggestions"][0])
            res['response']['text'] += txt[:txt.find('<')] + txt[txt.find('>') + 1:]
            res['response']['tts'] += txt
            res['response']["end_session"] = True
        else:
            txt = warpath(sessionStorage[user_id]["warpath"], 1).replace('*', sessionStorage[user_id]["suggestions"][0])
            res['response']['text'] += '<speaker audio="dialogs-upload/1d991873-206a-403b-b' \
                                       '2bc-ad5fccbff23c/02af3341-7103-4d66-90d7-f3f7140fdaff.opus">' \
                                       ' Вы потерпели неудачу, но вас спасло благославение богов,' \
                                       ' полученное вами за успехи, продолжим путь, как будто ничего и не было...' \
                                       + txt[:txt.find('<')] + txt[txt.find('>') + 1:]
            res['response']['tts'] += '<speaker audio="dialogs-upload/1d991873-206a-403b-b' \
                                      '2bc-ad5fccbff23c/02af3341-7103-4d66-90d7-f3f7140fdaff.opus">' \
                                      ' Вы потерпели неудачу, но вас спасло благославение богов,' \
                                      ' полученное вами за успехи, продолжим путь, как будто ничего и не было...' + txt
        sessionStorage[user_id]['warpath'] += 1

    if len(sessionStorage[user_id]["suggestions"]) < 1:
        res['response']['text'] += ' К сожалению тест подошёл к концу,' \
                                   ' пезапустите навык для новой попытки.' \
                                   ' Вы дали %s правильных ответов из %s возможных' % (
                                       sessionStorage[user_id]["result"][0], sessionStorage[user_id]["result"][1])
        res['responce']['tts'] += '<speaker audio="dialogs-upload/1d991873-206a' \
                                  '-403b-b2bc-ad5fccbff23c/caad1650-33ae-4d66-aca4-3636451f42c0.opus">' \
                                  + res['response']['text']
        res['response']['end_session'] = True


def warpath(stage, answer):
    if stage == 0:
        if answer:
            return '<speaker audio="dialogs-upload/1d991873-206a-403b-b2bc-ad5fccbff23c/3d8' \
                   '976a6-c659-41e7-b952-93b31bcab52c.opus">Испытание новичка пройдено! Вы п' \
                   'олучили свой первый профессиональный заказ. ' \
                   'Убейте дракона на вершине ближайшей горы! Да, да, вы сразу идёте убивать дракона,' \
                   ' потому что это ничто по сравнению с экзаменами,' \
                   ' к которым вы готовитесь. Опустим ваши приготовления к такому' \
                   ' непростому путешествию и перенесёмся к подъёму в гору, который, судя по всему, ' \
                   'охраняет культ дракона. Срочно ответь какова формула *? Я слышал, что это отпугивает их.'
        return 'Вы не готовы к тому, что вас ждёт при попытке убийства дракона... ' \
               'Подучите формулы, иначе не сможете победить не только дракона, но и экзамены.'
    elif stage == 1:
        if answer:
            return 'Ур-ра! Они сбежали из-за панической фобии всего научного и ' \
                   'являющегося рационально правильным! Ваш подъём на гору начался и он не будет прост!\n' \
                   '<speaker audio="dialogs-upload/1d991873-206a-403b-b2bc-ad5fccbff23c/8ea33536-3ede' \
                   '-40ef-a5e1-c6537fd2bbd6.opus">Этот подъём потрепал ваши силы, но вы поднялись ко входу в пещеру,' \
                   ' ведущую далее к заснеженным хребтам. На входе стоит древняя эльфийская печать, гласящаяя:' \
                   ' "какая формула у *?". Возможно ответив на вопрос вы освободите путь...'
        return 'Вас принесли в жертву <speaker audio="dialogs-upload/1d991873-206a-403b-b2bc-ad5' \
               'fccbff23c/c72fe1b0-a23e-4786-a450-564304c20a68.opus"> Не стоит недооценивать культистов...'
    elif stage == 2:
        if answer:
            return ''
        return ''
    elif stage == 3:
        if answer:
            return ''
        return ''
    elif stage == 4:
        if answer:
            return ''
        return ''
    elif stage == 5:
        if answer:
            return ''
        return ''
    elif stage == 6:
        if answer:
            return ''
        return ''
    elif stage == 7:
        if answer:
            return ''
        return ''
    elif stage == 8:
        if answer:
            return ''
        return ''
    elif stage == 9:
        if answer:
            return ''
        return ''
    elif stage == 10:
        if answer:
            return ''
        return ''
    elif stage == 11:
        if answer:
            return ''
        return ''
    elif stage == 12:
        if answer:
            return ''
        return ''
    elif stage == 13:
        if answer:
            return ''
        return ''
    elif stage == 14:
        if answer:
            return ''
        return ''
    elif stage == 15:
        if answer:
            return ''
        return ''
    return 'Произошла ошибка симуляции'
