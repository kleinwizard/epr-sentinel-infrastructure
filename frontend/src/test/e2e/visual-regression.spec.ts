import { test, expect } from '@playwright/test'

test.describe('Visual Regression Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should match login page screenshot', async ({ page }) => {
    await expect(page).toHaveScreenshot('login-page.png')
  })

  test('should match dashboard screenshot', async ({ page }) => {
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'testpassword123')
    await page.click('button[type="submit"]')
    
    await expect(page).toHaveScreenshot('dashboard-page.png')
  })

  test('should match products page screenshot', async ({ page }) => {
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'testpassword123')
    await page.click('button[type="submit"]')
    await page.click('text=Products')
    
    await expect(page).toHaveScreenshot('products-page.png')
  })

  test('should match product modal screenshot', async ({ page }) => {
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'testpassword123')
    await page.click('button[type="submit"]')
    await page.click('text=Products')
    await page.click('[data-testid="add-product-button"]')
    
    await expect(page.locator('[data-testid="product-modal"]')).toHaveScreenshot('product-modal.png')
  })

  test('should match fees page screenshot', async ({ page }) => {
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'testpassword123')
    await page.click('button[type="submit"]')
    await page.click('text=Fees')
    
    await expect(page).toHaveScreenshot('fees-page.png')
  })

  test('should match reports page screenshot', async ({ page }) => {
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'testpassword123')
    await page.click('button[type="submit"]')
    await page.click('text=Reports')
    
    await expect(page).toHaveScreenshot('reports-page.png')
  })

  test('should match mobile login screenshot', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 })
    await expect(page).toHaveScreenshot('mobile-login-page.png')
  })

  test('should match mobile dashboard screenshot', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 })
    
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'testpassword123')
    await page.click('button[type="submit"]')
    
    await expect(page).toHaveScreenshot('mobile-dashboard-page.png')
  })

  test('should match error states', async ({ page }) => {
    await page.click('button[type="submit"]')
    
    await expect(page).toHaveScreenshot('login-validation-errors.png')
  })

  test('should match loading states', async ({ page }) => {
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'testpassword123')
    await page.click('button[type="submit"]')
    
    await expect(page.locator('[data-testid="loading-spinner"]')).toHaveScreenshot('loading-spinner.png')
  })
})
