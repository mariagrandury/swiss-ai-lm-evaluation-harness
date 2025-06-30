#!/usr/bin/env python3
"""Generate YAML task files for language groups in Global MMLU."""

import os
from pathlib import Path

BASE_DIR = "lm_eval/tasks/global_mmlu/full"

# Language groups
GROUPS = {
    "swiss": ["de", "fr", "it", "ro"],
    "europe": [
        "cs",  # Czech
        "de",  # German
        "el",  # Greek
        "en",  # English
        "es",  # Spanish
        "fr",  # French
        "it",  # Italian
        "lt",  # Lithuanian
        "nl",  # Dutch
        "pl",  # Polish
        "pt",  # Portuguese
        "ro",  # Romanian
        "ru",  # Russian
        "sr",  # Serbian
        "sv",  # Swedish
        "tr",  # Turkish
        "uk",  # Ukrainian
    ],
    "global": [
        "cs",  # Czech
        "de",  # German
        "el",  # Greek
        "en",  # English
        "es",  # Spanish
        "fr",  # French
        "it",  # Italian
        "lt",  # Lithuanian
        "nl",  # Dutch
        "pl",  # Polish
        "pt",  # Portuguese
        "ro",  # Romanian
        "ru",  # Russian
        "sr",  # Serbian
        "sv",  # Swedish
        "tr",  # Turkish
        "uk",  # Ukrainian
        "bn",  # Bengali
        "fa",  # Persian/Farsi
        "fil",  # Filipino
        "he",  # Hebrew
        "hi",  # Hindi
        "id",  # Indonesian
        "ja",  # Japanese
        "ko",  # Korean
        "ky",  # Kyrgyz
        "ms",  # Malay
        "ne",  # Nepali
        "si",  # Sinhala
        "te",  # Telugu
        "vi",  # Vietnamese
        "zh",  # Chinese
        "am",  # Amharic
        "ar",  # Arabic
        "ha",  # Hausa
        "ig",  # Igbo
        "mg",  # Malagasy
        "ny",  # Chichewa/Nyanja
        "sn",  # Shona
        "so",  # Somali
        "sw",  # Swahili
        "yo",  # Yoruba
    ],
}

SUBJECTS = ["stem", "humanities", "social_sciences", "other"]


def create_yaml(group_name, languages, subject=None):
    """Create YAML content for a group and subject."""
    if subject:
        group_id = f"global_mmlu_full_{group_name}_{subject}"
        tasks = [f"  - global_mmlu_full_{lang}_{subject}" for lang in languages]
    else:
        group_id = f"global_mmlu_full_{group_name}"
        tasks = []
        for lang in languages:
            for subj in SUBJECTS:
                tasks.append(f"  - global_mmlu_full_{lang}_{subj}")

    return f"""group: {group_id}
task:
{chr(10).join(tasks)}
aggregate_metric_list:
  - metric: acc
    aggregation: mean
    weight_by_size: false  # Set to false if you want unweighted average
  - metric: acc_norm
    aggregation: mean
    weight_by_size: false
  - metric: perplexity
    aggregation: mean
    weight_by_size: false
  - metric: f1
    aggregation: mean
    weight_by_size: false
metadata:
  version: 1.0
"""


def main():
    base_dir = Path(BASE_DIR)

    for group_name, languages in GROUPS.items():
        # Filter to available languages only
        available = [lang for lang in languages if (base_dir / lang).exists()]
        if not available:
            continue

        print(f"Creating {group_name} ({len(available)} languages)")

        # Create group directory
        group_dir = base_dir / group_name
        group_dir.mkdir(exist_ok=True)

        # Create main file
        (group_dir / f"global_mmlu_full_{group_name}.yaml").write_text(
            create_yaml(group_name, available)
        )

        # Create subject files
        for subject in SUBJECTS:
            (group_dir / f"global_mmlu_full_{group_name}_{subject}.yaml").write_text(
                create_yaml(group_name, available, subject)
            )


if __name__ == "__main__":
    main()
