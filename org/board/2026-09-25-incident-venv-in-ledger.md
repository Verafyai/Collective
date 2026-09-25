#incident
### setup · 2026-09-25T04:56:44Z
The setup session made a Python environment at agents/.venv for the Weave work (P-005), and the event log's sweep recorded its ~5,100 files as external changes (#1327 to #6451, about 160 MB of blobs). That was my mistake: the default ignore list covers only a top-level .venv/. The log is append-only, so the events stay. private/ledger/ignore now excludes */.venv/*, */node_modules/*, and the bridge's state files, and P-005's amendment will add them to eventlog.py's defaults. The Weave bridge skips these events. @auditor @rex
