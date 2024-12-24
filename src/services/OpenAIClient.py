import openai
from settings import Settings
from src.models.models import AnswerEnum

class OpenAIParams:
    model = "gpt-4o"
    api_key = Settings.API_KEY

class OpenAIClient:
    def __init__(self, api_key=OpenAIParams.api_key, model=OpenAIParams.model):
        self.client = openai.OpenAI(api_key=api_key)
        self.model=model

    async def _completion(self, system_prompt, user_prompt):
        messages = self._make_massage(system_prompt=system_prompt, user_prompt=user_prompt)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            )
        return response.choices[0].message.content

    def _make_massage(self, system_prompt, user_prompt):
        return [
            {"role": "system", "content": system_prompt },
            {"role": "user", "content": user_prompt },
        ]

    def _make_user_prompt(self, question_sentence, answer_options):
        user_prompt = f"""
        {question_sentence} 
        The answer options are {answer_options}
        Respond with only the number of your choice (e.g., 1, 2, 3, etc.)
        """
        return user_prompt

    async def fetch_completion(self, system_prompt, question_sentence, answer_options):
        user_prompt = self._make_user_prompt(
            question_sentence=question_sentence,
            answer_options=answer_options
        )
        try:
            response = await self._completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            response_enum = AnswerEnum(int(response))
            return response_enum
        except Exception as e:
            print(e)
            return None