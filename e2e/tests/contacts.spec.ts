import { test, expect } from '@playwright/test';
import { deleteTestContactRows } from '../helper/contacts';
import { createTestContactRow } from '../helper/contacts';

test.beforeEach(async ({ page }) => {
    await page.goto('./contacts');
    await deleteTestContactRows(page);
});

test('contacts page has the correct layout', async ({ page }) => {
    await expect(page).toHaveURL('/contacts');
    await expect(page.getByRole('heading', { name: 'My Contacts' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Home' })).toBeVisible();
    await expect(page.getByRole('table', {  name: /contacts\-table/i})).toBeVisible();
    await expect(page.getByRole('button', { name: 'Add Contact' })).toBeVisible();
});

test('should be able to edit test contact', async ({ page }) => {
    await page.goto('./contacts');
    await createTestContactRow(page);
    const testUserRow = page.getByRole('row')
        .filter({ hasText: 'Test User' })
        .filter({ hasText: '20' });
    await testUserRow.getByRole('button', { name: 'Edit' }).click();
    // give me a regex to ensure that the url contains 'update_contact'
    await expect(page).toHaveURL(/\/update_contact\/.*/)
    await expect(page.getByLabel('Name:')).toHaveValue('Test User');
    await expect(page.getByLabel('Frequency:')).toHaveValue('20');
    await page.getByLabel('Name:').fill('Test User 2');
    await page.getByLabel('Frequency:').fill('30');
    await page.getByRole('button', { name: 'Save Changes' }).click();
    await expect(page).toHaveURL('/contacts');
    const editedRow = page.getByRole('row')
        .filter({ hasText: 'Test User 2' })
        .filter({ hasText: '30' });
    expect(await editedRow.count()).toBe(1);
});


