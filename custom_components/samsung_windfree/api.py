import logging
import aiohttp
import json
import os
from datetime import datetime, timedelta

_LOGGER = logging.getLogger(__name__)

TOKEN_URL = "https://auth-global.api.smartthings.com/oauth/token"
API_BASE_URL = "https://api.smartthings.com/v1"
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "token_store.json")

class SmartThingsOAuth2API:
    def __init__(self, client_id, client_secret, initial_refresh_token, device_id):
        self.client_id = client_id
        self.client_secret = client_secret
        self.device_id = device_id
        
        self.access_token = None
        # Default: gunakan token dari YAML
        self.refresh_token = initial_refresh_token
        self.token_expires_at = datetime.min
        
        # JIKA FILE ADA: Selalu timpa token YAML dengan token dari file
        self._load_tokens()

    def _load_tokens(self):
        """Memuat token dari file. Abaikan configuration.yaml jika file ini ada."""
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, "r") as f:
                    data = json.load(f)
                    if "refresh_token" in data:
                        self.access_token = data.get("access_token")
                        self.refresh_token = data.get("refresh_token")
                        expires_str = data.get("expires_at")
                        if expires_str:
                            self.token_expires_at = datetime.fromisoformat(expires_str)
                        _LOGGER.warning("Token berhasil dimuat dari token_store.json")
            except Exception as e:
                _LOGGER.error(f"Gagal membaca token file: {e}")

    def _save_tokens(self):
        """Menyimpan token terbaru ke file."""
        data = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.token_expires_at.isoformat()
        }
        try:
            with open(TOKEN_FILE, "w") as f:
                json.dump(data, f)
        except Exception as e:
            _LOGGER.error(f"Gagal menyimpan token file: {e}")

    async def _refresh_access_token(self):
        _LOGGER.warning("Meminta token baru via OAuth2...")
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token
        }
        auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(TOKEN_URL, data=payload, auth=auth) as response:
                if response.status == 200:
                    data = await response.json()
                    self.access_token = data.get("access_token")
                    if "refresh_token" in data:
                        self.refresh_token = data.get("refresh_token")
                    
                    expires_in = data.get("expires_in", 86400)
                    self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                    
                    self._save_tokens() 
                    _LOGGER.warning("SUKSES: Token OAuth2 berhasil diperbarui dan disimpan!")
                else:
                    _LOGGER.error(f"Gagal memperbarui token. HTTP {response.status}: {await response.text()}")

    async def get_headers(self):
        if datetime.now() >= self.token_expires_at or not self.access_token:
            await self._refresh_access_token()
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

    async def get_status(self):
        headers = await self.get_headers()
        url = f"{API_BASE_URL}/devices/{self.device_id}/status"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                _LOGGER.error(f"Gagal mengambil status. HTTP {response.status}: {await response.text()}")
                return None

    async def send_command(self, commands):
        headers = await self.get_headers()
        url = f"{API_BASE_URL}/devices/{self.device_id}/commands"
        payload = {"commands": commands}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    _LOGGER.error(f"Gagal mengirim perintah: {await response.text()}")
                    return False
                return True