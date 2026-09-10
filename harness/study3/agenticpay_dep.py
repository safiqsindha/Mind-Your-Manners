"""Clone-and-import helper for AgenticPay (arXiv 2602.06008),
`github.com/SafeRL-Lab/AgenticPay`.

Task spec instruction, quoted directly: "Before writing any integration
code: clone the repo and read the real task schema and metric definitions.
This is the exact failure that bit the Study 2 grader ... Do not repeat
it." Done before any of harness/study3/ was written -- see the gating
check writeup in RESULTS.md and this package's other modules for what was
actually verified against the real cloned code:
`agenticpay.models.base_llm.BaseLLM.generate(prompt, temperature, max_tokens,
**kwargs) -> str` is the only interface a model adapter must satisfy
(llm_adapter.py), `BaseAgent._build_prompt()`'s "You are {name},
{role_description}" is the one documented tone-injection point
(personas.py), buyer/seller offers are extracted from
`### BUYER_PRICE($X) ###` / `### SELLER_PRICE($X) ###` inside a
`<message>...</message>` block, and `env.step()` already computes
GlobalScore/BuyerScore/SellerScore on termination -- none of this is
reimplemented here, all of it is used as found.

AgenticPay is not published to PyPI, so it's cloned like SpreadsheetBench
(study2/dataset.py:ensure_repo()) rather than pip-installed from an index.
Its own requirements.txt pulls in torch/vllm/sglang/transformers for
optional local-model backends this harness never uses (every Study 3 call
routes through this harness's own OpenRouter-based Provider, see
llm_adapter.py) -- so this helper does not run `pip install -r
requirements.txt`; it installs only the one genuinely-missing lightweight
dependency confirmed during the gating check (`loguru`, used for logging
inside agenticpay.agents).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_URL = "https://github.com/SafeRL-Lab/AgenticPay.git"


def ensure_agenticpay_repo(cache_dir: Path) -> Path:
    """Clone AgenticPay into cache_dir if not already present, install its
    one missing lightweight dependency, and make the package importable
    (it ships as a plain source tree, not a PyPI package -- add the clone
    root to sys.path rather than pip-installing an index that doesn't
    have it). Returns the repo path. Network access required on first call."""
    cache_dir = Path(cache_dir)
    repo_dir = cache_dir / "AgenticPay"
    if not repo_dir.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "--depth", "1", REPO_URL, str(repo_dir)], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "loguru"], check=True)

    repo_str = str(repo_dir)
    if repo_str not in sys.path:
        sys.path.insert(0, repo_str)
    return repo_dir
