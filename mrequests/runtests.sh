export MICROPYPATH="$(pwd):$MICROPYPATH"

for testsuite in tests/test_*.py; do
    echo "Running tests in $testsuite..."
    micropython "$testsuite" "$@"
done
