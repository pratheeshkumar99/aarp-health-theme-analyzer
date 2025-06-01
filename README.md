# aarp-health-theme-analyzer


<!-- 1. What the repository about? -> Problem statement + aim + how should it be helpful
2. Setup instruction 1. local 2. docker
3. Project Tree
4. Methodology
5. Results - { Keywords & grouping of Articles } #pending
6. Future of scope - optional -->

## Project Overview

### What This Repository Is About

This repository contains the solution to the **AARP Data Science Internship Assignment (May 2025)**. The goal of the assignment is to build an automated system that can collect, analyze, and organize health-related articles from the [AARP Health Channel](https://www.aarp.org/health/) into meaningful, easy-to-understand themes using **Large Language Models (LLMs)**.


### Problem Statement


The AARP Health Channel publishes hundreds of articles on a wide range of topics—like nutrition, exercise, aging, chronic illnesses, and public health concerns. While this content is informative, it’s unstructured and scattered across many pages. As the number of articles grows, it becomes harder to manually track what’s being published, identify topic trends, or spot content gaps. Doing this by hand takes time, doesn’t scale well, and can lead to inconsistent results.


### Aim

The aim of this project is to create a **fully automated pipeline** that helps AARP make sense of its health articles in a clear, structured way. The system performs the following steps:

- **Scrapes** articles directly from the AARP Health Channel,
- **Cleans and prepares** the content so it's ready for analysis,
- **Generates clear, concise summaries** for each article using large language models (LLMs),
- **Finds recurring patterns and themes** across the articles using semantic analysis,
- And **groups the articles into theme-based clusters** so that AARP can easily see what kinds of health topics are being discussed the most.


### How This Is Helpful

This system turns a large, unstructured collection of articles into a clear, organized view of the main health themes AARP is covering. It creates practical value in the following ways:

- **Editorial teams** can quickly spot which topics are over- or under-covered, helping them plan new content, reduce duplication  maintaining a balanced editorial strategy.

- **Marketing and product teams** can use these theme clusters to guide their outreach and product positioning. Since the articles may come from a wide range of contributors—including staff writers, medical experts, partner organizations, and community voices—the themes captured by this system reflect not just internal priorities, but broader health trends and public concerns. This enables AARP to:
  - Time campaigns around seasonal health risks (e.g., heatstroke in summer),
  - Launch educational products around high-interest topics (e.g., memory health or hydration)

- **Data analysts and strategists** gain insight into how content priorities shift over time. For example, they might see high coverage of COVID-19 in 2021 and rising interest in mental wellness more recently. By comparing publishing trends, they can:
  - Monitor emerging or declining interest areas,
  - And inform leadership decisions about where to allocate resources, funding, or advocacy.








