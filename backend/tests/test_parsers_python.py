from app.parsers.python_parser import parse_python


SAMPLE_MODULE = '''"""Module docstring."""

import os

VALUE = 1


def greet(name: str) -> str:
    return f"hello {name}"


class Greeter:
    def speak(self) -> str:
        return "hi"
'''


def test_parse_python_extracts_module_preamble() -> None:
    blocks = parse_python(SAMPLE_MODULE)
    kinds = [block.chunk_kind for block in blocks]
    assert "module" in kinds
    module = next(block for block in blocks if block.chunk_kind == "module")
    assert module.start_line == 1
    assert module.end_line == 7
    assert "import os" in module.content


def test_parse_python_extracts_function() -> None:
    blocks = parse_python(SAMPLE_MODULE)
    functions = [block for block in blocks if block.chunk_kind == "function"]
    assert len(functions) == 1
    assert functions[0].symbol_name == "greet"
    assert functions[0].start_line == 8
    assert "def greet" in functions[0].content


def test_parse_python_extracts_class_and_method() -> None:
    blocks = parse_python(SAMPLE_MODULE)
    classes = [block for block in blocks if block.chunk_kind == "class"]
    methods = [block for block in blocks if block.chunk_kind == "method"]
    assert len(classes) == 1
    assert classes[0].symbol_name == "Greeter"
    assert len(methods) == 1
    assert methods[0].symbol_name == "Greeter.speak"
    assert methods[0].start_line >= classes[0].start_line


def test_parse_python_invalid_syntax_returns_empty() -> None:
    assert parse_python("def broken(:\n") == []
