# SwissAI Evaluation Tools

This directory contains tools for aggregating evaluation results by language groups.

## aggregate_by_language.py

A generic script for aggregating evaluation results across language groups/regions using configurable task definitions.

### Usage

```bash
python3 aggregate_by_language.py
```

The script automatically:
1. Loads task configurations from `config.json`
2. Processes each configured task that has available result files
3. Aggregates scores by subject categories for each language group
4. Generates comprehensive aggregated results

### Configuration

All settings are defined in `config.json` with two main sections:

```json
{
  "language_groups": {
    "group_name": ["lang1", "lang2", "lang3"]
  },
  "tasks": {
    "task_name": {
      "task_name_pattern": "{task}_{language}_{subject}",
      "overall_task_pattern": "{task}_{language}",
      "subjects": ["subject1", "subject2", "subject3"],
      "score_metric": "metric_name",
      "input_filename_pattern": "{task}_{language}.json"
    }
  }
}
```

#### Configuration Parameters:

**Language Groups:**
- **`language_groups`**: Define custom language groupings for aggregation

**Task Settings:**
- **`task_name_pattern`**: Pattern for subject-specific task names in results
- **`overall_task_pattern`**: Pattern for overall task names  
- **`subjects`**: List of subject categories to aggregate
- **`score_metric`**: Metric name to extract (e.g., "acc,none", "bleu", "exact_match")
- **`input_filename_pattern`**: Expected filename pattern for input files

#### Pre-configured Tasks:

- **`global_mmlu_full`**: MMLU evaluation with accuracy scores
- **`hellaswag_multilingual`**: HellaSwag evaluation with accuracy scores

### Adding New Tasks

1. Add a new configuration block to `config.json`
2. Ensure result files follow the expected naming pattern
3. Run the script - it will automatically process all configured tasks

### Output Structure

For each processed task and language group, the script generates:

- **Aggregated file**: `{task_name}_{group_name}.json` containing:
  - `aggregated_results`: Calculated average scores by subject
  - `languages`: List of languages included in aggregation
  - `results`: All individual task results from source languages  
  - `groups`: All group-level results from source languages
  - `group_subtasks`: Hierarchical task organization
  - `config`: Model/evaluation configuration

### Language Groups

Language groups are fully configurable in `task_config.json`. Default groups include:

- **swiss**: German (de), French (fr), Italian (it)
- **europe**: 17 European languages
- **asia**: 15 Asian languages  
- **africa**: 10 African languages

To modify language groups, edit the `language_groups` section in the configuration file. You can:
- Add new language groups
- Modify existing groupings
- Add or remove languages from any group 