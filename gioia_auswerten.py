from db.schema import settings
from langchain_handler import create_second_level_themes
from helper_functions import store_data_in_json
import json

all_concept_labels =[]
normalized_concept_themes = []

def get_concept_labels():
    """Extract concept labels with context into a list of dicts."""
    filepath = settings.BASE_DIR / "03_files" / "all_interviews.json"
    with open(filepath, "r") as json_file:
        data = json.load(json_file)

    if not data:
        print("No interviews found")
        return []

    label_list = []
    for element in data:
        for item in element.get("items", []):
            label_list.append({
                "concept_label": item.get("concept_label"),
                "reasoning": item.get("concept_reasoning"),
                "keywords": item.get("keywords"),
                "excerpt": item.get("answer_summary")  # or item.get("answer")
            })

    return label_list

def concept_labels_as_string():
    """Convert concept labels with context into an LLM-friendly string."""
    concepts = get_concept_labels()
    if not concepts:
        return "No concepts found."

    lines = []
    for c in concepts:
        lines.append(
            f"Concept: {c['concept_label']}\n"
            f"Reasoning: {c.get('reasoning', '')}\n"
            f"Keywords: {', '.join(c.get('keywords', []))}\n"
            f"Excerpt: {c.get('excerpt', '')}\n"
            "---"
        )
    return "\n".join(lines)


def flatten_second_level_themes() -> str:
    """flatten second level themes into string"""
    filepath = settings.BASE_DIR / "03_files" / "second_level_themes.json"

    with open(filepath, "r") as json_file:
        raw_data = json.load(json_file)
    data = raw_data[0]['themes']
    if data is None:
        print("No data")
    themes_lines = "\n".join(
        f"Theme: {theme['pattern_name']}\n"
        f"Weight: {theme['weight']}\n"
        f"Reasoning: {' '.join(theme['reasoning'])}\n"
        f"Dimensions: {', '.join(theme['broader_aggregate_dimensions'])}\n"
        for theme in data)

    return themes_lines


def main():
    labels  = concept_labels_as_string()
    second_level_themes = create_second_level_themes(labels)

    all_concept_labels.append(second_level_themes.model_dump())
    store_data_in_json(filename="second_level_themes.json", data=all_concept_labels)

    flattened_themes = flatten_second_level_themes()
    normalized_themes = create_second_level_themes(flattened_themes)

    normalized_concept_themes.append(normalized_themes.model_dump())
    store_data_in_json(filename="normalized_second_level_themes.json",
                       data=normalized_concept_themes)





if __name__ == '__main__':
    main()