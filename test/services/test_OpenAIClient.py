import pytest
#import pytest_mock
from unittest.mock import AsyncMock, patch

from src.services.OpenAIClient import OpenAIClient, Gpt4oMini, Gpto1Preview, Roles

class TestOpenAIClient:
    EXPECTED_TEMPERATURE = 0
    EXPECTED_SEED = 42
    
    @pytest.mark.asyncio
    async def test_completion_without_history_recorder(self, mocker):
        mock_client = AsyncMock()
        
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock(message=AsyncMock(content="test response"))]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        client = OpenAIClient(
            api_key="fake-api-key",
            model=Gpt4oMini,
            api_history_recorder=None,
        )
        client.client = mock_client

        messages = [{"role": "user", "content": "Hello, how are you?"}]

        response = await client._completion(messages)

        assert response == "test response"
        
        mock_client.chat.completions.create.assert_called_once_with(
            model=Gpt4oMini.model,
            messages=messages,
            temperature=self.EXPECTED_TEMPERATURE,
            seed=self.EXPECTED_SEED,
        )
    
    def test_make_messages_without_images(self):
        prompts_list = [
            {Roles.system: 'dummy_system_prompt'},
            {Roles.user: 'dummy_user_prompt1'},
            {Roles.assistant: 'dummy_assistant_prompt'},
            {Roles.user: 'dummy_user_prompt2'},
        ]
        openaiclient = OpenAIClient(
            api_key="fake-api-key",
            model=Gpt4oMini,
            api_history_recorder=None,
        )
        message = openaiclient._make_message(prompts_list=prompts_list)
        
        expected_message = [
            {"role": 'system', "content": 'dummy_system_prompt'},
            {"role": 'user', "content": 'dummy_user_prompt1'},
            {"role": 'assistant', "content": 'dummy_assistant_prompt'},
            {"role": 'user', "content": 'dummy_user_prompt2'},
        ]
        assert message == expected_message
    
    def test_make_messages_with_images(self):
        prompts_list = [
            {Roles.system: 'dummy_system_prompt'},
            {Roles.user: 'dummy_user_prompt1'},
            {Roles.assistant: 'dummy_assistant_prompt'},
            {Roles.user: 'dummy_user_prompt2'},
        ]
        openaiclient = OpenAIClient(
            api_key="fake-api-key",
            model=Gpt4oMini,
            api_history_recorder=None,
        )
        dummy_base64_image = 'dummy_base64_image'
        message = openaiclient._make_message(
            prompts_list=prompts_list,
            base64_image=dummy_base64_image,
        )
        
        expected_message = [
            {"role": 'system', "content": 'dummy_system_prompt'},
            {"role": 'user', "content": 'dummy_user_prompt1'},
            {"role": 'assistant', "content": 'dummy_assistant_prompt'},
            {"role": 'user', "content": 'dummy_user_prompt2'},
            {"role": 'user', "content": [
                {
                    "type": 'image_url',
                    "image_url": {
                        "url": 'data:image/jpeg;base64,dummy_base64_image'
                    }
                }
            ]}
        ]
        assert message == expected_message

    def test_make_messages_without_system_prompt_without_images(self):
        prompts_list = [
            {Roles.system: 'dummy_system_prompt'},
            {Roles.user: 'dummy_user_prompt1'},
            {Roles.assistant: 'dummy_assistant_prompt'},
            {Roles.user: 'dummy_user_prompt2'},
        ]
        openaiclient = OpenAIClient(
            api_key="fake-api-key",
            model=Gpt4oMini,
            api_history_recorder=None,
        )
        message = openaiclient._make_message_without_system_prompt(prompts_list=prompts_list)
        
        expected_message = [
            {"role": 'user', "content": 'dummy_system_prompt'}, # system prompts are converted to user one
            {"role": 'user', "content": 'dummy_user_prompt1'},
            {"role": 'assistant', "content": 'dummy_assistant_prompt'},
            {"role": 'user', "content": 'dummy_user_prompt2'},
        ]
        assert message == expected_message
    
    def test_make_messages_without_system_prompt_with_images(self):
        prompts_list = [
            {Roles.system: 'dummy_system_prompt'},
            {Roles.user: 'dummy_user_prompt1'},
            {Roles.assistant: 'dummy_assistant_prompt'},
            {Roles.user: 'dummy_user_prompt2'},
        ]
        openaiclient = OpenAIClient(
            api_key="fake-api-key",
            model=Gpt4oMini,
            api_history_recorder=None,
        )
        dummy_base64_image = 'dummy_base64_image'
        message = openaiclient._make_message_without_system_prompt(
            prompts_list=prompts_list,
            base64_image=dummy_base64_image,
        )
        
        expected_message = [
            {"role": 'user', "content": 'dummy_system_prompt'}, # system prompts are converted to user one
            {"role": 'user', "content": 'dummy_user_prompt1'},
            {"role": 'assistant', "content": 'dummy_assistant_prompt'},
            {"role": 'user', "content": 'dummy_user_prompt2'},
            {"role": 'user', "content": [
                {
                    "type": 'image_url',
                    "image_url": {
                        "url": 'data:image/jpeg;base64,dummy_base64_image'
                    }
                }
            ]}
        ]
        assert message == expected_message

    @pytest.mark.asyncio
    @pytest.mark.parametrize('model, is_system_prompt_neccesary', [
    (Gpt4oMini(), True),
    (Gpto1Preview(), False),
  ])
    async def test_fetch_completion_with_images(
        self,
        mocker,
        model,
        is_system_prompt_neccesary,
    ):
        mock_client = AsyncMock()
        
        dummy_response = "test response"
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock(message=AsyncMock(content="test response"))]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        client = OpenAIClient(
            api_key="fake-api-key",
            model=model,
            api_history_recorder=None,
        )
        client.client = mock_client
        prompts_list = [
            {Roles.system: 'dummy_system_prompt'},
            {Roles.user: 'dummy_user_prompt1'},
            {Roles.assistant: 'dummy_assistant_prompt'},
            {Roles.user: 'dummy_user_prompt2'},
        ]

        expected_response = dummy_response

        expected_prompts = [
            {"role": 'system' if is_system_prompt_neccesary else 'user' , "content": 'dummy_system_prompt'}, # system prompts are converted to user one
            {"role": 'user', "content": 'dummy_user_prompt1'},
            {"role": 'assistant', "content": 'dummy_assistant_prompt'},
            {"role": 'user', "content": 'dummy_user_prompt2'},
            {"role": 'user', "content": [
                {
                    "type": 'image_url',
                    "image_url": {
                        "url": 'data:image/jpeg;base64,dummy_base64_image'
                    }
                }
            ]}
        ]

        dummy_base64_image = 'dummy_base64_image'
        response = await client.fetch_completion(
            prompts_list=prompts_list,
            base64_image=dummy_base64_image,
        )

        assert response == expected_response
        mock_client.chat.completions.create.assert_called_once_with(
            model=model.model,
            messages=expected_prompts,
            temperature=self.EXPECTED_TEMPERATURE,
            seed=self.EXPECTED_SEED,
        )

    @pytest.mark.asyncio
    async def test_fetch_completion_sleep_if_raising_Exception(mocker):
        openaiclient = OpenAIClient(
            api_key="fake-api-key",
            model=Gpt4oMini,
            api_history_recorder=None,
        )
        mock_completion = AsyncMock(side_effect=Exception("Mock Exception"))  # 常に例外を投げる
        mock_sleep = AsyncMock()
        
        prompts_list = [{Roles.system:'dummy prompt'}]

        with patch.object(openaiclient, "_completion", mock_completion), patch("asyncio.sleep", mock_sleep):
            result = await openaiclient.fetch_completion(prompts_list=prompts_list)

        assert mock_completion.call_count == openaiclient.MAX_FETCH_NUM

        assert mock_sleep.call_count == openaiclient.MAX_FETCH_NUM
        mock_sleep.assert_called_with(openaiclient.SLEEP_TIME_SEC)

        assert result is None
            
            
        
