import json
from pathlib import Path

MODID = "xaeroworldmap"
ROOT_DIR = Path(__file__).resolve().parent.parent
JSON_DIR = ROOT_DIR / f"assets/{MODID}/lang"
# INPUT = JSON_DIR / "zh_cn.json"   # Original json file to be sorted
# OUTPUT = JSON_DIR / "zh_cn.json"  # Output json file, set to the same as INPUT for in-place sorting
SORT_ZH = True  # Sort json keys of Chinese locale
SORT_EN = True  # Sort json keys of English locale


def sort_json_keys(obj):
    """
    Sort all dictionary keys in the JSON structure recursively.

    Parameters
    ----------
    obj : dict or list
        JSON data to be sorted (dictionary or list).

    Returns
    -------
        JSON data after reordering.
    """
    if isinstance(obj, dict):
        return {key: sort_json_keys(obj[key]) for key in sorted(obj.keys())}
    elif isinstance(obj, list):
        return [sort_json_keys(item) for item in obj]
    else:
        return obj


def reorder_json_file(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    sorted_data = sort_json_keys(data)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=4)


# reorder_json_file(INPUT, OUTPUT)

if SORT_ZH:
    INPUT_ZH = JSON_DIR / "zh_cn.json"
    OUTPUT_ZH = JSON_DIR / "zh_cn.json"
    reorder_json_file(INPUT_ZH, OUTPUT_ZH)
    print("Chinese JSON sorting completed.")
if SORT_EN:
    INPUT_EN = JSON_DIR / "en_us.json"
    OUTPUT_EN = JSON_DIR / "en_us.json"
    reorder_json_file(INPUT_EN, OUTPUT_EN)
    print("English JSON sorting completed.")

print("JSON sorting completed.")
