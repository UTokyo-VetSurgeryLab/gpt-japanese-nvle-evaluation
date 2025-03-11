import pytest
from unittest.mock import AsyncMock, patch

from src.services.OpenAIClient import Roles
from src.strategies.translate_to_English_by_openai import translate_to_English_by_openai, TranslateToEnglishPrompt

class DummyPrompt(TranslateToEnglishPrompt):
    prompt_name = 'dummy'
    system_prompt = 'dummy system prompt'

@pytest.mark.asyncio
async def test_translate_to_English_by_openai(mocker):
    mock_client = AsyncMock()
    dummy_response = 'dummy response'
    mock_client.fetch_completion = AsyncMock(return_value=dummy_response)
    
    dummy_text = 'dummy text'
    translated_text = await translate_to_English_by_openai(
        openai_client=mock_client,
        text=dummy_text,
        translate_to_english_prompt=DummyPrompt,
    )
    assert translated_text == dummy_response
    
    expected_prompts_list = [
        {Roles.system: DummyPrompt.system_prompt},
        {Roles.user: dummy_text},
    ]
    mock_client.fetch_completion.assert_called_once_with(
        prompts_list=expected_prompts_list
    )
