# Ecosystem

## Component Repositories

| Component | Repository | Status |
|-----------|------------|--------|
| **Orchestrator** | [tools-impact-engine-orchestrator](https://github.com/eisenhauerIO/tools-impact-engine-orchestrator) | Implemented (mock components) |
| **MEASURE** | [tools-impact-engine-measure](https://github.com/eisenhauerIO/tools-impact-engine-measure) | Needs integration |
| **EVALUATE** | [tools-impact-engine-evaluate](https://github.com/eisenhauerIO/tools-impact-engine-evaluate) | Needs integration |
| **ALLOCATE** | [tools-impact-engine-allocate](https://github.com/eisenhauerIO/tools-impact-engine-allocate) | Needs integration |
| **SCALE** | Reuses MEASURE | — |
| **SIMULATE** | [tools-catalog-generator](https://github.com/eisenhauerIO/tools-catalog-generator) | Implemented |

## SIMULATE (Appendix)

**Package**: `tools-catalog-generator`

**Purpose**: Generate synthetic data with known treatment effects for validating the measurement pipeline.

**Use Case**: System validation and testing, not production.

- Provides controlled test data for validating MEASURE accuracy
- Ground truth enables comparing estimated effects vs actual effects
