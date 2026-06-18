#!/bin/bash

echo "============================================="
echo "   FinHelp - E2E Tests      "
echo "============================================="

# Ensure Playwright is installed in the frontend
cd frontend
echo "-> Installing Playwright testing dependencies..."
npm install -D @playwright/test

echo "-> Installing Playwright browsers (if needed)..."
npx playwright install chromium

# Run the Playwright tests
echo "-> Running Playwright E2E test suite..."
echo "(This will automatically start the frontend and backend servers as configured in playwright.config.js)"
echo ""

npx playwright test

TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ E2E Testing Completed Successfully!"
else
    echo ""
    echo "❌ E2E Testing Failed!"
fi

exit $TEST_EXIT_CODE
