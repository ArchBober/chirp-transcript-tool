from google import genai
from google.genai import types

from typing import List, Tuple, Dict

from config import LLM_MODEL, LLM_INPUT_TOKEN_PRICE, LLM_OUTPUT_TOKEN_PRICE

def llm(client: genai.Client, input_content: Dict[str, str], cost_single: bool = False, verbose: bool = False, prompt: str = "") -> Dict[str, str]:
    try:
        responses = {}
        if verbose:
            tokens_input_overall = 0.
            tokens_output_overall = 0.
            print(f"Setting LLM client for transcript tuning with model and getting response ({LLM_MODEL})")

        for key, val in input_content.items():
            response = client.models.generate_content(
                model=LLM_MODEL,
                contents=val,
                config=types.GenerateContentConfig(
                    system_instruction=prompt
                ),
            )

            if verbose:
                print("Got response - adding to list of responses")

            responses[key] = response.text

            if verbose:
                print("\n---Response---")
                print(response.text)
                print("---------\n")
                
                tokens_input = response.usage_metadata.prompt_token_count
                tokens_output = response.usage_metadata.candidates_token_count

                tokens_input_cost = response.usage_metadata.prompt_token_count / 1_000_000 * LLM_INPUT_TOKEN_PRICE
                tokens_output_cost = response.usage_metadata.candidates_token_count / 1_000_000 * LLM_OUTPUT_TOKEN_PRICE

                tokens_input_overall += tokens_input
                tokens_output_overall += tokens_output
                if cost_single:
                    print("\n===COST===")
                    print(f"Prompt tokens: {tokens_input} --- Cost: {tokens_input_cost:.8f} $")
                    print(f"Response tokens: {tokens_output} --- Cost: {tokens_output_cost:.8f} $")
                    print("===$$$===\n")

        if verbose:
            tokens_input_cost_overall, tokens_output_cost_overall = _calculate_price(tokens_input_overall, tokens_output_overall)
            tokens_overall = tokens_input_overall+tokens_output_overall
            tokens_cost_overall = tokens_input_cost_overall+tokens_output_cost_overall
            
            print("\n===OVERALL COST===")
            print(f"Prompt tokens: {tokens_input_overall} --- Cost: {tokens_input_cost_overall:.8f} $")
            print(f"Response tokens: {tokens_output_overall} --- Cost: {tokens_output_cost_overall:.8f} $")
            print(f"Summary: {tokens_overall} tokens --- {tokens_cost_overall:.8f} $")
            print("===$$$===\n")

    except Exception as e:
        print(f"\nError: {e}")

    return responses


def _calculate_price(tokens_input: int, tokens_output: int) -> Tuple[int, int]:
    tokens_input_cost = tokens_input / 1_000_000 * LLM_INPUT_TOKEN_PRICE
    tokens_output_cost = tokens_output / 1_000_000 * LLM_OUTPUT_TOKEN_PRICE

    return tokens_input_cost, tokens_output_cost

