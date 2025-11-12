from math import isnan
import os
import pandas as pd

from src.models.models import Question, AnswerEnum

def is_nan(x):
    return type(x) is float and isnan(x)

def read_excel(
        file_path,
    ) -> list[Question]:
    
    is_type_d = file_path[-1] == 'd'
    
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
            image_num = (question_number+1) // 2 if is_type_d else question_number
            image_path = f'{images_file_path}/image{image_num}.PDF'
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
            return []
        question.read_correct_answer(correct_answer)
    
    if is_type_d:
        type_d_common_sentence_file_path = f'{file_path}/questions_common_sentence.xlsx'
        
        df = pd.read_excel(type_d_common_sentence_file_path, engine="openpyxl")
        data_dict = df.to_dict(orient="records")

        for record in data_dict:
            question_number_float = record['number']
            common_question_sentence = record['question']
            if is_nan(question_number_float) or is_nan(common_question_sentence):
                continue
            
            question_number = int(question_number_float)
            
            for i in range(question_number*2-2, question_number*2):
                questions[i].type_d_common_sentence = common_question_sentence

    return questions
    


