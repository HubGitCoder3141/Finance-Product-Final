"""Strict integration boundary: no SDK, HTTP client, key lookup, or live mode."""

from dataclasses import dataclass
import re
from typing import Protocol

LABEL = "Demo coach — live Claude integration is not connected."
CLARIFICATIONS = {
    "expected_value": "Expected value is a probability-weighted average. Multiply each possible value by its probability, then add. The average need not be one possible outcome. Which outcome has the most weight?",
    "independence": "Events are independent when knowing one occurred leaves the other's probability unchanged. An independent coin has no memory of previous flips. What physical mechanism could change the next flip?",
    "conditional_probability": "A condition restricts the group you count. For P(A given B), count only B cases, then find the fraction also in A. Reversing A and B usually changes the denominator. Which group is given?",
    "base_rates": "Start with how common the target group is, then count clues within both groups. A clue can come from either group. How many clue cases came from the larger group?",
}
HINTS = {
    "expected_value": "List the outcomes and their probabilities. Multiply each pair, then add the contributions. Before calculating, check that the probabilities total one. What is your first weighted contribution?",
    "independence": "Compare the probability before and after learning about the first event. For a draw, ask whether the object was replaced. Which counts change?",
    "conditional_probability": "Name the group after the word 'given'. Use its size as the denominator. Now identify the overlap. Which people or objects remain in your sample space?",
    "base_rates": "Start with a countable population. Split it using prevalence, apply the clue rate to each group, then compare target clues with all clues. Which two groups contribute clues?",
}


@dataclass(frozen=True)
class Reply:
    text: str
    route: str
    provider_mode: str = "placeholder"


class CoachService(Protocol):
    """A future provider must implement this interface behind a separate reviewed change."""
    def respond(self, message: str, module: str, quiz_context: bool = False) -> Reply: ...


class PlaceholderCoach:
    def respond(self, message: str, module: str, quiz_context: bool = False) -> Reply:
        if not isinstance(message, str) or not message.strip() or len(message) > 1000:
            raise ValueError("Enter a message of 1–1,000 characters.")
        if module not in CLARIFICATIONS:
            raise ValueError("Choose a probability module first.")
        text = message.casefold()
        if re.search(r"\b(bet|bets|betting|gambl\w*|casino|poker|roulette|wager\w*|sportsbook)\b", text):
            return Reply("Scripted demo: I can't advise on real bets or games played for money. We can study the same probability idea with classroom objects. What could a marble draw help you explore?", "betting_redirect")
        if re.search(r"\b(answer|solve|homework|assessment|exam|calculate|compute)\b", text):
            return Reply("Scripted demo: I won't solve a submitted assessment or homework problem for you. Let's work on the method: " + HINTS[module], "answer_redirect")
        if quiz_context or re.search(r"\b(hint|help|stuck)\b", text):
            return Reply("Scripted demo hint: " + HINTS[module], "hint")
        if re.search(r"\b(why|explain|mean|definition|expected|average|independent|independence|coin|due|conditional|given|base|prevalence|clue)\b", text):
            return Reply("Scripted demo: " + CLARIFICATIONS[module], "clarification")
        if re.search(r"\b(yes|no|okay|ok|because)\b", text):
            return Reply("Scripted follow-up: " + HINTS[module], "follow_up")
        return Reply("Scripted demo: I have a small set of authored replies and cannot interpret arbitrary questions. Try 'explain this concept', 'hint', or 'why?'. You can also revisit the worked example.", "fallback")
