from abc import ABC
import asyncio
import openai

from settings import Settings

class OpenAIModel(ABC):
    model = ""
    is_system_prompt_necessary = True

class Gpt4o(OpenAIModel):
    model = "gpt-4o"
    is_system_prompt_necessary = True

class Gpt4oMini(OpenAIModel):
    model = "gpt-4o-mini"
    is_system_prompt_necessary = True

class Gpto1Preview(OpenAIModel):
    model = "o1-preview"
    is_system_prompt_necessary = False

class Gpto1Mini(OpenAIModel):
    model = "o1-mini"
    is_system_prompt_necessary = False

class OpenAIParams:
    api_key = Settings.API_KEY

class OpenAIClient:
    MAX_FETCH_NUM = 3
    SLEEP_TIME_SEC = 1
    def __init__(
        self,
        api_key=OpenAIParams.api_key,
        model=Gpt4oMini,
    ):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model=model.model

    async def _completion(self, system_prompt, user_prompt):
        messages = self._make_massage(system_prompt=system_prompt, user_prompt=user_prompt)
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            )
        return response.choices[0].message.content

    def _make_massage(self, system_prompt, user_prompt):
        return [
            {"role": "system", "content": system_prompt },
            {"role": "user", "content": user_prompt },
        ]


    async def fetch_completion(self, system_prompt, user_prompt):
        for _ in range(self.MAX_FETCH_NUM):
            try:
                response = await self._completion(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt
                )
                return response
            except Exception as e:
                print(e)
                asyncio.sleep(self.SLEEP_TIME_SEC)
        return None