import { test, expect } from '@playwright/test'

test.describe('Compliance Reports', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'testpassword123')
    await page.click('button[type="submit"]')
    await page.click('text=Reports')
    await expect(page).toHaveURL('/reports')
  })

  test('should display reports overview', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Compliance Reports')
    
    await expect(page.locator('[data-testid="reports-table"]')).toBeVisible()
    await expect(page.locator('[data-testid="generate-report-button"]')).toBeVisible()
  })

  test('should generate new report', async ({ page }) => {
    await page.click('[data-testid="generate-report-button"]')
    
    await expect(page.locator('[data-testid="report-modal"]')).toBeVisible()
    await expect(page.locator('h2')).toContainText('Generate Report')
    
    await page.fill('input[name="title"]', 'Q1 2024 Compliance Report')
    await page.selectOption('select[name="type"]', 'quarterly')
    await page.fill('input[name="startDate"]', '2024-01-01')
    await page.fill('input[name="endDate"]', '2024-03-31')
    
    await page.click('button[type="submit"]')
    
    await expect(page.locator('text=Report generation started')).toBeVisible()
  })

  test('should display report status', async ({ page }) => {
    const statusCell = page.locator('[data-testid="report-status"]').first()
    await expect(statusCell).toContainText(['Processing', 'Completed', 'Failed'])
  })

  test('should download completed report', async ({ page }) => {
    const downloadButton = page.locator('[data-testid="download-report-button"]').first()
    
    if (await downloadButton.isVisible()) {
      const downloadPromise = page.waitForEvent('download')
      await downloadButton.click()
      
      const download = await downloadPromise
      expect(download.suggestedFilename()).toMatch(/.*\.pdf/)
    }
  })

  test('should view report details', async ({ page }) => {
    await page.click('[data-testid="view-report-button"]')
    
    await expect(page.locator('[data-testid="report-details-modal"]')).toBeVisible()
    
    await expect(page.locator('[data-testid="report-title"]')).toBeVisible()
    await expect(page.locator('[data-testid="report-period"]')).toBeVisible()
    await expect(page.locator('[data-testid="report-summary"]')).toBeVisible()
  })

  test('should filter reports by status', async ({ page }) => {
    await page.selectOption('[data-testid="status-filter"]', 'completed')
    
    const rows = page.locator('[data-testid="reports-table"] tbody tr')
    await expect(rows).toHaveCountGreaterThan(0)
  })

  test('should filter reports by date range', async ({ page }) => {
    await page.fill('[data-testid="date-from"]', '2024-01-01')
    await page.fill('[data-testid="date-to"]', '2024-12-31')
    await page.click('[data-testid="apply-filter"]')
    
    await expect(page.locator('[data-testid="reports-table"] tbody tr')).toHaveCountGreaterThan(0)
  })

  test('should delete report', async ({ page }) => {
    await page.click('[data-testid="delete-report-button"]')
    
    await expect(page.locator('[data-testid="confirm-dialog"]')).toBeVisible()
    await page.click('[data-testid="confirm-delete"]')
    
    await expect(page.locator('text=Report deleted successfully')).toBeVisible()
  })

  test('should show report analytics', async ({ page }) => {
    await page.click('[data-testid="analytics-tab"]')
    
    await expect(page.locator('[data-testid="compliance-chart"]')).toBeVisible()
    await expect(page.locator('[data-testid="fee-trends-chart"]')).toBeVisible()
    await expect(page.locator('[data-testid="material-breakdown-chart"]')).toBeVisible()
  })

  test('should export report data', async ({ page }) => {
    const downloadPromise = page.waitForEvent('download')
    await page.click('[data-testid="export-data-button"]')
    
    const download = await downloadPromise
    expect(download.suggestedFilename()).toBe('reports-data.csv')
  })
})
