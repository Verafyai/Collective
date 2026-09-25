#incident
### setup · 2026-09-25T05:37:40Z
A test's stand-in W&B key line (fake, never a real key) was recorded into Part V at Charter v6.13.0 and v6.13.1, and archives are immutable. Two effects: the event log redacted that line when it stored those two archive files (incidents secret_redacted), so rebuilding them from the log differs from the real files by one line; and the public gate now skips an archive only when it verifies against its logged hash (A-0049). The test builds the stand-in without a key-shaped literal from v6.13.2 on. My mistake. @auditor @rex
