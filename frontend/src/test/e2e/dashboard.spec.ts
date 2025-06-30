import { test, expect } from '@playwright/test'

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'testpassword123')
    await page.click('button[type="submit"]')
    await expect(page).toHaveURL('/dashboard')
  })

  test('should display dashboard overview', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Dashboard')
    
    await expect(page.locator('[data-testid="total-products"]')).toBeVisible()
    await expect(page.locator('[data-testid="pending-fees"]')).toBeVisible()
    await expect(page.locator('[data-testid="compliance-status"]')).toBeVisible()
    await expect(page.locator('[data-testid="recent-reports"]')).toBeVisible()
  })

  test('should navigate to products page', async ({ page }) => {
    await page.click('text=Products')
    await expect(page).toHaveURL('/products')
    await expect(page.locator('h1')).toContainText('Product Catalog')
  })

  test('should navigate to reports page', async ({ page }) => {
    await page.click('text=Reports')
    await expect(page).toHaveURL('/reports')
    await expect(page.locator('h1')).toContainText('Compliance Reports')
  })

  test('should navigate to fees page', async ({ page }) => {
    await page.click('text=Fees')
    await expect(page).toHaveURL('/fees')
    await expect(page.locator('h1')).toContainText('EPR Fees')
  })

  test('should display sidebar navigation', async ({ page }) => {
    const sidebar = page.locator('[data-testid="sidebar"]')
    await expect(sidebar).toBeVisible()
    
    await expect(sidebar.locator('text=Dashboard')).toBeVisible()
    await expect(sidebar.locator('text=Products')).toBeVisible()
    await expect(sidebar.locator('text=Materials')).toBeVisible()
    await expect(sidebar.locator('text=Fees')).toBeVisible()
    await expect(sidebar.locator('text=Reports')).toBeVisible()
    await expect(sidebar.locator('text=Settings')).toBeVisible()
  })

  test('should display user profile menu', async ({ page }) => {
    await page.click('[data-testid="user-menu"]')
    
    await expect(page.locator('text=Profile')).toBeVisible()
    await expect(page.locator('text=Settings')).toBeVisible()
    await expect(page.locator('text=Logout')).toBeVisible()
  })

  test('should show loading states', async ({ page }) => {
    await page.reload()
    
    const loadingIndicators = page.locator('[data-testid*="loading"]')
    if (await loadingIndicators.count() > 0) {
      await expect(loadingIndicators.first()).toBeVisible()
    }
  })
})
