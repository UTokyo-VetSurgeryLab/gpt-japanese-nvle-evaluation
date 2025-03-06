from abc import ABC
import asyncio

from src.models.models import AnswerEnum, Question
from src.services.OpenAIClient import OpenAIClient, Roles
from src.services.image_encoder import pdf_encoder_in_base64
from src.services.output_result_to_excel import output_result_to_excel
from .translate_to_English_by_openai import (
    translate_to_English_by_openai,
    TranslateToEnglishPrompt,
    BasicTranslateToEnglishPrompt,
)


class SolveQuestionPrompt(ABC):
    prompt_name = ""
    system_prompt = ""

class BasicSolveQuestionPrompt(SolveQuestionPrompt):
    prompt_name = "basic"
    system_prompt = "You have to solve the problem of veterinary medicine.\
    Notably, the examination is of Japan.\
    Therefore, you should refer to the low, guidelines, and criteria of Japan."

class OptimizedSolveQuestionPrompt1(SolveQuestionPrompt):
    prompt_name = "optimized_1"
    system_prompt = "As a vet, provide a diagnosis, treatment, and prevention for any illness or desease\
    based on a through examination of the patient's age, symptoms, and clinical course.\
    Use your expertise to answer clinical veterinary medicine or public health questions\
    related to Japan, and output your choice. It is quite important to refer to Japanese\
    lows, guidelines, and criteion. Additionally, 'in our country' means 'in Japan'."

def make_question_user_prompt(question_sentence, answer_options):
        user_prompt = f"{question_sentence}\
        The answer options are {answer_options}\
        Respond with only the number of your choice (e.g., 1, 2, 3, etc.)"
        return user_prompt

async def solve_questions_by_openai_independently(
    openai_client: OpenAIClient,
    questions: list[Question], 
    batch_size: int = 5,
    is_translated_to_English: bool = False,
    excel_output_path: str = '',
    does_also_write_openai_answer: bool = False,
    solve_question_prompt: SolveQuestionPrompt = BasicSolveQuestionPrompt,
    translate_to_english_prompt: TranslateToEnglishPrompt = BasicTranslateToEnglishPrompt,
    is_image_contained: bool = False,
    is_dry_run: bool = False,
):
    system_prompt = solve_question_prompt.system_prompt

    async def process_question(question: Question):
        try:
            if is_translated_to_English:
                question_sentence_in_English = await translate_to_English_by_openai(
                    openai_client=openai_client,
                    text=question.question_sentence,
                    translate_to_english_prompt=translate_to_english_prompt
                )
                answer_options_in_English = await translate_to_English_by_openai(
                    openai_client=openai_client,
                    text=question.answer_options,
                    translate_to_english_prompt=translate_to_english_prompt
                )
                question.question_sentence_in_English = question_sentence_in_English
                question.answer_options_in_English = answer_options_in_English
                if question.type_d_common_sentence is None:
                        user_prompt = make_question_user_prompt(
                        question_sentence=question_sentence_in_English,
                        answer_options=answer_options_in_English,
                    )
                else:
                    type_d_common_sentence_in_English = await translate_to_English_by_openai(
                        openai_client=openai_client,
                        text=question.type_d_common_sentence,
                        translate_to_english_prompt=translate_to_english_prompt
                    )
                    question.type_d_common_sentence_in_English = type_d_common_sentence_in_English
                    question_sentences_in_English = '\n'.join([
                        type_d_common_sentence_in_English,
                        question_sentence_in_English,
                    ])
                    user_prompt = make_question_user_prompt(
                        question_sentence=question_sentences_in_English,
                        answer_options=answer_options_in_English,
                    )
            else:
                question_sentence = question.question_sentence
                answer_options = question.answer_options
                if question.type_d_common_sentence is None:
                    user_prompt = make_question_user_prompt(
                        question_sentence=question_sentence,
                        answer_options=answer_options,
                    )
                else:
                    type_d_common_sentence = question.type_d_common_sentence
                    question_sentences = '\n'.join([
                        type_d_common_sentence,
                        question_sentence,
                    ])
                    user_prompt = make_question_user_prompt(
                        question_sentence=question_sentences,
                        answer_options=answer_options,
                    )
            
            base64_image = None
            if is_image_contained:
                image_path = question.image_path
                if image_path is None:
                    print('Error: cannot find image path')
                try:
                    base64_image = pdf_encoder_in_base64(image_path=image_path)
                except Exception as e:
                    print(f'Error: {e}')

            prompts_list = [
                {Roles.system: system_prompt},
                {Roles.user: user_prompt},
            ]
            print(prompts_list)
            if is_dry_run:
                return None
            
            response = await openai_client.fetch_completion(
                prompts_list=prompts_list,
                base64_image=base64_image
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
        output_result_to_excel(
            questions=questions,
            openai_client_model_str=openai_client.model.model, 
            is_translated_to_English=is_translated_to_English,
            excel_output_path=excel_output_path,
            does_also_write_openai_answer=does_also_write_openai_answer,
            solve_question_prompt_str=solve_question_prompt.prompt_name,
            translate_to_english_prompt_str=translate_to_english_prompt.prompt_name,
            is_image_contained=is_image_contained,
        )
    return questions

async def solve_type_d_questions_by_openai_dependently(
    openai_client: OpenAIClient,
    questions: list[Question], 
    batch_size: int = 5,
    is_translated_to_English: bool = False,
    excel_output_path: str = '',
    does_also_write_openai_answer: bool = False,
    solve_question_prompt: SolveQuestionPrompt = BasicSolveQuestionPrompt,
    translate_to_english_prompt: TranslateToEnglishPrompt = BasicTranslateToEnglishPrompt,
    is_image_contained: bool = False,
    is_dry_run: bool = False,
):
    system_prompt = solve_question_prompt.system_prompt
    HEAD_STRINGS_NUM_TO_CONFIRM_SAME_COMMON_SENTENCE = 20

    async def process_question(question1: Question, question2: Question):
        if question1.type_d_common_sentence is None or question2.type_d_common_sentence is None:
            print('Error: This question is not type D.\nThe common sentence is blank.')
            return None
        q1_head_sentence = question1.type_d_common_sentence[:HEAD_STRINGS_NUM_TO_CONFIRM_SAME_COMMON_SENTENCE]
        q2_head_sentence = question2.type_d_common_sentence[:HEAD_STRINGS_NUM_TO_CONFIRM_SAME_COMMON_SENTENCE]
        if q1_head_sentence != q2_head_sentence:
            print('Error: The combination of questions seems wrong.')
            return None
        try:
            if is_translated_to_English:
                q1_question_sentence_in_English = await translate_to_English_by_openai(
                    openai_client=openai_client,
                    text=question1.question_sentence,
                    translate_to_english_prompt=translate_to_english_prompt
                )
                q1_answer_options_in_English = await translate_to_English_by_openai(
                    openai_client=openai_client,
                    text=question1.answer_options,
                    translate_to_english_prompt=translate_to_english_prompt
                )
                q2_question_sentence_in_English = await translate_to_English_by_openai(
                    openai_client=openai_client,
                    text=question2.question_sentence,
                    translate_to_english_prompt=translate_to_english_prompt
                )
                q2_answer_options_in_English = await translate_to_English_by_openai(
                    openai_client=openai_client,
                    text=question2.answer_options,
                    translate_to_english_prompt=translate_to_english_prompt
                )

                question1.question_sentence_in_English = q1_question_sentence_in_English
                question1.answer_options_in_English = q1_answer_options_in_English
                question2.question_sentence_in_English = q2_question_sentence_in_English
                question2.answer_options_in_English = q2_answer_options_in_English

                type_d_common_sentence_in_English = await translate_to_English_by_openai(
                    openai_client=openai_client,
                    text=question1.type_d_common_sentence,
                    translate_to_english_prompt=translate_to_english_prompt
                )
                question1.type_d_common_sentence_in_English = type_d_common_sentence_in_English
                question2.type_d_common_sentence_in_English = type_d_common_sentence_in_English

                q1_question_sentences_in_English = '\n'.join([
                    type_d_common_sentence_in_English,
                    q1_question_sentence_in_English,
                ])
                q1_user_prompt = make_question_user_prompt(
                    question_sentence=q1_question_sentences_in_English,
                    answer_options=q1_answer_options_in_English,
                )
                q2_user_prompt = make_question_user_prompt(
                    question_sentence=q2_question_sentence_in_English,
                    answer_options=q2_answer_options_in_English,
                )
            else:
                q1_question_sentence = question1.question_sentence
                q1_answer_options = question1.answer_options
                q2_question_sentence = question2.question_sentence
                q2_answer_options = question2.answer_options

                type_d_common_sentence = question1.type_d_common_sentence
                q1_question_sentences = '\n'.join([
                    type_d_common_sentence,
                    q1_question_sentence,
                ])
                q1_user_prompt = make_question_user_prompt(
                    question_sentence=q1_question_sentences,
                    answer_options=q1_answer_options,
                )
                q2_user_prompt = make_question_user_prompt(
                    question_sentence=q2_question_sentence,
                    answer_options=q2_answer_options,
                )
            #print(f'q1_user_prompt:{q1_user_prompt}')
            print(q1_question_sentence)
            
            base64_image = None
            if is_image_contained:
                if question1.image_path != question2.image_path:
                    print('Error: The paths of image do not match')
                image_path = question1.image_path
                if image_path is None:
                    print('Error: cannot find image path')
                    return None
                try:
                    base64_image = pdf_encoder_in_base64(image_path=image_path)
                except Exception as e:
                    print(f'Error: {e}')

            prompts_list = [
                {Roles.system: system_prompt},
                {Roles.user: q1_user_prompt},
            ]
            print(prompts_list)
            if is_dry_run:
                return None
            
            response1 = await openai_client.fetch_completion(
                prompts_list=prompts_list,
                base64_image=base64_image,
            )
            print(f'response1:{response1}')
            answer1 = AnswerEnum(int(response1.strip()[0]))
            question1.openai_answer = answer1
            
            prompts_list.append({Roles.assistant: str(answer1.value)})
            prompts_list.append({Roles.user: q2_user_prompt})
            print(prompts_list)
            
            response2 = await openai_client.fetch_completion(
                prompts_list=prompts_list,
                base64_image=base64_image,
            )
            print(f'response2:{response2}')
            answer2 = AnswerEnum(int(response2.strip()[0]))
            question2.openai_answer = answer2
        except Exception as e:
            print(f"Error processing question: {e}")

    for i in range(0, len(questions), batch_size*2):
        tasks = []
        question_list = questions[i:min(len(questions), i + batch_size*2)]
        for num in range(0, len(question_list), 2):
            tasks.append(process_question(
                question1=question_list[num],
                question2=question_list[num+1],
            ))
        await asyncio.gather(*tasks)

    if excel_output_path:
        output_result_to_excel(
            questions=questions,
            openai_client_model_str=openai_client.model.model, 
            is_translated_to_English=is_translated_to_English,
            excel_output_path=excel_output_path,
            does_also_write_openai_answer=does_also_write_openai_answer,
            solve_question_prompt_str=solve_question_prompt.prompt_name,
            translate_to_english_prompt_str=translate_to_english_prompt.prompt_name,
            is_image_contained=is_image_contained,
            is_independently=False, # dependently
        )
    return questions
