## Purpose

定义后端仓库骨架的可观察行为：可安装、可启动、分层目录就位，并提供健康检查与数据库连通证明。

## ADDED Requirements

### Requirement: Layered API package exists
The repository SHALL provide an `api/` Python package layout with `controllers`, `services`, and `core` packages present as importable modules (even if empty beyond package markers).

#### Scenario: Required packages import
- **WHEN** a developer runs the project’s documented import smoke check for the API package
- **THEN** importing `controllers`, `services`, and `core` MUST succeed without error

### Requirement: Health endpoint
The API SHALL expose an HTTP health endpoint that indicates the process is running.

#### Scenario: Health check succeeds
- **WHEN** a client sends `GET /health`
- **THEN** the response status MUST be `200` and the body MUST indicate a healthy status

### Requirement: SQLite connectivity smoke
The API SHALL be able to open a configured SQLite database file for future persistence (no workflow tables required in this change).

#### Scenario: Database opens
- **WHEN** the application initializes with its default local SQLite configuration
- **THEN** a connectivity check MUST succeed (for example via a trivial query or engine connect)

### Requirement: Automated smoke tests
The API project SHALL include automated tests that cover health and package/import smoke for this bootstrap.

#### Scenario: Smoke tests pass
- **WHEN** a developer runs the documented test command for `api/`
- **THEN** the bootstrap smoke tests MUST pass
