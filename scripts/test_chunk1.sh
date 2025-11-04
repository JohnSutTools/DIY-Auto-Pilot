#!/bin/bash
# Comprehensive test suite for Chunk 1 - CarParams Setup
# Tests setup and verification in WSL environment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "======================================================================"
echo "  Chunk 1 Test Suite - CarParams Setup"
echo "======================================================================"
echo ""

# Function to print test results
print_test() {
    local status=$1
    local message=$2
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✓${NC} $message"
    elif [ "$status" = "FAIL" ]; then
        echo -e "${RED}✗${NC} $message"
        return 1
    elif [ "$status" = "WARN" ]; then
        echo -e "${YELLOW}⚠${NC} $message"
    else
        echo -e "${BLUE}ℹ${NC} $message"
    fi
}

# Find project root (handle Windows path in WSL)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Test Environment:"
echo "  Script Dir:   $SCRIPT_DIR"
echo "  Project Root: $PROJECT_ROOT"
echo "  User:         $(whoami)"
echo "  OS:           $(uname -s)"
echo ""

# Test 1: Check directory structure
echo "======================================================================"
echo "Test 1: Directory Structure"
echo "======================================================================"

test1_passed=true

if [ -d "$PROJECT_ROOT/openpilot/openpilot" ]; then
    print_test "PASS" "Openpilot directory exists"
else
    print_test "FAIL" "Openpilot directory NOT found at $PROJECT_ROOT/openpilot/openpilot"
    test1_passed=false
fi

if [ -f "$PROJECT_ROOT/scripts/setup_mock_carparams.py" ]; then
    print_test "PASS" "setup_mock_carparams.py exists"
else
    print_test "FAIL" "setup_mock_carparams.py NOT found"
    test1_passed=false
fi

if [ -f "$PROJECT_ROOT/scripts/test_carparams.py" ]; then
    print_test "PASS" "test_carparams.py exists"
else
    print_test "FAIL" "test_carparams.py NOT found"
    test1_passed=false
fi

echo ""

if [ "$test1_passed" = false ]; then
    echo -e "${RED}Test 1 FAILED - Fix directory structure first${NC}"
    exit 1
fi

# Test 2: Check openpilot installation
echo "======================================================================"
echo "Test 2: Openpilot Installation"
echo "======================================================================"

test2_passed=true
OPENPILOT_PATH="$PROJECT_ROOT/openpilot/openpilot"

if [ -d "$OPENPILOT_PATH/selfdrive" ]; then
    print_test "PASS" "selfdrive/ directory exists"
else
    print_test "FAIL" "selfdrive/ directory NOT found"
    test2_passed=false
fi

if [ -d "$OPENPILOT_PATH/cereal" ]; then
    print_test "PASS" "cereal/ directory exists"
else
    print_test "FAIL" "cereal/ directory NOT found"
    test2_passed=false
fi

if [ -d "$OPENPILOT_PATH/.venv" ]; then
    print_test "PASS" "Python venv exists"
    VENV_EXISTS=true
else
    print_test "WARN" "Python venv NOT found (openpilot needs to be built)"
    VENV_EXISTS=false
fi

echo ""

if [ "$test2_passed" = false ]; then
    echo -e "${RED}Test 2 FAILED - Openpilot installation incomplete${NC}"
    exit 1
fi

# Test 3: Try to import openpilot modules (if venv exists)
echo "======================================================================"
echo "Test 3: Python Environment"
echo "======================================================================"

if [ "$VENV_EXISTS" = true ]; then
    cd "$OPENPILOT_PATH"
    source .venv/bin/activate
    
    # Test if we can import cereal
    if python3 -c "from cereal import car; print('OK')" 2>/dev/null | grep -q "OK"; then
        print_test "PASS" "Can import cereal module"
    else
        print_test "FAIL" "Cannot import cereal module"
        echo "  Error output:"
        python3 -c "from cereal import car" 2>&1 | head -5 | sed 's/^/    /'
        exit 1
    fi
    
    # Test if we can import Params
    if python3 -c "from openpilot.common.params import Params; print('OK')" 2>/dev/null | grep -q "OK"; then
        print_test "PASS" "Can import Params module"
    else
        print_test "FAIL" "Cannot import Params module"
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
else
    print_test "WARN" "Skipping Python tests (venv not found)"
    echo ""
    echo -e "${YELLOW}To build openpilot:${NC}"
    echo "  cd $OPENPILOT_PATH"
    echo "  scons -j4"
    echo ""
    exit 1
fi

echo ""

# Test 4: Run setup_mock_carparams.py
echo "======================================================================"
echo "Test 4: CarParams Setup"
echo "======================================================================"

# Clear any existing CarParams first
echo "Clearing existing CarParams (if any)..."
python3 -c "from openpilot.common.params import Params; p = Params(); p.remove('CarParams'); p.remove('CarParamsCache'); p.remove('CarParamsPersistent')" 2>/dev/null || true

echo "Running setup_mock_carparams.py..."
echo ""

if python3 "$PROJECT_ROOT/scripts/setup_mock_carparams.py"; then
    print_test "PASS" "setup_mock_carparams.py executed successfully"
else
    print_test "FAIL" "setup_mock_carparams.py failed"
    exit 1
fi

echo ""

# Test 5: Verify CarParams was created
echo "======================================================================"
echo "Test 5: CarParams Verification"
echo "======================================================================"

# Check if params exist
python3 << 'PYTHON_CHECK'
import sys
sys.path.insert(0, 'openpilot/openpilot')

from cereal import car
from openpilot.common.params import Params

params = Params()

# Check all three keys
keys = ["CarParams", "CarParamsCache", "CarParamsPersistent"]
all_present = True

for key in keys:
    data = params.get(key)
    if data:
        print(f"✓ {key}: {len(data)} bytes")
    else:
        print(f"✗ {key}: MISSING")
        all_present = False
        sys.exit(1)

# Parse CarParams
cp_bytes = params.get("CarParams")
CP = car.CarParams.from_bytes(cp_bytes)

print(f"\n✓ Parsed CarParams successfully")
print(f"  - Fingerprint: {CP.carFingerprint}")
print(f"  - Brand: {CP.brand}")
print(f"  - notCar: {CP.notCar}")

# Validate critical fields
if CP.notCar != True:
    print(f"✗ notCar should be True, got {CP.notCar}")
    sys.exit(1)

if CP.openpilotLongitudinalControl != False:
    print(f"✗ openpilotLongitudinalControl should be False, got {CP.openpilotLongitudinalControl}")
    sys.exit(1)

print("\n✓ All critical fields validated")
PYTHON_CHECK

if [ $? -eq 0 ]; then
    print_test "PASS" "CarParams verification completed"
else
    print_test "FAIL" "CarParams verification failed"
    exit 1
fi

echo ""

# Test 6: Run test_carparams.py
echo "======================================================================"
echo "Test 6: Run test_carparams.py"
echo "======================================================================"

if python3 "$PROJECT_ROOT/scripts/test_carparams.py"; then
    print_test "PASS" "test_carparams.py executed successfully"
else
    print_test "FAIL" "test_carparams.py failed"
    exit 1
fi

echo ""

# Test 7: Test that controlsd can import CarParams
echo "======================================================================"
echo "Test 7: Controlsd CarParams Access"
echo "======================================================================"

python3 << 'PYTHON_CHECK'
import sys
sys.path.insert(0, 'openpilot/openpilot')

from cereal import car
import cereal.messaging as messaging
from openpilot.common.params import Params

# Simulate what controlsd does
params = Params()
CP_bytes = params.get("CarParams", block=False)

if CP_bytes is None:
    print("✗ CarParams not accessible (block=False)")
    sys.exit(1)

print("✓ CarParams accessible with block=False")

CP = messaging.log_from_bytes(CP_bytes, car.CarParams)
print(f"✓ Successfully loaded with messaging.log_from_bytes")
print(f"  - Car fingerprint: {CP.carFingerprint}")
print(f"  - Steering type: {CP.steerControlType}")

# Check if we can create a controlsd-like object
print("\n✓ Simulated controlsd CarParams access successful")
PYTHON_CHECK

if [ $? -eq 0 ]; then
    print_test "PASS" "Controlsd can access CarParams"
else
    print_test "FAIL" "Controlsd cannot access CarParams"
    exit 1
fi

echo ""

# Final summary
echo "======================================================================"
echo "  Test Results Summary"
echo "======================================================================"
echo ""
echo -e "${GREEN}✅ All tests PASSED!${NC}"
echo ""
echo "Chunk 1 is working correctly. Key achievements:"
echo "  ✓ CarParams created and saved"
echo "  ✓ notCar mode enabled"
echo "  ✓ LKAS-only configuration set"
echo "  ✓ Accessible by openpilot processes"
echo ""
echo "======================================================================"
echo "  Ready for Chunk 2!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "  1. Fix bridge message handling (Chunk 2)"
echo "  2. Update process launcher (Chunk 3)"
echo "  3. Full system test (Chunk 4)"
echo ""

exit 0
