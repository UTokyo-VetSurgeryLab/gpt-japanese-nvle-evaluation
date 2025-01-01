from abc import ABC
import asyncio
import datetime

from src.models.models import AnswerEnum, Question
from src.services.OpenAIClient import OpenAIClient
from src.services.accuracy import calculate_accuracy
from src.services.write_to_excel import write_to_excel
from .translate_to_English_by_openai import (
    translate_to_English_by_openai,
    TranslateToEnglishPrompt,
    BasicTranslateToEnglishPrompt,
)

class SolveQuestionPrompt(ABC):
    prompt_name = ""
    system_prompt = ""

class BasicSolveQuestionPrompt(SolveQuestionPrompt):
    prompt_name = "basic_solve_question_prompt"
    system_prompt = """
    You have to solve the problem of veterinary medicine.
    Notably, the examination is of Japan.
    Therefore, you should refer to the low, guidelines, and criteria of Japan. 
    """

class OptimizedSolveQuestionPrompt1(SolveQuestionPrompt):
    prompt_name = "optimized_solve_question_prompt_1"
    system_prompt = """
    As a vet, provide a diagnosis, treatment, and prevention for any illness or desease
    based on a through examination of the patient's age, symptoms, and clinical course.
    Use your expertise to answer clinical veterinary medicine or public health questions
    related to Japan, and output your choice. It is quite important to refer to Japanese
    lows, guidelines, and criteion. Additionally, "in our country" means "in Japan".
    """

def make_question_user_prompt(question_sentence, answer_options):
        user_prompt = f"""
        {question_sentence} 
        The answer options are {answer_options}
        Respond with only the number of your choice (e.g., 1, 2, 3, etc.)
        """
        return user_prompt

async def solve_questions_by_openai(
    openai_client: OpenAIClient,
    questions: list[Question], 
    batch_size: int = 10,
    is_translated_to_English: bool = False,
    excel_output_path: str = '',
    does_also_write_openai_answer: bool = False,
    solve_question_prompt: SolveQuestionPrompt = BasicSolveQuestionPrompt,
    translate_to_english_prompt: TranslateToEnglishPrompt = BasicTranslateToEnglishPrompt
):
    system_prompt = solve_question_prompt.system_prompt
    
    async def process_question(question: Question):
        try:
            if is_translated_to_English:
                response = await translate_to_English_by_openai(
                    openai_client=openai_client,
                    question=question,
                    translate_to_english_prompt=translate_to_english_prompt
                )
                question_sentence = response['question_sentence_in_English']
                answer_options = response['answer_options_in_English']
                question.question_sentence_in_English = question_sentence
                question.answer_options_in_English = answer_options
            else:
                question_sentence = question.get_question_sentence()
                answer_options = question.get_answer_options()

            user_prompt = make_question_user_prompt(
                question_sentence=question_sentence,
                answer_options=answer_options,
            )
            response = await openai_client.fetch_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
            answer = AnswerEnum(int(response.strip()[0]))
            question.set_openai_answer(answer)
        except Exception as e:
            print(f"Error processing question: {e}")

    for i in range(0, len(questions), batch_size):
        tasks = []
        question_list = questions[i:min(len(questions), i + batch_size)]
        for question in question_list:
            tasks.append(process_question(question))
        await asyncio.gather(*tasks)

    if excel_output_path:
        header_list = []
        dt_now = datetime.datetime.now()
        now = dt_now.strftime('%Y/%m/%d %H:%M')
        header_list.append(now)
        model = f"model:{openai_client.model}"
        header_list.append(model)
        header_list.append(f"\nsolve_prompt:{solve_question_prompt.prompt_name}")
        if is_translated_to_English:
            header_list.append(f"\ntranslation:{translate_to_english_prompt.prompt_name}")
        header = '\n'.join(header_list)
        if does_also_write_openai_answer:
            openai_answer_list = [question.openai_answer for question in questions]
            write_to_excel(
                header=header,
                values=openai_answer_list,
                excel_path=excel_output_path,
            )
        openai_iscorrect_list = [
            "O" if question.is_correct() else "X" for question in questions
        ]
        # 正答率をエクセルの最下段に書き込む
        accuracy = calculate_accuracy(questions=questions)
        openai_iscorrect_list.append(round(accuracy, 2))

        write_to_excel(
            header=header,
            values=openai_iscorrect_list,
            excel_path=excel_output_path,
        )
    return questions
