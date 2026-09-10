"""Model registry and run configuration for all studies.

ROSTER (2026-09-10 revision, superseding the Gemini-anchored 5-model set --
see git history): four models, all OpenAI-compatible and routed through
OpenRouter on one key. Both Gemini tiers are dropped:

  Slot                  Model                    Scope
  OpenAI cheap tier     GPT-5.6 Luna             all studies
  Chinese open-weight   GLM 5.3 Flash            all studies
  Chinese open-weight   DeepSeek (current tier)  all studies
  Chinese open-weight   Qwen (current tier)      all studies

DROPPED, with reasons (checked live, 2026-09-10):
  - Gemini 3.8 Flash: at $0.75/$3.75 (input/output per 1M), this model made
    up roughly 78% of total projected spend across the old 4-model roster
    for the *lowest* agentic index in the group (artificial-analysis
    agentic_index 41.1) -- worst cost-per-capability by a wide margin, not
    a close call. LIMITATION worth stating plainly: Gemini is the model
    family Dobariya & Kumar's papers actually ran, so dropping it removes
    the closest thread of cross-paper comparability this roster had. That
    tradeoff is accepted for a 4x-ish budget improvement at equal or better
    agentic capability from GLM instead (see below).
  - Gemini 3.1 Flash-Lite: existed only to pair with Gemini 3.8 Flash for
    Study 1's two-Gemini-tier design; Study 1 is retired (see README "Why
    this is one study now, not three"), so this model has no remaining
    reason to be in the roster at all.
  - GLM and Kimi were considered and dropped in the original roster pass on
    cost/recognition grounds. Re-checked live 2026-09-10: GLM's real price
    ($0.075/$0.25) is roughly an order of magnitude below the estimate that
    drove the earlier exclusion, and its agentic index (51.2) beats every
    other model in the current roster, Gemini included. It's back in, as
    GLM_CURRENT below. Kimi was not re-checked and stays out.

VERIFICATION (every model_id, price, provider, and reasoning-control
mechanism below was checked against OpenRouter's own live catalog, not
carried over from memory, a training-data guess, or a third-party price
tracker -- see item (c) below on why that last distinction matters):

  model_id                          input $/1M   output $/1M   date checked
  openai/gpt-5.6-luna                  0.20          1.20      2026-09-10  (a)(c)
  z-ai/glm-5.3-flash                   0.075         0.25      2026-09-10  (d)
  deepseek/deepseek-v4.1-flash         0.30          1.20      2026-09-10  (b)(f)
  qwen/qwen3.8-flash                   0.15          0.47      2026-09-10  (e)

  (a) Pinned to the plain "OpenAI" endpoint (provider_pin="OpenAI"), NOT
      "openai/flex" ($0.10/$0.60) or "openai/fast" ($0.40/$2.40) -- all
      three currently share provider_name "OpenAI" in OpenRouter's
      /endpoints listing for this model_id, distinguished only by an
      internal `tag` field ("openai", "openai/flex", "openai/fast") that
      this harness's served-provider assertion (openai_compatible.py,
      checks `openrouter_metadata.endpoints.endpoints[].provider` against
      `provider_pin`) does NOT currently read or verify -- it only checks
      the shared provider_name. OPEN RISK, not yet resolved: as far as
      this check can tell, a call pinned to "OpenAI" could in principle be
      served by any of the three tags without tripping
      ProviderPinViolation, silently changing both price (up to 4x) and
      latency profile. Verify this against a real live call (does the
      response distinguish which tag served it?) before trusting the pin
      fully; not fixed here because guessing at OpenRouter's tag-pinning
      syntax without a live call to confirm against risks a pin that looks
      more specific than it is.
  (b) NOT pinned to the first-party "DeepSeek" endpoint despite one
      existing in the catalog -- see (f) below. Pinned to "Novita"
      instead (100% uptime at check time, real fp8 quantization).
      Re-checked and re-pinned 2026-09-10, superseding the -0731
      snapshot this roster previously used -- see "Prior DeepSeek
      verification trail" below the table for why. Price is
      TIME-OF-DAY-VARYING on OpenRouter's first-party listing:
      $0.15/$0.60 off-peak, $0.30/$1.20 during weekday UTC 01:00-04:00
      and 06:00-10:00; Novita's actually-used pin reported the same
      $0.30/$1.20 at check time, recorded above so the pre-call
      projection doesn't under-estimate (real billing uses OpenRouter's
      actual per-call usage.cost regardless -- see item (c) below).
  (c) Luna's price is genuinely disputed in the wild: third-party trackers
      still show $1.00/$6.00 (the rate before OpenAI's announced 80% cut on
      2026-07-30; some gateways were still billing the old rate weeks
      after the cut per public reports). $0.20/$1.20 above is what
      OpenRouter's live `/api/v1/models` endpoint actually returns for
      `openai/gpt-5.6-luna` today -- the number to trust is whichever one
      the API reports at call time, not either figure taken on faith.
      `spend_tracker.compute_cost_usd()` already prefers OpenRouter's
      per-call `usage.cost` over this static table when present, precisely
      because a table like this one can drift; the static price here is
      only a pre-call spend *projection* input. Also note: Luna's
      `supported_parameters` (checked live) does NOT include `temperature`
      -- this harness sends `temperature=0.0` on every call regardless
      (openai_compatible.py always sets it), so for Luna specifically that
      parameter is very likely silently ignored by the API rather than
      actually zeroing sampling variance. Not verified against a real
      response (no live key available while writing this); flagged here
      rather than assumed either way.
  (d) "Z.AI" endpoint (the model's own first-party host), fp8. Chosen over
      24 third-party re-hosts (DeepInfra, Relace, Morph, Fireworks, etc.,
      $0.075-$0.15/1M input) for the same vendor-fidelity-over-marginal-
      cost reasoning as the rest of this roster (see below) -- and unlike
      GPT-Luna/Qwen's first-party endpoints, Z.AI's own listing reports a
      real, disambiguating quantization value, so this model needs
      quantization_pin, not quantization_not_exposed.
  (e) Official "Alibaba" OpenRouter endpoint. Unchanged from the previous
      revision.
  (f) DeepSeek's own first-party endpoint IS listed live in /endpoints for
      this model_id, but a real call against it returns HTTP 404: "Paid
      model training violation (account settings)... configurable at
      https://openrouter.ai/settings/privacy". That's this OpenRouter
      account's own data-policy guardrail excluding that specific
      endpoint -- an account-level policy decision, not a capacity or
      pin-syntax problem, and not something retrying fixes (404 is
      deliberately excluded from openai_compatible.py's
      RETRYABLE_STATUS_CODES). Discovered live 2026-09-10 while
      re-verifying the roster was on the latest snapshot at the user's
      prompting. If this account's privacy settings are relaxed later,
      the first-party pin becomes usable again and would be worth
      revisiting -- but that's a call for whoever owns the account
      settings, not something this harness can or should route around.

  Checked via `GET https://openrouter.ai/api/v1/models` (no auth required)
  and `GET https://openrouter.ai/api/v1/models/{id}/endpoints` for
  per-provider/quantization detail. Re-run this verification before a live
  run if it's been more than a few weeks -- OpenRouter's catalog, pricing,
  and endpoint availability all change frequently, and a provider that
  looked pinnable today can disappear.

  Prior DeepSeek verification trail (kept for history -- four revisions,
  not two):
    1. Original pin (`provider_pin="DeepSeek"`, claimed as "the official
       DeepSeek endpoint") did not correspond to any real provider in
       OpenRouter's live endpoint list for `deepseek-v4-flash-0731` at
       all, only third-party re-hosts -- caught while merging in the
       mandatory-quantization-pin enforcement.
    2. Re-pinned to "DeepInfra" (fp8, well-established third-party
       re-host) -- the best available option at the time, since no
       first-party endpoint existed for that snapshot.
    3. Re-checked 2026-09-10 after two consecutive live HTTP 429s from
       DeepInfra's shared pool ("temporarily rate-limited upstream...
       shared pool") during a pre-pilot spot check, at the user's
       prompting to confirm the roster was actually on the latest
       available snapshot rather than assume DeepInfra's congestion was
       just bad luck. It wasn't just the pin needing a retry (see
       harness/providers/openai_compatible.py's retry logic, added
       separately) -- `deepseek-v4.1-flash`, released the same day,
       turned out to have the first-party "DeepSeek" endpoint the -0731
       snapshot never had. Re-pinned to that instead of DeepInfra,
       resolving the original compromise from step 2 rather than
       patching around it again.
    4. That first-party pin, in turn, failed its own live verification
       call with HTTP 404 -- not congestion, but this OpenRouter
       account's own privacy/data-policy guardrails excluding the
       endpoint (see footnote (f) above). Checked the other 3 live
       /endpoints entries for this model_id (Io Net 73.4% uptime,
       Novita 100% uptime + real fp8, DeepInfra 98.2% uptime -- the
       same pool that caused step 3's 429s) and re-pinned to Novita,
       the only one that's both reliable and not the pool already
       known to be congested.

PINNING TRAPS in OpenRouter's live catalog, checked directly against the
four chosen model_ids (none of them trip these, by construction -- kept
here as the documented reason why, and as a guardrail other future roster
edits should re-check against):
  - `~`-prefixed model IDs (e.g. `~deepseek/deepseek-v4-flash-latest`,
    confirmed live and currently resolving to a *cheaper* price than the
    dated -0731 snapshot this roster used to pin -- exactly the kind of
    silent drift that makes it tempting) are "latest" aliases that
    redirect to whatever OpenRouter currently considers newest. None of
    the four model_ids below start with `~` -- each is itself a dated
    snapshot id, not an alias to one. Note this is a genuinely separate
    concern from picking a *stale* dated snapshot (see the DeepSeek
    v4.1-flash re-pin above) -- pinning a specific date avoids the
    aliasing trap, but doesn't by itself mean that date is still the best
    one available; both need periodic re-checking.
  - `:batch` suffixed variants (confirmed live for gpt-5.6-luna,
    gpt-5.6-luna-pro, and glm-5.3-flash, roughly half the non-batch price
    each; no `:batch` variant exists for deepseek-v4.1-flash specifically,
    checked live 2026-09-10) are asynchronous-only and cannot serve a
    synchronous ReAct loop. None of the four model_ids below carry a
    `:batch` suffix. tests/test_roster.py asserts both of these
    mechanically for every entry in ALL_MODELS.

QUANTIZATION PIN: checked live for all 4 models (2026-09-10, DeepSeek
re-checked same day after its pin changed -- see footnote (f) above). GLM
5.3 Flash's real endpoint reports a usable, disambiguating quantization
value (`quantization_pin=["fp8"]`); so does DeepSeek V4.1 Flash's actual
pin (Novita, `quantization_pin=["fp8"]`) -- DeepSeek's first-party
endpoint would have reported "unknown" like the two below, but it isn't
the one actually used (blocked by account guardrails, see footnote (f)).
GPT-5.6 Luna (OpenAI's own endpoint, plus every Azure/Bedrock re-host) and
Qwen3.8 Flash's official Alibaba endpoint report quantization "unknown" on
every listed pricing tier -- this looks like a structural gap in how
OpenRouter's catalog represents proprietary, first-party APIs (as opposed
to open-weight models on GPU-cloud re-hosts, where advertising
fp8/fp4/bf16 is closer to a selling point), not a one-off data gap
research can fill in. Qwen has a third-party alternative that reports a
real quantization (Makora/fp4, near-identical price), but switching would
mean giving up the first-party endpoint for the sake of satisfying a check
-- exactly the per-provider-savings-chasing this roster's design already
rejects (see below). These two are marked `quantization_not_exposed=True`
instead: provider.only already pins each to the single first-party
endpoint that serves it, so there is no other precision variant for
`quantizations` to rule out in the first place -- see
harness/providers/openai_compatible.py.

REASONING CONTROL, per model (checked live 2026-09-10 against each
model's `reasoning` catalog field -- not every model in this roster can
truly disable reasoning, so conditions are recorded per-model below rather
than described as "thinking on/off" uniformly; see also `thinking_enabled`
on ModelConfig and README "The thinking arm"):

  model            mandatory?   effort levels available    "off" exists?
  GPT-5.6 Luna     no           max/xhigh/high/medium/low/none   yes ("none")
  GLM 5.3 Flash    YES          max/high/low                     no
  DeepSeek V4.1    no           max/high/low                     no
  Qwen3.8 Flash    no           (no effort enum -- token-budget   n/a --
                                 based via `reasoning.max_tokens`, controlled
                                 not wired up by this harness;      by provider
                                 reasoning_effort left None below)  default

  Only GPT-5.6 Luna has an explicit, harness-controllable "none" effort
  level, which is why it's the model that carries the on/off thinking arm
  (see README "The thinking arm" and the with_thinking() helper below).
  GLM's reasoning is mandatory -- reasoning_effort is pinned explicitly to
  its cheapest allowed level ("low") specifically so a run never silently
  defaults to GLM's own default_effort ("max"), which would be far more
  expensive. Qwen's reasoning isn't controlled by this harness at all
  (reasoning_effort=None -- no reasoning parameter is sent, so whatever
  the Alibaba endpoint's own default behavior is applies); wiring up
  `reasoning.max_tokens` for Qwen is future work, not done here.

Each of the 4 chosen models is pinned to ONE specific OpenRouter-listed
provider (`provider_pin`) chosen for vendor fidelity over marginal cost
savings -- e.g. several third-party fp8/fp4 re-hosts of GLM/DeepSeek's same
weights would be cheaper, and it's still the right choice, for the same
reason the harness routes everything through OpenRouter on one key rather
than chasing per-provider savings (see README "Single provider path").
Full `provider.only`/`allow_fallbacks`/`quantizations` enforcement and the
served-provider assertion live in harness/providers/openai_compatible.py,
not here -- this file only records the *intended* pin (see item (a) above
for a known gap in how specific that assertion actually is for Luna).

Every ModelConfig.key below is referenced by name from study run configs, so
keep keys stable once a run has started (results rows are keyed by
model.key, not model_id, precisely so a mid-run model_id fix doesn't
silently fragment the dataset).
"""
from __future__ import annotations

from dataclasses import replace

from .providers.base import ModelConfig

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def with_thinking(model: ModelConfig, enabled: bool, key: str | None = None) -> ModelConfig:
    """Return a copy of `model` with reasoning explicitly turned on/off.

    Only meaningful for a model with a real "none" effort level in
    OpenRouter's own `reasoning.supported_efforts` (see this module's
    REASONING CONTROL table) -- GPT-5.6 Luna is the only roster model that
    has one today, which is why it's the one that carries the on/off
    thinking arm. Calling this with enabled=False on a model without a
    real "none" level (e.g. GLM, whose reasoning is mandatory) would just
    send an effort value the API doesn't accept -- check the REASONING
    CONTROL table before using this on anything but Luna.
    """
    return replace(
        model,
        reasoning_effort="none" if not enabled else model.reasoning_effort,
        thinking_enabled=enabled,
        key=key or model.key,
    )

# ---------------------------------------------------------------------------
# Target model set -- see module docstring for the verification table and
# roster rationale.
# ---------------------------------------------------------------------------
GPT_LUNA = ModelConfig(
    key="gpt-luna",
    provider="openai_compatible",
    model_id="openai/gpt-5.6-luna",
    canonical_slug="openai/gpt-5.6-luna-20260709",  # checked live 2026-09-10
    display_name="GPT-5.6 Luna",
    temperature=0.0,
    api_base=OPENROUTER_BASE_URL,
    provider_pin="OpenAI",
    quantization_not_exposed=True,  # checked 2026-09-10 -- see module docstring's QUANTIZATION PIN section
    reasoning_effort="low",  # pinned explicitly -- default is "medium"; low keeps this the cheap/fast slot it's meant to be
    thinking_enabled=True,  # main-run condition; see GPT_LUNA_CALIBRATION below for the thinking-disabled arm
    max_tokens=2048,
    input_price_per_1m=0.20,
    output_price_per_1m=1.20,
)

# The calibration arm (README "The thinking arm"): same model, same tasks,
# same tones as GPT_LUNA's main-run condition, but with reasoning turned
# off via its real "none" effort level -- not a different model pinned
# for the "on" state (e.g. gpt-5.6-luna-pro), since that would bake the
# comparison into a model-choice difference rather than a single parameter.
# Not in CORE_MODELS -- it's a separate arm, not part of the main run.
GPT_LUNA_CALIBRATION = with_thinking(GPT_LUNA, enabled=False, key="gpt-luna-calibration")

GLM_CURRENT = ModelConfig(
    key="glm-current",
    provider="openai_compatible",
    model_id="z-ai/glm-5.3-flash",
    canonical_slug="z-ai/glm-5.3-flash-20260826",  # checked live 2026-09-10
    display_name="GLM 5.3 Flash",
    temperature=0.0,
    api_base=OPENROUTER_BASE_URL,
    provider_pin="Z.AI",
    quantization_pin=["fp8"],  # Z.AI's own endpoint reports a real quantization -- see module docstring's QUANTIZATION PIN section
    reasoning_effort="low",  # reasoning is MANDATORY on this model (no "none" effort) -- pinned to its cheapest allowed level, not left to default to "max"
    thinking_enabled=True,  # cannot be otherwise -- reasoning is mandatory, see module docstring's REASONING CONTROL table
    max_tokens=2048,
    input_price_per_1m=0.075,
    output_price_per_1m=0.25,
)

DEEPSEEK_CURRENT = ModelConfig(
    key="deepseek-current",
    provider="openai_compatible",
    model_id="deepseek/deepseek-v4.1-flash",
    canonical_slug="deepseek/deepseek-v4.1-flash-20260910",  # checked live 2026-09-10 -- the previous
    # pin (deepseek-v4-flash-0731, from 2026-07-31) was re-checked after two live 429s in a row on
    # DeepInfra's shared pool, at the user's prompting ("make sure you're using the latest, that could
    # be the issue"). v4.1-flash was released 2026-09-10 (same day) and, unlike -0731, HAS a real
    # first-party "DeepSeek" endpoint listed in /endpoints -- but a live call against it returns HTTP
    # 404 ("Paid model training violation (account settings)"): this OpenRouter account's own privacy /
    # data-policy guardrails (openrouter.ai/settings/privacy) exclude that specific endpoint. That's an
    # account-level policy decision, not a capacity problem -- retrying it (see
    # harness/providers/openai_compatible.py's RETRYABLE_STATUS_CODES, which deliberately excludes 404)
    # would never succeed. Checked all 4 endpoints /endpoints reported live: DeepSeek (blocked, above),
    # Io Net (73.4% uptime -- too flaky), Novita (100% uptime, real fp8 quantization), DeepInfra (98.2%
    # uptime -- the original congested pool that started this investigation). Re-pinned to Novita: the
    # best non-blocked, non-congested option actually verified live, not just chasing "latest" or
    # "first-party" for their own sake. If this account's privacy settings are later relaxed to allow
    # the first-party endpoint, that would be a legitimate reason to revisit this pin.
    display_name="DeepSeek V4.1 Flash",
    temperature=0.0,
    api_base=OPENROUTER_BASE_URL,
    provider_pin="Novita",  # confirmed live 2026-09-10 -- see canonical_slug comment above; DeepSeek's
    # own first-party endpoint is blocked by this account's guardrails, not chosen here
    quantization_pin=["fp8"],  # Novita's endpoint reports a real quantization (unlike the blocked first-party one)
    reasoning_effort="low",  # optional on this model; pinned for cost/latency consistency with the rest of the roster
    thinking_enabled=True,
    max_tokens=2048,
    # v4.1-flash has TIME-OF-DAY-VARYING pricing on OpenRouter's first-party listing (checked live):
    # $0.15/$0.60 off-peak, $0.30/$1.20 during weekday UTC 01:00-04:00 and 06:00-10:00. Novita's pin
    # (actually used) reported the same $0.30/$1.20 rate at check time; recorded here at the higher of
    # the two so the pre-call spend *projection* (estimate_cost_usd) doesn't under-estimate -- actual
    # billing already prefers OpenRouter's real per-call usage.cost over this static table regardless
    # (see spend_tracker.compute_cost_usd), so this only affects the projection shown before a live run,
    # not what's actually charged.
    input_price_per_1m=0.30,
    output_price_per_1m=1.20,
)

QWEN_CURRENT = ModelConfig(
    key="qwen-current",
    provider="openai_compatible",
    model_id="qwen/qwen3.8-flash",
    canonical_slug="qwen/qwen3.8-flash-20260826",  # checked live 2026-09-10
    display_name="Qwen3.8 Flash",
    temperature=0.0,
    api_base=OPENROUTER_BASE_URL,
    provider_pin="Alibaba",
    quantization_not_exposed=True,  # checked 2026-09-10 -- see module docstring's QUANTIZATION PIN section
    reasoning_effort=None,  # no effort enum for this model (token-budget based instead) -- see module docstring's REASONING CONTROL table
    thinking_enabled=None,  # not controlled by this harness -- provider default applies, see REASONING CONTROL table
    max_tokens=2048,
    input_price_per_1m=0.15,
    output_price_per_1m=0.47,
)

# Models used in every study.
CORE_MODELS: list[ModelConfig] = [GPT_LUNA, GLM_CURRENT, DEEPSEEK_CURRENT, QWEN_CURRENT]

# Study 1 is retired (see README) and no longer pulls in an extra model --
# kept as a distinct name since study1/cli.py still imports it.
STUDY1_MODELS: list[ModelConfig] = CORE_MODELS

# Optional frontier spot-check. NOT yet migrated to the OpenRouter-only path
# (item 3's "single provider path" applies to the 4-model roster above) --
# left on direct Anthropic access since it's an occasional spot-check, not
# a routine run; revisit if that becomes inconsistent in practice.
FRONTIER_SPOTCHECK = ModelConfig(
    key="frontier-spotcheck",
    provider="anthropic",
    model_id="claude-sonnet-5",  # VERIFY exact public API model string before use -- see README caveat
    display_name="Claude (frontier spot-check)",
    temperature=0.0,
    max_tokens=2048,
    input_price_per_1m=3.00,
    output_price_per_1m=15.00,
)

# NOT a target model -- see harness/providers/claude_cli_provider.py
# docstring. Exists only so the harness can be smoke-tested with genuine
# (non-mocked) inference from a Claude Code session that has no raw
# ANTHROPIC_API_KEY. Cost is read from the CLI's own reported
# total_cost_usd (see spend_tracker.compute_cost_usd), not the price
# fields below, hence they're 0.
CLAUDE_CLI_SMOKETEST = ModelConfig(
    key="claude-cli-smoketest",
    provider="claude_cli",
    model_id="haiku",  # CLI model alias; cheapest available for repeated smoke-test calls
    display_name="Claude (local CLI smoke test only)",
    temperature=0.0,
    max_tokens=1024,
    input_price_per_1m=0.0,
    output_price_per_1m=0.0,
)

# NOT a target model -- for validating a real, live OpenRouter call (the
# actual triple-pin/cache-assertion/instrumentation code path in
# harness/providers/openai_compatible.py) once an OPENROUTER_API_KEY exists,
# before spending on the real roster. README's "Single provider path"
# already flags free-tier OpenRouter endpoints as "for debugging/pilots
# only" -- this is that.
#
# An OpenAI-branded free option was checked first (per request) and isn't
# currently usable: `openai/gpt-oss-20b:free` and `openai/gpt-oss-120b:free`
# both exist as catalog IDs but currently resolve to zero active endpoints
# (checked live, 2026-09-10) -- i.e. the slug exists but nothing actually
# serves it right now. `google/gemma-4-26b-a4b-it:free` does have a real,
# live, $0/$0 endpoint (served directly by Google AI Studio, not a
# third-party re-host), so it's substituted here instead. Re-check both
# before relying on this if it's been a while -- free-tier availability on
# OpenRouter changes without notice.
OPENROUTER_FREE_SMOKETEST = ModelConfig(
    key="openrouter-free-smoketest",
    provider="openai_compatible",
    model_id="google/gemma-4-26b-a4b-it:free",
    display_name="Gemma 4 26B (OpenRouter free tier, smoke test only)",
    temperature=0.0,
    api_base=OPENROUTER_BASE_URL,
    provider_pin="Google AI Studio",
    quantization_not_exposed=True,  # checked 2026-09-10, same "unknown" pattern as the roster's Google-pinned models
    max_tokens=1024,
    input_price_per_1m=0.0,
    output_price_per_1m=0.0,
)

# NOT a target model -- second free smoke-test option, requested by name
# for a live pipeline test. Checked live 2026-09-10: `nex-agi/nex-n2.5-pro:free`
# has exactly one real, active endpoint (`GET
# /api/v1/models/nex-agi/nex-n2.5-pro:free/endpoints` -- the plain
# catalog `id`, NOT the canonical_slug alone, which returns a
# zero-endpoint listing for this model the same way the rejected
# openai/gpt-oss free models did above; a real trap, not a typo),
# provider_name "Nex AGI" (first-party), tag "nex-agi/fp8", quantization
# "fp8" -- a REAL disambiguating value, unlike every other smoke-test/
# roster model pinned to a first-party endpoint so far, so this one uses
# quantization_pin rather than the quantization_not_exposed escape hatch.
# $0/$0, 262144 context, 99.6% uptime over the last 30 min at check time.
NEX_FREE_SMOKETEST = ModelConfig(
    key="nex-free-smoketest",
    provider="openai_compatible",
    model_id="nex-agi/nex-n2.5-pro:free",
    canonical_slug="nex-agi/nex-n2.5-pro-20260907",
    display_name="Nex-N2.5-Pro (OpenRouter free tier, smoke test only)",
    temperature=0.0,
    api_base=OPENROUTER_BASE_URL,
    provider_pin="Nex AGI",
    quantization_pin=["fp8"],
    max_tokens=1024,
    input_price_per_1m=0.0,
    output_price_per_1m=0.0,
)

ALL_MODELS: list[ModelConfig] = STUDY1_MODELS + [
    GPT_LUNA_CALIBRATION, FRONTIER_SPOTCHECK, CLAUDE_CLI_SMOKETEST,
    OPENROUTER_FREE_SMOKETEST, NEX_FREE_SMOKETEST,
]

MODELS_BY_KEY: dict[str, ModelConfig] = {m.key: m for m in ALL_MODELS}


def with_temperature(model: ModelConfig, temperature: float, seed: int | None = None) -> ModelConfig:
    """Return a copy of `model` at a different temperature/seed.

    Used to build the temperature-1.0, 3-trials-per-item variance-estimate
    run from the same base model configs used for the temperature-0 primary
    run, without duplicating the model registry.
    """
    return replace(model, temperature=temperature, seed=seed)


# ---------------------------------------------------------------------------
# Budget caps -- enforced by harness/spend_tracker.py. Study 1 has a
# two-tier cap (a soft warning threshold and a hard stop) per the current
# projection across the four-model roster; Studies 2 and 3 keep a single
# hard cap each.
# ---------------------------------------------------------------------------
STUDY1_SOFT_BUDGET_CAP_USD = 50.0
STUDY1_HARD_BUDGET_CAP_USD = 75.0

# Retained for any caller still importing the old single-cap name.
STUDY1_BUDGET_CAP_USD = STUDY1_HARD_BUDGET_CAP_USD

# Study 2 keeps its pilot -> core staging. STUDY2_CORE_BUDGET_CAP_USD
# ($150) is set generously against price uncertainty rather than tightly
# against a single point estimate: Luna's live-verified price ($0.20/$1.20,
# see config.py's VERIFICATION table) puts the 50-task/7-tone/3-trial main
# run's Luna share near $35 and the other three (GLM, DeepSeek, Qwen)
# combined near $17 -- roughly $52 total -- but third-party trackers were
# still showing Luna's pre-price-cut rate ($1.00/$6.00) as recently as
# this revision, which would put the same run near $100. $150 covers that
# spread with headroom rather than needing to be re-tuned if OpenRouter's
# billed price and this file's static estimate disagree; the CLI still
# prints a real projection and requires confirmation before the first paid
# call either way (see confirm_projection() in cli.py), and
# spend_tracker.compute_cost_usd() prefers OpenRouter's actually-billed
# usage.cost over this static price table per call, so this cap is a
# circuit breaker, not the number a run is expected to actually spend.
# The frontier spot-check is a separate, optional tier with its own
# independent cap.
STUDY2_PILOT_BUDGET_CAP_USD = 20.0
STUDY2_CORE_BUDGET_CAP_USD = 150.0
STUDY2_FRONTIER_BUDGET_CAP_USD = 150.0

STUDY3_BUDGET_CAP_USD = 100.0  # at 100 negotiations per cell, bilateral subset (harness/study3/)
