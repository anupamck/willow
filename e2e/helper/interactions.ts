export async function deleteTestInteractionRows(page, title) {
    let testInteractionRows = page.getByRole('row')
        .filter({ hasText: title })

    while (await testInteractionRows.count() > 0) {
        page.on('dialog', async dialog => {
            if (!dialog.handled) {
                await dialog.accept();
              }
          });
        await testInteractionRows.first().getByRole('button', { name: 'Delete' }).click();
    }
}

export async function createTestInteractionRow(page, title, date, notes) {
    await page.getByRole('button', { name: 'Add Interaction' }).click();
    await page.getByLabel('Title:').fill(title);
    await page.getByLabel('Date:').fill(date);
    await page.getByLabel('Notes:').fill(notes);
    await page.getByRole('button', { name: 'Save Changes' }).click();
}