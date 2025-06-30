import { test, expect } from '@playwright/test'

test.describe('Product Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'testpassword123')
    await page.click('button[type="submit"]')
    await page.click('text=Products')
    await expect(page).toHaveURL('/products')
  })

  test('should display product catalog', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Product Catalog')
    
    await expect(page.locator('[data-testid="products-table"]')).toBeVisible()
    await expect(page.locator('[data-testid="add-product-button"]')).toBeVisible()
  })

  test('should open add product modal', async ({ page }) => {
    await page.click('[data-testid="add-product-button"]')
    
    await expect(page.locator('[data-testid="product-modal"]')).toBeVisible()
    await expect(page.locator('h2')).toContainText('Add New Product')
    
    await expect(page.locator('input[name="name"]')).toBeVisible()
    await expect(page.locator('textarea[name="description"]')).toBeVisible()
    await expect(page.locator('select[name="category"]')).toBeVisible()
    await expect(page.locator('input[name="weight"]')).toBeVisible()
  })

  test('should create new product', async ({ page }) => {
    await page.click('[data-testid="add-product-button"]')
    
    await page.fill('input[name="name"]', 'Test Product')
    await page.fill('textarea[name="description"]', 'A test product for E2E testing')
    await page.selectOption('select[name="category"]', 'Electronics')
    await page.fill('input[name="weight"]', '2.5')
    
    await page.click('[data-testid="add-material-button"]')
    await page.selectOption('select[name="material"]', 'Plastic')
    await page.fill('input[name="percentage"]', '80')
    
    await page.click('button[type="submit"]')
    
    await expect(page.locator('[data-testid="product-modal"]')).not.toBeVisible()
    await expect(page.locator('text=Product created successfully')).toBeVisible()
  })

  test('should search products', async ({ page }) => {
    const searchInput = page.locator('[data-testid="product-search"]')
    await searchInput.fill('Test Product')
    
    await expect(page.locator('[data-testid="products-table"] tbody tr')).toHaveCount(1)
  })

  test('should filter products by category', async ({ page }) => {
    await page.selectOption('[data-testid="category-filter"]', 'Electronics')
    
    const rows = page.locator('[data-testid="products-table"] tbody tr')
    await expect(rows).toHaveCountGreaterThan(0)
  })

  test('should edit product', async ({ page }) => {
    await page.click('[data-testid="edit-product-button"]')
    
    await expect(page.locator('[data-testid="product-modal"]')).toBeVisible()
    await expect(page.locator('h2')).toContainText('Edit Product')
    
    await page.fill('input[name="name"]', 'Updated Product Name')
    await page.click('button[type="submit"]')
    
    await expect(page.locator('text=Product updated successfully')).toBeVisible()
  })

  test('should delete product', async ({ page }) => {
    await page.click('[data-testid="delete-product-button"]')
    
    await expect(page.locator('[data-testid="confirm-dialog"]')).toBeVisible()
    await page.click('[data-testid="confirm-delete"]')
    
    await expect(page.locator('text=Product deleted successfully')).toBeVisible()
  })

  test('should bulk import products', async ({ page }) => {
    await page.click('[data-testid="bulk-import-button"]')
    
    await expect(page.locator('[data-testid="import-modal"]')).toBeVisible()
    
    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles('test-data/products.csv')
    
    await page.click('[data-testid="import-submit"]')
    
    await expect(page.locator('text=Products imported successfully')).toBeVisible()
  })

  test('should export products', async ({ page }) => {
    const downloadPromise = page.waitForEvent('download')
    await page.click('[data-testid="export-button"]')
    
    const download = await downloadPromise
    expect(download.suggestedFilename()).toBe('products.csv')
  })
})
