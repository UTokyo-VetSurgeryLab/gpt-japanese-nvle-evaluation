def calculate_accuracy(questions):
    correct = 0
    wrong = 0
    for question in questions:
        if question.is_correct():
            correct += 1
        else:
            wrong += 1
    if correct + wrong == 0:
        print('ERROR: the question list is empty')
        return None
    return correct / (correct + wrong)