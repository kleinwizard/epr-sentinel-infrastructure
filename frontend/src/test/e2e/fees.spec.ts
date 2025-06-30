import { test, expect } from '@playwright/test'

test.describe('EPR Fees Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'testpassword123')
    await page.click('button[type="submit"]')
    await page.click('text=Fees')
    await expect(page).toHaveURL('/fees')
  })

  test('should display fees overview', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('EPR Fees')
    
    await expect(page.locator('[data-testid="fee-calculator"]')).toBeVisible()
    await expect(page.locator('[data-testid="fee-summary"]')).toBeVisible()
    await expect(page.locator('[data-testid="payment-history"]')).toBeVisible()
  })

  test('should calculate fees for products', async ({ page }) => {
    await page.click('[data-testid="select-products-button"]')
    
    await expect(page.locator('[data-testid="product-selection-modal"]')).toBeVisible()
    
    await page.check('[data-testid="product-checkbox-1"]')
    await page.check('[data-testid="product-checkbox-2"]')
    
    await page.click('[data-testid="calculate-fees-button"]')
    
    await expect(page.locator('[data-testid="fee-breakdown"]')).toBeVisible()
    await expect(page.locator('[data-testid="total-fee"]')).toContainText('$')
  })

  test('should show fee breakdown by material', async ({ page }) => {
    await page.click('[data-testid="select-products-button"]')
    await page.check('[data-testid="product-checkbox-1"]')
    await page.click('[data-testid="calculate-fees-button"]')
    
    await expect(page.locator('[data-testid="plastic-fee"]')).toBeVisible()
    await expect(page.locator('[data-testid="metal-fee"]')).toBeVisible()
    await expect(page.locator('[data-testid="glass-fee"]')).toBeVisible()
  })

  test('should process payment', async ({ page }) => {
    await page.click('[data-testid="select-products-button"]')
    await page.check('[data-testid="product-checkbox-1"]')
    await page.click('[data-testid="calculate-fees-button"]')
    
    await page.click('[data-testid="pay-now-button"]')
    
    await expect(page.locator('[data-testid="payment-modal"]')).toBeVisible()
    
    await page.fill('[data-testid="card-number"]', '4242424242424242')
    await page.fill('[data-testid="card-expiry"]', '12/25')
    await page.fill('[data-testid="card-cvc"]', '123')
    
    await page.click('[data-testid="submit-payment"]')
    
    await expect(page.locator('text=Payment successful')).toBeVisible()
  })

  test('should display payment history', async ({ page }) => {
    const historyTable = page.locator('[data-testid="payment-history-table"]')
    await expect(historyTable).toBeVisible()
    
    await expect(historyTable.locator('th')).toContainText(['Date', 'Amount', 'Status', 'Invoice'])
  })

  test('should download invoice', async ({ page }) => {
    const downloadPromise = page.waitForEvent('download')
    await page.click('[data-testid="download-invoice-button"]')
    
    const download = await downloadPromise
    expect(download.suggestedFilename()).toMatch(/invoice.*\.pdf/)
  })

  test('should filter payment history', async ({ page }) => {
    await page.fill('[data-testid="date-from"]', '2024-01-01')
    await page.fill('[data-testid="date-to"]', '2024-12-31')
    await page.click('[data-testid="apply-filter"]')
    
    await expect(page.locator('[data-testid="payment-history-table"] tbody tr')).toHaveCountGreaterThan(0)
  })

  test('should show fee rate information', async ({ page }) => {
    await page.click('[data-testid="fee-rates-info"]')
    
    await expect(page.locator('[data-testid="rates-modal"]')).toBeVisible()
    await expect(page.locator('text=Current EPR Rates')).toBeVisible()
    
    await expect(page.locator('[data-testid="rates-table"]')).toBeVisible()
  })
})
