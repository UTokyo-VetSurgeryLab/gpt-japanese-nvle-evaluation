from math import isnan
import os
import pandas as pd

from src.models.models import Question, AnswerEnum

def is_nan(x):
    return type(x) is float and isnan(x)

def read_excel(
        file_path
    ):
    
    problem_file_path = f'{file_path}/questions.xlsx'
    answer_file_path = f'{file_path}/answers.xlsx'
    images_file_path = f'{file_path}/images'
    
    is_image_contained = os.path.exists(images_file_path)
    
    questions = []

    df = pd.read_excel(problem_file_path, engine="openpyxl")
    data_dict = df.to_dict(orient="records")

    for record in data_dict:
        question_number_float = record['number']
        question_sentence = record['question']
        answer_options = record['options']
        if is_nan(question_number_float) or is_nan(question_sentence) or is_nan(answer_options):
            continue
        
        question_number = int(question_number_float)
        
        if is_image_contained:
            image_path = f'{images_file_path}/q{question_number}.heic'
            question = Question(
                question_number=question_number,
                question_sentence=question_sentence,
                answer_options=answer_options,
                image_path=image_path,
            )
        else:
            question = Question(
                question_number=question_number,
                question_sentence=question_sentence,
                answer_options=answer_options,
            )

        questions.append(question)

    df = pd.read_excel(answer_file_path, engine="openpyxl")
    data_dict = df.to_dict(orient="records")

    for record in data_dict:
        question_number = int(record['number'])
        try:
            answer = record['answer']
            answers = str(answer).split(',')
            correct_answer = set(map(lambda x:AnswerEnum(int(x)), answers))
        except Exception as e:
            print(e)
            correct_answer = AnswerEnum(None)
        question = questions[question_number-1]
        if question.get_question_number() != question_number:
            print('ERROR: CANNOT READ EXCEL FILE WELL')
            return None
        question.read_correct_answer(correct_answer)

    return questions
    


