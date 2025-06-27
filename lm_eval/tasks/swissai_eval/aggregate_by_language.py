#!/usr/bin/env python3
"""Generic aggregation of evaluation results by language groups."""

import json
import statistics
from pathlib import Path
from typing import Dict, List

CONFIG_FILE = "lm_eval/tasks/swissai_eval/config.json"


def load_config() -> tuple:
    """Load configuration from JSON file."""
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    return config["language_groups"], config["tasks"]


def load_results(file_path: Path) -> Dict:
    """Load evaluation results from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)


def find_task_language_files(results_dir: Path, task_name: str, task_config: Dict, language_groups: Dict) -> Dict[str, Path]:
    """Find all result files for a specific task, grouped by language."""
    language_files = {}
    
    # Find files matching the pattern from task config
    all_languages = {lang for group_langs in language_groups.values() for lang in group_langs}
    input_pattern = task_config["input_filename_pattern"]
    
    for lang in all_languages:
        expected_filename = input_pattern.format(task=task_name, language=lang)
        file_path = results_dir / expected_filename
        if file_path.exists():
            language_files[lang] = file_path
    
    return language_files


def get_subject_scores(results: Dict, task_name: str, language: str, task_config: Dict) -> Dict[str, float]:
    """Extract subject scores from results using configured task patterns."""
    scores = {}
    subjects = task_config["subjects"]
    task_pattern_template = task_config["task_name_pattern"]
    score_metric = task_config["score_metric"]
    
    for subject in subjects:
        task_pattern = task_pattern_template.format(task=task_name, language=language, subject=subject)
        
        # Look in both results and groups sections
        for section in ["results", "groups"]:
            if task_pattern in results.get(section, {}):
                score = results[section][task_pattern].get(score_metric)
                if score != "N/A" and score is not None:
                    scores[subject] = score
                    break
    
    return scores


def get_overall_score(results: Dict, task_name: str, language: str, task_config: Dict) -> float:
    """Extract overall score for a language if available."""
    overall_pattern_template = task_config["overall_task_pattern"]
    score_metric = task_config["score_metric"]
    overall_task_pattern = overall_pattern_template.format(task=task_name, language=language)
    
    for section in ["results", "groups"]:
        if overall_task_pattern in results.get(section, {}):
            score = results[section][overall_task_pattern].get(score_metric)
            if score != "N/A" and score is not None:
                return score
    return None


def extract_and_verify_configs(results_by_lang: Dict[str, Dict]) -> Dict:
    """Extract and verify config information is consistent across evaluation results."""
    configs = []
    
    for lang, results in results_by_lang.items():
        if "config" in results and results["config"]:
            config = results["config"].copy()
            configs.append(config)

    if not configs:
        return {}
    
    base_config = configs[0]
    for config in configs[1:]:
        if config != base_config:
            print(f"Warning: Config differs between {base_config} and {config}")
            # Print key differences for debugging
            for key in set(base_config.keys()) | set(config.keys()):
                if base_config.get(key) != config.get(key):
                    print(f"  {key}: {base_config.get(key)} vs {config.get(key)}")
    
    return base_config


def merge_sections(results_by_lang: Dict[str, Dict], section_name: str, available_langs: List[str]) -> Dict:
    """Merge a specific section from all language results."""
    merged = {}
    
    for lang in available_langs:
        results = results_by_lang[lang]
        if section_name in results:
            merged.update(results[section_name])
    
    return merged


def calculate_group_scores(results_by_lang: Dict[str, Dict], task_name: str, available_langs: List[str], task_config: Dict) -> Dict[str, float]:
    """Calculate aggregated scores for a language group."""
    group_scores = {}
    subjects = task_config["subjects"]
    
    # Aggregate by subject
    for subject in subjects:
        subject_scores = []
        for lang in available_langs:
            lang_scores = get_subject_scores(results_by_lang[lang], task_name, lang, task_config)
            if subject in lang_scores:
                subject_scores.append(lang_scores[subject])
        
        if subject_scores:
            group_scores[subject] = statistics.mean(subject_scores)
    
    # Calculate overall score
    overall_scores = []
    for lang in available_langs:
        overall_score = get_overall_score(results_by_lang[lang], task_name, lang, task_config)
        if overall_score is not None:
            overall_scores.append(overall_score)
    
    if overall_scores:
        group_scores["overall"] = statistics.mean(overall_scores)
    elif group_scores:
        # Fallback: calculate overall as mean of subject scores
        group_scores["overall"] = statistics.mean(group_scores.values())
    
    return group_scores


def create_aggregated_entries(task_name: str, group_name: str, group_scores: Dict[str, float], task_config: Dict) -> tuple:
    """Create new aggregated entries for results/groups sections and group_subtasks."""
    group_task_entries = {}
    group_subtask_list = []
    subjects = task_config["subjects"]
    score_metric = task_config["score_metric"]
    
    # Create entries for each subject
    for subject in subjects:
        if subject in group_scores:
            task_subject_name = f"{task_name}_{group_name}_{subject}"
            entry = {
                score_metric: group_scores[subject],
                f"{score_metric.split(',')[0]}_stderr,none": "N/A",
                "alias": f" - {task_subject_name}"
            }
            group_task_entries[task_subject_name] = entry
            group_subtask_list.append(task_subject_name)
    
    # Create overall entry
    group_subtasks_entry = {}
    if "overall" in group_scores:
        overall_task_name = f"{task_name}_{group_name}"
        overall_entry = {
            score_metric: group_scores["overall"],
            f"{score_metric.split(',')[0]}_stderr,none": "N/A", 
            "alias": overall_task_name
        }
        group_task_entries[overall_task_name] = overall_entry
        group_subtasks_entry[overall_task_name] = group_subtask_list
    
    return group_task_entries, group_subtasks_entry


def aggregate_group(results_by_lang: Dict[str, Dict], task_name: str, group_name: str, languages: List[str], task_config: Dict) -> Dict:
    """Aggregate results for a language group."""
    available_langs = [lang for lang in languages if lang in results_by_lang]
    if not available_langs:
        return {}
    
    print(f"Aggregating {task_name} - {group_name}: {available_langs}")
    
    # Calculate aggregated scores
    group_scores = calculate_group_scores(results_by_lang, task_name, available_langs, task_config)
    
    # Extract and verify config information
    config_info = extract_and_verify_configs(results_by_lang)
    
    # Merge all sections from original results
    merged_results = merge_sections(results_by_lang, "results", available_langs)
    merged_groups = merge_sections(results_by_lang, "groups", available_langs)  
    merged_group_subtasks = merge_sections(results_by_lang, "group_subtasks", available_langs)
    
    # Create and add aggregated entries
    group_task_entries, group_subtasks_entry = create_aggregated_entries(task_name, group_name, group_scores, task_config)
    
    merged_results.update(group_task_entries)
    merged_groups.update(group_task_entries)
    merged_group_subtasks.update(group_subtasks_entry)
    
    return {
        "aggregated_results": group_scores,
        "languages": available_langs,
        "results": merged_results,
        "groups": merged_groups,
        "group_subtasks": merged_group_subtasks,
        "config": config_info
    }


def main():
    results_dir = Path("lm_eval/tasks/swissai_eval/results")
    
    # Load configuration
    language_groups, task_configs = load_config()
    
    # Process each task
    for task_name, task_config in task_configs.items():
        # Find all language files for this task
        language_files = find_task_language_files(results_dir, task_name, task_config, language_groups)
        
        # Load results for all languages
        results_by_language = {}
        for lang, file_path in language_files.items():
            results_by_language[lang] = load_results(file_path)
        
        # Generate aggregations for each group
        for group_name, languages in language_groups.items():
            aggregated = aggregate_group(results_by_language, task_name, group_name, languages, task_config)
            
            if aggregated and aggregated["aggregated_results"]:
                # Save aggregated results: <task_name>_<language_group>.json
                output_file = results_dir / f"{task_name}_{group_name}.json"
                with open(output_file, 'w') as f:
                    json.dump(aggregated, f, indent=2)

if __name__ == "__main__":
    main()
