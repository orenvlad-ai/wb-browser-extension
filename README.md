# WB Price Extension

Repository for a Chrome extension that will help an owner prepare and apply
price changes to their own Wildberries products.

The current implementation is an inert Manifest V3 shell with an accessible
local popup placeholder. It does not request permissions or contain price
change behavior, a Wildberries API client, credentials, storage, background
networking, telemetry, deployment automation, or live platform integration.

After this bootstrap, all feature changes must enter through the exact DCP
`wb-price-extension` / `repo-only` target, pass the `baseline` check and fresh
review, and merge through the trusted DCP admission controller.

See [Project brief](docs/PROJECT_BRIEF.md),
[Architecture](docs/ARCHITECTURE.md), and [repository rules](AGENTS.md).
