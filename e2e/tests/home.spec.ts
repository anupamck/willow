import { test, expect } from '@playwright/test';
import { loginAs } from '../helper/login';

test.describe('User with overdue contacts', () => {
    test.beforeEach(async ({ page }) => {
        await loginAs(page, 'ashoka', process.env.TEST_USER_PASSWORD!)
    });

    test('home page has the correct layout', async ({ page }) => {
        await expect(page).toHaveURL('/home');
        await expect(page.getByRole('heading', { name: 'Long time no speak' })).toBeVisible();
        await expect(page.getByRole('link', { name: 'contacts' })).toBeVisible();
        await expect(page.getByRole('table', { name: /home\-table/i })).toBeVisible();
    });

    test('overdue user appears on homepage', async ({ page }) => {
        await expect(page.getByRole('row', { name: /Overdue Test User/i })).toBeVisible();
    });

    test('user is logged out', async ({ page }) => {
        await page.getByRole('button', { name: 'Logout' }).click();
        await expect(page).toHaveURL('/');
    });
});

test.describe('User without overdue contacts', () => {
    test.beforeEach(async ({ page }) => {
        await loginAs(page, 'chandragupta', process.env.TEST_USER_PASSWORD2!)
    });

    test('Home page should say you are all caught up', async ({ page }) => {
        await expect(page.getByText("Congratulations! You are all caught up.")).toBeVisible();
        await expect(page.getByRole('img', { name: 'A more colourful willow tree' })).toBeVisible();
        await expect(page.getByRole('link', { name: 'here' })).toBeVisible();
    });

    test('Link should open contact form', async ({ page }) => {
        await page.getByRole('link', { name: 'here' }).click();
        await expect(page).toHaveURL('/add_contact');
        await expect(page.getByLabel('Name:')).toBeVisible();
        await expect(page.getByRole('button', { name: 'Save' })).toBeVisible();
    });
});
