from db.schema import settings
from langchain_handler import create_second_level_themes
from helper_functions import store_data_in_json
import json

all_concept_labels =[]
normalized_concept_themes = []

def get_concept_labels():
    """flatten concept labels into list"""
    filepath = settings.BASE_DIR / "03_files" / "all_interviews.json"
    with open(filepath, "r") as json_file:
        data = json.load(json_file)

    if data is None:
        print("No interviews found")
    label_list= [item.get('concept_label')
              for element in data
              for item in element['items']]
    return ",".join(label_list)


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
    labels  = get_concept_labels()
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