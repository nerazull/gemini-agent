import os
from dotenv import load_dotenv
from google import genai
import argparse
from google.genai import types
from prompts import system_prompt
from call_function import available_functions, call_function
import sys


load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if api_key is None:
    raise RuntimeError("Environment variable not found.")

client = genai.Client(api_key=api_key)

parser = argparse.ArgumentParser(description="Chatbot")
parser.add_argument("user_prompt", type=str, help="User prompt")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()

messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

for _ in range(20):
    response = client.models.generate_content(
        model='gemini-2.5-flash', contents=messages, config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt)
    )

    if response.candidates:
        for candidate in response.candidates:
            messages.append(candidate)

    if response.usage_metadata is None:
        raise RuntimeError("No usage metadata to display.")

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        #print(response.text)

    function_call_result = []

    if response.function_calls:
        for func_call in response.function_calls:
            function_call_result.append(call_function(func_call))
            if args.verbose:
                print(f'-> {function_call_result[-1].parts[0].function_response.response["result"]}')
    else:
        print(response.text)
        break

    for result in function_call_result:
        if not result.parts:
            raise Exception("Function call result empty list")

    for obj in function_call_result:
        for part in obj.parts:
            if part.function_response is None:
                raise Exception("Part function response is None")
        
    for obj in function_call_result:
        for parts in obj.parts:
            if parts.function_response.response is None:
                raise Exception("Part function response.response is None")
        
    function_results = []

    for obj in function_call_result:
        function_results.append(obj.parts[0])

    messages.append(types.Content(role="user", parts=function_results))
    
else:
    print("Agent did not produce a final response within 20 iterations.", file=sys.stderr)
    sys.exit(1)
