# Prompt Feedback & Skill Assessment

## Your Prompt Skill Rating: 7/10 — Strong Foundation, Room for Precision

---

## What You Did Well

### 1. Clear Project Vision (Prompt 1)
>
> "provides the weather climate change prediction for cities in india, geographical advantage, related land price today and prediction over each year"

One sentence that defined the entire scope — cities, climate, land price, population, scoring. This is the most important prompting skill: **knowing what you want**.

### 2. Natural Iteration Pattern

Your prompts followed a textbook engineering progression:

```
Build core (P1) → Document (P2) → Expand scope (P3) → Add real data (P4) 
→ Verify completeness (P5) → Implement advanced features (P6) 
→ Understand tradeoffs (P7) → Validate correctness (P8) 
→ Fix + expand (P9-P10) → Reflect + learn (P11)
```

This is better than most — you didn't just generate code, you verified, documented, and questioned it.

### 3. Asking "Why" and "How" (Prompts 7-8)

Prompts like "Document all the tradeoffs" and "How accurate are the results" show critical thinking. Most people skip this and just keep adding features.

### 4. Increasing Specificity Over Time

- Prompt 1: "cities in india" (vague but fine for start)
- Prompt 10: "Ayanavaram, Kolathur, Saligramam, Arumbakkam, Gerukambakkam, Nolambur" (exact areas)

This is the right trajectory.

---

## Where You Can Improve

### 1. Batch Related Asks

**What happened:** Prompts 9 and 10 were related — both added areas and dashboard features.

**Better approach:**

```
Add these specific Chennai areas: [list all 11]. 
Also add outskirts: Oragadam, Guduvanchery, Thirumazhisai, Red Hills, Chengalpattu.
Create a "Price Timeline" dashboard page showing ₹/sqft from 2015→2070 
with a growth multiplier table.
```

One prompt instead of two saves context window and gives better coherent output.

### 2. State Constraints and Format

**What you wrote:** "Add data world wise"

**Better version:**

```
Add 10-15 global cities (Singapore, Dubai, London, NYC, Tokyo, Sydney, etc.) 
using the same CityProfile dataclass. Prices in USD/sqft. 
Add a "World Cities" dashboard page with a comparison table and bar chart 
benchmarking against Indian cities.
```

The more specific you are about **what, how many, format, and where it shows up**, the fewer iterations needed.

### 3. Reference Existing Code

**What you wrote:** "Add LLM-powered query interface"

**Better version:**

```
Wire the existing QueryEngine class from src/llm/query_engine.py 
into the Streamlit dashboard as a new sidebar page called "AI Query" 
with a text input and results table.
```

When you reference exact files/classes, Claude doesn't need to search the codebase.

### 4. Define Acceptance Criteria

**What you wrote:** "Dashboards to show the price increase of land over the years"

**Better version:**

```
Add a "Price Timeline" page with:
- Line chart: ₹/sqft from 2015 to 2070 for user-selected cities (multiselect)
- Table showing: 10yr growth multiplier, CAGR, 2025→2050 multiplier
- Separate tab for Chennai outskirts with highest-growth-potential areas
```

---

## Prompt Templates You Can Reuse

### For Adding Features

```
Add [feature] to [file/component].
It should [behavior].
Use [existing code/pattern] as reference.
Show it as [UI element] with [specific data points].
```

### For Debugging

```
[Error message or behavior]
Expected: [what should happen]
Actual: [what's happening]
Relevant files: [list them]
```

### For Learning/Understanding

```
Explain how [module/concept] works in this project.
Include: what data flows in, what transformations happen, what comes out.
Use a concrete example with actual city data.
```

### For Code Review

```
Review [file] for:
- Bugs and edge cases
- Security issues
- Performance bottlenecks
- Missing error handling
Rate severity of each issue found.
```

---

## How to Get Maximum Value from Claude

| Technique | Why It Works |
|---|---|
| **Select code in editor, then ask** | Claude sees exact context — no ambiguity |
| **"Show me 3 approaches with tradeoffs"** | Forces comparison before committing |
| **"What would break if..."** | Surfaces edge cases before they happen |
| **"Write the test first, then implement"** | Test-driven prompting produces cleaner specs |
| **Paste error messages directly** | Stack traces give Claude exact debugging info |
| **"Given the existing [module], extend it to..."** | Builds on code instead of rewriting |
| **Ask for learning materials within context** | "Explain CAGR using our Coimbatore data" > generic explanation |
| **Use multi-turn refinement** | "Good, now also handle the edge case where..." |

---

## Prompt Progression Recommendations

Based on your current level, practice these next:

1. **Constraint-first prompting** — Start every feature request with constraints (max files to change, performance requirements, must use existing patterns)
2. **Negative specification** — "Do NOT add new dependencies" or "Do NOT refactor existing code"
3. **Example-driven** — "Like the Chennai Areas page but for Pondicherry" gives Claude a concrete template
4. **Decomposition** — Break complex asks into numbered steps yourself instead of letting Claude decide the order
