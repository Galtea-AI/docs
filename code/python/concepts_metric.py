# @start creating_custom_metrics_via_partial
judge_prompt = """
**Evaluation Criteria:**
Check if the ACTUAL_OUTPUT is good by comparing it to what was expected. Focus on:
1. Factual accuracy and correctness
2. Completeness of the ACTUAL_OUTPUT, regarding the user INPUT
3. Appropriate use of provided CONTEXT information to answer the user INPUT
4. Overall helpfulness and relevance to the user INPUT

**Rubric:**
Score 1 (Good): The ACTUAL_OUTPUT is accurate, complete, uses information properly, and truly helps the user.
Score 0 (Bad): The ACTUAL_OUTPUT has major errors, missing parts, ignores important info, or doesn't help the user.
"""
# @end creating_custom_metrics_via_partial
# @start creating_custom_metrics_via_full_prompt

judge_prompt = """
You are an expert evaluator. Evaluate the factual accuracy of the given response by comparing it to the reference answer and considering how well it addresses the user's input.

**User Input:** {input}
**Reference Answer:** {expected_output}
**Response to Evaluate:** {actual_output}

Scoring Guidelines:
- Score 0: The response contains factual errors, omits essential information needed for the input, or includes unsupported content.
- Score 0.5: The response is partially accurate. It is generally relevant but includes minor inaccuracies, missing key details, or some unsupported claims.
- Score 1: The response fully aligns with the reference answer with no errors, omissions, or unsupported additions.
"""
# @end creating_custom_metrics_via_full_prompt
# @start creating_custom_metrics_via_full_prompt_1

judge_prompt = """
Evaluate the following conversation for consistency. The agent should not contradict itself across the conversation.

**Conversation History:**
{conversation_turns}

**Evaluation Criteria:**
- Does the agent's final response contradict any of its previous statements?
- Are the agent's responses logically consistent throughout the conversation?

**Scoring Guidelines:**
- Score 1: The agent is fully consistent with no contradictions across all turns.
- Score 0.5: The agent has minor inconsistencies that don't significantly impact the conversation quality.
- Score 0: The agent clearly contradicts itself or provides conflicting information.
"""
# @end creating_custom_metrics_via_full_prompt_1
