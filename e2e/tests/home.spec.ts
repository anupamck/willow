import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
    await page.goto('./');
});

test('home page has the correct layout', async ({ page }) => {
    await expect(page).toHaveURL('/');
    await expect(page.getByRole('heading', { name: 'Home' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Contacts' })).toBeVisible();
    await expect(page.getByRole('table', {  name: /home\-table/i})).toBeVisible();
});

