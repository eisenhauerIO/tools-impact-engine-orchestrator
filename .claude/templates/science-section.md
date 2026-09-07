# Canonical science.html Section Template

This template defines the standard structure for each component section within
`promotion/website/science.html`. The science page has three sections, one per
pipeline stage (Measure, Evaluate, Allocate).

## Section Template

```html
<h2>{Discipline} — {Question}</h2>
<p>
    {Science explanation — why this question matters and what the underlying
    discipline contributes. 3-4 sentences. Written for a business audience
    that understands data but not necessarily statistics.}
</p>
<!-- TODO: add {stage} diagram -->
<h4>
    <span class="badges">
        <a href="https://github.com/eisenhauerIO/tools-impact-engine-{stage}/actions/workflows/ci.yaml" target="_blank"><img src="https://github.com/eisenhauerIO/tools-impact-engine-{stage}/actions/workflows/ci.yaml/badge.svg" alt="CI"></a>
        <a href="https://github.com/eisenhauerIO/tools-impact-engine-{stage}/actions/workflows/docs.yml" target="_blank"><img src="https://github.com/eisenhauerIO/tools-impact-engine-{stage}/actions/workflows/docs.yml/badge.svg?branch=main" alt="Docs"></a>
    </span>
    Impact Engine — {Stage}
</h4>
<p>
    The <strong>Impact Engine — {Stage}</strong> {software description — what
    the package implements, referencing the science explanation above.
    2-3 sentences.}
</p>
```

## Section Mapping

| Stage | Discipline | Question | h2 Heading |
|-------|-----------|----------|------------|
| Measure | Causal Inference | What happened? | Causal Inference — What happened? |
| Evaluate | Evidence Assessment | What did we learn? | Evidence Assessment — What did we learn? |
| Allocate | Decision Theory | What should we do? | Decision Theory — What should we do? |

## Rules

### Structure
- Each section follows the pattern: `<h2>` science heading, `<p>` science explanation, `<h4>` software heading with badges, `<p>` software description
- The `<h2>` introduces the scientific discipline and question
- The `<h4>` introduces the software component that implements it

### Badges
- Exactly 2 badges per component: CI and Docs
- Both link to GitHub Actions workflows with `target="_blank"`
- Badges appear inside `<span class="badges">` before the component name

### Science Paragraph
- Written for a business audience
- Explains the fundamental problem the discipline addresses
- Does NOT mention the software — that comes in the software paragraph

### Software Paragraph
- Starts with `The <strong>Impact Engine — {Stage}</strong>`
- Describes what the software implements, referencing concepts from the science paragraph
- Must be consistent with the README tagline and opening description for the same component

### Cross-Document Alignment

**README is the source of truth.** science.html content is derived from the component README:
- science.html science explanation ← README problem paragraph (adapted for business audience)
- science.html software paragraph ← README solution paragraph (adapted for mixed audience)

When a README changes, update science.html to match.

| Source | Scope | Audience |
|--------|-------|----------|
| README problem paragraph | Why this matters | Developers |
| README solution paragraph | What the package does | Developers |
| science.html science explanation | Adapted from README problem | Business |
| science.html software paragraph | Adapted from README solution | Business + technical |
