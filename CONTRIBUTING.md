# Contributing

Thanks for your interest in improving AI Business Analytics Studio.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_sample_data.py
streamlit run app.py
```

## Architecture rules

1. **`core/` holds business logic and must not import Streamlit** — except `state.py`,
   `theme.py` and `ai.py`, which are explicitly session-aware. This keeps every analytic
   function testable and reusable outside the UI.
2. **`views/` holds one file per page** and should contain layout plus calls into `core/`.
   If a view grows its own algorithm, move it into `core/`.
3. **Never hard-code column names.** Read them through `core.state.col("revenue")` or the
   mapping dict, so the feature works on any dataset.
4. **Cleaning/transform functions return `(dataframe, message)`** so the UI can log and undo.
5. **Fail soft.** If a role is unmapped or a library is missing, show a helpful message rather
   than raising — see `reports.fig_to_png` and `reports.build_pptx` for the pattern.

## Adding a page

1. Create `views/my_page.py`.
2. Start with `page_header(...)` and `if not state.require_data(): st.stop()`.
3. Register it in the `PAGES` dict in `app.py`.

## Testing

```bash
# logic smoke test
PYTHONPATH=. python -c "import tests.smoke"    # or run your own script against core/
# UI smoke test — renders every page headlessly
PYTHONPATH=. python tests/test_views.py
```

Every PR should keep both green and add coverage for new modules.

## Style

- 4-space indent, ~100 char lines, type hints on public functions.
- Docstring at the top of each module explaining its single responsibility.
- Keep user-facing copy plain and specific — no jargon in error messages.
