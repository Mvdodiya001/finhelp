import { test, expect } from '@playwright/test';

test.describe('FinHelp E2E Tests', () => {
  test('should load the homepage and display the login screen initially', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h2:has-text("Secure Access")')).toBeVisible();
  });

  test('should login and display empty state', async ({ page }) => {
    await page.goto('/');
    
    // Mock the backend API for token login
    await page.route('**/api/token', async route => {
      await route.fulfill({ json: { access_token: 'fake-token' } });
    });

    await page.fill('input[placeholder="Username"]', 'testuser');
    await page.fill('input[placeholder="Password"]', 'testpass');
    await page.click('button:has-text("Authenticate")');

    // Check if the empty state is visible after login
    const emptyState = page.locator('.empty-state');
    await expect(emptyState).toBeVisible({ timeout: 10000 });
    
    // Check if header elements exist
    await expect(page.locator('header')).toBeVisible();
    await expect(page.locator('text=FinHelp')).toBeVisible();
  });

  test('should allow entering a ticker and fetching analysis', async ({ page }) => {
    await page.goto('/');

    // Mock login
    await page.route('**/api/token', async route => {
      await route.fulfill({ json: { access_token: 'fake-token' } });
    });

    await page.fill('input[placeholder="Username"]', 'testuser');
    await page.fill('input[placeholder="Password"]', 'testpass');
    await page.click('button:has-text("Authenticate")');

    // Wait for login to complete and main app to show
    await expect(page.locator('header')).toBeVisible({ timeout: 10000 });

    // We locate the search input using its accessible name
    const searchInput = page.getByRole('combobox', { name: /Ticker/i });
    await expect(searchInput).toBeVisible();

    // Fill in a ticker
    await searchInput.fill('AAPL');

    // Click the Execute button
    const executeButton = page.getByRole('button', { name: /EXECUTE/i });
    await expect(executeButton).toBeVisible();
    await executeButton.click();

    // Verify loading skeletons appear
    const skeleton = page.locator('.skeleton-hero');
    await expect(skeleton).toBeVisible();

    // Note: To fully test this, the backend will attempt to fetch real data for AAPL
    // So we just verify that the loading state triggers correctly for this E2E test.
  });
});
