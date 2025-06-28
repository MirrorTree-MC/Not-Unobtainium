import json
import re
from pathlib import Path

MODID = "xaeroworldmap"
ROOT_DIR = Path(__file__).resolve().parent.parent
JSON_DIR = ROOT_DIR / f"assets/{MODID}/lang"
LANG_SOURCE = JSON_DIR / "en_us.json"  # 原始语言文件，默认使用英文
LANG_TARGET = JSON_DIR / "zh_cn.json"  # 目标语言文件，可替换成你自己的语言文件
IGNORE_PATTERNS = [r"doge", r"froge", r".color"]
MERGE = True  # 是否自动合并新的键到目标文件


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def should_ignore_key(key, ignore_patterns):
    """
    判断某个键是否需要忽略（支持正则匹配）。

    Parameters
    ----------
    key : str
        需要检测的键（例如 "metadata.author"）。
    ignore_patterns : list
        正则表达式模式列表。

    Returns
    -------
    bool
        如果匹配则返回 True，否则 False。
    """
    return any(re.search(pattern, key) for pattern in ignore_patterns)


def find_untranslated_keys(source, localized, untranslated_keys=None, parent_key="", ignore_patterns=None):
    """
    递归查找未翻译的键，支持正则表达式排除指定键。

    Parameters
    ----------
    source
        原始 JSON 数据。
    localized
        本地化后的 JSON 数据。
    untranslated_keys : list, optional
        用于记录未翻译键的列表。
    parent_key : str, optional
        用于记录嵌套的键路径。
    ignore_patterns : list, optional
        要排除的正则表达式模式列表。

    Returns
    -------
    list
        未翻译键的列表。
    """
    if untranslated_keys is None:
        untranslated_keys = []
    if ignore_patterns is None:
        ignore_patterns = []

    if isinstance(source, dict):
        for key, value in source.items():
            new_key = f"{parent_key}.{key}" if parent_key else key

            if should_ignore_key(new_key, ignore_patterns):
                continue

            if key in localized:
                if isinstance(value, (dict, list)):
                    find_untranslated_keys(
                        value, localized[key], untranslated_keys, new_key, ignore_patterns
                    )
                elif localized[key] == value:
                    untranslated_keys.append(new_key)
            else:
                untranslated_keys.append(new_key)

    elif isinstance(source, list) and isinstance(localized, list):
        for index, (s_item, l_item) in enumerate(zip(source, localized)):
            find_untranslated_keys(
                s_item, l_item, untranslated_keys, f"{parent_key}[{index}]", ignore_patterns
            )

    return untranslated_keys


def merge_translations(source, localized, ignore_patterns, parent_key=""):
    """
    递归合并英文原文到目标翻译中，如果发现目标文件缺失某个键，
    则自动将该键及其英文值添加进去。

    Parameters
    ----------
    source : dict or list
        英文原文 JSON 数据。
    localized : dict or list
        本地化后的 JSON 数据。
    ignore_patterns : list
        要忽略的正则表达式模式列表。
    parent_key : str
        用于记录嵌套的键路径。

    Returns
    -------
    int
        新添加键的数量。
    """
    added_count = 0

    if isinstance(source, dict):
        for key, value in source.items():
            new_key = f"{parent_key}.{key}" if parent_key else key
            if should_ignore_key(new_key, ignore_patterns):
                continue

            if key not in localized:
                localized[key] = value
                added_count += 1
            else:
                # 如果都是字典，则递归合并
                if isinstance(value, dict) and isinstance(localized[key], dict):
                    added_count += merge_translations(value, localized[key], ignore_patterns, new_key)
                # 对于列表，假设长度相同，进行逐项合并
                elif isinstance(value, list) and isinstance(localized[key], list):
                    for i, (s_item, l_item) in enumerate(zip(value, localized[key])):
                        if isinstance(s_item, dict) and isinstance(l_item, dict):
                            added_count += merge_translations(
                                s_item, l_item, ignore_patterns, f"{new_key}[{i}]"
                            )
    elif isinstance(source, list) and isinstance(localized, list):
        for i, (s_item, l_item) in enumerate(zip(source, localized)):
            if isinstance(s_item, dict) and isinstance(l_item, dict):
                added_count += merge_translations(s_item, l_item, ignore_patterns, f"{parent_key}[{i}]")
    return added_count


source_json = load_json(LANG_SOURCE)
localized_json = load_json(LANG_TARGET)

untranslated_keys = find_untranslated_keys(source_json, localized_json, ignore_patterns=IGNORE_PATTERNS)

if untranslated_keys:
    print(f"You have {len(untranslated_keys)} untranslated keys:")
    for key in untranslated_keys:
        print(key)
else:
    print("All keys are translated!")

# 自动添加 zh_cn.json 中缺失的键（使用英文值）

if not MERGE:
    exit()

added = merge_translations(source_json, localized_json, IGNORE_PATTERNS)
if added:
    with open(LANG_TARGET, "w", encoding="utf-8") as f:
        json.dump(localized_json, f, ensure_ascii=False, indent=4)
    print(f"\nAutomatically added {added} untranslated key(s) to {LANG_TARGET.name}.")
else:
    print("\nNo new untranslated keys were added.")
