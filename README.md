# Samsung WindFree AC for Home Assistant

A Home Assistant custom component to control Samsung WindFree Air Conditioners via the SmartThings API using OAuth2 authentication. Specifically designed to provide precise control and expose specific features like the **WindFree** mode switch, which is currently unavailable in the default SmartThings integration.

## Features
* 🌡️ AC Mode (Cool, Dry, Fan, Auto) & Temperature Control (16°C - 30°C).
* 💨 Fan Speed Control (Auto, Low, Medium, High).
* 🍃 **Dedicated WindFree Mode** (Integrated as a Thermostat Preset and a standalone Switch).
* 🔄 Built-in OAuth2 Token Auto-Refresh system (Prevents 24-hour token expiration automatically).
* 🍎 Fully optimized for Apple HomeKit Bridge support.

## Prerequisites
Due to recent SmartThings API policies, you need personal OAuth2 credentials to establish a direct local-to-cloud connection. You will need to prepare these 4 items:
1. `client_id`
2. `client_secret`
3. `refresh_token` (One-time use for initial setup)
4. `device_id` (Your AC's unique ID)

### 🔑 How to get Client ID, Secret, and Refresh Token
Please follow this comprehensive tutorial on SmartThings OAuth2:
👉 **[SmartThings API: Taming the OAuth 2.0 Beast](https://levelup.gitconnected.com/smartthings-api-taming-the-oauth-2-0-beast-5d735ecc6b24)**

*Important Note: You ONLY need to follow **Step 1 to Step 3** of the tutorial to generate your `client_id`, `client_secret`, and `refresh_token`. You **DO NOT** need to perform Steps 4 and 5 (creating a Python server), as the auto-refresh mechanism is already built natively into this custom component!*

### 📱 How to get your Device ID
1. Open your browser and log in to the **[SmartThings Advanced Web App](https://my.smartthings.com/advanced)** using your Samsung account.
2. Click on the **Devices** menu on the left panel.
3. Find your Samsung WindFree AC in the list and click on its name.
4. Look for the **Device ID** row (it looks like a long alphanumeric string, e.g., `123e4567-e89b-12d3-a456-426614174000`).
5. Copy this ID.

## Installation via HACS (Recommended)
1. Open HACS in your Home Assistant -> **Integrations** tab.
2. Click the three-dot menu in the top right corner -> **Custom repositories**.
3. Enter this repository's URL, select **Integration** as the category, and click **Add**.
4. Search for *Samsung WindFree AC* in HACS, then click the **Download** button.
5. Restart your Home Assistant.

## Configuration
Add the following code to your `configuration.yaml` file, replacing the placeholders with the credentials you obtained from the steps above:

```yaml
samsung_windfree:
  client_id: "YOUR_CLIENT_ID"
  client_secret: "YOUR_CLIENT_SECRET"
  refresh_token: "YOUR_INITIAL_REFRESH_TOKEN"
  device_id: "YOUR_AC_DEVICE_ID"
