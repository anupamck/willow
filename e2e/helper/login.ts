import { Page } from "@playwright/test";

export async function loginAs(page: Page, username: string, password: string) {
    await page.goto('/');
    await page.getByRole('textbox', { name: 'username' }).type(username);
    await page.getByRole('textbox', { name: 'password' }).type(password);
    await page.getByRole('button', { name: 'Login' }).click();
}