---
title: LangGraph Memory
type: guide
tags: [memory, langgraph, checkpoints]
---
# LangGraph Memory

LangGraph memory preserves conversation state across turns and threads. Use it
when an agent must recall durable state after the current model call.

## Checkpoints

Checkpoints persist graph state so a later execution can resume the same thread.
