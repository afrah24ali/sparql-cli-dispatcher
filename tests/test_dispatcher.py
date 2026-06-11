import pytest

from query import get_query, main, query_type, supported_intents


def test_has_at_least_five_intents():
    assert len(supported_intents()) >= 5


@pytest.mark.parametrize(
    "intent, expected_parts",
    [
        (
            "list authors at NeurIPS",
            ["SELECT", "?author", ":publishedIn", ":NeurIPS"],
        ),
        (
            "papers per topic",
            ["SELECT", "COUNT", "GROUP BY"],
        ),
        (
            "top 5 cited",
            ["SELECT", ":citationCount", "ORDER BY DESC", "LIMIT 5"],
        ),
        (
            "any NeurIPS papers",
            ["ASK", ":publishedIn", ":NeurIPS"],
        ),
        (
            "construct 2023 authored graph",
            ["CONSTRUCT", "WHERE"],
        ),
    ],
)
def test_each_intent_returns_expected_sparql_structure(intent, expected_parts):
    sparql = get_query(intent)

    for part in expected_parts:
        assert part in sparql


def test_query_type_detects_select():
    sparql = get_query("top 5 cited")
    assert query_type(sparql) == "SELECT"


def test_query_type_detects_ask():
    sparql = get_query("any NeurIPS papers")
    assert query_type(sparql) == "ASK"


def test_query_type_detects_construct():
    sparql = get_query("construct 2023 authored graph")
    assert query_type(sparql) == "CONSTRUCT"


def test_show_query_prints_sparql(capsys):
    exit_code = main(["top 5 cited", "--show-query"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "SELECT" in captured.out
    assert "LIMIT 5" in captured.out


def test_unknown_intent_exits_nonzero(capsys):
    with pytest.raises(SystemExit) as error:
        main(["wrong english question"])

    captured = capsys.readouterr()

    assert error.value.code != 0
    assert "usage:" in captured.err
    assert "Unknown intent" in captured.err
    assert "Supported intents" in captured.err