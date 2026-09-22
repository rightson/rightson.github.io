"""Set the site author without reserializing dates, URLs, or article bodies."""

from pathlib import Path
import re
import yaml

AUTHOR = "Scott Yo-Ru Chen"


def normalize(text):
    match = re.match(r"\A(\ufeff?---\r?\n)(.*?)(^---\s*$|^\.\.\.\s*$)", text, re.M | re.S)
    if not match:
        raise ValueError("Missing YAML front matter")
    header = match[2]
    root = yaml.compose(header, Loader=yaml.SafeLoader)
    if not isinstance(root, yaml.MappingNode) or root.flow_style:
        raise ValueError("Front matter must be a block YAML mapping")
    newline = "\r\n" if "\r\n" in match[1] else "\n"
    authors = [(key, value) for key, value in root.value if key.value == "author"]
    # Fail safely on aliases/anchors instead of corrupting shared YAML values.
    for key, value in reversed(authors):
        start, end = key.start_mark.index, value.end_mark.index
        if value.start_mark.index < key.end_mark.index or header[key.end_mark.index:end].lstrip(": \t").startswith("&"):
            raise ValueError("Author aliases/anchors require manual normalization")
        suffix = newline if end > start and header[end - 1] == "\n" else ""
        replacement = f"author: {AUTHOR}" if key is authors[0][0] else ""
        header = header[:start] + replacement + suffix + header[end:]
    if not authors:
        header = f"author: {AUTHOR}{newline}" + header
    return match[1] + header + text[match.end(2):]


def main():
    updates = []
    for path in sorted(Path("_posts").rglob("*")):
        if path.suffix.lower() not in {".md", ".markdown", ".html"}:
            continue
        text = path.read_bytes().decode("utf-8")
        try:
            updated = normalize(text)
        except (ValueError, yaml.YAMLError) as error:
            raise SystemExit(f"{path}: {error}") from error
        if updated != text:
            updates.append((path, updated))
    for path, updated in updates:
        path.write_bytes(updated.encode("utf-8"))
        print(f"Normalized author: {path}")


if __name__ == "__main__":
    main()
