from enum import Enum


class Question:
    def __init__(self, question_number, question_sentence, answer_options):
        self.question_number = question_number
        self.question_sentence = question_sentence
        self.answer_options = answer_options
        self.supplimentary_information = None
        self.correct_answer = set()
        self.openai_answer = None

    def is_correct(self):
        if self.openai_answer is None:
            return None
        else:
            return self.openai_answer in self.correct_answer

    def read_supplimentary_information(self, text):
        self.supplimentary_information = text

    def read_correct_answer(self, text):
        self.correct_answer = text

    def set_openai_answer(self, text):
        self.openai_answer = text

    def get_question_number(self):
        return self.question_number

    def get_question_sentence(self):
        return self.question_sentence

    def get_answer_options(self):
        return self.answer_options

    def __str__(self):
        return f'{self.question_number}: {self.question_sentence}'


class AnswerEnum(Enum):
    CHOICE_1 = 1
    CHOICE_2 = 2
    CHOICE_3 = 3
    CHOICE_4 = 4
    CHOICE_5 = 5
    UNKNOWN = None


class Answer:
    def __init__(self, answer: AnswerEnum):
        self.answer = answer

    def get_answer(self):
        return self.answer
        