import pandas as pd

from src.models.models import Question, AnswerEnum

def read_excel(
        problem_file_path,
        answer_file_path,
    ):
    questions = []

    df = pd.read_excel(problem_file_path, engine="openpyxl")
    data_dict = df.to_dict(orient="records")

    for record in data_dict:
        question_number = record['number']
        question_sentence = record['question']
        answer_options = record['answer_options']
        question = Question(
            question_number=question_number,
            question_sentence=question_sentence,
            answer_options=answer_options
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
    


