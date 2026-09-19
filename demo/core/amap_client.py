"""
Amap (AutoNavi) Web Service & MCP Client
(高德开放平台 Web 服务网关与真实地理特征提取器)
Provides Geocoding, Nearby Logistics POI Search, Distance Matrix, and Weather.
"""

import os
import json
import urllib.request
import urllib.parse
from typing import Dict, List, Any, Optional

class AmapClient:
    def __init__(self, config_path=None):
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "config.json")
        self.config_path = config_path
        self.api_key = os.getenv("AMAP_MAPS_KEY", "") or os.getenv("AMAP_KEY", "")
        self.load_key_from_config()
        self.base_url = "https://restapi.amap.com/v3"

    def load_key_from_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    if cfg.get("amap_key"):
                        self.api_key = cfg["amap_key"].strip()
            except Exception as e:
                print("Failed to read config.json:", e)

    def save_key_to_config(self, key: str):
        self.api_key = key.strip()
        cfg = {}
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            except:
                pass
        cfg["amap_key"] = self.api_key
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        return True

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) >= 16)

    def get_masked_key(self) -> str:
        if not self.is_configured():
            return "未配置"
        return f"{self.api_key[:4]}****{self.api_key[-4:]}"

    def _http_get(self, endpoint: str, params: dict) -> dict:
        if not self.is_configured():
            return {"status": "0", "info": "AMAP Key not configured"}
        params["key"] = self.api_key
        query_str = urllib.parse.urlencode(params)
        url = f"{self.base_url}/{endpoint}?{query_str}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AntigravityLogistics/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = resp.read().decode("utf-8")
                return json.loads(data)
        except Exception as e:
            return {"status": "0", "info": str(e)}

    def test_key(self) -> dict:
        """测试 Key 是否有效"""
        res = self._http_get("geocode/geo", {"address": "天安门", "city": "北京"})
        if res.get("status") == "1" and res.get("geocodes"):
            return {"valid": True, "info": "连接成功", "formatted_address": res["geocodes"][0].get("formatted_address")}
        return {"valid": False, "info": res.get("info", "未知错误")}

    def geocode(self, address: str, city: str = "北京") -> dict:
        """地理编码：地址转经纬度"""
        res = self._http_get("geocode/geo", {"address": address, "city": city})
        if res.get("status") == "1" and res.get("geocodes"):
            geo = res["geocodes"][0]
            lng, lat = map(float, geo["location"].split(","))
            return {
                "success": True,
                "formatted_address": geo.get("formatted_address"),
                "lng": lng,
                "lat": lat,
                "district": geo.get("district", ""),
                "adcode": geo.get("adcode", "")
            }
        return {"success": False, "info": res.get("info", "未找到该地点")}

    def search_around_logistics(self, lng: float, lat: float, radius: int = 800) -> list:
        """周边搜：扫描附近快递、自提柜、驿站等设施"""
        res = self._http_get("place/around", {
            "location": f"{lng},{lat}",
            "keywords": "快递|菜鸟驿站|丰巢|自提柜|速递",
            "radius": radius,
            "offset": 20
        })
        results = []
        if res.get("status") == "1" and res.get("pois"):
            for p in res["pois"]:
                try:
                    p_lng, p_lat = map(float, p["location"].split(","))
                    results.append({
                        "id": p.get("id"),
                        "name": p.get("name"),
                        "type": p.get("type"),
                        "address": p.get("address"),
                        "lng": p_lng,
                        "lat": p_lat,
                        "distance_m": float(p.get("distance", 0))
                    })
                except:
                    continue
        return results

    def get_weather(self, city_adcode: str = "110100") -> dict:
        """气象实况查询"""
        res = self._http_get("weather/weatherInfo", {"city": city_adcode, "extensions": "base"})
        if res.get("status") == "1" and res.get("lives"):
            live = res["lives"][0]
            return {
                "weather": live.get("weather"),
                "temperature": live.get("temperature"),
                "winddirection": live.get("winddirection"),
                "windpower": live.get("windpower"),
                "humidity": live.get("humidity"),
                "reporttime": live.get("reporttime")
            }
        return {}

if __name__ == "__main__":
    client = AmapClient()
    print("Is configured:", client.is_configured(), "Masked:", client.get_masked_key())
