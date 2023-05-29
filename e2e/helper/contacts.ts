export async function deleteTestContactRows(page) {
    const testUserRows = page.getByRole('row')
        .filter({ hasText: "Test User's" })
        .filter({ hasText: '20' });

    const testUserEditedRows = page.getByRole('row')
        .filter({ hasText: '"Test User 2"' })
        .filter({ hasText: '30' });

    page.on('dialog', dialog => dialog.accept());
    while (await testUserRows.count() > 0) {
        await testUserRows.first().getByRole('button', { name: 'Delete' }).click();
    }
    while (await testUserEditedRows.count() > 0) {
        await testUserEditedRows.first().getByRole('button', { name: 'Delete' }).click();
    }
}

export async function createTestContactRow(page) {
    await page.getByRole('button', { name: 'Add Contact' }).click();
    await page.getByLabel('Name:').fill("Test User's");
    await page.getByLabel('Frequency:').fill('20');
    await page.getByRole('button', { name: 'Save Changes' }).click();
}

