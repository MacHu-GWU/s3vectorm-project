# s3vectorm Project Guide

## Project Overview

See @README.rst for complete project overview.

## Core Development Guides

### Python Development Standards

- **Virtual Environment**: @./.claude/md/Python-virtual-environment-setup-instruction.md
- **Testing Strategy**: @./.claude/md/Python-test-strategy-instruction.md
- **Docstring Guide**: @./.claude/md/pywf-open-source-Python-docstring-guide.md
- **API Documentation**: @./.claude/md/pywf-open-source-Python-cross-reference-api-doc-guide.md
- **Documentation Structure**: @./.claude/md/pywf-open-source-Python-documentation-structure-guide.md

## Essential Commands

- **All Operations**: @./Makefile (run `make help` for full command list)
- **Python Execution**: Use `.venv/bin/python` for all Python scripts in:
  - `debug/**/*.py` - Debug utilities
  - `scripts/**/*.py` - Automation scripts
  - `config/**/*.py` - Configuration deployment
  - `tests/**/*.py` - Unit and integration tests

## Quick Start Workflow

1. **Setup**: `make venv-create && make install-all`
2. **Update Dependencies**: ``make poetry-lock && make poetry-export && make install``
3. **Development**: Edit code in ``s3vectorm/**/*.py`` → Run tests ``.venv/bin/python tests/**/*.py``
4. **Testing**: `make test` or `make cov` for coverage
5. **Build Document**: `make build-doc && make view-doc` for build sphinx docs and open local html doc site in web browser

## Overview

Pydantic-S3-ORM: Type-Safe Object Storage with SQL-like Querying

This project introduces a lightweight Object-Relational Mapping (ORM) framework that combines the power of Pydantic's type validation with AWS S3 as a storage backend. The goal is to provide a modern, type-safe data persistence layer that maintains the familiar querying patterns developers expect from traditional ORMs while leveraging cloud-native storage solutions.

Core Concept

The framework uses Pydantic models as both data validation schemas and ORM entities, ensuring type safety throughout the data lifecycle. Instead of relying on traditional relational databases, data is persisted to AWS S3, making it ideal for applications that need scalable, cost-effective storage with the flexibility of schema evolution. This approach is particularly valuable for analytics workloads, data lakes, or applications dealing with semi-structured data that benefit from both type validation and cloud-scale storage.

SQLAlchemy-Inspired Query Interface

To maintain developer familiarity and reduce the learning curve, the project implements a SQLAlchemy-style query interface. Developers can construct filters using intuitive syntax like User.name.eq("Alice") or User.age.gt(18), making database queries feel natural and readable. This query builder translates these expressions into appropriate S3 operations, whether through metadata filtering, object tagging, or intelligent data organization strategies.

Key Benefits

By combining Pydantic's runtime type checking with S3's scalability and SQLAlchemy's ergonomic query patterns, this framework offers the best of all worlds: type safety at development time, cost-effective storage at scale, and an intuitive API that doesn't require learning entirely new paradigms. This makes it an excellent choice for modern Python applications that need robust data handling without the overhead of traditional database infrastructure.
