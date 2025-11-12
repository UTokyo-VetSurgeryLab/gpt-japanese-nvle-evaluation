from abc import ABC

from src.services.OpenAIClient import OpenAIClient, Roles

class TranslateToEnglishPrompt(ABC):
    prompt_name = ""
    system_prompt = ""

class BasicTranslateToEnglishPrompt(TranslateToEnglishPrompt):
    prompt_name = "basic"
    system_prompt = "You have to translate sentence below to English which\
    must be quite plain and easy to understand.\
    If the terminology is too difficult, you must add explanation for that words."

class OptimizedTranslateToEnglishPrompt1(TranslateToEnglishPrompt):
    prompt_name = "optimized_1"
    system_prompt = "you need an English translator, spell checker, and veterinary medical language\
    expert who can translate Japanese text into English.The translation must be\
    improved and simplified to make it easier to understand for non-specialists at\
    a high school level. My request is to keep the meaning intact, but with a more\
    literal translation. Notably, you need describe the specific name of country if\
    necessary. Especially you should use 'in Japan' instead of 'in our country'.\
    Restrictions:\
    - The response must be only one translation, containiing only corrections and\
    improvements to the Japanese text, not notes or anythins else."

class OptimizedTranslateToEnglishPrompt(TranslateToEnglishPrompt):
    prompt_name = "optimized"
    system_prompt = (
        "You are an expert in English translation, spelling correction, and veterinary medical terminology. "
        "Your task is to translate Japanese text into clear, accurate English that is easy for non-specialists "
        "to understand—ideally at a high school reading level. Preserve the original meaning as much as possible, "
        "but favor a more literal translation when it improves clarity. If the original text refers to a country "
        "without naming it (e.g., 'our country'), explicitly state the country's name. For instance, use 'in Japan' "
        "instead of 'in our country'."
        "Return only the corrected and improved English translation."
        "Do not include notes, explanations, or multiple translation options."
    )


class NormalTranslateToEnglishPrompt(TranslateToEnglishPrompt):
    prompt_name = "normal"
    system_prompt = (
        "Please translate to English."
    )
    
class TranslationError(Exception):
    pass

async def translate_to_English_by_openai(
    openai_client: OpenAIClient,
    text: str,
    translate_to_english_prompt: type[TranslateToEnglishPrompt] = BasicTranslateToEnglishPrompt,
):
    system_prompt = translate_to_english_prompt.system_prompt
    prompts_list = [
        {Roles.system: system_prompt},
        {Roles.user: text},
    ]
    
    try:
        text_in_English = await openai_client.fetch_completion(
            prompts_list=prompts_list,
        )
        if text_in_English is None:
            raise TranslationError
        return text_in_English
    except Exception as e:
        print(e)
