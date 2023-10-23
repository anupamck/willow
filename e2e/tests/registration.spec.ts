import { test, expect } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.goto("/register");
});

test("User cannot register with an existing username", async ({ page }) => {
  await page.getByLabel("Username").type("ashoka");
  await page.getByLabel("E-mail").type("ashoka@email.com");
  await page.getByLabel("Password:", { exact: true }).type("password");
  await page.getByLabel("Confirm Password").type("password");
  await page.getByRole("button", { name: "Register" }).click();
  await expect(page.getByText("Username is already taken")).toBeVisible();
});

test("User cannot register with an existing email address", async ({
  page,
}) => {
  await page.getByLabel("Username").type("ashoka1");
  await page.getByLabel("E-mail").type("ashoka@maghada.com");
  await page.getByLabel("Password:", { exact: true }).type("password");
  await page.getByLabel("Confirm Password").type("password");
  await page.getByRole("button", { name: "Register" }).click();
  await expect(
    page.getByText("This e-mail address is already registered")
  ).toBeVisible();
});

test("User cannot register with mismatched passwords", async ({ page }) => {
  await page.getByLabel("Username").type("ashoka1");
  await page.getByLabel("E-mail").type("ashoka@email.com");
  await page.getByLabel("Password:", { exact: true }).type("password");
  await page.getByLabel("Confirm Password").type("password1");
  await page.getByRole("button", { name: "Register" }).click();
  await expect(
    page.getByText("Password and confirm password must match")
  ).toBeVisible();
});
