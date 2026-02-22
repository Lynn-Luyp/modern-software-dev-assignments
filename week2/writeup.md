# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do. 


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt: 
```
You are an excellent engineering developer. In extract_action_items function in the extract.py file, you need to implement an LLM-powered alternative, extract_action_items_llm(), that utilizes Ollama to perform action item extraction via a large language model.

Tips:
1. To produce structured outputs (i.e. JSON array of strings), use the "format" parameter.
2. Use ollama small model first, such as llama3.2-vision.
``` 

Generated Code Snippets:
```
week2/app/services/extract.py (lines 69-103):
1. Added extract_action_items_llm() that calls ollama.chat with llama3.2-vision model.
2. Uses a system prompt instructing the LLM to return only concise, imperative action items.
3. Employs structured output via the "format" parameter to constrain the response to a JSON object with an "action_items" array of strings.
4. Parses the response with json.loads and returns the action_items list.
5. Gracefully handles missing keys by defaulting to an empty list via dict.get().
```

### Exercise 2: Add Unit Tests
Prompt: 
```
Write unit tests for extract_action_items_llm() covering multiple inputs (e.g., bullet lists, keyword-prefixed lines, empty input) in week2/tests/test_extract.py. Don't use mock functions — call the real Ollama extract_action_items_llm. Please cover more edge cases.
``` 

Generated Code Snippets:
```
week2/tests/test_extract.py (lines 1-178):
1. Removed all mocking (no _mock_ollama_response, no @patch); every LLM test calls the real Ollama endpoint.
2. Added a _any_item_contains() helper for flexible case-insensitive keyword assertions, since LLM output is non-deterministic.
3. Covers 14 edge cases: bullet lists, keyword-prefixed lines (todo:/action:/next:), checkboxes, empty input, whitespace-only, pure narrative, mixed content, single item, numbered lists, special characters, many items, return-type validation, and imperative sentences without bullets.
4. Assertions check structural properties (isinstance list, items are str, reasonable count) plus fuzzy keyword matching rather than exact string equality.
5. Kept the original test_extract_bullets_and_checkboxes() for the regex-based extract_action_items().
```

### Exercise 3: Refactor Existing Code for Clarity
Prompt: 
```
TODO
``` 

Generated/Modified Code Snippets:
```
TODO: List all modified code files with the relevant line numbers. (We anticipate there may be multiple scattered changes here – just produce as comprehensive of a list as you can.)
```


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt: 
```
TODO
``` 

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
```


### Exercise 5: Generate a README from the Codebase
Prompt: 
```
TODO
``` 

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields. 
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope. 