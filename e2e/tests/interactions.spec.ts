import { test, expect } from '@playwright/test';
import { createTestInteractionRow, deleteTestInteractionRows } from '../helper/interactions';

test.beforeEach(async ({ page }) => {
    await page.goto('./contacts');
    await page.getByRole('link', { name: /Interaction test user/ }).click();
});

test('should be able to edit test interaction', async ({ page }) => {
    const testInteractionTitle = "Test Interaction's";
    const testInteractionTitleEdited = '"Test Interaction 2"';
    await deleteTestInteractionRows(page, testInteractionTitle);
    await deleteTestInteractionRows(page, testInteractionTitleEdited);
    await createTestInteractionRow(page, testInteractionTitle, '2021-01-01', '"Test Notes"');
    const testInteractionRow = page.getByRole('row')
        .filter({ hasText: testInteractionTitle })
        .filter({ hasText: '2021-01-01' })
        .filter({ hasText: '"Test Notes"' });
    await testInteractionRow.getByRole('button', { name: 'Edit' }).click();
    // give me a regex to ensure that the url contains 'update_interaction'
    await expect(page).toHaveURL(/\/update_interaction\/.*/)
    await expect(page.getByLabel('Title:')).toHaveValue(testInteractionTitle);
    await expect(page.getByLabel('Date:')).toHaveValue('2021-01-01');
    await expect(page.getByLabel('Notes:')).toHaveValue('"Test Notes"');
    await page.getByLabel('Title:').fill('"Test Interaction 2"');
    await page.getByLabel('Date:').fill('2021-01-02');
    await page.getByLabel('Notes:').fill('"Test Notes 2"');
    await page.getByRole('button', { name: 'Save Changes' }).click();
    await expect(page).toHaveURL(/\/interactions/);
    const editedRow = await page.getByRole('row')
        .filter({ hasText: '"Test Interaction 2"' })
        .filter({ hasText: '2021-01-02' })
        .filter({ hasText: '"Test Notes 2"' });
    expect(await editedRow.count()).toBe(1);
});

test('Cancelling edit interaction modal should redirect user back to interactions page', async ({ page }) => {
    const testInteractionRow = page.getByRole('row')
        .filter({ hasText: 'Click on x - Edit' })
    await testInteractionRow.getByRole('button', { name: 'Edit' }).click();
    await page.locator('#close-modal').click();
    await expect(page).toHaveURL(/\/interactions/);
    await expect((page).getByRole('heading', { name: 'Interactions - Interaction test user' })).toBeVisible();
});

test('Cancelling add interaction modal should redirect user back to interactions page', async ({ page }) => {
    await page.getByRole('button', { name: 'Add Interaction' }).click();
    await page.locator('#close-modal').click();
    await expect(page).toHaveURL(/\/interactions/);
    await expect((page).getByRole('heading', { name: 'Interactions - Interaction test user' })).toBeVisible();
});

