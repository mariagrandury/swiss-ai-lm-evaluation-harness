# Language Group Generator

This unified script generates language group YAML files for various evaluation tasks across different language regions. It supports 7 different tasks with automatic language detection and hierarchical group structures.

## Usage

```bash
python3 scripts/group_languages.py <task> [--groups <group1> <group2> ...]
```

### Arguments

- `task`: The task to generate groups for (required)
  - `global_mmlu`: Global MMLU benchmark with subject categories
  - `hellaswag`: Multilingual Hellaswag benchmark
  - `arc`: Multilingual ARC benchmark
  - `xwinograd`: Cross-lingual Winograd Schema Challenge
  - `xnli`: Cross-lingual Natural Language Inference
  - `xcopa`: Cross-lingual Choice of Plausible Alternatives
  - `include`: Include benchmark with full language names
  - `all`: Run all tasks

- `--groups`: Language groups to generate (optional, default: all)
  - `swiss`: Swiss languages (de, fr, it)
  - `europe`: European languages (25+ languages)
  - `africa`: African languages (10 languages)
  - `asia`: Asian languages (20+ languages)
  - `global`: Hierarchical group referencing regional groups

## Examples

### Generate all groups for Global MMLU
```bash
python3 scripts/group_languages.py global_mmlu
```

### Generate only Swiss group for Hellaswag
```bash
python3 scripts/group_languages.py hellaswag --groups swiss
```

### Generate multiple specific groups
```bash
python3 scripts/group_languages.py global_mmlu --groups swiss europe asia
```

### Generate all tasks with all groups
```bash
python3 scripts/group_languages.py all
```

### Generate Europe group for all tasks
```bash
python3 scripts/group_languages.py all --groups europe
```

## Configuration

The script uses `scripts/group_config.yaml` to define:

- **Language Groups**: Common language groups used across all tasks
- **Task Configurations**: Task-specific settings including subjects and patterns
- **Language Mapping**: ISO codes to full language names for include task
- **Output Paths**: Where generated files should be placed

### Configuration Structure

```yaml
language_groups:
  swiss: [de, fr, it]
  europe: [ca, cs, da, de, el, en, es, eu, fr, hr, hu, it, lt, nl, pl, pt, ro, ru, sk, sr, sv, tr, uk]
  africa: [am, ar, ha, ig, mg, ny, sn, so, sw, yo]
  asia: [ar, bn, fa, fil, gu, he, hi, hy, id, ja, kn, ko, ky, ml, mr, ms, ne, si, ta, te, vi, zh]

language_mapping:
  de: "German"
  fr: "French"
  it: "Italian"
  # ... more mappings

tasks:
  task_name:
    base_dir: "path/to/source/files"
    output_dir: "path/to/output"
    task_pattern: "task_{lang}"
    group_pattern: "task_{group}"
    has_subjects: true/false
    subjects: [list of subjects if applicable]
    use_full_language_names: true/false
    file_pattern: "custom_pattern.yaml"  # optional
```

## Supported Tasks

### Global MMLU (`global_mmlu`)
- **Has subjects**: Yes (stem, humanities, social_sciences, other)
- **Output location**: `lm_eval/tasks/global_mmlu/full/{group}/`
- **Files generated per group**: 
  - Main group file: `global_mmlu_full_{group}.yaml`
  - Subject files: `global_mmlu_full_{group}_{subject}.yaml`
- **Languages**: 42 available languages
- **Task pattern**: `global_mmlu_full_{lang}_{subject}`

### Hellaswag (`hellaswag`)
- **Has subjects**: No
- **Output location**: `lm_eval/tasks/okapi/hellaswag_multilingual/`
- **Files generated**: `hellaswag_{group}.yaml`
- **Languages**: 30 available languages
- **Task pattern**: `hellaswag_{lang}`

### ARC (`arc`)
- **Has subjects**: No
- **Output location**: `lm_eval/tasks/okapi/arc_multilingual/`
- **Files generated**: `arc_{group}.yaml`
- **Languages**: 31 available languages
- **Task pattern**: `arc_{lang}`

### XWinograd (`xwinograd`)
- **Has subjects**: No
- **Output location**: `lm_eval/tasks/xwinograd/`
- **Files generated**: `xwinograd_{group}.yaml`
- **Languages**: 5 available languages (en, fr, pt, ru, zh)
- **Task pattern**: `xwinograd_{lang}`

### XNLI (`xnli`)
- **Has subjects**: No
- **Output location**: `lm_eval/tasks/xnli/`
- **Files generated**: `xnli_{group}.yaml`
- **Languages**: 12 available languages
- **Task pattern**: `xnli_{lang}`

### XCOPA (`xcopa`)
- **Has subjects**: No
- **Output location**: `lm_eval/tasks/xcopa/`
- **Files generated**: `xcopa_{group}.yaml`
- **Languages**: 7 available languages
- **Task pattern**: `xcopa_{lang}`
- **Special**: Uses `default_{lang}.yaml` file pattern but `xcopa_{lang}` task names

### Include (`include`)
- **Has subjects**: Yes (11 subjects including applied_science, arts_humanities, business_commerce, etc.)
- **Output location**: `lm_eval/tasks/include/default/{group}/`
- **Files generated per group**:
  - Main group file: `include_base_44_{group}.yaml`
  - Subject files: `include_base_44_{group}_{subject}.yaml`
- **Languages**: 32 available languages
- **Task pattern**: `include_base_44_{language_name}_{subject}`
- **Special**: Uses full language names (e.g., "German") instead of ISO codes

## Language Groups

### Swiss Group (3 languages)
- **Languages**: German (de), French (fr), Italian (it)
- **Purpose**: Swiss national languages evaluation

### Europe Group (25 languages)
- **Languages**: Catalan, Czech, Danish, German, Greek, English, Spanish, Basque, French, Croatian, Hungarian, Italian, Lithuanian, Dutch, Polish, Portuguese, Romanian, Russian, Slovak, Serbian, Swedish, Turkish, Ukrainian
- **Purpose**: European multilingual evaluation

### Africa Group (10 languages)
- **Languages**: Amharic, Arabic, Hausa, Igbo, Malagasy, Chichewa, Shona, Somali, Swahili, Yoruba
- **Purpose**: African multilingual evaluation

### Asia Group (22 languages)
- **Languages**: Arabic, Bengali, Persian, Filipino, Gujarati, Hebrew, Hindi, Armenian, Indonesian, Japanese, Kannada, Korean, Kyrgyz, Malayalam, Marathi, Malay, Nepali, Sinhala, Tamil, Telugu, Vietnamese, Chinese
- **Purpose**: Asian multilingual evaluation

### Global Group (Hierarchical)
- **Structure**: References regional groups instead of individual languages
- **Composition**: `europe`, `asia`, `africa` (only includes regions with available languages for each task)
- **Purpose**: Comprehensive multilingual evaluation through regional groupings

## Language Coverage and Warnings

The script includes a language coverage system that:

1. **Detects all available languages** for each task automatically
2. **Compares with defined language groups** to check coverage
3. **Shows warnings** for available languages not included in any group
4. **Provides guidance** to update configuration if needed

Example warning output:
```
⚠️  WARNING: Available languages not in any group: xx, yy, zz
   Consider adding these languages to appropriate language groups in group_config.yaml
```

## How It Works

1. **Configuration Loading**: Loads language groups, task configs, and language mappings from YAML file
2. **Language Detection**: Automatically detects which languages are available for each task by checking file/directory existence
3. **Subject Detection**: Uses task-specific subjects from configuration or detects dynamically
4. **Smart Grouping**: Creates appropriate file structures based on task requirements
5. **Missing Language Filtering**: Only includes languages that actually exist for each task
6. **Hierarchical Global Groups**: Creates global groups that reference regional groups instead of individual languages
7. **Comprehensive Coverage**: Warns about any available languages not included in language groups

## Key Features

### Automatic Language Detection
- Scans task directories to find available languages
- Handles different file patterns (e.g., `default_{lang}.yaml` for xcopa)
- Supports both directory-based (subjects) and file-based (no subjects) tasks

### Hierarchical Global Structure
- Global groups reference regional groups instead of listing all individual languages
- Only includes regional groups that have available languages for each task
- Cleaner evaluation structure with better organization

### Smart Subject Handling
- Automatically detects which subjects are available for each language
- Only creates subject files if underlying language files exist
- Skips unavailable combinations gracefully

### Full Language Name Support
- Maps ISO language codes to full names for tasks that require them
- Handles spaces and special characters in language names
- Supports mixed ISO/full name patterns

## Generated File Examples

### Simple Task (Hellaswag Swiss)
```yaml
group: hellaswag_swiss
task:
  - hellaswag_de
  - hellaswag_fr
  - hellaswag_it
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
```

### Task with Subjects (Global MMLU Swiss)
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
```

### Hierarchical Global Group (XNLI Global)
```yaml
group: xnli_global
task:
  - xnli_europe
  - xnli_asia
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
```

## Adding New Tasks

To add support for a new task, add an entry to the `tasks` section in `scripts/group_config.yaml`:

```yaml
new_task:
  base_dir: "path/to/task/files"
  output_dir: "path/to/output"
  task_pattern: "task_{lang}"
  group_pattern: "task_{group}"
  has_subjects: false  # or true if it has subjects
  subjects: []  # list of subjects if has_subjects is true
  use_full_language_names: false  # true if task uses full language names
  file_pattern: "custom_{lang}.yaml"  # optional, if different from task_pattern.yaml
```

## Performance and Statistics

When running `python3 scripts/group_languages.py all`, the script:

- **Processes 7 tasks** across 5 language groups
- **Generates 70+ group files** depending on language availability
- **Covers 54 defined languages** across all regional groups
- **Achieves 100% coverage** with no missing language warnings
- **Creates hierarchical structures** for better organization
- **Runs in under 5 seconds** for complete generation

## Error Handling

The script includes robust error handling:

- **Missing directories**: Skips languages without available files
- **Missing subjects**: Only creates subject files that exist
- **Empty groups**: Skips language groups with no available languages
- **Missing regional groups**: Global groups only reference existing regional groups
- **Invalid configurations**: Clear error messages for configuration issues

## Troubleshooting

### No files generated for a language group
- Check that the language group languages are available in the task directory
- Verify the `base_dir` path in the configuration
- Ensure file patterns match the actual file names

### Missing subjects
- Check that subject files exist for the specified languages
- Verify the `subjects` list in the task configuration
- Ensure subject file naming matches the expected pattern

### Global group is empty
- Ensure at least one regional group (europe, asia, africa) has available languages
- Check that regional group files were created successfully
- Verify that the global group is run after regional groups 