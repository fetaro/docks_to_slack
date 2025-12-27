import pytest
from src.slack_list_generator import SlackListGenerator, GenerateResult

@pytest.fixture
def generator():
    return SlackListGenerator()

def test_simple_list(generator):
    html = """
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
    </ul>
    """
    result = generator.generate(html)
    assert isinstance(result, GenerateResult)
    assert "Item 1" in result.plain_text
    assert "Item 2" in result.plain_text
    assert len(result.binary_data) > 0

def test_nested_list(generator):
    html = """
    <ul>
        <li>Level 1
            <ul>
                <li>Level 2</li>
            </ul>
        </li>
    </ul>
    """
    result = generator.generate(html)
    assert "Level 1" in result.plain_text
    assert "\tLevel 2" in result.plain_text

def test_fallback_text(generator):
    html = "<p>Just some text</p>"
    result = generator.generate(html)
    assert "Just some text" in result.plain_text
