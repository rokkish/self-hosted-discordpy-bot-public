import pytest
from quiz import Quiz


@pytest.mark.parametrize(
    # user input, system answer, expected_filter
    "search_theme, selected_title, expected",
    [
        ("onepiece", "onepiece", ""),
        ("onepiece", "one piece", ""),
        ("one piece", "onepiece", ""),
        ("one piece", "one piece", ""),
        ("onepiece", "onepiece ()", ""),
        ("onepiece ()", "onepiece", ""),
        ("onepiece ()", "onepiece ()", ""),
        ("onepiece", "onepiece(x)", ""),
        ("onepiece", "onepiece（x）", ""),
        ("onepiece", "abc （onepiece）", "abc"),
    ],
)
def test_get_title_near(search_theme, selected_title, expected):
    quiz = Quiz()
    assert expected in quiz.get_title_near(search_theme, selected_title)

@pytest.mark.parametrize(
    "title, title_near, user_answer, expected",
    [
        ("onepiece", [], "ONEPIECE", True),
        ("ONEPIECE", [], "onepiece", True),
        ("abc （onepiece）", ["abc"], "onepiece", False),
        ("abc （onepiece）", ["abc"], "abc", True),
    ]
)
def test_is_correct(title, title_near, user_answer, expected):
    quiz = Quiz()
    quiz.title = title
    quiz.title_near = title_near
    assert expected == quiz.is_correct(user_answer)
