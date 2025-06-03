import pytest
from unittest.mock import AsyncMock, call

from src.models.models import AnswerEnum, Question
from src.services.OpenAIClient import Roles
#from src.services.output_result_to_excel import output_result_to_excel
from src.strategies.solve_questions_by_openai import (
    make_question_user_prompt,
    solve_questions_by_openai_independently,
    solve_type_d_questions_by_openai_dependently,
    SolveQuestionPrompt,
)
from src.strategies.translate_to_English_by_openai import TranslateToEnglishPrompt


class DummySolveQuestionPromt(SolveQuestionPrompt):
    prompt_name = 'dummy'
    system_prompt = 'dummy system prompt'

def test_make_question_user_prompt():
    dummy_question_sentence = 'dummy question sentence.'
    dummy_answer_options = 'dummy answer options'
    question_user_prompt = make_question_user_prompt(
        question_sentence=dummy_question_sentence,
        answer_options=dummy_answer_options,
    )
    expected_question_user_prompt = (
        "dummy question sentence. The answer options are dummy answer options. "
        "Respond with only the number of your choice (e.g., 1, 2, 3, etc.)."
    )
    assert question_user_prompt == expected_question_user_prompt

@pytest.mark.asyncio
async def test_solve_questions_by_openai_independently_in_Japanese_without_images(mocker):
    mock_client = AsyncMock()
    dummy_response_list = ['3', '1']
    mock_client.fetch_completion = AsyncMock(side_effect=dummy_response_list)
    mock_client.model.model = 'dummy model'
    
    dummy_question1 = Question(
        question_number=1,
        question_sentence="dummy question sentence 1",
        answer_options="dummy answer options 1",
        image_path="dummy/image/path/1",
    )
    dummy_question2 = Question(
        question_number=2,
        question_sentence="dummy question sentence 2",
        answer_options="dummy answer options 2",
        image_path="dummy/image/path/2",
    )
    dummy_questions = [dummy_question1, dummy_question2]
    dummy_excel_output_path = 'dummy/excel/output/path'
    
    mock_make_question_user_prompt = mocker.patch("src.strategies.solve_questions_by_openai.make_question_user_prompt", return_value='dummy user prompt')
    mock_output_result_to_excel = mocker.patch("src.strategies.solve_questions_by_openai.output_result_to_excel")
    
    outputed_questions = await solve_questions_by_openai_independently(
        openai_client=mock_client,
        questions=dummy_questions,
        batch_size=2,
        excel_output_path=dummy_excel_output_path,
        solve_question_prompt=DummySolveQuestionPromt,
    )
    
    for i, expeced_answer_str in enumerate(dummy_response_list):
        expected_answer = AnswerEnum(int(expeced_answer_str))
        assert outputed_questions[i].openai_answer == expected_answer
    
    expected_call_count = 2
    assert mock_make_question_user_prompt.call_count == expected_call_count

    mock_output_result_to_excel.assert_called_once_with(
        questions=outputed_questions,
        openai_client_model_str=mock_client.model.model, 
        is_translated_to_English=False,
        excel_output_path=dummy_excel_output_path,
        does_also_write_openai_answer=False,
        solve_question_prompt_str=DummySolveQuestionPromt.prompt_name,
        translate_to_english_prompt_str='',
        is_image_contained=False,
        is_independently=True,
    )

@pytest.mark.asyncio
async def test_solve_questions_by_openai_independently_in_English_with_images(mocker):
    mock_client = AsyncMock()
    dummy_response_list = ['3', '1']
    mock_client.fetch_completion = AsyncMock(side_effect=dummy_response_list)
    mock_client.model.model = 'dummy model'
    
    dummy_question1 = Question(
        question_number=1,
        question_sentence="dummy question sentence 1",
        answer_options="dummy answer options 1",
        image_path="dummy/image/path/1",
    )
    dummy_question2 = Question(
        question_number=2,
        question_sentence="dummy question sentence 2",
        answer_options="dummy answer options 2",
        image_path="dummy/image/path/2",
    )
    dummy_questions = [dummy_question1, dummy_question2]

    dummy_excel_output_path = 'dummy/excel/output/path'

    mock_translate_to_English_by_openai = mocker.patch(
        "src.strategies.solve_questions_by_openai.translate_to_English_by_openai",
        side_effect=[
            'dummy question sentence1 in English',
            'dummy answer options1 in English',
            'dummy question sentence2 in English',
            'dummy answer options2 in English',
        ],
    )
    mock_make_question_user_prompt = mocker.patch("src.strategies.solve_questions_by_openai.make_question_user_prompt", return_value='dummy user prompt')
    mock_output_result_to_excel = mocker.patch("src.strategies.solve_questions_by_openai.output_result_to_excel")
    mock_pdf_encoder_in_base64 = mocker.patch("src.strategies.solve_questions_by_openai.pdf_encoder_in_base64", return_value='dummy base64 image')

    class DummyTranslateToEnglishPrompt(TranslateToEnglishPrompt):
        prompt_name = 'dummy translate to English prompt'
        system_prompt = 'dummy translate to English prompt'

    outputed_questions = await solve_questions_by_openai_independently(
        openai_client=mock_client,
        questions=dummy_questions,
        batch_size=2,
        is_translated_to_English=True,
        excel_output_path=dummy_excel_output_path,
        solve_question_prompt=DummySolveQuestionPromt,
        translate_to_english_prompt=DummyTranslateToEnglishPrompt,
        is_image_contained=True,
    )
    
    # mock_translate_to_Enclishが正しくcallされているか検証
    expected_call_count = 4
    assert mock_translate_to_English_by_openai.call_count == expected_call_count
    mock_translate_to_English_by_openai.assert_has_calls([
        call(
            openai_client=mock_client,
            text='dummy question sentence 1',
            translate_to_english_prompt=DummyTranslateToEnglishPrompt,
        ),
        call(
            openai_client=mock_client,
            text='dummy answer options 1',
            translate_to_english_prompt=DummyTranslateToEnglishPrompt,
        ),
        call(
            openai_client=mock_client,
            text='dummy question sentence 2',
            translate_to_english_prompt=DummyTranslateToEnglishPrompt,
        ),
        call(
            openai_client=mock_client,
            text='dummy answer options 2',
            translate_to_english_prompt=DummyTranslateToEnglishPrompt,
        ),
    ])
    
    # mock_pdf_encoder_in_base64
    expected_call_count = 2
    mock_pdf_encoder_in_base64.call_count == expected_call_count
    mock_pdf_encoder_in_base64.assert_has_calls([
        call(image_path='dummy/image/path/1'),
        call(image_path='dummy/image/path/2'),
    ])
    
    # 解答を正しくobjectに反映させられているか検証
    for i, expeced_answer_str in enumerate(dummy_response_list):
        expected_answer = AnswerEnum(int(expeced_answer_str))
        assert outputed_questions[i].openai_answer == expected_answer
    
    # make_question_user_promptが正しくcallされているか検証
    expected_call_count = 2
    assert mock_make_question_user_prompt.call_count == expected_call_count

    expected_question_sentence_1 = "dummy question sentence1 in English"
    expected_question_sentence_2 = "dummy question sentence2 in English"

    mock_make_question_user_prompt.assert_has_calls([
        call(
            question_sentence=expected_question_sentence_1,
            answer_options='dummy answer options1 in English',
        ),
        call(
            question_sentence=expected_question_sentence_2,
            answer_options='dummy answer options2 in English',
        ),
    ])

    # mock_client.fetch_completionの検証
    expected_call_count = 2
    assert mock_client.fetch_completion.call_count == expected_call_count

    expected_prompts_list_1 = [
        {Roles.system: 'dummy system prompt'},
        {Roles.user: 'dummy user prompt'},
    ]
    expected_prompts_list_2 = [
        {Roles.system: 'dummy system prompt'},
        {Roles.user: 'dummy user prompt'},
    ]
    mock_client.fetch_completion.assert_has_calls([
        call(
            prompts_list=expected_prompts_list_1,
            base64_image='dummy base64 image',
        ),
        call(
            prompts_list=expected_prompts_list_2,
            base64_image='dummy base64 image',
        ),
    ])

    # mock_output_result_to_excelが正しくcallされているか検証
    mock_output_result_to_excel.assert_called_once_with(
        questions=outputed_questions,
        openai_client_model_str=mock_client.model.model, 
        is_translated_to_English=True,
        excel_output_path=dummy_excel_output_path,
        does_also_write_openai_answer=False,
        solve_question_prompt_str=DummySolveQuestionPromt.prompt_name,
        translate_to_english_prompt_str=DummyTranslateToEnglishPrompt.prompt_name,
        is_image_contained=True,
        is_independently=True,
    )

@pytest.mark.asyncio
async def test_solve_type_d_questions_by_openai_dependently_in_Japanese_without_images(mocker):
    mock_client = AsyncMock()
    dummy_response_list = ['3', '1']
    mock_client.fetch_completion = AsyncMock(side_effect=dummy_response_list)
    mock_client.model.model = 'dummy model'
    
    dummy_question1 = Question(
        question_number=1,
        question_sentence="dummy question sentence 1",
        answer_options="dummy answer options 1",
    )
    dummy_question2 = Question(
        question_number=2,
        question_sentence="dummy question sentence 2",
        answer_options="dummy answer options 2",
    )
    dummy_questions = [dummy_question1, dummy_question2]
    for dummy_question in dummy_questions:
        dummy_question.type_d_common_sentence = 'dummy type d common sentence'

    dummy_excel_output_path = 'dummy/excel/output/path'

    mock_make_question_user_prompt = mocker.patch("src.strategies.solve_questions_by_openai.make_question_user_prompt", return_value='dummy user prompt')
    mock_output_result_to_excel = mocker.patch("src.strategies.solve_questions_by_openai.output_result_to_excel")

    outputed_questions = await solve_type_d_questions_by_openai_dependently(
        openai_client=mock_client,
        questions=dummy_questions,
        batch_size=2,
        excel_output_path=dummy_excel_output_path,
        solve_question_prompt=DummySolveQuestionPromt,
    )
    
    for i, expeced_answer_str in enumerate(dummy_response_list):
        expected_answer = AnswerEnum(int(expeced_answer_str))
        assert outputed_questions[i].openai_answer == expected_answer
    
    expected_call_count = 2
    assert mock_make_question_user_prompt.call_count == expected_call_count

    expected_question_sentence_1 = (
        "dummy type d common sentence "
        "dummy question sentence 1"
    )
    expected_question_sentence_2 = "dummy question sentence 2"

    mock_make_question_user_prompt.assert_has_calls([
        call(
            question_sentence=expected_question_sentence_1,
            answer_options='dummy answer options 1',
        ),
        call(
            question_sentence=expected_question_sentence_2,
            answer_options='dummy answer options 2',
        ),
    ])

    # mock_client.fetch_completionの検証
    expected_call_count = 2
    assert mock_client.fetch_completion.call_count == expected_call_count

    expected_prompts_list_1 = [
        {Roles.system: 'dummy system prompt'},
        {Roles.user: 'dummy user prompt'},
    ]
    expected_prompts_list_2 = [
        {Roles.system: 'dummy system prompt'},
        {Roles.user: 'dummy user prompt'},
        {Roles.assistant: '3'},
        {Roles.user: 'dummy user prompt'}
    ]
    mock_client.fetch_completion.assert_has_calls(
        [
            call(
                prompts_list=expected_prompts_list_1,
                base64_image='',
            ),
            call(
                prompts_list=expected_prompts_list_2,
                base64_image='',
            ),
        ],
        any_order=True,
    )

    mock_output_result_to_excel.assert_called_once_with(
        questions=outputed_questions,
        openai_client_model_str=mock_client.model.model, 
        is_translated_to_English=False,
        excel_output_path=dummy_excel_output_path,
        does_also_write_openai_answer=False,
        solve_question_prompt_str=DummySolveQuestionPromt.prompt_name,
        translate_to_english_prompt_str='',
        is_image_contained=False,
        is_independently=False,
    )

@pytest.mark.asyncio
async def test_solve_type_d_questions_by_openai_dependently_in_English_with_images(mocker):
    mock_client = AsyncMock()
    dummy_response_list = ['3', '1']
    mock_client.fetch_completion = AsyncMock(side_effect=dummy_response_list)
    mock_client.model.model = 'dummy model'
    
    dummy_question1 = Question(
        question_number=1,
        question_sentence="dummy question sentence 1",
        answer_options="dummy answer options 1",
        image_path="dummy/image/path",
    )
    dummy_question2 = Question(
        question_number=2,
        question_sentence="dummy question sentence 2",
        answer_options="dummy answer options 2",
        image_path="dummy/image/path",
    )
    dummy_questions = [dummy_question1, dummy_question2]
    for dummy_question in dummy_questions:
        dummy_question.type_d_common_sentence = 'dummy type d common sentence'

    dummy_excel_output_path = 'dummy/excel/output/path'

    mock_translate_to_English_by_openai = mocker.patch(
        "src.strategies.solve_questions_by_openai.translate_to_English_by_openai",
        side_effect=[
            'dummy question sentence1 in English',
            'dummy answer options1 in English',
            'dummy question sentence2 in English',
            'dummy answer options2 in English',
            'dummy type d common sentence in English',
        ],
    )
    mock_make_question_user_prompt = mocker.patch("src.strategies.solve_questions_by_openai.make_question_user_prompt", return_value='dummy user prompt')
    mock_output_result_to_excel = mocker.patch("src.strategies.solve_questions_by_openai.output_result_to_excel")
    mock_pdf_encoder_in_base64 = mocker.patch("src.strategies.solve_questions_by_openai.pdf_encoder_in_base64", return_value='dummy base64 image')

    class DummyTranslateToEnglishPrompt(TranslateToEnglishPrompt):
        prompt_name = 'dummy translate to English prompt'
        system_prompt = 'dummy translate to English prompt'

    outputed_questions = await solve_type_d_questions_by_openai_dependently(
        openai_client=mock_client,
        questions=dummy_questions,
        batch_size=2,
        is_translated_to_English=True,
        excel_output_path=dummy_excel_output_path,
        solve_question_prompt=DummySolveQuestionPromt,
        translate_to_english_prompt=DummyTranslateToEnglishPrompt,
        is_image_contained=True,
    )
    
    # mock_translate_to_Enclishが正しくcallされているか検証
    expected_call_count = 5
    assert mock_translate_to_English_by_openai.call_count == expected_call_count
    mock_translate_to_English_by_openai.assert_has_calls([
        call(
            openai_client=mock_client,
            text='dummy question sentence 1',
            translate_to_english_prompt=DummyTranslateToEnglishPrompt,
        ),
        call(
            openai_client=mock_client,
            text='dummy answer options 1',
            translate_to_english_prompt=DummyTranslateToEnglishPrompt,
        ),
        call(
            openai_client=mock_client,
            text='dummy question sentence 2',
            translate_to_english_prompt=DummyTranslateToEnglishPrompt,
        ),
        call(
            openai_client=mock_client,
            text='dummy answer options 2',
            translate_to_english_prompt=DummyTranslateToEnglishPrompt,
        ),
        call(
            openai_client=mock_client,
            text='dummy type d common sentence',
            translate_to_english_prompt=DummyTranslateToEnglishPrompt,
        ),
    ])
    
    # mock_pdf_encoder_in_base64
    mock_pdf_encoder_in_base64.assert_called_once_with(
        image_path='dummy/image/path'
    )
    
    # 解答を正しくobjectに反映させられているか検証
    for i, expeced_answer_str in enumerate(dummy_response_list):
        expected_answer = AnswerEnum(int(expeced_answer_str))
        assert outputed_questions[i].openai_answer == expected_answer
    
    # make_question_user_promptが正しくcallされているか検証
    expected_call_count = 2
    assert mock_make_question_user_prompt.call_count == expected_call_count

    expected_question_sentence_1 = (
        "dummy type d common sentence in English "
        "dummy question sentence1 in English"
    )
    expected_question_sentence_2 = "dummy question sentence2 in English"

    mock_make_question_user_prompt.assert_has_calls([
        call(
            question_sentence=expected_question_sentence_1,
            answer_options='dummy answer options1 in English',
        ),
        call(
            question_sentence=expected_question_sentence_2,
            answer_options='dummy answer options2 in English',
        ),
    ])

    # mock_client.fetch_completionの検証
    expected_call_count = 2
    assert mock_client.fetch_completion.call_count == expected_call_count

    expected_prompts_list_1 = [
        {Roles.system: 'dummy system prompt'},
        {Roles.user: 'dummy user prompt'},
    ]
    expected_prompts_list_2 = [
        {Roles.system: 'dummy system prompt'},
        {Roles.user: 'dummy user prompt'},
        {Roles.assistant: '3'},
        {Roles.user: 'dummy user prompt'}
    ]
    mock_client.fetch_completion.assert_has_calls([
        call(
            prompts_list=expected_prompts_list_1,
            base64_image='dummy base64 image',
        ),
        call(
            prompts_list=expected_prompts_list_2,
            base64_image='dummy base64 image',
        ),
    ])

    # mock_output_result_to_excelが正しくcallされているか検証
    mock_output_result_to_excel.assert_called_once_with(
        questions=outputed_questions,
        openai_client_model_str=mock_client.model.model, 
        is_translated_to_English=True,
        excel_output_path=dummy_excel_output_path,
        does_also_write_openai_answer=False,
        solve_question_prompt_str=DummySolveQuestionPromt.prompt_name,
        translate_to_english_prompt_str=DummyTranslateToEnglishPrompt.prompt_name,
        is_image_contained=True,
        is_independently=False,
    )
