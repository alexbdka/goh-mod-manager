# GoH Mod Manager Docs

This documentation set is split into two parts:

- hand-written guides for architecture, UI flow, and packaging
- generated API reference for the core, application, and service layers

## Read this first

- [Architecture](architecture.md): repository layers, responsibilities, and data flow
- [UI Flow](ui-flow.md): how the desktop UI behaves at runtime
- [Packaging](packaging.md): local builds, CI, and release packaging

## API reference

The generated API pages focus on the layers that are most stable and most useful to understand without Qt runtime context:

- `src/core`
- `src/application`
- `src/services`

The UI layer is intentionally kept out of the first generated pass because it is more workflow-oriented and better explained by the hand-written guides.

## Local docs commands

Install documentation dependencies:

```bash
uv sync --group docs
```

Run the local docs server:

```bash
uv run --group docs mkdocs serve
```

Build the static site:

```bash
uv run --group docs mkdocs build
```
