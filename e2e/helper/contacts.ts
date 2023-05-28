export async function deleteTestContactRows(page) {
    const testUserRows = page.getByRole('row')
        .filter({ hasText: 'Test User' })
        .filter({ hasText: '20' });

    const testUserEditedRows = page.getByRole('row')
        .filter({ hasText: 'Test User 2' })
        .filter({ hasText: '30' });

    page.on('dialog', dialog => dialog.accept());
    for (let i = 0; i < await testUserRows.count(); i++) {
        await testUserRows.first().getByRole('button', { name: 'Delete' }).click();
    }
    for (let i = 0; i < await testUserEditedRows.count(); i++) {
        await testUserEditedRows.first().getByRole('button', { name: 'Delete' }).click();
    }
}

export async function createTestContactRow(page) {
    await page.getByRole('button', { name: 'Add Contact' }).click();
    await page.getByLabel('Name:').fill('Test User');
    await page.getByLabel('Frequency:').fill('20');
    await page.getByRole('button', { name: 'Save Changes' }).click();
}

