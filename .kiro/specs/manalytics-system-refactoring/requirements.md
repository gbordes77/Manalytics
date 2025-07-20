# Requirements Document

## Introduction

This document outlines the requirements for analyzing and refactoring the Manalytics system - a complex MTG (Magic: The Gathering) analytics pipeline that aims to replace a distributed ecosystem of 8+ interdependent repositories with a unified, autonomous solution. The current system already has significant functionality (13 visualizations, 18 advanced analytics features, processing 5,521 decks) but suffers from critical robustness issues, external dependencies, and performance bottlenecks that must be addressed to achieve the vision of a production-ready SaaS platform.

## Requirements

### Requirement 1: Critical Bug Fixes and System Stabilization

**User Story:** As a system maintainer, I want to fix the critical errors preventing reliable operation, so that the pipeline can run consistently without failures.

#### Acceptance Criteria

1. WHEN processing League data THEN the system SHALL handle empty DataFrames without throwing "max() iterable argument is empty" errors
2. WHEN filtering League 5-0 data THEN the system SHALL include valid tournament results instead of excluding them
3. WHEN encountering unknown archetype conditions THEN the system SHALL log warnings but continue processing without failure
4. WHEN the Fbettega API returns 403 errors THEN the system SHALL implement proper retry logic and fallback mechanisms
5. IF external API calls fail THEN the system SHALL gracefully degrade functionality rather than crash
6. WHEN processing tournament data THEN the system SHALL validate data completeness and handle edge cases

### Requirement 2: External Dependencies Elimination

**User Story:** As a system architect, I want to eliminate external repository dependencies, so that the system becomes truly autonomous and maintainable.

#### Acceptance Criteria

1. WHEN replacing MTGODecklistCache THEN the system SHALL implement local scraping with equivalent data coverage
2. WHEN replacing MTGOFormatData THEN the system SHALL create an internal archetype classification engine with configurable rules
3. WHEN replacing Aliquanto3 R-Meta-Analysis THEN the system SHALL reimplement the statistical methodology in pure Python
4. IF external APIs are unavailable THEN the system SHALL continue operating with cached or alternative data sources
5. WHEN implementing local alternatives THEN the system SHALL maintain backward compatibility with existing data formats
6. WHEN decoupling dependencies THEN the system SHALL document the migration path and provide rollback capabilities

### Requirement 3: Performance Optimization to Sub-20s Pipeline

**User Story:** As a user, I want the analytics pipeline to complete in under 20 seconds, so that I can get timely insights for tournament preparation.

#### Acceptance Criteria

1. WHEN running the full pipeline THEN it SHALL complete in under 20 seconds (currently ~30s)
2. WHEN processing large datasets THEN the system SHALL use vectorized Pandas operations and avoid loops
3. WHEN making multiple API calls THEN the system SHALL implement async/await parallelization
4. WHEN accessing frequently used data THEN the system SHALL implement intelligent caching strategies
5. IF data processing is CPU-intensive THEN the system SHALL utilize multiprocessing where appropriate
6. WHEN profiling the pipeline THEN the system SHALL identify and eliminate the top 3 performance bottlenecks
7. WHEN caching results THEN the system SHALL implement cache invalidation based on data freshness

### Requirement 4: Orchestrator Refactoring and Modularization

**User Story:** As a maintainer, I want to break down the monolithic orchestrator.py (5,361 lines), so that the codebase becomes more maintainable and testable.

#### Acceptance Criteria

1. WHEN refactoring the orchestrator THEN I SHALL split it into logical modules with single responsibilities
2. WHEN creating new modules THEN each SHALL have a maximum of 500 lines and clear interfaces
3. WHEN implementing module separation THEN I SHALL maintain the existing pipeline functionality
4. IF modules need to communicate THEN I SHALL use well-defined interfaces and dependency injection
5. WHEN testing modules THEN each SHALL be independently testable with >80% code coverage
6. WHEN documenting modules THEN I SHALL provide clear API documentation and usage examples
7. WHEN handling errors THEN each module SHALL implement proper error handling and logging

### Requirement 5: Robust Error Handling and Monitoring

**User Story:** As a system operator, I want comprehensive error handling and monitoring, so that I can quickly identify and resolve issues in production.

#### Acceptance Criteria

1. WHEN external APIs fail THEN the system SHALL implement circuit breaker patterns with exponential backoff
2. WHEN processing data THEN the system SHALL validate data quality and log anomalies
3. WHEN errors occur THEN the system SHALL provide detailed logging with context for debugging
4. IF critical components fail THEN the system SHALL implement graceful degradation rather than complete failure
5. WHEN monitoring the system THEN it SHALL provide health checks for all external dependencies
6. WHEN handling retries THEN the system SHALL implement intelligent retry logic with jitter
7. WHEN logging events THEN the system SHALL use structured logging for better observability

### Requirement 6: Advanced MTG Analytics Enhancement

**User Story:** As an MTG competitive player, I want advanced statistical insights beyond basic win rates, so that I can make informed meta decisions and deck choices.

#### Acceptance Criteria

1. WHEN calculating win rates THEN the system SHALL provide Bayesian confidence intervals and sample size considerations
2. WHEN analyzing metagame evolution THEN the system SHALL detect significant meta shifts using statistical tests
3. WHEN generating matchup matrices THEN the system SHALL account for asymmetric matchups and provide confidence levels
4. IF insufficient data exists THEN the system SHALL clearly indicate statistical significance and reliability
5. WHEN clustering archetypes THEN the system SHALL use advanced algorithms (DBSCAN/K-means) for automatic classification
6. WHEN analyzing temporal trends THEN the system SHALL identify post-ban/release impact with statistical significance
7. WHEN calculating probabilities THEN the system SHALL use hypergeometric distribution for deck construction insights

### Requirement 7: Testing and Quality Assurance

**User Story:** As a developer, I want comprehensive test coverage and quality assurance, so that changes can be made confidently without breaking existing functionality.

#### Acceptance Criteria

1. WHEN writing tests THEN the system SHALL achieve minimum 80% code coverage on critical modules
2. WHEN testing the pipeline THEN it SHALL include integration tests that verify end-to-end functionality
3. WHEN testing external integrations THEN it SHALL use contract tests to verify API compatibility
4. IF performance regressions occur THEN automated tests SHALL detect them and fail the build
5. WHEN testing data processing THEN it SHALL verify data quality and statistical accuracy
6. WHEN running tests THEN they SHALL complete in under 5 minutes for rapid feedback
7. WHEN testing error scenarios THEN it SHALL verify proper error handling and recovery

### Requirement 8: SaaS Platform Foundation

**User Story:** As a product owner, I want to establish the foundation for a SaaS platform, so that the system can evolve into a multi-tenant service with API access.

#### Acceptance Criteria

1. WHEN designing the API THEN it SHALL use FastAPI with proper authentication and rate limiting
2. WHEN implementing user management THEN it SHALL support multi-tenant architecture with data isolation
3. WHEN providing web interface THEN it SHALL be responsive and accessible (WCAG AA compliance)
4. IF users need API access THEN it SHALL provide comprehensive API documentation and SDKs
5. WHEN scaling the platform THEN it SHALL support horizontal scaling and load balancing
6. WHEN handling user data THEN it SHALL implement proper security and privacy controls
7. WHEN deploying updates THEN it SHALL support zero-downtime deployments and rollback capabilities
