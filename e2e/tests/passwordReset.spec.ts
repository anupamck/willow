// Write tests for password reset functionality
// 1. Should display error when email address is not found
// 3. Should display success message when email address is valid
// 4. Should display error when reset token is invalid

import { test, expect } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.goto("./forgot_password");
});

test("Should display error when email address is not found", async ({
  page,
}) => {
  await page
    .getByRole("textbox", { name: "E-mail:" })
    .fill("mysteryman@gmail.com");
  await page.getByRole("button", { name: "Submit" }).click();
  await expect(page).toHaveURL("/forgot_password");
  await expect(page.getByText("E-mail is not registered.")).toBeVisible();
});

test("Should display success message when email address is valid", async ({
  page,
}) => {
  await page
    .getByRole("textbox", { name: "E-mail:" })
    .fill("wingfooted@gmail.com");
  await page.getByRole("button", { name: "Submit" }).click();
  await expect(page).toHaveURL("/");
  await expect(
    page.getByText(
      "A password reset link has been sent to your e-mail address."
    )
  ).toBeVisible();
});

test("Should display error when reset token is invalid", async ({ page }) => {
  await page.goto("./reset_password/invalid_token");
  await expect(page).toHaveURL("/");
  await expect(
    page.getByText("Invalid token. Please try again.")
  ).toBeVisible();
});
