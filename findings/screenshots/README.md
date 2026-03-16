# Screenshot Evidence

This directory stores the screenshot evidence referenced by the report, week plan, and slide deck.

## Required files

- 01-dashboard-health.png
- 02-blocked-classic-pi.png
- 03-bypass-paraphrase-pi.png
- 04-allowed-normal-workflow.png

Recommended mapping:

- 01-dashboard-health.png: Aegis dashboard or health view proving the gateway was running during evaluation.
- 02-blocked-classic-pi.png: A blocked prompt injection case such as B04-01.
- 03-bypass-paraphrase-pi.png: A prompt injection bypass such as PI01-02, PI01-03, or PI01-04 from the real rule-based track.
- 04-allowed-normal-workflow.png: A benign developer workflow such as WF01-01 or WF01-02 being allowed.

## Optional files

- 05-false-positive-pytest.png
- 06-openclaw-workflow.png

Recommended mapping:

- 05-false-positive-pytest.png: The workflow false positive on WF01-03 where pytest flags are misread as suspicious input.
- 06-openclaw-workflow.png: OpenClaw CLI agentic testing terminal output (benign task completion or SSRF block). Note: agentic validation was performed via CLI terminal output — see `tests/test_agentic_deepseek.py` for the DeepSeek agent results and presentation script slide 12 for OpenClaw CLI output.

## Quick usage

Use the capture plan in CAPTURE_PLAN.md.

Each image should show enough context to answer three questions:

1. What input or tool call was tested?
2. What decision did Aegis return?
3. Is this a block, bypass, or benign workflow result?

For bypass screenshots, keep the exact payload, returned decision, and any trace or policy explanation visible in the same frame whenever possible.

Do not crop too aggressively. Keep the page title, status area, or trace details visible where possible.

