import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
    await page.goto('/');
});

test('User cannot login with incorrect username', async ({ page }) => {
    await page.getByRole('textbox', { name: 'username' }).type('wrongusername');
    await page.getByRole('textbox', { name: 'password' }).type(process.env.TEST_USER_PASSWORD!);
    await page.getByRole('button', { name: 'Login' }).click();
    await expect(page).toHaveURL('/');
    await expect(page.getByText('Incorrect username or password')).toBeVisible();
});

test('User cannot login with incorrect password', async ({ page }) => {
    await page.getByRole('textbox', { name: 'username' }).type('ashoka');
    await page.getByRole('textbox', { name: 'password' }).type('wrongpassword');
    await page.getByRole('button', { name: 'Login' }).click();
    await expect(page).toHaveURL('/');
    await expect(page.getByText('Incorrect username or password')).toBeVisible();
});

test('Test User 2 is logged into the correct database', async ({ page }) => {
    await page.getByRole('textbox', { name: 'username' }).type('chandragupta');
    await page.getByRole('textbox', { name: 'password' }).type(process.env.TEST_USER_PASSWORD2!);
    await page.getByRole('button', { name: 'Login' }).click();
    await expect(page).toHaveURL('/home');
    await expect(page.getByText("Congratulations! You are all caught up.")).toBeVisible();
});