---
source_type: public-web-article
title: "Of course you can build dynamic AI agents with Temporal"
url: "https://temporal.io/blog/of-course-you-can-build-dynamic-ai-agents-with-temporal"
canonical_url: "https://temporal.io/blog/of-course-you-can-build-dynamic-ai-agents-with-temporal"
authors:
  - "Mason Egger"
  - "Steve Androulakis"
publisher: "Temporal"
published: 2025-11-12
accessed: "2026-06-12T06:05:30.257Z"
language: en
category: "Temporal Voices"
duration: "10 MIN"
tags:
  - Python
  - Temporal Primitives
  - AI/ML
  - Architecture
  - Code Samples
raw_admission_reason: "User saved the public article output and requested cleanup into raw with frontmatter."
preservation_mode: article-body
full_text_preserved: true
cleanup_note: "Removed site navigation, table of contents, share links, promotional blocks, footer links, and cookie banner text; retained the article title, byline metadata in frontmatter, and article body content."
---

Over the past few weeks I’ve heard some variation of the following statement:
"We can't use Temporal for our AI agent.
LLMs are inherently non-deterministic
and our agent doesn’t follow a predefined path like ‘Do Step 1, then Step 2,
then Step 3’.
And since Temporal requires determinism we can’t use it for our very clever
and dynamic agents."
Every time I hear this, I have a similar reaction:

![what](https://images.ctfassets.net/0uuz8ydxyd9p/3t2P1ifn8rIPUmE5Spa1w8/fb56ea37126a5fcdc2193736adb68800/what.gif)

This is **100% incorrect**.
Not only _can_ you build AI agents with Temporal,
I’d argue it’s the best way to do it.
Heck, OpenAI’s Codex web agent is built on Temporal.
So is Replit’s new long-running Agent 3.
Temporal’s determinism requirement doesn’t limit the behavior of your agent,
it’s actually what makes AI agents reliable in production.

Let me show you why this misconception exists,
and how Temporal's architecture is perfectly designed for powerful agents
that follow very dynamic paths and trajectories.

So let’s bust this myth.

![mythbusters](https://images.ctfassets.net/0uuz8ydxyd9p/77WkP6qbtbaUMQtDuY9V7r/337e3ad4c524e4eb7c72277bc318c969/mythbusters.gif)

## What Temporal actually requires

So I get where this is coming from.
If you look at Temporal’s documentation, or take an online tutorial or course,
you may come across the phrase “Temporal requires your Workflows to be
deterministic” and automatically jump to this conclusion.
And that’s fair, but there are _tons_ of people using Temporal
for all _sorts_ of things, including AI agents.
So where are the wires crossed?

So here’s the critical distinction that people are missing.
**While Temporal requires that your Workflow code is deterministic, your AI
Agent can absolutely make decisions based on non-deterministic LLM outcomes.**

Let me show you what this means visually:
![workflow-activity-diagram](https://images.ctfassets.net/0uuz8ydxyd9p/4jRU8f5FRFKls9L8hZWxh3/cdb3d654125279773285237ad6b37a2c/workflow-activity-diagram.png)

Your **Workflow** is the orchestration layer,
the blueprint that defines the structure of your application.
It needs to be deterministic
so Temporal can help your agent survive through process crashes, outages,
and other failures.

Your **Activities** are where the actual work happens: calling LLMs,
invoking tools, making API requests.
These can be as unpredictable and non-deterministic as needed.

This separation is _exactly_ what makes Temporal perfect for AI agents.
In fact, the longer running your agents are,
the more valuable Temporal’s
[Durable Execution](https://temporal.io/blog/what-is-durable-execution)
superpowers become.

## Not all who wander are lost

In sum, Temporal AI Agents are:

* **Deterministic in execution**:
  An agent will always take the same path given the same context
  and LLM decisions
* **BUT NOT predetermined**:
  You don't know what the LLM will decide until runtime

Deterministic execution unlocks durability.
If the Workflow has to recover from a crash,
it “replays” your agent’s progress to date.
But the Workflow does not ask the agent for a new plan
for decisions it has already made...
The agent instead uses Temporal’s Event History as a record of past decisions.
This makes the execution **durable**
and is what makes the agent able to survive a crash and resume exactly
where it left off.

From the point of recovery,
the agent is free to dynamically plan its next steps as it always does,
make decisions and generally be the clever cookie it is.
Because the agent is using non-deterministic LLM results to make decisions,
its path is **not** **pre-determined**.

### Without Temporal

If your agent fails, you’re back to step one.
You restart the process from the beginning,
repeating LLM calls that take time and cost money.
Even worse, your restarted agent takes a _different_ path:
your agent’s first execution can absolutely make decisions
that are inconsistent with the restarted execution.
For example, your vacation agent booked flights for a ski trip to Whistler,
Canada before crashing at the “find hotels” step.
The restarted process decided to book flights to Japan.
That flight to Whistler is going to need cancelling.

Or perhaps you’ve “checkpointed” your agent’s progress with an external
database.
Are you sure you’ve saved all relevant state in those checkpoints
so the agent can reliably continue?
Do you have a strategy for quickly detecting an agent crash,
restoring its state from the last checkpoint,
and then continuing its progress from that point forward?

### With Temporal

The Workflow replays your agent’s progress using the recorded LLM decisions from
the Event History.
Your vacation planning agent picks up right at “find hotels in Whistler,
Canada” using the exact same state.
No re-analysis.
No different decisions nor different path.
No inconsistency.
The user never knows anything went wrong.

![flight-diagram-half-pt1](https://images.ctfassets.net/0uuz8ydxyd9p/7Lo2SYqUCseBuUWUI7P21o/3fc2b8045d3cc7e3acfb80a2fc25c0df/flight-diagram-half-pt1.png)
![flight-diagram-half-pt2](https://images.ctfassets.net/0uuz8ydxyd9p/2RoHY2eEmtPBanATEfYo2v/508ce7b4417399b429e169937a0818fe/flight-diagram-half-pt2.png)

This is why OpenAI uses Temporal for Codex.
That’s an AI coding agent running on Temporal in production,
handling millions of requests.
Codex will write code then execute it,
evaluating the result and deciding whether it has more coding work to do or
if it’s completed the user’s request.
If Temporal couldn’t handle the twists and turns of sophisticated AI agents,
OpenAI wouldn't be using it.

So you want truly dynamic, free-flowing agents,
but ones that can automatically survive failures and pick up
where they left off?
**Temporal will durably follow your non-predetermined, LLM-driven AI plans.**
In other words, you get the power of surviving failures
while keeping all the agentic smarts.

## The architecture that makes this work

Here’s the visual breakdown of how a Temporal AI Agent handles the split between
deterministic and non-deterministic components:

![flight-workflow](https://images.ctfassets.net/0uuz8ydxyd9p/1W8QTOCQwAOoenYLLUtlZu/ee2c66c16245c47d3a6bcffa75234f43/flight-workflow.png)

In this example, a user is booking a flight to Austin, Texas.
They ask their Agent to do so.
The Workflow then kicks off a loop,
working towards accomplishing the users goal.
When the goal is not achieved,
it provides the context to the LLM so the LLM can decide the next step to take.
That step may be asking for more clarification from the user,
searching for flights using Expedia’s MCP server,
or any other step the LLM thinks will help it accomplish its goal.

The distinction here is that while the orchestration of the LLM
and tool calls is deterministic, the calls, the plan,
the tools executed are completely non-deterministic.

Let’s look at another example:

![dragon-donkey](https://images.ctfassets.net/0uuz8ydxyd9p/12Jeeb4a05Ow12Vr5kjB1O/15f43671ed231ff0cc762209d8c2950d/dragon-donkey.png)

In this example we are saving our precious donkey from an evil dragon
(although the donkey is annoying and wont stop singing).
Again we ask the LLM what to do, it provides the tool,
and we save our jabbering donkey.

![donkey](https://images.ctfassets.net/0uuz8ydxyd9p/3tFdfg9sMGGfLBUWQbyAnH/9b894da7655edf92814fa71cce2b6625/donkey.gif)

Note how while the prompts are _wildly_ different,
the workflow control logic didn’t change at all.
The LLM is still in the driver’s seat.
It is dynamically determining which tools to execute based on the given context
(flight bookings vs slaying dragons).
The Workflow is the orchestrator.
It ensures that these tools are executed reliably.
And to the Agent, it’s all the same.
It executes towards a defined goal using the tools it needs.

![same-picture](https://images.ctfassets.net/0uuz8ydxyd9p/4YTTGqj5uCIxdPuB3y2TP6/67bc2b0699b6bb60690281676e573fad/same-picture.png)

This gives us non-deterministic Agents with durable execution.
And this is _exactly_ the type of problem Temporal is primed to solve.

## Just show me the code

Let me show you what this looks like in practice.
Here's a simplified AI agent Workflow:

```python
@workflow.defn
class AIAgentWorkflow:
    @workflow.run
    async def run(self, user_goal: str) -> str:
        conversation_history = []

        while not self.is_goal_achieved(conversation_history):
            # THIS is where non-determinism lives:
            # next_action.tool could be ANY of your activities
            # It's determined at runtime by the LLM, not hardcoded
            next_action = await workflow.execute_activity(
                llm_decide_next_action,
                LLMRequest(
                    goal=user_goal,
                    history=conversation_history,
                    available_tools=self.get_available_tools()
                ),
                start_to_close_timeout=timedelta(seconds=30),
            )

            # But the execution? Completely deterministic.
            result = await workflow.execute_activity(
                next_action.tool,  # Could be send_email, search_web, calculate, etc.
                next_action.params,
                start_to_close_timeout=timedelta(seconds=30)
            )

            conversation_history.append({
                "action": next_action,
                "result": result
            })

        return self.format_final_result(conversation_history)
```

Look at what’s happening here:

1. The **Workflow structure**
   (the while loop, the sequence of operations) is deterministic
2. The **LLM's decisions**
   (which tool to call, what parameters to use) are dynamic
3. The **tool executions** have dynamic results
   that can alter the LLM’s decision making

This is exactly what you want.
The LLM can make different decisions in different runs based on context,
but given the same sequence of LLM responses,
the Workflow will always execute the same way.
This is what allows Temporal to resume your Workflow
after failures without duplicating work or making different decisions.

Another neat thing about the code sample above is
that the agent can evaluate its own results.
It may decide the goal isn’t achieved
(maybe the while loop condition `is_goal_achieved()` calls an LLM to judge the
current outcome).
It might loop a few times over,
making decisions and running tools
until it’s finally ready to return a final result to the user.
You can see how the execution path can vary widely each time depending on input,
context, and the probabilistic nature of LLMs.

### But my agent dynamically generates plans

![plan](https://images.ctfassets.net/0uuz8ydxyd9p/1KdLGyQvYrEb5I84HsUlIa/fe50d821af09607440be32a5c52d4c5f/plan.gif)

Ooh, fancy.
So your agent generates a “to-do list” of steps to complete?
Awesome.
Sounds like the kind of thing you want to keep track of
and \*certainly\* ensure you don’t re-execute any steps.

Let’s re-use the previous example and introduce a parent Workflow to wrap it.
This code uses an LLM to generate a plan and works through.
In pseudocode, for brevity:

```python
# LLM generates a multi-step plan as a list
plan = execute_activity(llm_generate_plan...)
context = []

# Execute each step in the plan
for step in plan:
    # Each step runs the workflow in the sample above
    result = execute_child_workflow(step)
    context.add(result)
```

The agent might generate a list of 2 steps to fulfill a request.
The next time it may generate a list of 10 completely different ones.
These steps can execute in sequence or in parallel.

Maybe you say “plan me a bunch (!!!) of vacations for next year.”
The LLM might break down your request into 3 major steps: “ski in Canada,
” “road trip to eat BBQ in Austin Texas,” “pet Koalas in Australia.”
Each of those vacation bookings is running its own LLM decision loop —
calling tools, evaluating results, deciding next steps —
exactly like the first code sample showed
(I hope you have the funds, globetrotter!).

The important thing is the `llm_generate_plan` step runs inside a Temporal
Activity, so the Workflow is unfazed by this unpredictability in agent execution
path.

And if something goes wrong during this lengthy multi-vacation booking process,
the Event History of each Workflow automatically saves it all
so you don’t lose a thing.

See?
Your Workflows can absolutely be a harness for powerful, free-flowing agents.
Temporal allows them to be dynamic, yet durable.

## Myth busted

So I think it’s safe to say the myth that Temporal can't handle dynamic,
non-deterministic AI agents is officially busted.

![busted](https://images.ctfassets.net/0uuz8ydxyd9p/6OzswR8COdVIKicrwJjXfH/a60dac719d02f09568ff85c4be2dbf98/busted.gif)

So let’s review:

**What Temporal actually requires:**

* Workflow orchestration code must be deterministic
* ….and that’s it.
  That’s all that’s required

**What Temporal does NOT require:**

* Activities to be deterministic
* LLM responses to be predictable
* Your agent to always make the same decisions

Your LLM can be as creative, adaptive, and “non-deterministic” as you want.
Temporal just ensures that whatever your LLM decides to do gets executed
reliably and can be recovered if something goes wrong.

That’s not a limitation.
That’s exactly what you need to build production-grade AI agents.

## Want to build AI agents with Temporal?

Check out these resources:

* [Temporal AI Agent Bundle](https://temporal.io/pages/durable-ai-agent-bundle)
  — comprehensive guide to building agents
* [Mental Model for Agentic AI Applications](https://temporal.io/blog/a-mental-model-for-agentic-ai-applications)
  — understanding the architecture
* [AI Cookbook](https://docs.temporal.io/ai-cookbook) —
  practical examples and patterns
* [Temporal Community](https://temporal.io/community) —
  join the discussion on Slack, GitHub, or our forum

And if you run into someone spreading the “Temporal can’t do AI agents” myth?
Send them here.
Let’s put this one to bed.
