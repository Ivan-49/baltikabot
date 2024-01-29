#-*- coding: utf-8 -*-
from fuzzywuzzy import fuzz

from os.path import exists
import re, random


class Brain:
    # диапазон длины текста
    TEXT_LENGTH_RANGE = (2, 125)

    # question, answer
    Q, A = 'q:', 'a:'
    # line break
    LB = '\n'
    # пороговое значение
    Q_THRESHOLD = 69
    # максимальное количество ответов в одном файле
    A_MAX_COUNT = 12

    MEMORY_EXTENSION = '.memory'
    ENCODING = 'utf-8'

    def __init__(self, brain_dir_path):
        self.brain_dir_path = brain_dir_path

    # создает файл, если его нет и возвращает путь
    def memory_path(self, chat_id):
        path = f'{self.brain_dir_path}/{chat_id}{self.MEMORY_EXTENSION}'
        if not exists(path):
            with open(path, 'w'):
                pass
        return path

    def filter_text(self, text):
        # удаление ненужных пробельных символов
        text = ' '.join(text.split())
        # я хуй знает, честно; какая-то нормализация пунктуации (взял из другого проекта)
        text = re.sub(r'\s+(?=(?:[,.?!:;…]))', '', text)

        if len(text) < self.TEXT_LENGTH_RANGE[0]:
            return None
        if len(text) > self.TEXT_LENGTH_RANGE[1]:
            return None

        return text

    # очищает строку от префиксов и line break'ов
    def clear_qa_and_lb(self, text):
        return text.lstrip(self.Q).lstrip(self.A).rstrip(self.LB)

    def get_answers(self, chat_id, q):
        answers = []

        with open(self.memory_path(chat_id), 'r', encoding=self.ENCODING) as f:
            is_answer = False
            for line in f:
                # если строка является ответом
                if is_answer:
                    answers.append(self.clear_qa_and_lb(line))
                    is_answer = False
                    continue
                # если текущая строка,- вопрос, то следующая - ответ

                if  fuzz.token_set_ratio(q, line.startswith(self.Q) and self.clear_qa_and_lb(line)) >=self.Q_THRESHOLD:#нечеткое сравниение
                    is_answer = True


                # if line.startswith(self.Q) and self.clear_qa_and_lb(line) == q:# четкое сравниение
                #     is_answer = True



        return answers

    async def train(self, chat_id, q, a):
        q, a = self.filter_text(q), self.filter_text(a)
        # если вопрос и ответ отфильтрованы и ответов на данный вопрос не больше, чем A_MAX_COUNT
        if q and a and len(self.get_answers(chat_id, q)) < self.A_MAX_COUNT:
            # возможно надо будет переписать под aiofiles
            with open(self.memory_path(chat_id), 'a', encoding=self.ENCODING) as f:
                f.write(f'{self.Q}{q}{self.LB}{self.A}{a}{self.LB}')

    async def answer(self, chat_id, q):
        q = self.filter_text(q)
        if not q:
            return None

        answers = self.get_answers(chat_id, q)
        if not answers:
            return None

        # выбираем рандомный ответ
        return random.choice(answers)
