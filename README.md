# WB Price Extension

Bootstrap repository for a future Chrome extension that will help an owner
prepare and apply price changes to their own Wildberries products.

This initial `main` contains repository policy, high-level boundaries, and a
model-free baseline only. It does not contain extension product code, a
Wildberries API client, credentials, deployment automation, or live platform
integration.

After this bootstrap, all feature changes must enter through the exact DCP
`wb-price-extension` / `repo-only` target, pass the `baseline` check and fresh
review, and merge through the trusted DCP admission controller.

See [Project brief](docs/PROJECT_BRIEF.md),
[Architecture](docs/ARCHITECTURE.md), and [repository rules](AGENTS.md).
