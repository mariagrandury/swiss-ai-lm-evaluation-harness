# Language Group Generator

This unified script generates language group YAML files for various evaluation tasks across different language regions.

## Usage

```bash
python3 lm_eval/tasks/global_mmlu/group_languages.py <task> [--groups <group1> <group2> ...]
```

### Arguments

- `task`: The task to generate groups for (required)
  - `global_mmlu`: Global MMLU benchmark with subject categories
  - `hellaswag`: Multilingual Hellaswag benchmark

- `--groups`: Language groups to generate (optional, default: all)
  - `swiss`: Swiss languages (de, fr, it, ro)
  - `europe`: European languages
  - `global`: All available languages

## Examples

### Generate all groups for Global MMLU
```bash
python3 lm_eval/tasks/global_mmlu/group_languages.py global_mmlu
```

### Generate only Swiss group for Hellaswag
```bash
python3 lm_eval/tasks/global_mmlu/group_languages.py hellaswag --groups swiss
```

### Generate multiple specific groups
```bash
python3 lm_eval/tasks/global_mmlu/group_languages.py global_mmlu --groups swiss europe
```

## Supported Tasks

### Global MMLU (`global_mmlu`)
- **Has subjects**: Yes (stem, humanities, social_sciences, other)
- **Output location**: `lm_eval/tasks/global_mmlu/full/{group}/`
- **Files generated**: 
  - Main group file: `global_mmlu_full_{group}.yaml`
  - Subject files: `global_mmlu_full_{group}_{subject}.yaml`
- **Languages**: 42 available languages
- **Task pattern**: `global_mmlu_full_{lang}_{subject}`

### Hellaswag (`hellaswag`)
- **Has subjects**: No
- **Output location**: `lm_eval/tasks/hellaswag_groups/`
- **Files generated**: `hellaswag_{group}.yaml`
- **Languages**: 30 available languages
- **Task pattern**: `hellaswag_{lang}`

## Language Groups

### Swiss Group
- **Languages**: German (de), French (fr), Italian (it), Romanian (ro)
- **Purpose**: Swiss national languages evaluation

### Europe Group  
- **Languages**: 17+ European languages including Catalan, Danish, German, Spanish, Basque, French, Croatian, Hungarian, Italian, Dutch, Portuguese, Romanian, Russian, Slovak, Serbian, Swedish, Ukrainian
- **Purpose**: European multilingual evaluation

### Global Group
- **Languages**: All available languages from European, Asian, and African regions
- **Purpose**: Comprehensive multilingual evaluation

## How It Works

1. **Language Detection**: Automatically detects which languages are available for each task
2. **Subject Detection**: Automatically determines if a task has subjects (like Global MMLU) or not (like Hellaswag)
3. **Smart Grouping**: Creates appropriate file structures based on task requirements
4. **Skipping**: Automatically skips language groups that have no available languages for a task
5. **Standardized Metrics**: Uses consistent metrics across all tasks and groups

## Metrics

All generated group files use the same standardized metrics format:

```yaml
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
```

## Adding New Tasks

To add support for a new task, add an entry to `TASK_CONFIGS` in the script:

```python
"new_task": {
    "base_dir": "path/to/task/files",
    "output_dir": "path/to/output",
    "task_pattern": "task_{lang}",
    "group_pattern": "task_{group}",
    "has_subjects": False,  # or True if it has subjects
}
```

## Generated File Examples

### Hellaswag Swiss Group
```yaml
group: hellaswag_swiss
task:
  - hellaswag_de
  - hellaswag_fr
  - hellaswag_it
  - hellaswag_ro
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
```

### Global MMLU Swiss Group (with subjects)
```yaml
group: global_mmlu_full_swiss
task:
  - global_mmlu_full_swiss_stem
  - global_mmlu_full_swiss_humanities
  - global_mmlu_full_swiss_social_sciences
  - global_mmlu_full_swiss_other
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
``` 