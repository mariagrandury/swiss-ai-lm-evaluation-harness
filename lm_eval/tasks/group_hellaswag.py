#!/usr/bin/env python3
"""Generate YAML task files for language groups in Hellaswag."""

import os
from pathlib import Path

BASE_DIR = "lm_eval/tasks/okapi/hellaswag_multilingual"
OUTPUT_DIR = "lm_eval/tasks/hellaswag_groups"

# Language groups
GROUPS = {
    "swiss": ["de", "fr", "it", "ro"],
    "europe": [
        "ca",  # Catalan
        "da",  # Danish
        "de",  # German
        "es",  # Spanish
        "eu",  # Basque
        "fr",  # French
        "hr",  # Croatian
        "hu",  # Hungarian
        "it",  # Italian
        "nl",  # Dutch
        "pt",  # Portuguese
        "ro",  # Romanian
        "ru",  # Russian
        "sk",  # Slovak
        "sr",  # Serbian
        "sv",  # Swedish
        "uk",  # Ukrainian
    ],
    "asia": [
        "ar",  # Arabic
        "bn",  # Bengali
        "gu",  # Gujarati
        "hi",  # Hindi
        "hy",  # Armenian
        "id",  # Indonesian
        "kn",  # Kannada
        "ml",  # Malayalam
        "mr",  # Marathi
        "ne",  # Nepali
        "ta",  # Tamil
        "te",  # Telugu
        "vi",  # Vietnamese
    ],
    "global": [
        # European languages
        "ca",
        "da",
        "de",
        "es",
        "eu",
        "fr",
        "hr",
        "hu",
        "it",
        "nl",
        "pt",
        "ro",
        "ru",
        "sk",
        "sr",
        "sv",
        "uk",
        # Asian languages
        "ar",
        "bn",
        "gu",
        "hi",
        "hy",
        "id",
        "kn",
        "ml",
        "mr",
        "ne",
        "ta",
        "te",
        "vi",
    ],
}


def create_group_yaml(group_name, languages):
    """Create YAML content for a hellaswag language group."""
    group_id = f"hellaswag_{group_name}"
    tasks = [f"  - hellaswag_{lang}" for lang in languages]

    return f"""group: {group_id}
task:
{chr(10).join(tasks)}
aggregate_metric_list:
  - metric: acc
    aggregation: mean
    higher_is_better: true
  - metric: acc_norm
    aggregation: mean
    higher_is_better: true
metadata:
  version: 1.0
"""


def main():
    base_dir = Path(BASE_DIR)
    output_dir = Path(OUTPUT_DIR)

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    for group_name, languages in GROUPS.items():
        # Filter to available languages only
        available = []
        for lang in languages:
            hellaswag_file = base_dir / f"hellaswag_{lang}.yaml"
            if hellaswag_file.exists():
                available.append(lang)

        if not available:
            print(f"No available languages for {group_name} group")
            continue

        print(
            f"Creating hellaswag_{group_name} ({len(available)} languages: {', '.join(available)})"
        )

        # Create group file
        group_file = output_dir / f"hellaswag_{group_name}.yaml"
        group_file.write_text(create_group_yaml(group_name, available))
        print(f"  Created {group_file}")


if __name__ == "__main__":
    main()
