#!/usr/bin/env python3
"""Generate YAML task files for language groups across different tasks."""

import argparse
import os
from pathlib import Path

# Common language groups used across all tasks
LANGUAGE_GROUPS = {
    "swiss": ["de", "fr", "it", "ro"],
    "europe": [
        "ca",  # Catalan
        "cs",  # Czech
        "da",  # Danish
        "de",  # German
        "el",  # Greek
        "en",  # English
        "es",  # Spanish
        "eu",  # Basque
        "fr",  # French
        "hr",  # Croatian
        "hu",  # Hungarian
        "it",  # Italian
        "lt",  # Lithuanian
        "nl",  # Dutch
        "pl",  # Polish
        "pt",  # Portuguese
        "ro",  # Romanian
        "ru",  # Russian
        "sk",  # Slovak
        "sr",  # Serbian
        "sv",  # Swedish
        "tr",  # Turkish
        "uk",  # Ukrainian
    ],
    "global": [
        # European languages
        "ca",
        "cs",
        "da",
        "de",
        "el",
        "en",
        "es",
        "eu",
        "fr",
        "hr",
        "hu",
        "it",
        "lt",
        "nl",
        "pl",
        "pt",
        "ro",
        "ru",
        "sk",
        "sr",
        "sv",
        "tr",
        "uk",
        # Asian languages
        "ar",
        "bn",
        "fa",
        "fil",
        "gu",
        "he",
        "hi",
        "hy",
        "id",
        "ja",
        "kn",
        "ko",
        "ky",
        "ml",
        "mr",
        "ms",
        "ne",
        "si",
        "ta",
        "te",
        "vi",
        "zh",
        # African languages
        "am",
        "ha",
        "ig",
        "mg",
        "ny",
        "sn",
        "so",
        "sw",
        "yo",
    ],
}

SUBJECTS = ["stem", "humanities", "social_sciences", "other"]

# Task configurations
TASK_CONFIGS = {
    "global_mmlu": {
        "base_dir": "lm_eval/tasks/global_mmlu/full",
        "output_dir": "lm_eval/tasks/global_mmlu/full",
        "task_pattern": "global_mmlu_full_{lang}",
        "subject_pattern": "global_mmlu_full_{lang}_{subject}",
        "group_pattern": "global_mmlu_full_{group}",
        "has_subjects": True,
    },
    "hellaswag": {
        "base_dir": "lm_eval/tasks/okapi/hellaswag_multilingual",
        "output_dir": "lm_eval/tasks/hellaswag_groups",
        "task_pattern": "hellaswag_{lang}",
        "group_pattern": "hellaswag_{group}",
        "has_subjects": False,
    },
}


def detect_available_languages(task_name, config):
    """Detect which languages are available for a given task."""
    base_dir = Path(config["base_dir"])
    available_languages = []

    if config["has_subjects"]:
        # For tasks with subjects, check if language directories exist
        for lang in LANGUAGE_GROUPS["global"]:
            lang_dir = base_dir / lang
            if lang_dir.exists() and lang_dir.is_dir():
                available_languages.append(lang)
    else:
        # For tasks without subjects, check for individual task files
        for lang in LANGUAGE_GROUPS["global"]:
            task_file = base_dir / f"{config['task_pattern'].format(lang=lang)}.yaml"
            if task_file.exists():
                available_languages.append(lang)

    return available_languages


def create_group_yaml(task_name, config, group_name, languages, subject=None):
    """Create YAML content for a group and subject."""
    if subject:
        group_id = f"{config['group_pattern'].format(group=group_name)}_{subject}"
        if config["has_subjects"]:
            tasks = [
                f"  - {config['subject_pattern'].format(lang=lang, subject=subject)}"
                for lang in languages
            ]
        else:
            # This shouldn't happen for tasks without subjects
            tasks = [
                f"  - {config['task_pattern'].format(lang=lang)}" for lang in languages
            ]
    else:
        group_id = config["group_pattern"].format(group=group_name)
        if config["has_subjects"]:
            # Reference subject groups
            tasks = []
            for subj in SUBJECTS:
                tasks.append(
                    f"  - {config['group_pattern'].format(group=group_name)}_{subj}"
                )
        else:
            # Reference individual language tasks
            tasks = [
                f"  - {config['task_pattern'].format(lang=lang)}" for lang in languages
            ]

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
    parser = argparse.ArgumentParser(
        description="Generate language group YAML files for evaluation tasks"
    )
    parser.add_argument(
        "task", choices=list(TASK_CONFIGS.keys()), help="Task to generate groups for"
    )
    parser.add_argument(
        "--groups",
        nargs="+",
        choices=list(LANGUAGE_GROUPS.keys()),
        default=list(LANGUAGE_GROUPS.keys()),
        help="Language groups to generate (default: all)",
    )

    args = parser.parse_args()

    task_name = args.task
    config = TASK_CONFIGS[task_name]

    print(f"Generating language groups for task: {task_name}")

    # Detect available languages
    available_languages = detect_available_languages(task_name, config)
    print(
        f"Available languages: {len(available_languages)} ({', '.join(sorted(available_languages))})"
    )

    if not available_languages:
        print(f"No available languages found for {task_name}")
        return

    # Create output directory
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(exist_ok=True)

    for group_name in args.groups:
        languages = LANGUAGE_GROUPS[group_name]

        # Filter to available languages only
        available = [lang for lang in languages if lang in available_languages]
        if not available:
            print(f"No available languages for {group_name} group in {task_name}")
            continue

        print(
            f"Creating {group_name} ({len(available)} languages: {', '.join(available)})"
        )

        # Create group directory if needed (for tasks with subjects)
        if config["has_subjects"]:
            group_dir = output_dir / group_name
            group_dir.mkdir(exist_ok=True)
            output_file = (
                group_dir / f"{config['group_pattern'].format(group=group_name)}.yaml"
            )
        else:
            output_file = (
                output_dir / f"{config['group_pattern'].format(group=group_name)}.yaml"
            )

        # Create main group file
        output_file.write_text(
            create_group_yaml(task_name, config, group_name, available)
        )
        print(f"  Created {output_file}")

        # Create subject files if the task has subjects
        if config["has_subjects"]:
            for subject in SUBJECTS:
                subject_file = (
                    group_dir
                    / f"{config['group_pattern'].format(group=group_name)}_{subject}.yaml"
                )
                subject_file.write_text(
                    create_group_yaml(task_name, config, group_name, available, subject)
                )
                print(f"  Created {subject_file}")


if __name__ == "__main__":
    main()
