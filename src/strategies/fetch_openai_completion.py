from src.models.models import Question
from src.services.OpenAIClient import OpenAIClient

async def fetch_openai_completion(
    openai_client: OpenAIClient,
    questions: list[Question],
    batch_size=10,
):
    system_prompt = """
    You have to solve the problem of veterinary medicine.
    """
    question_size = len(questions)
    for i in range(0, question_size, batch_size):
        question_list = questions[i:i+batch_size]
        for question in question_list:
            question_sentence = question.get_question_sentence()
            answer_options = question.get_answer_options()
            answer = await openai_client.fetch_completion(
                system_prompt=system_prompt,
                question_sentence=question_sentence,
                answer_options=answer_options,
            )
            question.set_openai_answer(answer)
    return questions