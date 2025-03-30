# System Patterns

This file documents recurring patterns and standards used in the project.
It is optional, but recommended to be updated as the project evolves.
2025-03-28 20:03:00 - Initial creation of Memory Bank.

## Coding Patterns

- **Mathematical Docstrings**: Python implementations include LaTeX mathematical definitions in docstrings
- **Type Hints**: Python code uses type hints to enforce data types
- **Unified Interface**: Core classes (AgentTemporal, etc.) provide consistent API patterns
- **Bidirectional Conversion**: Methods for converting between agent time and human time are consistently paired
- **Hierarchical Structure**: Code organization mirrors the mathematical hierarchy of time concepts

## Architectural Patterns

- **Math-First Development**: Mathematical definitions precede implementation
- **Documentation-Code Integration**: Tight coupling between documentation and implementation
- **Cross-Language Consistency**: Future implementations (JS, R) will follow the same patterns as Python
- **Script-Based Integration**: Scripts maintain consistency across components
- **Research-Driven Development**: Development is guided by formal research hypotheses
- **Sphinx-Quarto Integration**: Sphinx-generated API docs embedded in Quarto documentation
- **Continuous Integration Flow**: Linting → Testing → Documentation → Deployment
- **Container-Based Development**: Docker containers ensure consistent environments
- **Automated Documentation**: Documentation automatically generated from code and updated
- **Version-Controlled Documentation**: Documentation versions match code versions
- **Math-First Development**: Mathematical definitions precede implementation
- **Documentation-Code Integration**: Tight coupling between documentation and implementation
- **Cross-Language Consistency**: Future implementations (JS, R) will follow the same patterns as Python
- **Script-Based Integration**: Scripts maintain consistency across components
- **Structured Documentation Organization**: Documentation organized into theory, implementation, research, and reference sections to align with research-oriented architecture (2025-03-28 21:57:00)

- **Research-Driven Development**: Development is guided by formal research hypotheses

## Testing Patterns

- **Unit Testing**: Core mathematical operations have comprehensive unit tests
- **Theory Testing**: Tests verify that implementations match mathematical definitions
- **Property-Based Testing**: Tests for mathematical properties like associativity, commutativity, etc.
- **Conversion Testing**: Bidirectional conversion between time representations is thoroughly tested
- **Integration Testing**: Tests for consistency between components
- **Documentation Testing**: Automated validation of code examples in documentation
- **Coverage Testing**: Ensure test coverage meets or exceeds 90%
- **Performance Benchmarking**: Critical operations have performance tests
- **CI Pipeline Testing**: Tests run automatically on each commit via GitHub Actions
- **Unit Testing**: Core mathematical operations have comprehensive unit tests
- **Theory Testing**: Tests verify that implementations match mathematical definitions
- **Property-Based Testing**: Tests for mathematical properties like associativity, commutativity, etc.
- **Conversion Testing**: Bidirectional conversion between time representations is thoroughly tested

## 2025-03-28 22:33:45 - Documentation Organization Patterns

### Architectural Patterns

- **Research-Oriented Documentation Structure**: The documentation is now organized following a research-oriented pattern with clear separation of:

  - Theory (mathematical foundations)
  - Implementation (code that realizes the theory)
  - Research (hypotheses, experiments, results)
  - Architecture (system design and development plans)
  - Reference (supporting materials, guidelines, and templates)

- **Bidirectional Traceability Pattern**: All implementation documentation explicitly references the theoretical concepts it implements, and all theoretical documentation includes references to its implementation.

- **Placeholder-First Development**: Creating well-structured placeholders for documentation before filling in content ensures consistency and completeness across the documentation.

### Documentation Patterns

- **Theory-Implementation-Research Triad**: Each core concept has corresponding documentation in theory, implementation, and research sections, forming a cohesive triad.

- **README-First Navigation**: Each directory contains a README.md file that explains the purpose of the directory and provides navigation to its contents.

- **Consistent Document Structure**: All documentation follows a consistent structure with Overview, Details, Examples, and Related Concepts sections.

### File Organization Patterns

- **Functional Grouping**: Files are organized by their function (theory, implementation, research) rather than by file type.

- **Reference Separation**: Supporting materials that aren't part of the core product are kept in a separate reference directory.

- **Migration Path**: Old documentation paths redirect or link to new locations during transition period.

## 2025-03-28 22:38:00 - MVP Completion Patterns

### Coding Patterns

- **Mathematical-First Documentation**: All implementations must include LaTeX mathematical definitions in docstrings that directly reference the corresponding definition or theorem in the theoretical framework

- **API Consistency Pattern**: Ensure all public methods follow consistent naming and parameter conventions across all components

- **Error Pattern**: Provide descriptive error messages that include context, explanation, and suggested solution

- **Convenience Method Pattern**: Add wrapper methods for common complex operations to improve API usability

### Architectural Patterns

- **Integration-Focused Testing**: Test the interaction between components rather than just individual units

- **Bidirectional Referencing**: Each code component explicitly references its mathematical foundation, and each mathematical concept links to its implementation

- **Example-Driven Development**: Create comprehensive examples first, then enhance API to support these workflows

- **Visualization Pipeline**: Follow a consistent pattern for data preparation, visualization creation, and display options

### Testing Patterns

- **Multi-Component Workflow Testing**: Test complete workflows that span multiple components

- **Example-Based Tests**: Convert all examples into automated tests to ensure they remain functional

- **Property-Based Mathematical Verification**: Use property-based testing to verify mathematical properties like associativity

- **Performance Regression Testing**: Establish baseline performance metrics and create tests that verify performance does not degrade

### Documentation Patterns

- **Executable Documentation**: All code examples in documentation must be executable and tested

- **Layered Documentation Approach**: Provide multiple layers of documentation (overview → detailed concepts → API reference)

- **Visual Learning Pattern**: Include diagrams, visualizations, and animations to explain complex concepts

- **Cross-Reference Network**: Create a dense network of cross-references between related concepts and implementations

## 2025-03-29 12:43:00 - Phase 2 Implementation Patterns

### Testing Patterns

- **Component Integration Testing**: Tests verify interactions between components (e.g., TaskScheduler + AgentTemporal) rather than just individual components in isolation

- **Complete Workflow Testing**: Tests simulate end-to-end user workflows spanning multiple components to verify system cohesion

- **Hypothesis-Based Testing**: Property-based tests verify mathematical hypotheses about temporal operations

- **Multi-Agent Verification**: Tests explicitly verify correct behavior across multiple agent configurations

- **Adaptation Testing**: Specific tests verify system behavior before and after temporal adaptation

### Documentation Patterns

- **Docstring-Theory Linkage**: Docstrings reference theoretical foundations using explicit cross-links

- **LaTeX Mathematical Formulations**: Mathematical concepts are expressed in LaTeX notation within docstrings

- **Documentation Deduplication**: Information is defined in exactly one place with cross-references used instead of duplication

- **Hierarchical Information Flow**: Information flows from theory to implementation to API to examples

- **Bidirectional Traceability**: Navigation paths exist both from theory to implementation and from implementation back to theory

### Implementation Patterns

- **Integration-First Focus**: Development focuses on integration points between components first, then refines individual components

- **Example-Driven Enhancement**: API enhancements are driven by needs identified in comprehensive examples

- **Workflow-Oriented Design**: System components are designed to be composed into complete workflows

- **Cross-Component Visualization**: Visualization components can represent data from multiple system components simultaneously

## Architectural Patterns

- [2025-03-29 21:26:00] - **GCP Authentication Strategy:** Adopted a dual approach:
  - **Local Development:** Application Default Credentials (ADC) via authenticated user (`gcloud auth application-default login`).
  - **CI/CD / Automated:** Service Account key file (`GOOGLE_APPLICATION_CREDENTIALS` environment variable).
  - **Rationale:** Balances local development security/convenience with standard practices for automated environments. See `docs/reference/gcp-consultant-recommendation.md`.

## [2025-03-30 11:44:00] - Development Environment Patterns

### Architectural Patterns

- **Vertex AI Workbench Integration:** Utilized as the primary managed environment for interactive development, research, testing, and documentation building, leveraging integrated GCP authentication (User ADC for UI, Service Account for instance execution) and scalability features. (Ref: `docs/implementation/vertex-ai-workbench-integration-plan.md`)

* **Integration Testing**: Tests for consistency between components
