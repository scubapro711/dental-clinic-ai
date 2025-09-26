# Development Guidelines for Manus AI - Dental Clinic Management Interface

## Implementation and Aggressive Testing Plan for Manus.im

Based on the detailed architecture, design principles, and the need for a scalable platform, I have prepared a comprehensive, step-by-step guideline set for project execution for manus.im.

The plan is built modularly to handle memory and context limitations, emphasizing an aggressive and continuous testing protocol based on open-source tools, as requested.

## 1. Core Philosophy and Guiding Principles

The project will be based on three fundamental principles to ensure stability, scalability, and reliability:

### Modular Development
Every component in the system (each AI agent, each UI module) will be developed and tested as an independent unit before integration. This approach reduces context complexity at each stage and facilitates bug detection.

### Test-Driven Development (TDD)
For each feature, tests defining the desired behavior will be written first. Code will then be written with the goal of passing these tests.

### Continuous Evaluation
System testing, especially AI agent performance evaluation, will not be a one-time event. They will be integrated into the CI/CD process and run automatically and frequently to identify regressions and failures immediately.

## 2. Modular Implementation Plan - Step by Step

Development will be carried out in defined phases, where each phase provides measurable value and builds upon the previous one.

### Phase 0: Foundation Setup and Testing Infrastructure (Week 1-2)

**Goal:** Prepare an automated, stable, and reproducible development and testing environment.

#### Version Control Setup:
- **Action:** Create a central Git repository
- **Guideline:** Define a clear Branching Policy (e.g., GitFlow) for separation between development, testing, and production

#### Infrastructure as Code (IaC) Configuration:
- **Action:** Write Terraform or AWS CDK scripts to set up all AWS infrastructure components (VPC, EC2, RDS, Fargate, IAM Roles)
- **Guideline:** Infrastructure will be configured with strict network separation (Private/Public Subnets) and HIPAA compliance from day one (encryption, minimal access control)

#### CI/CD Pipeline Construction:
- **Action:** Set up an automated process using GitHub Actions
- **Guideline:** The pipeline will be configured so that every push to the development branch automatically triggers:
  - Unit Tests
  - Code quality checks (Linters)
  - Docker container building and pushing to repository (ECR)
  - Automatic deployment to dedicated Staging environment

### Phase 1: MVP - Text Agent and Core Management Interface (Week 3-8)

**Goal:** Validate core business logic and create an initial sustainable product.

#### Module 1.1: Knowledge Base Setup (agent_kb):
- **Action:** Create physical directory structure (core_docs, knowledge_cards) and manage under Git
- **Guideline:** Write initial versions of core documents (persona, tool_specifications) and create sample YAML files for schedules and services

#### Module 1.2: Core Agent Development (CrewAI):
- **Action:** Develop agents: ReceptionistAgent, SchedulerAgent, and KnowledgeBaseManager
- **Guideline:** Develop the central DentalPMS Tool as an Abstraction Layer over the Open Dental API, implementing the "availability engine"

#### Module 1.3: Basic Management Interface Development (React + Ant Design):
- **Action:** Build critical modules for MVP: "Conversation History and Control" (including chat interface for intervention) and "Team and Knowledge Management" (initial version allowing YAML file editing)
- **Guideline:** The interface will be developed using modular components to enable easy future expansion

#### Aggressive Testing Protocol - Phase 1:
- **Unit Tests (Jest):** 100% coverage for logic in DentalPMS Tool and service functions in the interface
- **Component Tests (React Testing Library):** Testing each UI component separately, including basic user interactions
- **E2E Tests (Playwright):** Create 5-10 core user scenarios simulating complete WhatsApp conversations, including human intervention through chat interface

#### Agent Evaluation (DeepEval):
- Create a "Golden Dataset" of 50 example conversations with expected results
- Automatic execution of Answer Relevancy, Faithfulness, and Task Completion tests against this dataset in every build

## 3. Aggressive and Continuous Testing Protocol

This is the heart of quality assurance. It will operate parallel to all development phases.

### 3.1. Toolbox (Open Source):

#### UI Testing (Functionality and E2E): Playwright
Chosen for its powerful capabilities for cross-browser testing, scenario recording, and automatic element waiting (Auto-wait), reducing "Flaky tests".

#### Unit and Component Testing (JS): Jest combined with React Testing Library
Industry standard for React testing, with built-in Snapshot and Mocking capabilities.

#### Load Testing (API): Locust
Chosen for its ability to define complex user behavior in simple Python code, and its high compatibility for testing FastAPI services.

#### LLM Agent Evaluation: DeepEval
Chosen for its simple integration with Pytest, variety of built-in metrics (RAG, conversation, tool usage), and ability to define custom metrics.

### 3.2. Testing Timing and Cadence:

Tests will run at different frequencies to balance between feedback speed and comprehensive coverage:

#### On Every Commit to Development Branch:
- **What runs:** All unit tests, component tests, and code quality checks (Linters)
- **Goal:** Immediate feedback to developer (less than 2 minutes)

#### On Pull Request Opening to Main Branch:
- **What runs:** All tests from previous stage + condensed E2E test suite ("Smoke Tests") + basic agent evaluation suite on 20 cases
- **Goal:** Ensure the change doesn't break critical functionality before merging

#### Nightly Build on Main Branch:
- **What runs:** All tests, including:
  - Complete Playwright E2E suite
  - Complete agent evaluation (DeepEval) on entire "Golden Dataset"
  - Basic load test (Locust) with 50 virtual users for 10 minutes
- **Goal:** Identify regressions, agent performance degradation, and initial performance issues

#### Weekly Run (in Staging Environment):
- **What runs:** Aggressive load test (Locust) simulating hundreds of simultaneous users for an hour
- **Goal:** Identify memory leaks, database bottlenecks, and system behavior under sustained pressure

### 3.3. Testing Types Breakdown:

#### Simulation Tests (Playwright & DeepEval):
**Guideline:** Create test files defining complex end-to-end conversation scenarios. For example: "User requests appointment, agent doesn't find one, user changes request, agent offers 3 options, user chooses, agent confirms". Each such scenario is a test file.

#### Load Tests (Locust):
**Guideline:** Create locustfile.py defining "user behavior" including sending messages, waiting for response, and sending follow-up messages. Locust will run hundreds of such "users" in parallel against the FastAPI API.

#### Click Tests (Playwright):
**Guideline:** Use Playwright Recorder to record user interactions in the management interface (e.g., filtering conversations, opening transcripts, taking over conversations) and convert them to automated tests that run again in every build.

#### User Simulation Tests:
**Guideline:** This is a combination of all tools. An E2E scenario in Playwright will trigger a conversation, and in parallel, a test script will verify using DeepEval that the agent's responses meet defined quality metrics, and check system logs to ensure interactions with Open Dental API occurred as expected.

## Summary

By adopting this modular plan and aggressive testing protocol, manus.im will be able to handle the complexity of an agent system, ensure high reliability, and provide a stable foundation for adding new capabilities and agents in the future.

---

**Creation Date:** September 26, 2025  
**Version:** 1.0  
**Intended for:** Manus AI Development Team
