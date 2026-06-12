---
source_type: public-web-article
title: "Trading Airflow + EMR for Temporal + Bauplan: The Mediaset tale"
url: "https://temporal.io/blog/trading-airflow-emr-temporal-bauplan-mediaset"
canonical_url: "https://temporal.io/blog/trading-airflow-emr-temporal-bauplan-mediaset"
authors:
  - "Stu Kendall"
publisher: "Temporal"
published: 2025-04-10
accessed: "2026-06-12T06:21:50.214Z"
language: en
category: "Community"
duration: "4 MIN"
tags:
  - Cloud
raw_admission_reason: "User saved the public article output and requested cleanup into raw with frontmatter."
preservation_mode: article-body
full_text_preserved: true
cleanup_note: "Removed site navigation, table of contents, share links, promotional blocks, related-post cards, footer links, and cookie banner text; retained the article title, article body, body images, body links, and final in-article CTA."
---

What do you get when you mix a legacy Airflow stack, a mountain of AWS services,
and a news dashboard that takes an hour to refresh?

Frustrated engineers, slow feedback loops, and a ton of missed opportunities.

This is how Mediaset—one of Europe’s largest private broadcasters—
went from “it works, but don’t touch it” to a modern,
Python-native data stack built with Temporal and Bauplan.
In just a few weeks, they shipped a near real-time dashboard
that updates in minutes instead of hours.

## The Setup: Video Views, Petabytes, and Plenty of Pain

Mediaset digital by the numbers (2024):

* 24 million registered users (nearly half of Italy’s population)
* 10 billion video views (roughly 25 million views per day)
* 76 petabytes of data processed

Their original data stack looked like a greatest-hits collection of AWS
services: EMR, Glue, Athena, Redshift, plus Airflow duct-taped on top.
Building just one internal dashboard for TGCOM24—their flagship news property—
took three months, required a team of senior engineers and consultants,
and still had a frustrating one-hour data lag.
![temporal bauplan legacy](https://images.ctfassets.net/0uuz8ydxyd9p/3BeOyGq3b7LFPhSgJ4khna/635cd4d7a1c8301edabd8dfaafafd13d/temporal_bauplan_legacy.drawio__4___1_.png)

## Rebuilding from First Principles

Rather than another temporary fix, the Mediaset team decided to start fresh.
Here’s what changed:

* **Airflow → Temporal** for orchestration
* **EMR + Glue + Athena + Redshift → Bauplan** serverless platform
  for data management and pipelines.
  The goal wasn’t just a tech upgrade.
  It was to build a simpler,
  more reliable system that could be developed
  and maintained by any competent engineering
  and data science team without needing deep infra expertise.
  ![temporal bauplan NOW](https://images.ctfassets.net/0uuz8ydxyd9p/5b5lJ8g9Q7Q57I3yalkQEA/7462585277481a0b37568addde3a27a8/temporal_bauplan_NOW.drawio__1___1_.png)

## What Bauplan Does, and Why It Beats the Traditional AWS Stack

Bauplan is a
[serverless platform](https://docs.bauplanlabs.com/en/latest/index.html)
specifically built for data and AI workloads.
It’s designed for developers who want to ship fast without wrangling infra.

Here’s what it replaces:

* EMR → no more cluster management
* Glue → no more boilerplate job authoring
* Athena/Redshift → no need for a data warehouse

Instead, you write Python functions,
chain them together to build pipelines and run them
as serverless functions in the cloud and get nicely typed objects back
(boto3, looking at you!):

```python
client.create_branch("my_dev_branch")
client.import_data("s3://my-bucket")
client.run("quality_pipeline")
client.merge("my_dev_branch", "main")
```

Data remains securely in your S3 buckets, stored in open formats like Iceberg.
There’s no lock-ins, no data copies, and no hidden compute bills.
You treat your data like code: versioned, testable, and portable.

## What Temporal Does, and Why It’s Better than Airflow

Temporal is a workflow engine built for reliability.
It handles retries, failures, and orchestration state without losing state.
Why Mediaset picked it over Airflow:

* [Durable, replayable Workflows](https://temporal.io/how-it-works) with
  [automatic retries](https://docs.temporal.io/evaluate/development-production-features/failure-detection)
* Everything is code—no YAML, no flaky UI debugging
* Built-in support for
  [scheduling](https://docs.temporal.io/evaluate/development-production-features/schedules),
  [signals](https://docs.temporal.io/evaluate/development-production-features/workflow-message-passing),
  and
  [complex flows](https://docs.temporal.io/evaluate/development-production-features/throughput-composability)

Airflow is fine when it works.
But when it breaks (and it will),
debugging DAGs across multiple AWS services becomes a full-time job.
Temporal just works.

## Real-world Results

After switching to Temporal and Bauplan:

* Data freshness improved from **1 hour → 5 minutes**
* Dev cycles shrank from **3 months → 6 weeks**
* Infrastructure complexity went from **6+ AWS services → 2 tools**

The new stack enabled fast iteration, clean interfaces, and resilient workflows—
without requiring a team of platform specialists or months of onboarding.

## Why It Works

Temporal manages orchestration, and Bauplan handles the data.
Together, they give you a full CI/CD workflow for your pipelines,
minus the traditional complexity of big data stacks.
You write Python.
You commit your changes.
You ship.
The dashboard was just the beginning.
Mediaset is now rolling out even more ambitious use cases:

* AI pipelines with LLMs for content summarization
* Real-time ad optimization
* A full migration away from legacy tooling

Learn even more about the Mediaset journey and try Temporal for yourself.
[Watch the talk](https://www.youtube.com/watch?v=WIlViQ3_XWo),
[try Bauplan for free](https://www.bauplanlabs.com/),
and [sign up for Temporal Cloud](https://temporal.io/get-cloud)
and get $1000 in free credits.
