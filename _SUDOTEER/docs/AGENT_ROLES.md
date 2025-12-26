# 🤖 _SUDOTEER Agent Roles & Responsibilities

## Overview
_SUDOTEER uses a tiered agency model where agents collaborate in a structured chain (The "Pass-the-Torch" validation chain).

## Core Agents

### 1. Supervisor Agent (`supervisor`)
- **Role**: The Entry Point / Router.
- **Responsibility**: Decomposes user goals into subtasks and routes them to the appropriate specialist agents.
- **Protocol**: Orchestrates the high-level workflow.

### 2. Architect Agent (`architect`)
- **Role**: The Strategic Planner.
- **Responsibility**: Creates high-level architectural plans, defines component structures, and identifies technical constraints.
- **Output**: Multi-component design blueprints.

### 3. Coder Agent (`coder`)
- **Role**: The Implementer.
- **Responsibility**: Generates production-quality code based on the Architect's plan.
- **Standards**: Enforces 100% Tab indentation and PascalCase for types.

### 4. Tester Agent (`tester`)
- **Role**: The Logical Validator.
- **Responsibility**: Generates and executes test suites to ensure the code meets the specified requirements.
- **Task**: Logical validation and edge-case testing.

### 5. Documenter Agent (`documenter`)
- **Role**: The Knowledge Manager.
- **Responsibility**: Generates comprehensive technical documentation and API references.
- **Output**: Clean Markdown documentation for the entire project.

### 6. Validator Agent (`validator`)
- **Role**: The Quality Auditor.
- **Responsibility**: Performs a final holistic audit of the code, tests, and documentation.
- **Authority**: Can reject the bundle if quality standards (e.g., indentation, style, or logic) are not met.

## Experimental Agents

### 7. Seeker Agent (`seeker`)
- **Role**: The External Knowledge Researcher.
- **Responsibility**: Searches for external information, documentation, and market trends to inform agent decisions.

## Agent communication (A2A)
Agents communicate via the `A2AMessage` protocol over a shared `bus`. This ensures that all interactions are logged, traceable, and secure.
