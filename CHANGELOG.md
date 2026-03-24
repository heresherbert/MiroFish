# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Fixed
- **KuzuDB Concurrency Bug**: Implemented in-memory graph database handle caching to guarantee consistent node queries across concurrent threads.
- **NumPy 2.x Conflict**: Locked `numpy<2` using Astral `uv` to resolve critical initialization failures bounding PyTorch 1.x macros.
- **Idle Simulation Halt**: Solved a critical race condition inside `run_test.py` where active hours patching executed prior to full configuration creation by moving hooks after `/prepare` confirms `completed`.
- **Background TTY Locks**: Appended `--no-wait` commands preventing non-interactive shell freezes.

### Added
- **Direct Action History Queries**: Integrated trace analyzer lookups giving reporter agents access to precise reaction logs.
- **Responsive Layout Toggle Controller**: Refactored Dashboard history 3D deck stacks into fully fluid pure CSS Grid with a header toggle allowing choice between Grid and List structures effortlessly.
