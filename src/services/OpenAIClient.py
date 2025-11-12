from abc import ABC
import asyncio
from enum import Enum
import openai

from settings import Settings
from src.services.recorder import ApiHistoryRecorder

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

class Gpto1(OpenAIModel):
    model = "o1"
    is_system_prompt_necessary = False

class Gpto3(OpenAIModel):
    model = "o3"
    is_system_prompt_necessary = False

class Gpt5(OpenAIModel):
    model = "gpt-5"
    is_system_prompt_necessary = False

class Gpt5WithThinking(OpenAIModel):
    model = "gpt-5-thinking"
    is_system_prompt_necessary = False

class Roles(Enum):
    assistant = 'assistant'
    user = 'user'
    system = 'system'

class OpenAIParams:
    api_key = key if (key:=Settings.API_KEY) is not None else ""
    temperature = 1 #o1以降のモデルはtempretureが１に固定のため
    seed = 42

class OpenAIClient:
    MAX_FETCH_NUM = 3
    SLEEP_TIME_SEC = 5
    def __init__(
        self,
        api_key: str = OpenAIParams.api_key,
        temperature: float = OpenAIParams.temperature,
        seed: int = OpenAIParams.seed,
        model: type[OpenAIModel] = Gpt4oMini,
        api_history_recorder: ApiHistoryRecorder|None = None,
    ) -> None:
        """
        Args:
            api_key(str): OpenAI APIのAPI key
            model(OpenAIModel): 定義したOpenAIModel
            api_history_recorder(ApiHistoryRecorder): APIの使用履歴を記録する際に用いる
        """
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.temperature = temperature
        self.seed = seed
        self.model = model
        self.api_history_recorder = api_history_recorder

    async def _completion(self, messages):
        response = await self.client.chat.completions.create(
            model=self.model.model,
            messages=messages,
            temperature=self.temperature,
            seed=self.seed,
        )
        if self.api_history_recorder:
        # 一旦costは0でやる　ToDo:コスト計算機能実装
            cost = 0
            self.api_history_recorder.record(
                model_str=self.model.model,
                cost=cost
            )
        return response.choices[0].message.content

    def _make_message(self, prompts_list, base64_image=None):
        messages = []
        for prompt in prompts_list:
            for role, content in prompt.items():
                messages.append({"role": role.value, "content": content})
            
        if base64_image is not None:
            messages.append({"role": Roles.user.value, "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ]})
        return messages

    def _make_message_without_system_prompt(self, prompts_list, base64_image=None):
        messages = []
        for prompt in prompts_list:
            for role, content in prompt.items():
                messages.append({
                    "role": Roles.user.value if role == Roles.system else role.value,
                    "content": content,
                })
            
        if base64_image is not None:
            messages.append({"role": Roles.user.value, "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ]})
        return messages

    async def fetch_completion(self, prompts_list, base64_image=None):
        messages = self._make_message(
            prompts_list=prompts_list,
            base64_image=base64_image,
        ) if self.model.is_system_prompt_necessary else self._make_message_without_system_prompt(
            prompts_list=prompts_list,
            base64_image=base64_image,
        )
        for _ in range(self.MAX_FETCH_NUM):
            try:
                response = await self._completion(messages=messages)
                return response
            except Exception as e:
                print(e)
                await asyncio.sleep(self.SLEEP_TIME_SEC)
        return None