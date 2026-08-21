## Purpose

定义学习向文档与仓库入口说明的落点，使后续 blog 与读者能找到项目约定，而不要求本 change 写出机制文正文。

## ADDED Requirements

### Requirement: Root README documents how to run API
The repository root SHALL include a README that states the project purpose (Dify-aligned Workflow learning clone) and the minimal commands to install and run the API health check.

#### Scenario: README contains run instructions
- **WHEN** a new contributor opens the root README
- **THEN** they MUST find install/run commands sufficient to hit `GET /health`

### Requirement: Web placeholder without Next app
The repository SHALL include a `web/` directory with a README stating that the Next.js app will be added in a later change, and MUST NOT ship a runnable Next.js application in this change.

#### Scenario: Web is placeholder only
- **WHEN** a contributor inspects `web/` after this change
- **THEN** they MUST find guidance text and MUST NOT be required to run `next` to complete bootstrap

### Requirement: Blog catalog scaffold
The repository SHALL provide `docs/blog/` scaffolding including a CSDN catalog stub for this series.

#### Scenario: Catalog stub exists
- **WHEN** a contributor looks for where Flow Forge blog drafts will live
- **THEN** they MUST find `docs/blog/` and a catalog stub file ready for future entries
