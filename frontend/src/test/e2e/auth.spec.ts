import { test, expect } from '@playwright/test'

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should display login form', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Sign In')
    await expect(page.locator('input[type="email"]')).toBeVisible()
    await expect(page.locator('input[type="password"]')).toBeVisible()
    await expect(page.locator('button[type="submit"]')).toBeVisible()
  })

  test('should show validation errors for empty form', async ({ page }) => {
    await page.click('button[type="submit"]')
    await expect(page.locator('text=Email is required')).toBeVisible()
    await expect(page.locator('text=Password is required')).toBeVisible()
  })

  test('should login with valid credentials', async ({ page }) => {
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'testpassword123')
    await page.click('button[type="submit"]')
    
    await expect(page).toHaveURL('/dashboard')
    await expect(page.locator('h1')).toContainText('Dashboard')
  })

  test('should show error for invalid credentials', async ({ page }) => {
    await page.fill('input[type="email"]', 'invalid@example.com')
    await page.fill('input[type="password"]', 'wrongpassword')
    await page.click('button[type="submit"]')
    
    await expect(page.locator('text=Invalid credentials')).toBeVisible()
  })

  test('should navigate to registration page', async ({ page }) => {
    await page.click('text=Sign up')
    await expect(page).toHaveURL('/register')
    await expect(page.locator('h1')).toContainText('Create Account')
  })

  test('should register new user', async ({ page }) => {
    await page.goto('/register')
    
    await page.fill('input[name="email"]', 'newuser@example.com')
    await page.fill('input[name="username"]', 'newuser')
    await page.fill('input[name="password"]', 'newpassword123')
    await page.fill('input[name="confirmPassword"]', 'newpassword123')
    await page.click('button[type="submit"]')
    
    await expect(page).toHaveURL('/dashboard')
  })

  test('should logout user', async ({ page }) => {
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'testpassword123')
    await page.click('button[type="submit"]')
    
    await expect(page).toHaveURL('/dashboard')
    
    await page.click('[data-testid="user-menu"]')
    await page.click('text=Logout')
    
    await expect(page).toHaveURL('/')
    await expect(page.locator('h1')).toContainText('Sign In')
  })
})
