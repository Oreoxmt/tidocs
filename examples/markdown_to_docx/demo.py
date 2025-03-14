import json
from pathlib import Path

from tidocs.markdown_to_docx import MarkdownToWordConfig, markdown_to_docx

if __name__ == "__main__":
    # Define paths for config, input, and output files
    src_path = Path(__file__).resolve().parent
    config_json = src_path / "config.json"
    input_md = src_path / "input.md"
    output_docx = src_path / "output.docx"

    print(f"Loading configuration from: {config_json}")
    # Load configuration
    with config_json.open("r") as f:
        config = json.load(f)

    # Convert Markdown to Word using the configuration
    markdown_content = input_md.read_bytes()
    word_content = markdown_to_docx(markdown_content, MarkdownToWordConfig(**config))
    output_docx.write_bytes(word_content)
    print(f"Conversion complete. Output saved to: {output_docx}")
