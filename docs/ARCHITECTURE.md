# Chrome MV3 MVP architecture

## Purpose and scope

The MVP is an owner-operated Chrome Manifest V3 extension that lets an
authenticated Wildberries seller propose and apply a price change while
viewing one of that seller's own products. The extension assists with a
deliberate, user-confirmed mutation; it does not infer authority merely from
the page URL or visible page content.

In scope:

- identify the product represented by the current supported Wildberries page;
- obtain authoritative product, ownership, currency, and current-price data
  through an authenticated, typed Wildberries API adapter;
- accept a single proposed price, validate it, and show the exact old and new
  values before submission;
- queue one confirmed command in the extension background context, apply it
  through the adapter, and report a verifiable outcome;
- fail safely when authentication, ownership, connectivity, platform
  availability, or validation cannot be established.

The MVP does not include bulk or scheduled changes, automatic repricing,
competitor tracking, discount or promotion management, arbitrary seller
accounts, delegation, cross-device synchronization, analytics, telemetry, a
backend service, deployment, or unattended retries. It does not scrape the
page as proof of ownership, bypass Wildberries controls, or promise that a
price change is accepted or immediately visible.

This document defines future implementation boundaries. The repository
currently contains only an inert Manifest V3 shell with an accessible local
popup placeholder; it has no live integration or price-mutation behavior.

## Components and trust boundaries

### Page context and content script

The content script runs only on explicitly supported Wildberries product-page
origins and routes. It extracts the minimum stable product reference needed to
start a lookup and reports navigation changes. Page data is untrusted input:
product identity, ownership, price, and currency must all be resolved through
the authenticated adapter before confirmation.

It cannot read credentials, call privileged API operations directly, or apply
a price. Messages from the page are treated as hostile and are checked for
origin, sender, schema, size, and expected request state.

### Extension UI

An extension-owned side panel or popup displays the authoritative product
summary, proposed price, validation findings, confirmation view, progress, and
final outcome. Dynamic values are rendered as text, not HTML. The UI binds a
confirmation to a snapshot containing product reference, seller identity,
current price, currency, proposed price, and validation time; navigation or a
changed snapshot invalidates confirmation.

### MV3 service worker and command coordinator

The background service worker is the sole coordinator for privileged browser
operations and adapter calls. It validates every incoming message again,
maintains the command state machine, serializes commands for the same seller
and product, and attaches a client-generated operation ID for local
correlation and deduplication where the verified platform contract permits.

MV3 service workers may stop between events. Correctness must not depend on an
in-memory timer, open UI, or continuously running worker. The minimal
non-secret command journal may be persisted in extension-local storage so the
worker can reconcile an interrupted confirmed operation. It contains only the
operation ID, product reference, seller reference, price/currency snapshot,
state, timestamps, and sanitized outcome. Credentials, authorization headers,
raw platform bodies, and unnecessary catalogue data are excluded. Journal
entries have a short documented retention period and a user-visible clear
control.

### Authentication provider

Authentication is a separately reviewed runtime integration. It supplies the
adapter with short-lived authorization for the currently selected seller and
returns a stable, non-secret seller reference to the coordinator. The MVP
must use a Wildberries-supported authentication mechanism whose exact contract
has been verified from official documentation before implementation.

No token, password, cookie, refresh token, or API key is embedded in source,
the manifest, packaged assets, Git, fixtures, logs, URLs, page DOM, messages to
the content script, or extension storage. The extension does not copy browser
session cookies or invent a token vault. If the supported mechanism cannot
provide runtime authorization without extension-managed secret persistence,
implementation is blocked pending a separate security design.

### Typed Wildberries API adapter

All platform-specific behavior sits behind one typed boundary. Domain and UI
code depend on operations equivalent to:

```text
resolveOwnedProduct(authContext, productReference)
  -> OwnedProductSnapshot | NotOwned | NotFound | AuthenticationRequired

validatePrice(snapshot, proposedMoney)
  -> ValidatedPrice | ValidationRejection

applyPrice(authContext, confirmedCommand)
  -> Accepted | Rejected | Indeterminate

readPrice(authContext, productReference)
  -> CurrentPriceSnapshot | NotFound | AuthenticationRequired
```

`Money` uses an integer minor-unit amount plus an explicit currency; floating
point is not used. Requests and responses are schema-checked, errors are
normalized into the domain result types, timeouts are bounded, and logging is
redacted. Authentication details remain an opaque runtime context and never
enter domain values.

These names describe required capabilities, not Wildberries endpoint names or
claims about current platform behavior. No URL, HTTP method, payload, batch
limit, idempotency feature, price rule, or authorization flow is assumed here.
Before implementation, each mapping must be based on current official
Wildberries documentation, reviewed for least privilege, and covered by
contract fixtures. If an ownership-check, price-read, or price-write operation
cannot be supported by a verified contract, the MVP fails closed rather than
using a guessed endpoint or page automation.

## User-confirmed command flow

Every operation follows this state machine:

```text
Draft -> Validate -> Confirm -> Queue -> Apply -> Succeeded
   |         |          |         |        |
   +------> Cancelled <--+         |        +-> Rejected
             ^                    +----------> Indeterminate
             +-------- validation/auth/ownership failure
```

1. **Draft.** The owner enters a proposed price for the product shown on the
   current page. No mutation is possible in this state.
2. **Validate.** The coordinator resolves the product through the adapter,
   verifies that it belongs to the authenticated seller, parses the amount
   exactly, and applies both locally known invariants and authoritative
   platform validation. A stale, incomplete, unsupported, or ambiguous result
   fails closed.
3. **Confirm.** The extension shows product identity, seller context, old
   price, new price, currency, and validation result. The owner must perform a
   distinct confirmation action. Editing the draft, changing account or page,
   expiry of the snapshot, or a newly fetched price mismatch returns the flow
   to Validate.
4. **Queue.** The coordinator creates one immutable confirmed command and
   records it before attempting the mutation. A second active command for the
   same seller/product is rejected or held for a new confirmation; commands
   are never silently coalesced. Queueing is coordination, not permission for
   background or scheduled retries.
5. **Apply.** Immediately before submission, the adapter rechecks the relevant
   authenticated context and, when the verified API supports it, the current
   product snapshot. It submits the exact confirmed command once. The UI
   remains in progress until a response or reconciliation produces an outcome.

Only an authoritative response, preferably followed by `readPrice`
verification, yields `Succeeded`. A platform rejection yields `Rejected` with
a safe actionable reason. A timeout, worker interruption, malformed response,
or lost connection after submission yields `Indeterminate`, never success and
never an automatic resubmission.

## Permissions and security

The manifest requests only permissions demonstrated by the implementation.
Expected categories are the narrow supported Wildberries page host permission,
the verified API origin if different, extension-local storage for the
non-secret command journal, and a side-panel permission only if that surface is
chosen. Prefer optional host access when it preserves a usable flow. Broad
wildcards, `<all_urls>`, remote code, `eval`, unnecessary tabs/history access,
and externally connectable messaging are excluded.

MV3's Content Security Policy remains restrictive. All executable code is
packaged with the extension; remote scripts and inline execution are forbidden.
Messages use explicit discriminated schemas and unpredictable page content is
never interpreted as code. Adapter responses and errors are size-bounded and
schema-validated. Sensitive values are redacted at their source, and production
logging contains operation IDs and coarse result categories only.

Ownership authorization is enforced immediately before mutation through the
authenticated platform boundary, not solely by UI state. Seller and product
references are compared as canonical typed identifiers. The UI does not allow
the user or page to override the authenticated seller context.

## Offline and server-unavailable behavior

The extension may allow editing a local draft while offline, but it cannot
validate, confirm, queue, or apply it without fresh authoritative product and
ownership data. An already validated snapshot becomes stale when its documented
time window expires or connectivity/authentication changes, and must be
validated again.

Before submission, an unreachable platform leaves the command unapplied and
eligible for a new user-confirmed attempt after revalidation. Loss of contact
after submission is `Indeterminate`; the coordinator preserves the sanitized
journal entry and offers a status check. On worker restart it reconciles the
operation with `readPrice` where that can distinguish outcomes. It never
assumes failure, retries a mutation automatically, or reports success from a
locally cached price.

## Failure handling and rollback

Validation and authentication failures are non-mutating and return the owner
to an editable draft. Rate limits and transient service errors show a safe
retry time when the verified API provides one, but retry always requires a
fresh validation and confirmation. Permanent policy, ownership, or price-rule
rejections are shown without exposing raw platform responses.

The extension cannot promise transactional rollback of an external price
mutation. The pre-change price is retained in the short-lived command journal
for display and recovery reasoning, but it is never restored automatically.
If the owner requests a reversal, it is a new price change that must resolve
the latest authoritative state and pass the full Draft through Apply flow.
This prevents overwriting a legitimate intervening change. An indeterminate
operation must be reconciled before either retry or reversal is offered.

Crashes and worker suspension are recovered from the journal. A command found
in Queue that has no recorded submission may return to Confirm; a command that
may have been submitted becomes Indeterminate. Journal corruption or an
unknown state fails closed, disables mutation for that entry, and offers safe
local deletion after presenting the warning.

## Test strategy

All automated tests are model-free, credential-free, deterministic, and
network-denied. They use fakes and sanitized contract fixtures; they never call
a live Wildberries API.

- Unit tests cover exact money parsing, currency handling, schema validation,
  ownership mismatch, stale snapshots, state transitions, message validation,
  redaction, and permission-independent domain logic.
- State-machine tests prove that Apply is unreachable without fresh Validate
  and explicit Confirm, confirmation is snapshot-bound, duplicate commands are
  serialized, and indeterminate submissions are not retried automatically.
- Adapter contract tests validate typed fixture mappings for success,
  authentication failure, rejection, rate limit, malformed data, timeout, and
  indeterminate results without asserting invented endpoint details.
- MV3 integration tests use a packaged test extension and mocked adapter to
  cover supported-page detection, hostile page messages, navigation, UI
  confirmation, service-worker suspension/restart, journal reconciliation, and
  journal clearing.
- Security tests inspect the manifest and bundle for least privilege, remote
  code, forbidden dynamic execution, secret-like material, unsafe HTML sinks,
  sensitive logs, and credential leakage into storage or content-script
  messages.
- Failure-path tests cover offline startup, outage before and after submission,
  authentication expiry, concurrent price change, platform rejection,
  verification mismatch, corrupted journal data, and reversal as a new
  confirmed command.

Repository `baseline` remains the required source-policy check. Future product
tests extend verification but must remain isolated from credentials and live
services.

## MVP acceptance criteria

The MVP is acceptable for owner-controlled evaluation only when all of the
following are demonstrated with the mocked/fixture test environment:

- On a supported product page, an authenticated owner can enter one price and
  see authoritative product, seller, current-price, proposed-price, and
  currency details before a separate confirmation action.
- A mutation cannot be reached for an unauthenticated user, a product not
  authoritatively owned by the active seller, invalid or stale data, a changed
  page/account/snapshot, or an unconfirmed command.
- Exactly the confirmed seller, product, amount, and currency cross the typed
  adapter boundary, and no platform endpoint or behavior is used unless mapped
  from reviewed official documentation.
- Tokens and credentials are neither embedded nor persisted and cannot appear
  in Git, the extension package, storage, DOM, content-script messages, URLs,
  fixtures, or logs.
- Offline and unavailable states are explicit; a possible post-submission
  failure is marked Indeterminate and is not automatically retried.
- Success is based on an authoritative platform outcome and verification where
  supported, while rejection and uncertainty remain distinguishable.
- Worker suspension and restart preserve safe command recovery without
  duplicating a mutation, and the owner can clear the non-secret journal.
- Reversal is a newly validated and confirmed operation against current state,
  never an automatic rollback.
- The packaged manifest has reviewed least-privilege permissions, no remote
  code, and all automated tests and `baseline` pass without secrets or network
  access.

Passing these criteria does not deploy the extension, authorize a production
call, or constitute owner acceptance. Installation, runtime authentication,
live-platform validation, rollout, and any real price mutation are separate,
explicit owner-controlled decisions.
