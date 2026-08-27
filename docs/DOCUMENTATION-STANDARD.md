# SOC Home Lab Documentation Standard

This standard keeps every daily lab journal consistent, readable, and useful as both a project history and a cybersecurity portfolio artifact.

## Required section order

Use the following order. A section may be omitted only when it genuinely does not apply.

1. `# Day N — Descriptive Title`
2. Metadata table: Date, Status, Phase
3. `## Summary`
4. `## Objectives`
5. `## Environment`
6. `## Work Completed`
7. `## Implementation and Validation`
8. `## Commands and Queries`
9. `## Evidence`
10. `## Challenges and Troubleshooting`
11. `## Findings and Analyst Notes`
12. `## Decisions`
13. `## Skills Demonstrated`
14. `## Current Status`
15. `## Next Steps`
16. Previous/index/next navigation links

Long investigations may add `###` subsections under Implementation, Troubleshooting, or Findings. A Crawl–Walk–Run exercise may retain those phases as `###` subsections.

## Formatting rules

- Use exactly one H1 heading per file.
- Use H2 for standard sections and H3 for subsections.
- Use one blank line between blocks; avoid repeated blank lines.
- Use hyphen bullets instead of decorative bullet characters.
- Use Markdown tables for compact environment, status, and troubleshooting summaries.
- Use fenced code blocks with a language such as `bash`, `powershell`, `cmd`, `xml`, or `text`.
- Put commands in runnable order and keep explanatory prose outside code blocks.
- Use checkboxes only for completion state or planned work.
- Use relative repository links for screenshots, logs, and related documents.
- Preserve failed attempts and unresolved findings; do not rewrite the record to imply everything worked.
- Distinguish observations, evidence, interpretations, decisions, and next steps.
- Never include passwords, access tokens, private keys, session cookies, or other live credentials.
- Private RFC 1918 lab addresses, lab hostnames, and the `soclab.local` test domain may be documented when relevant.

## Writing standard

- Prefer direct, specific sentences.
- Explain why a command or finding mattered rather than merely listing it.
- Avoid inflated claims such as “enterprise-grade” unless supported by the implementation.
- Treat alerts as investigative leads, not proof of compromise.
- Record the stopping point precisely so the next session can resume without reconstruction.
- Preserve technically important commands, event IDs, queries, outcomes, and unresolved issues.

## Status vocabulary

Use one of these values in the metadata table:

- Complete
- In progress
- Blocked
- Superseded

Individual components may use:

- Operational
- Complete
- In progress
- Pending
- Blocked
- Discontinued
- Unresolved

## Validation

Before publishing documentation changes, run:

```bash
npx --yes markdownlint-cli2 'README.md' 'docs/*.md'
```

The repository configuration disables line-length enforcement and table-column alignment (`MD013` and `MD060`) because GitHub renders prose and tables correctly without hard wrapping or padded columns. All other enabled Markdown rules must pass.

## File naming

Daily journals use zero-padded names:

```text
Day01.md
Day02.md
Day03.md
...
```

Supporting evidence belongs under `screenshots/`, `recordings/`, or `docs/logs/` rather than being embedded as unstructured output in the journal.
