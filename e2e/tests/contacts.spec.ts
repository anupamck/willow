import { test, expect } from '@playwright/test';
import { deleteTestContactRows } from '../helper/contacts';
import { createTestContactRow } from '../helper/contacts';
import { loginAs } from '../helper/login';

test.beforeEach(async ({ page }) => {
    await loginAs(page, 'ashoka', process.env.TEST_USER_PASSWORD!)
    await page.goto('./contacts');
});

test('contacts page has the correct layout', async ({ page }) => {
    await expect(page).toHaveURL('/contacts');
    await expect(page.getByRole('heading', { name: 'My Contacts' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Home' })).toBeVisible();
    await expect(page.getByRole('table', { name: /contacts\-table/ })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Add Contact' })).toBeVisible();
});

test('should be able to edit test contact', async ({ page }) => {
    const testUserName = "Test User's";
    const testUserNameEdited = '"Test User 2"';
    await deleteTestContactRows(page, testUserName);
    await deleteTestContactRows(page, testUserNameEdited);
    await createTestContactRow(page, testUserName, '20');
    const testUserRow = page.getByRole('row')
        .filter({ hasText: testUserName })
        .filter({ hasText: '20' });
    await testUserRow.getByRole('button', { name: 'Edit' }).click();
    await expect(page).toHaveURL(/\/edit_contact\/.*/)
    await expect(page.getByLabel('Name:')).toHaveValue(testUserName);
    await expect(page.getByLabel('Frequency (in days):')).toHaveValue('20');
    await page.getByLabel('Name:').fill(testUserNameEdited);
    await page.getByLabel('Frequency (in days):').fill('30');
    await page.getByRole('button', { name: 'Save Changes' }).click();
    await expect(page).toHaveURL('/contacts');
    const editedRow = page.getByRole('row')
        .filter({ hasText: testUserNameEdited })
        .filter({ hasText: '30' });
    expect(await editedRow.count()).toBe(1);
});

test('Cancelling edit contact modal should redirect user back to contacts page', async ({ page }) => {
    const testUserRow = page.getByRole('row')
        .filter({ hasText: 'Interaction test user' })
    await testUserRow.getByRole('button', { name: 'Edit' }).click();
    await page.locator('#close-modal').click();
    await expect(page).toHaveURL('/contacts');
    await expect((page).getByRole('heading', { name: 'My Contacts' })).toBeVisible();
}
);


