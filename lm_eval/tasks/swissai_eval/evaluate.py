TEST_MODEL_EN = "sshleifer/tiny-gpt2"
TEST_MODEL_ES = "flax-community/gpt-2-spanish"

FACTUAL_AGNOSTIC_KNOWLEDGE = [
    "mmlu",
    "global_mmlu_swiss",
    "global_mmlu_europe",
    "global_mmlu",
    "global_mmlu_no_europe",
]

from lm_eval import evaluator


def eval_task(task, model=TEST_MODEL_EN):
    return evaluator.simple_evaluate(
        model="huggingface",
        model_args={"pretrained": model},
        tasks=[task],
        num_fewshot=0,
        batch_size=1,
        device="cuda:0",
        limit=1,
        verbosity="DEBUG",
        write_out=True,
        log_samples=True,
    )


if __name__ == "__main__":
    task = "global_mmlu_full_es"
    task_result = eval_task(task)
    print(task_result)
