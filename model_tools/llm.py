from google import genai
from google.genai import types

from config import LLM_MODEL, LLM_INPUT_TOKEN_PRICE, LLM_OUTPUT_TOKEN_PRICE

def llm(client: genai.Client, input_content: str, verbose: bool = False, prompt: str = "") -> str:
    try:
        if verbose:
            print(f"Setting LLM client with model and getting response ({LLM_MODEL})")

        response = client.models.generate_content(
            model=LLM_MODEL, 
            contents=input_content,
            config=types.GenerateContentConfig(
                system_instruction=prompt
            ),
        )

        if verbose:
            print("\n---Response---")
            print(response.text)
            print("---------\n")
            
            tokens_input = response.usage_metadata.prompt_token_count
            tokens_output = response.usage_metadata.candidates_token_count
            tokens_input_cost = tokens_input / 1_000_000 * LLM_INPUT_TOKEN_PRICE
            tokens_output_cost = tokens_output / 1_000_000 * LLM_OUTPUT_TOKEN_PRICE

            print("\n===COST===")
            print(f"Prompt tokens: {tokens_input} --- Cost: {tokens_input_cost:.8f} $")
            print(f"Response tokens: {tokens_output} --- Cost: {tokens_output_cost:.8f} $")
            print("===$$$===\n")

    except Exception as e:
        print(f"\nError: {e}")

    return response.text