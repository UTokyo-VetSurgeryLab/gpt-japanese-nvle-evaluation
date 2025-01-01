from abc import ABC

from src.models.models import Question
from src.services.OpenAIClient import OpenAIClient

class TranslateToEnglishPrompt(ABC):
    prompt_name = ""
    system_prompt = ""

class BasicTranslateToEnglishPrompt(TranslateToEnglishPrompt):
    prompt_name = "basic_translate_to_english_prompt"
    system_prompt = """
    You have to translate sentence below to English which
    must be quite plain and easy to understand.
    If the terminology is too difficult, you must add explanation for that words.
    """

class OptimizedTranslateToEnglishPrompt1(TranslateToEnglishPrompt):
    prompt_name = "optimized_translate_to_english_prompt_1"
    system_prompt = """
    you need an English translator, spell checker, and veterinary medical language
    expert who can translate Japanese text into English.The translation must to be
    improved and simplified to make it easier to understand for non-specialists at
    a high school level. My request is to keep the meaning intact, but with a more
    literal translation. Notably, you need describe the specific name of country if
    necessary. Especially you should use "in Japan" instead of "in our country".
    Restrictions:
    - The response must be only one translation, containiing only corrections and
    improvements to the Japanese text, not notes or anythins else.
    - Set tempreture = 0
    """

async def translate_to_English_by_openai(
    openai_client: OpenAIClient,
    question: Question,
    translate_to_english_prompt: TranslateToEnglishPrompt = BasicTranslateToEnglishPrompt,
):
    system_prompt = translate_to_english_prompt.system_prompt
    
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