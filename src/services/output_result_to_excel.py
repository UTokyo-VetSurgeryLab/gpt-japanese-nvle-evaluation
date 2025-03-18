import datetime

from src.models.models import Question
from src.services.accuracy import calculate_accuracy
from src.services.write_to_excel import write_api_answers_to_excel


def output_result_to_excel(
    questions: list[Question],
    openai_client_model_str: str = '', 
    is_translated_to_English: bool = False,
    excel_output_path: str = '',
    does_also_write_openai_answer: bool = False,
    solve_question_prompt_str: str = '',
    translate_to_english_prompt_str: str = '',
    is_image_contained: bool = False,
    is_independently: bool = True,
):
    header_list = []
    dt_now = datetime.datetime.now()
    now = dt_now.strftime('%Y/%m/%d %H:%M')
    header_list.append(now)
    model = f"model:{openai_client_model_str}"
    header_list.append(model)
    header_list.append(f"solve_prompt:{solve_question_prompt_str}")
    if is_translated_to_English:
        header_list.append(f"translation:{translate_to_english_prompt_str}")
    with_image = 'O' if is_image_contained else 'X'
    header_list.append(f"with_images:{with_image}")
    independently = 'O' if is_independently else 'X'
    header_list.append(f"independently:{independently}")
    header = '\n'.join(header_list)

    if does_also_write_openai_answer:
        openai_answer_list = [question.openai_answer for question in questions]
        write_api_answers_to_excel(
            header=header,
            values=openai_answer_list,
            excel_path=excel_output_path,
        )
    openai_iscorrect_list = [
        "O" if question.is_correct() else "X" for question in questions
    ]
    # 正答率をエクセルの最下段に書き込む
    accuracy = calculate_accuracy(questions=questions)
    openai_iscorrect_list.append(round(accuracy, 2))

    write_api_answers_to_excel(
        header=header,
        values=openai_iscorrect_list,
        excel_path=excel_output_path,
    )