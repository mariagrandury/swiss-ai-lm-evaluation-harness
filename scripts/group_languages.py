#!/usr/bin/env python3
"""Generate YAML task files for language groups across different tasks."""

import argparse
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "group_config.yaml"


def load_config():
    """Load configuration from YAML file."""
    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f)


def detect_available_languages(config, language_groups, language_mapping):
    """Detect which languages are available for a given task."""
    base_dir = Path(config["base_dir"])
    available = []

    for lang in language_groups["global"]:
        if config["has_subjects"]:
            # Tasks with subjects - check directory existence
            if config.get("use_full_language_names"):
                lang_name = language_mapping.get(lang, "")
                path = base_dir / lang_name if lang_name else None
            else:
                path = base_dir / lang

            if path and path.exists():
                available.append(lang)
        else:
            # Tasks without subjects - check file existence
            file_pattern = config.get("file_pattern", f"{config['task_pattern']}.yaml")
            if (base_dir / file_pattern.format(lang=lang)).exists():
                available.append(lang)

    return available


def get_subject_file_path(config, lang, subject, language_mapping):
    """Get the path to a subject file for a language."""
    base_dir = Path(config["base_dir"])

    if config.get("use_full_language_names"):
        # Include task pattern
        lang_name = language_mapping.get(lang, "")
        if not lang_name:
            return None
        lang_dir = lang_name
        filename = (
            f"include_base_44_{lang_name.lower().replace(' ', '_')}_{subject}.yaml"
        )
    else:
        # Global MMLU pattern (with underscore prefix)
        lang_dir = lang
        filename = f"_{config['task_pattern'].format(lang=lang)}_{subject}.yaml"

    return base_dir / lang_dir / filename


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
    config, group_name, available_languages, output_dir, language_mapping
):
    """Create group files for tasks with subjects."""
    group_dir = output_dir / group_name
    group_dir.mkdir(exist_ok=True)

    created_subjects = []

    for subject in config["subjects"]:
        tasks = []

        for lang in available_languages:
            subject_file = get_subject_file_path(
                config, lang, subject, language_mapping
            )
            if subject_file and subject_file.exists():
                if config.get("use_full_language_names"):
                    lang_name = language_mapping[lang].lower().replace(" ", "_")
                    task = config["subject_pattern"].format(
                        lang_name=lang_name, subject=subject
                    )
                else:
                    task = config["subject_pattern"].format(lang=lang, subject=subject)
                tasks.append(task)

        if tasks:
            created_subjects.append(subject)
            subject_id = f"{config['group_pattern'].format(group=group_name)}_{subject}"
            subject_file = group_dir / f"{subject_id}.yaml"
            subject_file.write_text(create_yaml_content(subject_id, tasks))
            print(f"  Created {subject_file}")

    # Create main group file
    main_id = config["group_pattern"].format(group=group_name)
    main_tasks = [f"{main_id}_{subject}" for subject in created_subjects]
    main_file = group_dir / f"{main_id}.yaml"
    main_file.write_text(create_yaml_content(main_id, main_tasks))
    print(f"  Created {main_file}")


def create_simple_group_file(config, group_name, available_languages, output_dir):
    """Create group file for tasks without subjects."""
    group_id = config["group_pattern"].format(group=group_name)
    tasks = [config["task_pattern"].format(lang=lang) for lang in available_languages]
    output_file = output_dir / f"{group_id}.yaml"
    output_file.write_text(create_yaml_content(group_id, tasks))
    print(f"  Created {output_file}")


def generate_groups_for_task(
    task_name, config, language_groups, selected_groups, language_mapping
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

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(exist_ok=True)

    for group_name in selected_groups:
        available = [
            lang for lang in language_groups[group_name] if lang in available_languages
        ]

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
            create_simple_group_file(config, group_name, available, output_dir)


def main():
    config_data = load_config()
    language_groups = config_data["language_groups"]
    task_configs = config_data["tasks"]
    language_mapping = config_data.get("language_mapping", {})

    parser = argparse.ArgumentParser(
        description="Generate language group YAML files for evaluation tasks"
    )
    task_choices = list(task_configs.keys()) + ["all"]
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

    tasks_to_run = task_configs.keys() if args.task == "all" else [args.task]

    if args.task == "all":
        print(f"Running all tasks: {', '.join(tasks_to_run)}")
        print("=" * 80)

    for i, task_name in enumerate(tasks_to_run):
        generate_groups_for_task(
            task_name,
            task_configs[task_name],
            language_groups,
            args.groups,
            language_mapping,
        )

        if args.task == "all" and i < len(tasks_to_run) - 1:
            print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
