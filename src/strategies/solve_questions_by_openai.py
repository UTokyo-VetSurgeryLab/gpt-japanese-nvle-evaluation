from src.models.models import AnswerEnum, Question
from src.services.OpenAIClient import OpenAIClient
from src.services.write_to_excel import write_to_excel
from .translate_to_English_by_openai import translate_to_English_by_openai

def make_user_prompt(question_sentence, answer_options):
        user_prompt = f"""
        {question_sentence} 
        The answer options are {answer_options}
        Respond with only the number of your choice (e.g., 1, 2, 3, etc.)
        """
        return user_prompt

async def solve_questions_by_openai(
    openai_client: OpenAIClient,
    questions: list[Question], 
    batch_size: int=10,
    is_translated_to_English: bool=False,
    excel_output_path: str = '',
    does_also_write_openai_answer: bool = False,
):
    system_prompt = """
    You have to solve the problem of veterinary medicine.
    Notably, the examination is of Japan.
    Therefore, you should refer to the low, guidelines, and criteria of Japan. 
    """
    question_size = len(questions)
    for i in range(0, question_size, batch_size):
        question_list = questions[i:i+batch_size]
        for question in question_list:
            if is_translated_to_English:
                response = await translate_to_English_by_openai(
                    openai_client=openai_client,
                    question=question,
                )
                question_sentence_in_English = response['question_sentence_in_English']
                answer_options_in_English = response['answer_options_in_English']
                question_sentence = question_sentence_in_English
                answer_options = answer_options_in_English
                question.question_sentence_in_English = question_sentence_in_English
                question.answer_options_in_English = answer_options_in_English
            else:
                question_sentence = question.get_question_sentence()
                answer_options = question.get_answer_options()
            user_prompt = make_user_prompt(
                question_sentence=question_sentence,
                answer_options=answer_options,
            )
            try:
                response = await openai_client.fetch_completion(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                )
                answer = AnswerEnum(int(response.strip()[0]))
                question.set_openai_answer(answer)
            except Exception as e:
                print(e)
    if excel_output_path:
        if does_also_write_openai_answer:
            openai_answer_list = [question.openai_answer for question in questions]
            write_to_excel(
                header='openai_answer',
                values=openai_answer_list,
                excel_path=excel_output_path,
            )
        openai_iscorrect_list = [
            "O" if question.is_correct() else "X" for question in questions
        ]
        write_to_excel(
            header="is_correct",
            values=openai_iscorrect_list,
            excel_path=excel_output_path,
        )
    return questions