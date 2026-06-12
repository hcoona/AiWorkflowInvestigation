---
source_type: public-web-article
title: "How to build deep research agents using Temporal and Braintrust"
url: "https://temporal.io/blog/how-to-build-deep-research-agents-using-temporal-and-braintrust"
canonical_url: "https://temporal.io/blog/how-to-build-deep-research-agents-using-temporal-and-braintrust"
authors:
  - "Martin Bergman"
publisher: "Temporal"
published: 2026-06-03
accessed: "2026-06-12T06:26:24.342Z"
language: en
category: "How-To"
duration: "6 MIN"
tags:
  - AI/ML
  - Observability
  - Code Samples
  - Python
raw_admission_reason: "User saved the public article output and requested cleanup into raw with frontmatter."
preservation_mode: article-body
full_text_preserved: true
cleanup_note: "Removed site navigation, table of contents, share links, promotional blocks, related-post cards, footer links, and cookie banner text; retained the article body, code samples, body links, and getting-started resources."
---

## How to build deep research agents using Temporal and Braintrust

### Deep research agents: Valuable, but hard to build

Deep research agents look great in demos.
You type a question, and minutes later you get a cited, evidence-based report.
The architecture behind that experience, though, is fragile.

A single research run can involve dozens of LLM calls,
multiple parallel web searches,
and a synthesis step stitching everything together.
A single API timeout or malformed response can tank the whole thing.

The Braintrust and Temporal teams have been collaborating on this problem.
The goal is to make deep research agents resilient with Durable Execution,
and improvable with evals and observability.
This post walks through what we built and how the pieces fit together.

### What is the deep research use case?

The system is a multi-agent pipeline that takes a research question
and produces an evidence-based report.
It decomposes the question, generates search queries,
retrieves web sources in parallel,
and synthesizes a final document with citations and confidence assessments.

Four specialized agents handle the work:

* **Planning:** breaks the research question into 3–7 key aspects,
  identifying source types and success criteria.
* **Query generation:** converts the plan into optimized search queries
  targeting factual data, expert analysis, case studies, and recent news.
* **Web search:** executes searches, prioritizes authoritative sources,
  and extracts findings with relevance scores.
* **Report synthesis:** combines findings into a report with an executive
  summary, confidence assessment, and follow-up questions.

The agents communicate through structured Pydantic models.
Every handoff is typed and validated.

### Why multi-agent systems are hard to run in practice

In a multi-agent pipeline, each stage builds on the output of the last.
The agents interact through well-defined interfaces,
and failures compound across stages.

This creates specific failure modes:

* **LLM API timeouts, especially with reasoning models.**
  A complex research question might take a planning model 30 seconds
  or three minutes.
  Too-short timeouts cause retry loops.
  Too-long timeouts let stuck requests block everything downstream.
* **Partial search failures are inevitable at scale.**
  Five parallel web searches won’t all succeed every time.
  The system needs to continue with partial results.
* **Nondeterministic outputs make debugging painful.**
  When a report comes back with bad information,
  the root cause could be in planning, query generation, search, or synthesis.
  Tracing through four agents to find it requires purpose-built tooling.
* **Long-running pipelines that fail mid-execution waste all prior compute.**
  Without durable state, a crash during search means re-running planning
  and query generation from scratch.

These failure modes can’t be solved with basic debugging.
They need infrastructure-level solutions.

### How to build deep research agents in Temporal

Each agent maps naturally to a Temporal Activity, an isolated,
retryable unit of work.
If the planning agent’s API call times out, Temporal retries it automatically.
If one web search fails, the others keep running.

Here’s the `DeepResearchWorkflow`:

```python
@workflow.defn
class DeepResearchWorkflow:
    @workflow.run
    async def run(self, query: str) -> str:
        # Step 1: Research Planning
        research_plan = await plan_research(query)

        # Step 2: Query Generation
        query_plan = await generate_queries(research_plan)

        # Step 3: Web Search (parallel execution with resilience)
        search_results = await self._execute_searches(query_plan.queries)

        if not search_results:
            raise ApplicationError(
                "All web searches failed - cannot generate report",
                non_retryable=True,
            )

        # Step 4: Report Synthesis
        final_report = await generate_synthesis(query, research_plan, search_results)

        return self._format_final_report(query, final_report)
```

Key design decisions:

**Activities as agent boundaries.**
Each agent is a Temporal Activity calling the LLM through a shared
`invoke_model` function.
Retry semantics, timeout handling, and state durability come from Temporal,
so no custom recovery logic is needed.

**Parallel search with graceful degradation.**
Searches run in parallel with `asyncio.gather`.
Failures are filtered out, and the pipeline continues with whatever succeeded:

```python
async def _execute_searches(self, search_queries) -> List[SearchResult]:
    async def execute_single_search(search_query):
        try:
            return await search_web(search_query)
        except Exception as e:
            workflow.logger.exception(f"Search failed: {e}")
            return None

    search_tasks = [execute_single_search(q) for q in search_queries]
    results = await asyncio.gather(*search_tasks)
    return [r for r in results if r is not None]
```

Three out of five searches succeed?
The pipeline moves forward.
The only hard failure is when every search fails.

**Timeout configuration.**
We set a 300-second `start_to_close_timeout` on all Activities.
Reasoning models have highly variable response times,
and this window handles complex queries without letting stuck requests block the
Worker.

**Structured data contracts.**
Every agent handoff uses Pydantic models: `ResearchPlan`, `SearchQuery`,
`SearchResult`, `ResearchReport`.
If an agent returns something that doesn’t match the schema,
it fails immediately.

### How to add observability and evals with Braintrust

A resilient pipeline still needs visibility.
When a report contains bad information,
you need to trace back through all four agents to find the root cause.

Braintrust’s `BraintrustPlugin` integrates directly with the Temporal Worker
and captures the full execution graph automatically:

```python
from braintrust import init_logger
from braintrust.contrib.temporal import BraintrustPlugin

init_logger(project="deep-research")

worker = Worker(
    client,
    task_queue="deep-research-task-queue",
    workflows=[DeepResearchWorkflow],
    activities=[invoke_model.invoke_model],
    plugins=[BraintrustPlugin()],
)
```

Every Workflow Execution is traced end-to-end: the research plan,
every search query and its rationale, web results with relevance scores,
and the final report, all connected in a single trace.

The `invoke_model` Activity wraps the OpenAI client with Braintrust tracing,
capturing the full request and response for every LLM call:

```python
client = wrap_openai(AsyncOpenAI())
resp = await client.responses.parse(**kwargs)
```

This lets you answer specific questions.
Why did a search for “recent clinical trials” return restaurant reviews?
The query generation agent left out domain-specific terms.
Why is the confidence assessment low?
Three of five searches returned relevance scores below 0.5.

### Build resiliency with evals

Observability is also the foundation for systematic improvement.
Once traces from real research runs flow into Braintrust,
you can build evaluation datasets from production data to identify
which query types produce low-relevance results,
spot patterns in planning failures,
and measure whether prompt changes improve output quality.

This creates a feedback loop.
Traces show where agents underperform, evals measure the gap,
prompt changes close it, and new traces confirm the fix.

The practical impact: reliability improves, manual intervention drops,
and developers gain confidence that changes are improvements they can measure.
Teams stop firefighting agent failures
and start systematically improving agent quality.

### Getting started

The full implementation is available as a
[Braintrust cookbook](https://github.com/braintrustdata/braintrust-cookbook/tree/main/examples/TemporalDeepResearch).
You’ll need a Braintrust API key, an OpenAI API key, and the Temporal CLI.
The README covers setup, running the Worker,
and executing your first research query.

To learn more:

* [Braintrust documentation](https://www.braintrust.dev/docs)
  on tracing and evals
* [Temporal Workflows documentation](https://docs.temporal.io/workflows)
  for Durable Execution patterns
* [Building evaluation datasets](https://www.braintrust.dev/docs/annotate/datasets)
  from production traces
