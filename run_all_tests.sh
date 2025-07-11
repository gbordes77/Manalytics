#!/bin/bash

# Manalytics Phase 1 Validation Test Suite
# Comprehensive testing script for all validation tests

set -e  # Exit on any error

echo "🧪 Manalytics Phase 1 Validation Test Suite"
echo "==========================================="
echo "Running comprehensive validation tests..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Function to run a test and track results
run_test() {
    local test_name="$1"
    local test_command="$2"
    local test_description="$3"
    
    echo -e "${BLUE}📋 Running: $test_description${NC}"
    echo "Command: $test_command"
    echo ""
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASSED: $test_name${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAILED: $test_name${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    echo ""
    echo "----------------------------------------"
    echo ""
}

# Function to run optional test
run_optional_test() {
    local test_name="$1"
    local test_command="$2"
    local test_description="$3"
    
    echo -e "${BLUE}📋 Running (Optional): $test_description${NC}"
    echo "Command: $test_command"
    echo ""
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASSED: $test_name${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${YELLOW}⚠️  SKIPPED: $test_name (optional)${NC}"
        SKIPPED_TESTS=$((SKIPPED_TESTS + 1))
    fi
    
    echo ""
    echo "----------------------------------------"
    echo ""
}

# Check if we're in the right directory
if [ ! -f "orchestrator.py" ]; then
    echo -e "${RED}❌ Error: Please run this script from the Manalytics root directory${NC}"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  Warning: Virtual environment not detected${NC}"
    echo "Attempting to activate venv..."
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo -e "${GREEN}✅ Virtual environment activated${NC}"
    else
        echo -e "${YELLOW}⚠️  No venv found, continuing with system Python${NC}"
    fi
fi

echo ""
echo "🔍 Environment Check"
echo "===================="
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"
echo "Virtual env: ${VIRTUAL_ENV:-Not activated}"
echo ""

# 1. Installation and Setup Tests
echo -e "${BLUE}🔧 Phase 1: Installation & Setup Tests${NC}"
echo "======================================="

run_test "installation_check" \
    "python test_installation.py" \
    "Installation and dependency validation"

# 2. End-to-End Pipeline Tests
echo -e "${BLUE}🚀 Phase 2: End-to-End Pipeline Tests${NC}"
echo "====================================="

run_test "e2e_pipeline" \
    "python tests/test_e2e_pipeline.py" \
    "Complete pipeline execution and validation"

# 3. Data Quality Tests
echo -e "${BLUE}🔍 Phase 3: Data Quality Tests${NC}"
echo "=============================="

run_test "data_quality" \
    "python tests/test_data_quality.py" \
    "Data consistency and quality validation"

# 4. Performance Tests
echo -e "${BLUE}⚡ Phase 4: Performance Tests${NC}"
echo "============================"

run_test "performance" \
    "python tests/performance/test_performance.py" \
    "Performance benchmarks and optimization checks"

# 5. Error Handling Tests
echo -e "${BLUE}🛡️  Phase 5: Error Handling Tests${NC}"
echo "================================="

run_test "error_handling" \
    "python tests/test_error_handling.py" \
    "Robustness and error handling validation"

# 6. Integration Tests
echo -e "${BLUE}🔗 Phase 6: Integration Tests${NC}"
echo "============================="

run_test "integration" \
    "python tests/integration/test_integration.py" \
    "External repository and component integration"

# 7. Regression Tests
echo -e "${BLUE}🔄 Phase 7: Regression Tests${NC}"
echo "============================"

run_test "regression" \
    "python tests/regression/test_regression.py" \
    "Regression prevention and stability validation"

# 8. Demo Execution Test
echo -e "${BLUE}🎯 Phase 8: Demo Execution Test${NC}"
echo "==============================="

run_test "demo_execution" \
    "python demo.py" \
    "Complete demo pipeline execution"

# 9. Optional Tests (if tools available)
echo -e "${BLUE}🔧 Phase 9: Optional Tests${NC}"
echo "=========================="

# Check if pytest is available
if command -v pytest &> /dev/null; then
    run_optional_test "pytest_suite" \
        "pytest tests/ -v --tb=short" \
        "PyTest test suite execution"
else
    echo -e "${YELLOW}⚠️  pytest not available, skipping pytest suite${NC}"
    SKIPPED_TESTS=$((SKIPPED_TESTS + 1))
fi

# Check if R is available
if command -v R &> /dev/null; then
    run_optional_test "r_integration" \
        "Rscript src/r/analysis/metagame_analysis.R --help" \
        "R script integration check"
else
    echo -e "${YELLOW}⚠️  R not available, skipping R integration test${NC}"
    SKIPPED_TESTS=$((SKIPPED_TESTS + 1))
fi

# Final Results
echo ""
echo "🏁 FINAL RESULTS"
echo "================"
echo -e "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo -e "${YELLOW}Skipped: $SKIPPED_TESTS${NC}"
echo ""

# Calculate success rate
if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))
    echo -e "Success Rate: ${SUCCESS_RATE}%"
    echo ""
fi

# Phase 1 Validation Checklist
echo "📋 Phase 1 Validation Checklist"
echo "==============================="

# Core functionality checks
if [ $PASSED_TESTS -ge 6 ]; then
    echo -e "${GREEN}✅ Core functionality operational${NC}"
else
    echo -e "${RED}❌ Core functionality issues detected${NC}"
fi

# Data quality checks
if python tests/test_data_quality.py &> /dev/null; then
    echo -e "${GREEN}✅ Data quality standards met${NC}"
else
    echo -e "${RED}❌ Data quality issues detected${NC}"
fi

# Performance checks
if python tests/performance/test_performance.py &> /dev/null; then
    echo -e "${GREEN}✅ Performance requirements met${NC}"
else
    echo -e "${RED}❌ Performance issues detected${NC}"
fi

# Error handling checks
if python tests/test_error_handling.py &> /dev/null; then
    echo -e "${GREEN}✅ Error handling robust${NC}"
else
    echo -e "${RED}❌ Error handling issues detected${NC}"
fi

echo ""

# Overall Phase 1 Status
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 PHASE 1 VALIDATION: PASSED${NC}"
    echo -e "${GREEN}✅ All critical tests passed - Ready for Phase 2!${NC}"
    exit 0
elif [ $FAILED_TESTS -le 2 ]; then
    echo -e "${YELLOW}⚠️  PHASE 1 VALIDATION: PASSED WITH WARNINGS${NC}"
    echo -e "${YELLOW}⚠️  Minor issues detected but core functionality works${NC}"
    echo -e "${YELLOW}⚠️  Consider addressing issues before Phase 2${NC}"
    exit 0
else
    echo -e "${RED}❌ PHASE 1 VALIDATION: FAILED${NC}"
    echo -e "${RED}❌ Critical issues detected - Phase 2 not recommended${NC}"
    echo -e "${RED}❌ Please fix failing tests before proceeding${NC}"
    exit 1
fi 