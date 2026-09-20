from app.services.generator import generate_answer


def test_generator_refuses_unsupported_question():
    answer = generate_answer(
        "What is the company vacation policy?",
        "Employees must use multi-factor authentication for all corporate accounts.",
    )

    assert answer == "I do not have enough information in the provided documents."
