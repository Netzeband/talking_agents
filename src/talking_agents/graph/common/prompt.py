from pathlib import Path
from jinja2 import FileSystemLoader, Environment, Template

PROMPT_DIRECTORY = Path(__file__).parent / ".." / "prompts"


def load_prompt(namespace: str, name: str) -> Template:
    env = Environment(loader=FileSystemLoader(str(PROMPT_DIRECTORY / namespace)))
    return env.get_template(f"{name}.j2")
