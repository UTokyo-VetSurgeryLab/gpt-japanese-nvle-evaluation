import openai
from settings import Settings

class OpenAIParams:
    model = "gpt-4o"
    api_key = Settings.API_KEY

class OpenAIClient:
    def __init__(self, api_key=OpenAIParams.api_key, model=OpenAIParams.model):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model=model

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
        try:
            response = await self._completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            return response
        except Exception as e:
            print(e)
            return None