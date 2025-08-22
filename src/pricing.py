from .config import PRICE_INPUT_PER_1K, PRICE_OUTPUT_PER_1K

def estimate_cost(total_input_tokens: int, total_output_tokens: int) -> float:
    """Estimate cost using simple per-1k-token pricing.
    Note: actual prices change over time. Adjust via .env variables.
    """
    cost_in = (total_input_tokens / 1000.0) * PRICE_INPUT_PER_1K
    cost_out = (total_output_tokens / 1000.0) * PRICE_OUTPUT_PER_1K
    return round(cost_in + cost_out, 6)
