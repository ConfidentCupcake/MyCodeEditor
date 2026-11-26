def test_spelling_ignores_python_identifiers():
    from ruff_implementation.spelling_core import check_words

    source = (
        "def blarghfunction(somevar):\n"
        '    """mispelled docstring"""\n'
        "    # mispelled comment\n"
        "    return somevar\n"
    )

    result = check_words(
        source,
        markdown=False,
        known=lambda word: word not in {
            "blarghfunction",
            "somevar",
            "mispelled",
        },
    )

    words = [item[3] for item in result.findings]

    assert result.complete
    assert "blarghfunction" not in words
    assert "somevar" not in words
    assert "mispelled" in words