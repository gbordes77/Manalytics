# Requirements Document

## Introduction

This specification focuses on the systematic reproduction and consolidation of the original multi-repository MTG analytics workflow into a unified, autonomous pipeline. The current Manalytics system attempts to replicate this workflow but has gaps in implementation that prevent complete reproduction of the original data collection and processing capabilities.

The primary objective is to methodically reproduce each step of the original workflow (Data Collection → Data Treatment → Visualization) with complete fidelity, then consolidate it into a maintainable, self-contained system that can operate independently of external repositories.

## Requirements

### Requirement 1: Step 1 Data Collection Reproduction

**User Story:** As a system operator, I want to reproduce the exact data collection workflow from the original multi-repository system, so that I can collect the same tournament data that the original system provided.

#### Acceptance Criteria

1. WHEN scraping MTGO Platform THEN the system SHALL implement the exact logic from fbettega/mtg_decklist_scrapper for tournament discovery with full documentation of original process vs current implementation
2. WHEN storing raw data THEN the system SHALL replicate the data structure from MTG_decklistcache/fbettega/MTG_decklistcache with complete mapping documentation
3. WHEN listening for matchups THEN the system SHALL implement equivalent functionality to Jiliac/MTGO-listener using MTGOSDK patterns with detailed documentation of listener workflow and current implementation status
4. WHEN combining data sources THEN the system SHALL merge data exactly as done in Jiliac/MTGODecklistCache with documentation of merge logic and current pipeline code
5. IF external repositories are unavailable THEN the system SHALL use locally implemented equivalents with identical behavior and comprehensive documentation of differences

### Requirement 2: Step 2 Data Treatment Reproduction

**User Story:** As a data analyst, I want the system to process raw tournament data exactly as the original workflow, so that archetype classification and data categorization matches the original system's output.

#### Acceptance Criteria

1. WHEN processing raw decklists THEN the system SHALL implement the exact parsing logic from Badaro/MTGOArchetypeParser
2. WHEN applying archetype rules THEN the system SHALL use the complete rule set from Badaro/MTGOFormatData maintained by Jiliac and iamactuallylvl1
3. WHEN categorizing by format THEN the system SHALL produce processed data identical to the original workflow's output
4. WHEN encountering unknown conditions THEN the system SHALL handle them using the same fallback logic as the original parsers
5. IF archetype rules are updated THEN the system SHALL maintain backward compatibility with existing classifications

### Requirement 3: Step 3 Visualization Reproduction and Enhancement

**User Story:** As an analyst, I want the system to generate visualizations that match or exceed the quality of current Manalytics reports while maintaining compatibility with the original workflow outputs, so that I preserve the excellent work already accomplished.

#### Acceptance Criteria

1. WHEN generating matchup matrices THEN the system SHALL produce outputs that match the quality and format of current Manalytics analyses while being compatible with Jiliac/R-Meta-Analysis fork
2. WHEN calculating meta-analysis statistics THEN the system SHALL preserve the current advanced analytics capabilities while using algorithms compatible with the original Aliquanto3/R-Meta-Analysis
3. WHEN creating visualizations THEN the system SHALL maintain the current professional visual style (MTGGoldfish/17lands standard) and expert color system already implemented
4. WHEN generating final reports THEN the system SHALL produce outputs that match the structure and quality of current Manalytics dashboard reports
5. IF enhancements are made THEN the system SHALL preserve backward compatibility with existing report formats and maintain all current analytical features

### Requirement 4: Workflow Integration and Validation

**User Story:** As a system validator, I want to verify that the reproduced workflow produces identical results to the original system, so that I can confirm complete fidelity of the reproduction.

#### Acceptance Criteria

1. WHEN comparing tournament data collection THEN the reproduced system SHALL collect the same tournaments as the original fbettega/mtg_decklist_scrapper
2. WHEN comparing archetype classification THEN the reproduced system SHALL classify decks identically to the original MTGOArchetypeParser + MTGOFormatData combination
3. WHEN comparing analysis outputs THEN the reproduced system SHALL generate statistics identical to the original R-Meta-Analysis implementation
4. WHEN validating data flow THEN each step SHALL produce intermediate outputs that match the original workflow's intermediate data
5. IF discrepancies are found THEN the system SHALL provide detailed comparison reports identifying the differences

### Requirement 5: Current System Issue Resolution

**User Story:** As a system operator, I want to resolve the specific issues preventing the current Manalytics system from working correctly, so that the reproduction process can proceed without blockers.

#### Acceptance Criteria

1. WHEN the Melee API returns 403 errors THEN the system SHALL diagnose and resolve authentication or access issues
2. WHEN Leagues Analysis encounters empty DataFrames THEN the system SHALL handle edge cases gracefully without crashing
3. WHEN ArchetypeEngine encounters unknown conditions THEN the system SHALL implement missing rule definitions locally
4. WHEN processing tournament data THEN the system SHALL validate data completeness before analysis
5. IF current integrations fail THEN the system SHALL provide detailed diagnostic information for troubleshooting

### Requirement 6: System Consolidation and Independence

**User Story:** As a project maintainer, I want a unified system that operates independently of external repositories, so that the system remains stable and maintainable long-term.

#### Acceptance Criteria

1. WHEN the system is deployed THEN it SHALL operate without requiring access to any external GitHub repositories
2. WHEN archetype rules need updates THEN the system SHALL use internal rule management instead of external MTGOFormatData
3. WHEN new tournament sources are added THEN the system SHALL integrate them using the internal scraping framework
4. IF external APIs change THEN the system SHALL continue operating using internal implementations
5. WHEN the system is handed off to new maintainers THEN it SHALL be completely self-contained and documented

### Requirement 7: Step-by-Step Reproduction Process

**User Story:** As a system implementer, I want a methodical approach to reproducing the original workflow, so that I can ensure each component is correctly implemented before moving to the next.

#### Acceptance Criteria

1. WHEN starting reproduction THEN the system SHALL implement Step 1 (Data Collection) completely before proceeding to Step 2
2. WHEN Step 1 is complete THEN the system SHALL validate data collection against original fbettega outputs before proceeding
3. WHEN implementing Step 2 THEN the system SHALL use the validated Step 1 outputs as input for data treatment
4. WHEN Step 2 is complete THEN the system SHALL validate archetype classification against original parser outputs
5. WHEN implementing Step 3 THEN the system SHALL use validated Step 2 outputs to generate visualizations identical to the original

### Requirement 8: Preservation of Existing Work and Quality

**User Story:** As the project owner, I want to preserve all the excellent work already accomplished in the current Manalytics system, so that the reproduction process enhances rather than replaces the existing capabilities.

#### Acceptance Criteria

1. WHEN implementing new components THEN the system SHALL preserve all current analytical features and visualization capabilities
2. WHEN reproducing original workflow components THEN the system SHALL enhance rather than replace existing functionality where current implementation is superior
3. WHEN generating reports THEN the system SHALL maintain the current high-quality dashboard format and professional appearance
4. WHEN consolidating systems THEN the system SHALL preserve all current advanced features (18 analytical features, expert color system, accessibility compliance)
5. IF changes are made to existing components THEN the system SHALL ensure no regression in quality or functionality

### Requirement 9: Continuous Integration and Progress Preservation

**User Story:** As the project owner, I want regular commits and pushes to the GitHub repository, so that no work is lost and progress is continuously preserved.

#### Acceptance Criteria

1. WHEN implementing any component THEN the developer SHALL commit and push changes to https://github.com/gbordes77/Manalytics at least every 20 minutes of active work
2. WHEN completing any sub-task THEN the developer SHALL immediately commit and push the completed work with descriptive commit messages
3. WHEN making significant progress THEN the developer SHALL push intermediate working states even if not fully complete
4. WHEN encountering blockers THEN the developer SHALL commit and push current state before investigating solutions
5. IF work sessions end THEN the developer SHALL ensure all progress is committed and pushed to prevent any loss of work

### Requirement 10: Documentation and Knowledge Transfer

**User Story:** As a future maintainer, I want comprehensive documentation of the reproduction process and system architecture, so that I can understand and maintain the system effectively.

#### Acceptance Criteria

1. WHEN each step is implemented THEN the system SHALL document the exact mapping from original repositories to internal implementation with side-by-side comparison of original process, Jilliac pipeline code, and current implementation
2. WHEN reproducing algorithms THEN the system SHALL document the source repository and specific implementation being replicated with detailed code analysis
3. WHEN consolidating components THEN the system SHALL maintain clear traceability to original workflow components with comprehensive documentation of each transformation
4. IF implementation differs from original THEN the system SHALL document the reasons and implications of the differences with detailed technical justification
5. WHEN the system is complete THEN it SHALL include comprehensive handoff documentation for new team members with complete workflow reproduction guide
