export async function deleteTestContactRows(page, testUserName) {
    const testUserRows = page.getByRole('row')
        .filter({ hasText: testUserName })
        
    while (await testUserRows.count() > 0) {
        page.on('dialog', dialog => dialog.accept());
        await testUserRows.first().getByRole('button', { name: 'Delete' }).click();
    }
}

export async function createTestContactRow(page, name, frequency) {
    await page.getByRole('button', { name: 'Add Contact' }).click();
    await page.getByLabel('Name:').fill(name);
    await page.getByLabel('Frequency:').fill(frequency);
    await page.getByRole('button', { name: 'Save Changes' }).click();
}

