import { test, expect, devices } from '@playwright/test'

test.use({ ...devices['iPhone 12'] })

test.describe('Mobile Experience', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should display mobile-friendly login', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Sign In')
    
    const form = page.locator('form')
    await expect(form).toBeVisible()
    
    const submitButton = page.locator('button[type="submit"]')
    await expect(submitButton).toBeVisible()
  })

  test('should navigate with mobile menu', async ({ page }) => {
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'testpassword123')
    await page.click('button[type="submit"]')
    
    await page.click('[data-testid="mobile-menu-button"]')
    await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible()
    
    await page.click('[data-testid="mobile-menu"] text=Products')
    await expect(page).toHaveURL('/products')
  })

  test('should handle touch interactions', async ({ page }) => {
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'testpassword123')
    await page.click('button[type="submit"]')
    
    const dashboardCard = page.locator('[data-testid="dashboard-card"]').first()
    await expect(dashboardCard).toBeVisible()
    
    await dashboardCard.tap()
  })

  test('should display responsive tables', async ({ page }) => {
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'testpassword123')
    await page.click('button[type="submit"]')
    await page.click('text=Products')
    
    const table = page.locator('[data-testid="products-table"]')
    await expect(table).toBeVisible()
    
    const mobileCards = page.locator('[data-testid="product-card"]')
    if (await mobileCards.count() > 0) {
      await expect(mobileCards.first()).toBeVisible()
    }
  })

  test('should handle mobile form inputs', async ({ page }) => {
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'testpassword123')
    await page.click('button[type="submit"]')
    await page.click('text=Products')
    
    await page.click('[data-testid="add-product-button"]')
    
    const modal = page.locator('[data-testid="product-modal"]')
    await expect(modal).toBeVisible()
    
    await page.fill('input[name="name"]', 'Mobile Test Product')
    await page.fill('input[name="weight"]', '1.5')
    
    await expect(page.locator('input[name="name"]')).toHaveValue('Mobile Test Product')
  })

  test('should scroll properly on mobile', async ({ page }) => {
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'testpassword123')
    await page.click('button[type="submit"]')
    
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
    
    await page.evaluate(() => window.scrollTo(0, 0))
  })

  test('should handle mobile orientation changes', async ({ page }) => {
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'testpassword123')
    await page.click('button[type="submit"]')
    
    await page.setViewportSize({ width: 812, height: 375 })
    
    await expect(page.locator('[data-testid="sidebar"]')).toBeVisible()
    
    await page.setViewportSize({ width: 375, height: 812 })
    
    await expect(page.locator('[data-testid="mobile-menu-button"]')).toBeVisible()
  })
})
