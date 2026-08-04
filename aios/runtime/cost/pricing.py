from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class ModelPricing:
    prompt_per_million: float
    completion_per_million: float


PRICING = {
    "deepseek-chat": ModelPricing(0.27, 1.10),
    "qwen": ModelPricing(0.30, 1.20),
    "groq": ModelPricing(0.00, 0.00),
    "cerebras": ModelPricing(0.00, 0.00),
    "anthropic": ModelPricing(3.00, 15.00),
}


def calculate_cost(model, prompt_tokens, completion_tokens):
    pricing = PRICING.get(model)

    if pricing is None:
        return 0.0, 0.0, 0.0

    prompt = prompt_tokens / 1_000_000 * pricing.prompt_per_million
    completion = completion_tokens / 1_000_000 * pricing.completion_per_million

    return prompt, completion, prompt + completion
