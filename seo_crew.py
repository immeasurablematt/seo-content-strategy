#!/usr/bin/env python3
"""
SEO Content Brief Generator using CrewAI and DataForSEO

This script orchestrates a team of AI agents to produce a comprehensive SEO content
brief. It integrates with the DataForSEO API for keyword metrics and live SERP data.

Key features:
- Sequential multi-agent workflow with memory between agents
- Concurrent research gathering from top SERP sources
- Verbose printing for progress tracking
- Robust error handling and friendly comments for beginners

Requirements (install once):
    pip install -r requirements.txt

Environment variables (create your .env from .env.example):
- DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD: Basic Auth for DataForSEO API
- OPENAI_API_KEY: LLM provider key for CrewAI
- GOOGLE_LOCATION_CODE (optional, default 2840 US)
- GOOGLE_LANGUAGE_CODE (optional, default EN)

Usage example:
    python seo_crew.py \
      --keyword "gpu cluster for machine learning" \
      --audience "ML engineers at Series B startups" \
      --goal "Generate demand for io.net GPU clusters" \
      --company "io.net"
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import sys
import textwrap
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv

# CrewAI core
from crewai import Agent, Crew, Process, Task

# Tool decoration
try:
    # Prefer crewai_tools' decorator if available
    from crewai_tools import tool  # type: ignore
except Exception:  # pragma: no cover
    try:
        # Fallback to langchain's tool decorator if present
        from langchain.tools import tool  # type: ignore
    except Exception:
        # Minimal no-op decorator fallback for environments without tool support
        def tool(func=None, **_kwargs):  # type: ignore
            def decorator(f):
                return f

            return decorator(func) if func else decorator


# -----------------------------
# Environment & Configuration
# -----------------------------
@dataclass
class Config:
    dataforseo_login: Optional[str]
    dataforseo_password: Optional[str]
    google_location_code: int
    google_language_code: str
    verbose: bool = True

    @staticmethod
    def load_from_env() -> "Config":
        load_dotenv(override=False)
        login = os.getenv("DATAFORSEO_LOGIN")
        password = os.getenv("DATAFORSEO_PASSWORD")
        location_code = int(os.getenv("GOOGLE_LOCATION_CODE", "2840"))  # United States
        language_code = os.getenv("GOOGLE_LANGUAGE_CODE", "EN")
        return Config(
            dataforseo_login=login,
            dataforseo_password=password,
            google_location_code=location_code,
            google_language_code=language_code,
            verbose=True,
        )


# -----------------------------
# DataForSEO API Client
# -----------------------------
class DataForSEOClient:
    """Thin wrapper around DataForSEO v3 API with helpful defaults.

    Notes for beginners:
    - DataForSEO uses Basic Auth (username + password) over HTTPS.
    - This client focuses on the four endpoints needed for this project.
    - All methods return Python dicts. We keep the raw-ish responses so
      troubleshooting is easier if something goes wrong.
    """

    BASE_URL = "https://api.dataforseo.com/v3"

    def __init__(
        self,
        login: Optional[str],
        password: Optional[str],
        location_code: int,
        language_code: str,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.login = login
        self.password = password
        self.location_code = location_code
        self.language_code = language_code
        self.timeout_seconds = timeout_seconds

        self._session = requests.Session()
        if login and password:
            self._session.auth = (login, password)
        self._session.headers.update({"Content-Type": "application/json"})

    def _check_creds(self) -> None:
        if not (self.login and self.password):
            raise RuntimeError(
                "Missing DATAFORSEO_LOGIN/DATAFORSEO_PASSWORD. Fill your .env first."
            )

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._check_creds()
        url = f"{self.BASE_URL}/{path.strip('/')}"
        try:
            resp = self._session.post(url, data=json.dumps(payload), timeout=self.timeout_seconds)
            if resp.status_code >= 400:
                raise RuntimeError(f"DataForSEO error {resp.status_code}: {resp.text[:500]}")
            data = resp.json()
            return data
        except requests.RequestException as e:
            raise RuntimeError(f"Network error calling DataForSEO: {e}") from e
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON from DataForSEO at {url}") from e

    # --- Endpoints ---
    def keywords_data_google_ads_search_volume(
        self, keywords: List[str]
    ) -> Dict[str, Any]:
        # live endpoint: keywords_data/google_ads/search_volume/live
        payload = {
            "keywords": keywords,
            # API does not require location/language for volume, but send for context
            "location_code": self.location_code,
            "language_code": self.language_code,
        }
        return self._post("keywords_data/google_ads/search_volume/live", payload)

    def dataforseo_labs_bulk_keyword_difficulty(self, keywords: List[str]) -> Dict[str, Any]:
        payload = {
            "keywords": keywords,
            "location_code": self.location_code,
            "language_code": self.language_code,
        }
        return self._post("dataforseo_labs/bulk_keyword_difficulty/live", payload)

    def dataforseo_labs_google_related_keywords(
        self, seed_keyword: str, include_seed_keyword: bool = True, limit: int = 25
    ) -> Dict[str, Any]:
        payload = {
            "keyword": seed_keyword,
            "include_seed_keyword": include_seed_keyword,
            "limit": limit,
            "location_code": self.location_code,
            "language_code": self.language_code,
        }
        return self._post("dataforseo_labs/google/related_keywords/live", payload)

    def serp_organic_live_advanced(
        self, keyword: str, depth: int = 10
    ) -> Dict[str, Any]:
        payload = {
            "keyword": keyword,
            "location_code": self.location_code,
            "language_code": self.language_code,
            # Ask for enough results for analysis
            "depth": max(10, depth),
        }
        return self._post("serp/google/organic/live/advanced", payload)


# Global client instance holder used by tools
_DATAFORSEO_CLIENT: Optional[DataForSEOClient] = None


def get_dataforseo_client() -> DataForSEOClient:
    global _DATAFORSEO_CLIENT
    if _DATAFORSEO_CLIENT is None:
        cfg = Config.load_from_env()
        _DATAFORSEO_CLIENT = DataForSEOClient(
            login=cfg.dataforseo_login,
            password=cfg.dataforseo_password,
            location_code=cfg.google_location_code,
            language_code=cfg.google_language_code,
        )
    return _DATAFORSEO_CLIENT


# -----------------------------
# Tool Wrappers (for Agents)
# -----------------------------
@tool("keywords_data_google_ads_search_volume")
def tool_keywords_search_volume(input_json: str) -> str:
    """Fetch Google Ads search volume for a list of keywords.

    Args (JSON string): {"keywords": ["kw1", "kw2", ...]}
    Returns (JSON string): Raw DataForSEO API response.
    """
    try:
        payload = json.loads(input_json)
        keywords = payload.get("keywords") or []
        if not isinstance(keywords, list) or not keywords:
            raise ValueError("Provide a non-empty 'keywords' list")
        client = get_dataforseo_client()
        res = client.keywords_data_google_ads_search_volume(keywords)
        return json.dumps(res)
    except Exception as e:  # keep tool boundary robust
        return json.dumps({"error": str(e)})


@tool("dataforseo_labs_bulk_keyword_difficulty")
def tool_bulk_keyword_difficulty(input_json: str) -> str:
    """Fetch keyword difficulty for a list of keywords.

    Args (JSON string): {"keywords": ["kw1", "kw2", ...]}
    Returns (JSON string): Raw DataForSEO API response.
    """
    try:
        payload = json.loads(input_json)
        keywords = payload.get("keywords") or []
        if not isinstance(keywords, list) or not keywords:
            raise ValueError("Provide a non-empty 'keywords' list")
        client = get_dataforseo_client()
        res = client.dataforseo_labs_bulk_keyword_difficulty(keywords)
        return json.dumps(res)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool("dataforseo_labs_google_related_keywords")
def tool_related_keywords(input_json: str) -> str:
    """Find related keywords for a seed keyword.

    Args (JSON string): {"seed_keyword": "...", "limit": 25}
    Returns (JSON string): Raw DataForSEO API response.
    """
    try:
        payload = json.loads(input_json)
        seed = payload.get("seed_keyword")
        limit = int(payload.get("limit", 25))
        if not seed or not isinstance(seed, str):
            raise ValueError("Provide 'seed_keyword' string")
        client = get_dataforseo_client()
        res = client.dataforseo_labs_google_related_keywords(seed, True, limit)
        return json.dumps(res)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool("serp_organic_live_advanced")
def tool_serp_organic_live(input_json: str) -> str:
    """Fetch live Google organic SERP (top results) for a keyword.

    Args (JSON string): {"keyword": "...", "depth": 10}
    Returns (JSON string): Raw DataForSEO API response.
    """
    try:
        payload = json.loads(input_json)
        keyword = payload.get("keyword")
        depth = int(payload.get("depth", 10))
        if not keyword or not isinstance(keyword, str):
            raise ValueError("Provide 'keyword' string")
        client = get_dataforseo_client()
        res = client.serp_organic_live_advanced(keyword, depth)
        return json.dumps(res)
    except Exception as e:
        return json.dumps({"error": str(e)})


# -----------------------------
# Helper Utilities
# -----------------------------

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\-\s]", "", text)
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text or "brief"


def safe_get(d: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    cur: Any = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def extract_serp_top_urls(serp_response: Dict[str, Any], max_results: int = 10) -> List[Tuple[str, str]]:
    """Attempt to extract (title, url) from DataForSEO SERP response."""
    results: List[Tuple[str, str]] = []
    tasks = serp_response.get("tasks") or []
    for t in tasks:
        items = safe_get(t, "result", 0, "items", default=[]) or []
        for item in items:
            if item.get("type") == "organic":
                title = item.get("title") or item.get("about_this_result", {}).get("title") or ""
                url = item.get("url") or item.get("link") or ""
                if url:
                    results.append((title, url))
                if len(results) >= max_results:
                    return results
    return results


def fetch_url_title_and_snippet(url: str, timeout: float = 15.0) -> Tuple[str, str]:
    """Fetch a page and pull the <title> and a short text snippet.

    This is intentionally simple (no heavy parsing libraries) to avoid extra deps.
    """
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0 (CrewAI SEO Brief Bot)"})
        r.raise_for_status()
        html = r.text
        # crude title extraction
        m = re.search(r"<title>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
        title = m.group(1).strip() if m else url
        # crude body snippet
        text = re.sub(r"<script[\s\S]*?</script>", " ", html)
        text = re.sub(r"<style[\s\S]*?</style>", " ", text)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        words = text.split(" ")
        snippet = " ".join(words[:50]) + ("..." if len(words) > 50 else "")
        return title, snippet
    except Exception:
        return url, ""


def concurrent_fetch_sources(urls: List[str], max_workers: int = 8) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        future_map = {ex.submit(fetch_url_title_and_snippet, u): u for u in urls}
        for fut in concurrent.futures.as_completed(future_map):
            url = future_map[fut]
            try:
                title, snippet = fut.result()
            except Exception:
                title, snippet = url, ""
            results.append({"title": title, "url": url, "snippet": snippet})
    return results


# -----------------------------
# Agent Factory
# -----------------------------

def build_agents(cfg: Config) -> Dict[str, Agent]:
    """Create and return the six agents used in the workflow."""
    common_kwargs = {
        "verbose": True,
        "memory": True,
        # You can set 'allow_delegation' if you want agents to spawn subtasks
        # "allow_delegation": False,
    }

    keyword_researcher = Agent(
        role="Keyword Researcher",
        goal=(
            "Collect keyword metrics (volume, difficulty) and related keywords from DataForSEO, "
            "then prioritize by opportunity for our target audience and goal."
        ),
        backstory=(
            "You are an SEO keyword strategist. You excel at identifying high-value keywords, "
            "balancing volume and difficulty, and finding semantic clusters."
        ),
        tools=[
            tool_keywords_search_volume,
            tool_bulk_keyword_difficulty,
            tool_related_keywords,
        ],
        **common_kwargs,
    )

    serp_analyst = Agent(
        role="SERP Analyst",
        goal=(
            "Analyze the top Google results to understand search intent, content types, and "
            "common patterns we must meet or exceed."
        ),
        backstory=(
            "You specialize in dissecting SERPs. You identify intent, content format, and gaps "
            "we can exploit to outrank competitors."
        ),
        tools=[tool_serp_organic_live],
        **common_kwargs,
    )

    content_analyzer = Agent(
        role="Content Analyzer",
        goal=(
            "From the keyword and SERP analysis, identify gaps, differentiators, and content "
            "requirements that competitors miss."
        ),
        backstory=(
            "You are a content strategist. You spot opportunities to add value and craft "
            "a compelling angle aligned with the company's positioning."
        ),
        tools=[],
        **common_kwargs,
    )

    research_gatherer = Agent(
        role="Research Gatherer",
        goal=(
            "Find authoritative supporting sources (docs, benchmarks, standards, research papers) "
            "to back up the brief's claims. Summarize key insights and keep clean citations."
        ),
        backstory=(
            "You are a meticulous researcher. You prefer primary sources and authoritative docs."
        ),
        tools=[],
        **common_kwargs,
    )

    brief_synthesizer = Agent(
        role="Brief Synthesizer",
        goal=(
            "Produce a complete content brief with SEO requirements, outline, competitor analysis, "
            "research sources, and success metrics."
        ),
        backstory=(
            "You are an editorial lead who creates clear, actionable briefs for writers."
        ),
        tools=[],
        **common_kwargs,
    )

    qa_validator = Agent(
        role="QA Validator",
        goal=(
            "Validate the brief for completeness, contradictions, and actionable clarity. "
            "If anything is missing, add it."
        ),
        backstory=(
            "You are a rigorous editor ensuring high quality and alignment with objectives."
        ),
        tools=[],
        **common_kwargs,
    )

    return {
        "keyword_researcher": keyword_researcher,
        "serp_analyst": serp_analyst,
        "content_analyzer": content_analyzer,
        "research_gatherer": research_gatherer,
        "brief_synthesizer": brief_synthesizer,
        "qa_validator": qa_validator,
    }


# -----------------------------
# Task Factory
# -----------------------------

def build_tasks(
    agents: Dict[str, Agent],
    inputs: Dict[str, Any],
    seed_data: Dict[str, Any],
) -> List[Task]:
    primary_keyword = inputs["primary_keyword"]
    target_audience = inputs["target_audience"]
    content_goal = inputs["content_goal"]
    company_name = inputs["company_name"]

    # Task 1: Keyword research
    t1 = Task(
        description=textwrap.dedent(
            f"""
            Use the provided tools to gather keyword metrics for "{primary_keyword}" and related keywords.
            1) Use related keywords tool to fetch ~25 related terms.
            2) Use bulk difficulty for the seed + related terms.
            3) Use search volume for the same set.
            4) Produce a prioritized list of 10-20 target keywords with metrics and rationale for selection.

            Consider the target audience: {target_audience}.
            Content goal: {content_goal} for {company_name}.
            """
        ).strip(),
        expected_output=textwrap.dedent(
            """
            JSON with keys: {
              "prioritized_keywords": [
                 {"keyword": str, "search_volume": int|None, "difficulty": float|None, "rationale": str}, ...
              ],
              "all_keywords": ["..."],
              "notes": str
            }
            """
        ).strip(),
        agent=agents["keyword_researcher"],
        context=[json.dumps(seed_data.get("related_keywords", {}))],
    )

    # Task 2: SERP analysis
    t2 = Task(
        description=textwrap.dedent(
            f"""
            Analyze the top 10 Google results for "{primary_keyword}".
            - Identify search intent, content formats (guides, docs, listicles), and common subtopics.
            - Note the quality bar and what would outperform it.
            - Provide structured findings.
            """
        ).strip(),
        expected_output=textwrap.dedent(
            """
            JSON with keys: {
              "intent": str,
              "content_patterns": [str, ...],
              "common_subtopics": [str, ...],
              "top_results": [ {"title": str, "url": str, "description": str|None}, ...],
              "opportunities": [str, ...]
            }
            """
        ).strip(),
        agent=agents["serp_analyst"],
        context=[json.dumps(seed_data.get("serp_top10", {}))],
    )

    # Task 3: Content gap analysis
    t3 = Task(
        description=textwrap.dedent(
            f"""
            Identify competitor content gaps and differentiators we can leverage.
            Use the outputs from keyword research and SERP analysis.
            Align recommendations with {company_name}'s positioning and the goal: {content_goal}.
            """
        ).strip(),
        expected_output=textwrap.dedent(
            """
            JSON with keys: {
              "key_gaps": [str, ...],
              "differentiators": [str, ...],
              "required_elements": [str, ...],
              "tone_and_style": str
            }
            """
        ).strip(),
        agent=agents["content_analyzer"],
        context=[t1, t2],
    )

    # Task 4: Research gatherer (we'll concurrently fetch sources in the runner and pass as context)
    t4 = Task(
        description=textwrap.dedent(
            """
            From the provided list of URLs, select the most authoritative sources and summarize
            their key points relevant to the brief. Create clean citations.
            """
        ).strip(),
        expected_output=textwrap.dedent(
            """
            JSON with keys: {
              "sources": [ {"title": str, "url": str, "snippet": str}, ...],
              "summary": str
            }
            """
        ).strip(),
        agent=agents["research_gatherer"],
        context=[],  # we will inject URLs at runtime
    )

    # Task 5: Brief synthesis
    t5 = Task(
        description=textwrap.dedent(
            f"""
            Synthesize a complete content brief for "{primary_keyword}" targeting {target_audience}.
            Include the following sections:
            - SEO requirements (primary/secondary keywords with metrics and usage guidance)
            - Content outline (H1, H2s, H3s)
            - Competitor analysis (intent, patterns, gaps, opportunities)
            - Research sources (with links)
            - Success metrics (KPIs like rankings, CTR, conversions, time on page)

            Ensure alignment with {company_name} and the goal: {content_goal}.
            """
        ).strip(),
        expected_output=textwrap.dedent(
            """
            A well-structured Markdown brief with the sections listed above.
            """
        ).strip(),
        agent=agents["brief_synthesizer"],
        context=[t1, t2, t3, t4],
    )

    # Task 6: QA validation
    t6 = Task(
        description=textwrap.dedent(
            """
            Validate the brief for completeness, contradictions, and clarity. Ensure each section is present
            and actionable. If missing or weak, add or revise content directly and output the final brief.
            """
        ).strip(),
        expected_output="Final polished Markdown content brief.",
        agent=agents["qa_validator"],
        context=[t5],
    )

    return [t1, t2, t3, t4, t5, t6]


# -----------------------------
# Orchestrator
# -----------------------------

def prefetch_seed_data(primary_keyword: str) -> Dict[str, Any]:
    """Best-effort fetch to provide deterministic data to the agents via context.

    This ensures we have DataForSEO results even if the LLM doesn't directly call tools.
    """
    seed: Dict[str, Any] = {"serp_top10": {}, "related_keywords": {}, "difficulty": {}, "volumes": {}}
    try:
        client = get_dataforseo_client()
    except Exception as e:
        print(f"[warn] DataForSEO client unavailable: {e}")
        return seed

    try:
        seed["serp_top10"] = client.serp_organic_live_advanced(primary_keyword, depth=10)
    except Exception as e:
        print(f"[warn] Could not fetch SERP: {e}")

    try:
        seed["related_keywords"] = client.dataforseo_labs_google_related_keywords(primary_keyword, True, 25)
        # collect candidate list for metrics
        candidates: List[str] = [primary_keyword]
        tasks = seed["related_keywords"].get("tasks") or []
        for t in tasks:
            items = safe_get(t, "result", 0, "items", default=[]) or []
            for it in items:
                kw = it.get("keyword") or it.get("keyword_data", {}).get("keyword")
                if isinstance(kw, str) and kw not in candidates:
                    candidates.append(kw)
                    if len(candidates) >= 30:
                        break
            if len(candidates) >= 30:
                break
        try:
            seed["volumes"] = client.keywords_data_google_ads_search_volume(candidates)
        except Exception as e:
            print(f"[warn] Could not fetch volumes: {e}")
        try:
            seed["difficulty"] = client.dataforseo_labs_bulk_keyword_difficulty(candidates)
        except Exception as e:
            print(f"[warn] Could not fetch difficulties: {e}")
    except Exception as e:
        print(f"[warn] Could not fetch related keywords: {e}")

    return seed


def run_workflow(
    primary_keyword: str,
    target_audience: str,
    content_goal: str,
    company_name: str,
    verbose: bool = True,
) -> str:
    cfg = Config.load_from_env()

    if verbose:
        print("[info] Prefetching DataForSEO seed data...")
    seed_data = prefetch_seed_data(primary_keyword)

    if verbose:
        print("[info] Building agents and tasks...")
    agents = build_agents(cfg)
    tasks = build_tasks(
        agents,
        inputs={
            "primary_keyword": primary_keyword,
            "target_audience": target_audience,
            "content_goal": content_goal,
            "company_name": company_name,
        },
        seed_data=seed_data,
    )

    # Inject concurrent research into Research Gatherer context (Task 4)
    serp_urls = extract_serp_top_urls(seed_data.get("serp_top10", {}), max_results=10)
    urls = [u for _title, u in serp_urls]
    if verbose and urls:
        print(f"[info] Concurrently fetching {len(urls)} sources for research...")
    sources = concurrent_fetch_sources(urls) if urls else []

    # Add sources JSON as context to t4
    tasks[3].context.append(json.dumps({"candidate_sources": sources}))

    if verbose:
        print("[info] Creating crew and running sequential process...")
    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential,
        memory=True,
        verbose=True,
    )

    final_result = crew.kickoff()

    # Basic validation: ensure the final result is a string brief
    output_text = str(final_result)
    required_sections = [
        "SEO requirements",
        "Content outline",
        "Competitor analysis",
        "Research sources",
        "Success metrics",
    ]
    missing = [s for s in required_sections if s.lower() not in output_text.lower()]
    if missing:
        print(f"[warn] The brief seems to miss sections: {', '.join(missing)}")

    return output_text


# -----------------------------
# CLI Entrypoint
# -----------------------------

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an SEO content brief using CrewAI and DataForSEO",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--keyword", required=True, help="Primary keyword")
    parser.add_argument("--audience", required=True, help="Target audience")
    parser.add_argument("--goal", required=True, help="Content goal")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument(
        "--no-save", action="store_true", help="Do not save brief to a local file"
    )
    return parser.parse_args(argv)


def save_output(brief_text: str, primary_keyword: str) -> str:
    """Save brief to an output Markdown file and return its path."""
    folder = os.path.join(os.getcwd(), "output")
    os.makedirs(folder, exist_ok=True)
    slug = slugify(primary_keyword)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(folder, f"brief_{slug}_{ts}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(brief_text)
    return path


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    # Quick input normalization for safety
    primary_keyword = args.keyword.strip()
    target_audience = args.audience.strip()
    content_goal = args.goal.strip()
    company_name = args.company.strip()

    if not os.getenv("OPENAI_API_KEY"):
        print(
            "[warn] OPENAI_API_KEY not found. Set it in your environment to enable the LLM.\n"
            "       See .env.example and run: export OPENAI_API_KEY=...",
            file=sys.stderr,
        )

    try:
        brief_text = run_workflow(
            primary_keyword=primary_keyword,
            target_audience=target_audience,
            content_goal=content_goal,
            company_name=company_name,
            verbose=True,
        )
    except Exception as e:
        print(f"[error] Failed to generate brief: {e}", file=sys.stderr)
        return 1

    print("\n===== CONTENT BRIEF =====\n")
    print(brief_text)

    if not args.no_save:
        try:
            out_path = save_output(brief_text, primary_keyword)
            print(f"\n[info] Brief saved to: {out_path}")
        except Exception as e:
            print(f"[warn] Could not save brief to file: {e}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
