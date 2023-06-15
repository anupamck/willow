import { test, expect } from '@playwright/test';
import { loginAs } from '../helper/login';

test.beforeEach(async ({ page }) => {
    await loginAs(page, 'ashoka', process.env.TEST_USER_PASSWORD!)
});

test('home page has the correct layout', async ({ page }) => {
    await expect(page).toHaveURL('/home');
    await expect(page.getByRole('heading', { name: 'Home' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Contacts' })).toBeVisible();
    await expect(page.getByRole('table', { name: /home\-table/i })).toBeVisible();
});

test('overdue user appears on homepage', async ({ page }) => {
    await expect(page.getByRole('row', { name: /Overdue Test User/i })).toBeVisible();
});

test('user is logged out', async ({ page }) => {
    await page.getByRole('button', { name: 'Logout' }).click();
    await expect(page).toHaveURL('/');
});
