#!/usr/bin/env python3
"""Generate YAML task files for language groups across different tasks."""

import argparse
import os
from pathlib import Path

import yaml

# Get script directory to locate config file
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "group_config.yaml"


def load_config():
    """Load configuration from YAML file."""
    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f)


def detect_available_languages(task_name, config, language_groups):
    """Detect which languages are available for a given task."""
    base_dir = Path(config["base_dir"])
    available_languages = []

    if config["has_subjects"]:
        # For tasks with subjects, check if language directories exist
        for lang in language_groups["global"]:
            lang_dir = base_dir / lang
            if lang_dir.exists() and lang_dir.is_dir():
                available_languages.append(lang)
    else:
        # For tasks without subjects, check for individual task files
        # Use file_pattern if available, otherwise fall back to task_pattern
        file_pattern = config.get("file_pattern", config["task_pattern"] + ".yaml")

        for lang in language_groups["global"]:
            task_file = base_dir / file_pattern.format(lang=lang)

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
            for subj in config["subjects"]:
                tasks.append(
                    f"  - {config['group_pattern'].format(group=group_name)}_{subj}"
                )
        else:
            # Reference individual language tasks using task_pattern (not file_pattern)
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


def generate_groups_for_task(task_name, config, language_groups, selected_groups):
    """Generate language groups for a specific task."""
    print(f"Generating language groups for task: {task_name}")

    # Detect available languages
    available_languages = detect_available_languages(task_name, config, language_groups)
    print(
        f"Available languages: {len(available_languages)} ({', '.join(sorted(available_languages))})"
    )

    if not available_languages:
        print(f"No available languages found for {task_name}")
        return

    # Create output directory
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(exist_ok=True)

    for group_name in selected_groups:
        languages = language_groups[group_name]

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
            for subject in config["subjects"]:
                subject_file = (
                    group_dir
                    / f"{config['group_pattern'].format(group=group_name)}_{subject}.yaml"
                )
                subject_file.write_text(
                    create_group_yaml(task_name, config, group_name, available, subject)
                )
                print(f"  Created {subject_file}")


def main():
    # Load configuration
    config_data = load_config()
    language_groups = config_data["language_groups"]
    task_configs = config_data["tasks"]

    # Create choices list with all task names plus "all"
    task_choices = list(task_configs.keys()) + ["all"]

    parser = argparse.ArgumentParser(
        description="Generate language group YAML files for evaluation tasks"
    )
    parser.add_argument(
        "task",
        choices=task_choices,
        help="Task to generate groups for (or 'all' for all tasks)",
    )
    parser.add_argument(
        "--groups",
        nargs="+",
        choices=list(language_groups.keys()),
        default=list(language_groups.keys()),
        help="Language groups to generate (default: all)",
    )

    args = parser.parse_args()

    # Determine which tasks to run
    if args.task == "all":
        tasks_to_run = task_configs.keys()
        print(f"Running all tasks: {', '.join(tasks_to_run)}")
        print("=" * 80)
    else:
        tasks_to_run = [args.task]

    # Run generation for each task
    for task_name in tasks_to_run:
        config = task_configs[task_name]
        generate_groups_for_task(task_name, config, language_groups, args.groups)

        # Add separator between tasks when running all
        if args.task == "all" and task_name != list(tasks_to_run)[-1]:
            print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
