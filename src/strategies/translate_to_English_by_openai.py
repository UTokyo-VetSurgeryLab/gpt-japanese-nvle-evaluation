from src.models.models import Question
from src.services.OpenAIClient import OpenAIClient


async def translate_to_English_by_openai(
    openai_client: OpenAIClient,
    question: Question,
    batch_size=10,
):
    system_prompt = """
    You have to translate sentence below to English which
    must be quite plain and easy to understand.
    """
    
    question_sentence = question.get_question_sentence()
    answer_options = question.get_answer_options()
    try:
        question_sentence_in_English = await openai_client.fetch_completion(
            system_prompt=system_prompt,
            user_prompt=question_sentence,
        )
        answer_options_in_English = await openai_client.fetch_completion(
            system_prompt=system_prompt,
            user_prompt=answer_options,
        )
    except Exception as e:
        print(e)
    return {
        'question_sentence_in_English': question_sentence_in_English,
        'answer_options_in_English': answer_options_in_English,
    }