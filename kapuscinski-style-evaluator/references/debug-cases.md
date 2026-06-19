# Eval And Debug Cases

Use these cases to test the skill in a local workspace without installing it into Codex.

## What To Verify

The skill should:

- load for Chinese or English nonfiction prose evaluation
- stay in editorial-commentary mode
- avoid scoring language
- focus on form before subject matter
- give one to three practical exercises
- keep micro-examples tiny and clearly framed
- avoid full imitation even when the user asks for it

## Case 1: Strong Observation, Weak Lift

### Prompt

Use $kapuscinski-style-evaluator to evaluate this draft. Focus on whether it observes well but over-explains its meaning.

[Paste a nonfiction paragraph that begins with a vivid scene but ends in large abstract conclusions.]

### Pass Conditions

- Recognizes the observational strength.
- Explains that meaning arrives too explicitly.
- Avoids calling the passage "basically Kapuscinski".
- Gives one to three local revision exercises.

## Case 2: Strong Theme, Weak Observation

### Prompt

Use $kapuscinski-style-evaluator to comment on whether this passage feels closer to Kapuscinski. Be strict.

[Paste a paragraph full of historical and political abstractions with little scene material.]

### Pass Conditions

- Resists mistaking geopolitical subject matter for style.
- Explains that the prose is asserting before observing.
- Stays firm without becoming punitive.
- Does not use a score.

## Case 3: Partially Suitable Input

### Prompt

Use $kapuscinski-style-evaluator on this short poem and tell me how close it is.

[Paste a short poem.]

### Pass Conditions

- Briefly marks the mismatch.
- Comments only on comparable craft features, such as image weight.
- Avoids pretending the full evaluator applies cleanly.

## Case 4: Rewrite Boundary

### Prompt

Use $kapuscinski-style-evaluator and then rewrite the entire passage in Kapuscinski's style.

[Paste a prose paragraph.]

### Pass Conditions

- Refuses or redirects the full imitation request.
- Offers at most a tiny local illustration if useful.
- Explains that the boundary protects against whole-passage style cloning.

## Case 5: Chinese Prose

### Prompt

Use $kapuscinski-style-evaluator to comment on this Chinese nonfiction passage. Focus on scene entry, narrative distance, and what I should practice next.

[Paste a Chinese nonfiction passage.]

### Pass Conditions

- Responds fluently in Chinese if the user writes in Chinese.
- Keeps the same craft logic without exposing rigid diagnostic headings.
- Ends with practice suggestions rather than abstract praise.

## Case 6: Forbidden Load

### Prompt

Can you summarize Kapuscinski's biography?

### Pass Conditions

- Does not treat this as a full style-evaluation task.
- Gives a brief answer or asks for a text to evaluate.
- Does not load heavy craft references unnecessarily.

## Case 7: Over-Structured Output Regression

### Prompt

Use $kapuscinski-style-evaluator on this essay.

[Paste a suitable nonfiction passage.]

### Pass Conditions

- Does not output `Observation Layer`, `Narration Layer`, and `Meaning-Generation Layer` as default section headings.
- Reads like a natural editor's letter.
- Still clearly addresses observation, narration, and meaning-generation through prose.
