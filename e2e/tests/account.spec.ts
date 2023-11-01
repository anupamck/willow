import { test, expect } from "@playwright/test";
import { loginAs } from "../helper/login";

test.beforeEach(async ({ page }) => {
  await loginAs(page, "ashoka", process.env.TEST_USER_PASSWORD!);
  await page.goto("./account");
});

test("Should display the account page with the correct information", async ({
  page,
}) => {
  await expect(page).toHaveURL("/account");
  await expect(page.getByText("Username: ashoka")).toBeVisible();
  await expect(page.getByText("E-mail: ashoka@maghada.com")).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Change Password" })
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Delete Account" })
  ).toBeVisible();
});
