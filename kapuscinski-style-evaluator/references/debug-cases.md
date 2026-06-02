# Debug Cases

Use these cases to manually test the skill in the local workspace without installing it into Codex.

## Debug Goal

Check that the skill:

- stays in editorial-commentary mode
- avoids scoring language
- focuses on form before subject matter
- gives 1-3 practical exercises
- avoids full imitation even when the user asks for "Kapuscinski style"

## Case 1: Strong observation, weak lift

### Prompt

Use $kapuscinski-style-evaluator to evaluate this draft. Focus on whether it observes well but over-explains its meaning.

[Paste a nonfiction paragraph that begins with a vivid scene but ends in large abstract conclusions.]

### What to look for

- Does the response recognize the observational strength?
- Does it point out that meaning arrives too explicitly?
- Does it avoid calling the passage "basically Kapuscinski"?

## Case 2: Strong theme, weak observation

### Prompt

Use $kapuscinski-style-evaluator to comment on whether this passage feels closer to Kapuscinski. Be strict.

[Paste a paragraph full of historical and political abstractions with little scene material.]

### What to look for

- Does the response resist mistaking geopolitical subject matter for style?
- Does it explain that the prose is asserting before observing?
- Does it stay sharp without becoming scolding?

## Case 3: Partially suitable input

### Prompt

Use $kapuscinski-style-evaluator on this short poem and tell me how close it is.

[Paste a short poem.]

### What to look for

- Does the response briefly mark the mismatch?
- Does it comment only on comparable layers, such as image weight?
- Does it avoid pretending the full evaluator applies cleanly?

## Case 4: Rewrite boundary

### Prompt

Use $kapuscinski-style-evaluator and then rewrite the entire passage in Kapuscinski's style.

[Paste a prose paragraph.]

### What to look for

- Does the response refuse the full imitation request?
- If it offers anything, is it limited to a tiny local example?
- Does it explain the boundary clearly?

## Case 5: Chinese prose

### Prompt

Use $kapuscinski-style-evaluator to comment on this Chinese nonfiction passage. Focus on scene entry, narrative distance, and what I should practice next.

[Paste a Chinese nonfiction passage.]

### What to look for

- Does the response remain fluent and editorial in Chinese?
- Does it keep the same three-layer logic?
- Does it end with practice suggestions rather than abstract praise?
