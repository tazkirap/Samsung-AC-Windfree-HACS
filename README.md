# Samsung WindFree AC for Home Assistant

Custom component Home Assistant untuk mengontrol AC Samsung WindFree melalui SmartThings API menggunakan otentikasi OAuth2. Dibuat khusus untuk memberikan kontrol lokal dan memunculkan fitur spesifik seperti sakelar **WindFree** yang tidak tersedia di integrasi bawaan.

## Fitur
* 🌡️ Kontrol Suhu & Mode AC (Cool, Dry, Fan, Auto).
* 💨 Kontrol Kecepatan Kipas (Auto, Low, Medium, High).
* 🍃 **Sakelar Khusus WindFree Mode** (terintegrasi di Thermostat & Switch terpisah).
* 🔄 Sistem Auto-Refresh Token OAuth2 bawaan (Token aman dari *expired* 24 jam).
* 🍎 Mendukung Apple HomeKit (Suhu 16-30°C, Mode, dan Sakelar WindFree).

## Persyaratan Awal (Prerequisites)
Karena kebijakan SmartThings terbaru, Anda membutuhkan kredensial OAuth2. Anda perlu menyiapkan 4 data berikut:
1. `client_id`
2. `client_secret`
3. `refresh_token` (Sekali pakai untuk inisialisasi awal)
4. `device_id` (ID dari AC Anda)

### 🔑 Cara Mendapatkan Client ID, Secret, dan Refresh Token
Silakan ikuti tutorial komprehensif mengenai SmartThings OAuth2 di artikel berikut ini:
👉 **[SmartThings API: Taming the OAuth 2.0 Beast](https://levelup.gitconnected.com/smartthings-api-taming-the-oauth-2-0-beast-5d735ecc6b24)**

*Catatan Penting: Anda hanya perlu mengikuti tutorial tersebut dari **Step 1 sampai Step 3** saja untuk memancing keluar `client_id`, `client_secret`, dan `refresh_token`. Anda **TIDAK PERLU** melakukan Step 4 dan 5 (membuat server Python), karena mesin auto-refresh token tersebut sudah ditanamkan langsung ke dalam custom component ini!*

### 📱 Cara Mendapatkan Device ID
1. Buka browser dan login ke **[SmartThings Advanced Web App](https://my.smartthings.com/advanced)** menggunakan akun Samsung Anda.
2. Klik menu **Devices** di panel sebelah kiri.
3. Cari perangkat AC Samsung WindFree Anda di daftar tersebut, lalu klik namanya.
4. Anda akan melihat baris **Device ID** (berupa kombinasi huruf dan angka panjang, misal: `123e4567-e89b-12d3-a456-426614174000`).
5. Salin ID tersebut.

## Instalasi via HACS (Direkomendasikan)
1. Buka HACS di Home Assistant Anda -> tab **Integrations**.
2. Klik menu tiga titik di pojok kanan atas -> **Custom repositories**.
3. Masukkan URL repositori ini, pilih kategori **Integration**, lalu klik **Add**.
4. Cari *Samsung WindFree AC* di HACS, lalu klik tombol **Download** di pojok kanan bawah.
5. Restart Home Assistant Anda.

## Konfigurasi
Tambahkan kode berikut ke dalam file `configuration.yaml` Anda, lalu masukkan kredensial yang sudah Anda dapatkan dari langkah-langkah di atas:

```yaml
samsung_windfree:
  client_id: "CLIENT_ID_ANDA"
  client_secret: "CLIENT_SECRET_ANDA"
  refresh_token: "REFRESH_TOKEN_AWAL_ANDA"
  device_id: "DEVICE_ID_AC_ANDA"
