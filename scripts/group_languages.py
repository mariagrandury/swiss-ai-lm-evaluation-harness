#!/usr/bin/env python3
"""Generate YAML task files for language groups across different tasks."""

import argparse
from pathlib import Path

import yaml

# Get script directory to locate config file
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "group_config.yaml"


def load_config():
    """Load configuration from YAML file."""
    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f)


def detect_available_languages(config, language_groups, language_mapping=None):
    """Detect which languages are available for a given task."""
    base_dir = Path(config["base_dir"])
    available_languages = []

    for lang in language_groups["global"]:
        if config["has_subjects"]:
            # For tasks with subjects, check if language directory exists
            if config.get("use_full_language_names", False):
                # Use full language name (like for include task)
                lang_dir_name = language_mapping.get(lang, "")
                if lang_dir_name and (base_dir / lang_dir_name).exists():
                    available_languages.append(lang)
            else:
                # Use ISO code (like for global_mmlu)
                if (base_dir / lang).exists():
                    available_languages.append(lang)
        else:
            # For tasks without subjects, check for individual files
            file_pattern = config.get("file_pattern", config["task_pattern"] + ".yaml")
            if (base_dir / file_pattern.format(lang=lang)).exists():
                available_languages.append(lang)

    return available_languages


def create_yaml_content(group_id, tasks):
    """Create YAML content with given group ID and task list."""
    return f"""group: {group_id}
task:
{chr(10).join(f"  - {task}" for task in tasks)}
aggregate_metric_list:
  - metric: acc
    aggregation: mean
    weight_by_size: false
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


def create_subject_group_files(
    config, group_name, available_languages, output_dir, language_mapping=None
):
    """Create group files for tasks with subjects (like include and global_mmlu)."""
    group_dir = output_dir / group_name
    group_dir.mkdir(exist_ok=True)

    created_subjects = []
    for subject in config["subjects"]:
        # Try to create this subject - collect languages that have it
        tasks = []
        for lang in available_languages:
            if config.get("use_full_language_names", False):
                # For include task
                lang_dir_name = language_mapping.get(lang, "")
                if lang_dir_name:
                    subject_file = (
                        Path(config["base_dir"])
                        / lang_dir_name
                        / f"include_base_44_{lang_dir_name.lower().replace(' ', '_')}_{subject}.yaml"
                    )
                    if subject_file.exists():
                        task = config["subject_pattern"].format(
                            lang_name=lang_dir_name.lower().replace(" ", "_"),
                            subject=subject,
                        )
                        tasks.append(task)
            else:
                # For global_mmlu, check for underscore-prefixed files
                subject_file = (
                    Path(config["base_dir"])
                    / lang
                    / f"_{config['task_pattern'].format(lang=lang)}_{subject}.yaml"
                )
                if subject_file.exists():
                    task = config["subject_pattern"].format(lang=lang, subject=subject)
                    tasks.append(task)

        # Only create subject file if we found at least one language with this subject
        if tasks:
            created_subjects.append(subject)
            subject_file = (
                group_dir
                / f"{config['group_pattern'].format(group=group_name)}_{subject}.yaml"
            )
            subject_file.write_text(
                create_yaml_content(
                    f"{config['group_pattern'].format(group=group_name)}_{subject}",
                    tasks,
                )
            )
            print(f"  Created {subject_file}")

    # Create main group file referencing created subjects
    main_tasks = [
        f"{config['group_pattern'].format(group=group_name)}_{subject}"
        for subject in created_subjects
    ]
    main_file = group_dir / f"{config['group_pattern'].format(group=group_name)}.yaml"
    main_file.write_text(
        create_yaml_content(
            config["group_pattern"].format(group=group_name), main_tasks
        )
    )
    print(f"  Created {main_file}")


def generate_groups_for_task(
    task_name, config, language_groups, selected_groups, language_mapping=None
):
    """Generate language groups for a specific task."""
    print(f"Generating language groups for task: {task_name}")

    available_languages = detect_available_languages(
        config, language_groups, language_mapping
    )
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

        if config["has_subjects"]:
            create_subject_group_files(
                config, group_name, available, output_dir, language_mapping
            )
        else:
            # Simple task without subjects
            tasks = [config["task_pattern"].format(lang=lang) for lang in available]
            output_file = (
                output_dir / f"{config['group_pattern'].format(group=group_name)}.yaml"
            )
            output_file.write_text(
                create_yaml_content(
                    config["group_pattern"].format(group=group_name), tasks
                )
            )
            print(f"  Created {output_file}")


def main():
    # Load configuration
    config_data = load_config()
    language_groups = config_data["language_groups"]
    task_configs = config_data["tasks"]
    language_mapping = config_data.get("language_mapping", {})

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
        generate_groups_for_task(
            task_name, config, language_groups, args.groups, language_mapping
        )

        # Add separator between tasks when running all
        if args.task == "all" and task_name != list(tasks_to_run)[-1]:
            print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
