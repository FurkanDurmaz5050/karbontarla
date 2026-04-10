from __future__ import annotations

"""MQTT IoT sensör veri köprüsü."""

import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class MQTTClient:
    """MQTT broker'a bağlanıp IoT sensör verilerini dinler."""

    def __init__(self, broker_host: str = "mosquitto", broker_port: int = 1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = None
        self.connected = False

    def connect(self):
        """MQTT broker'a bağlan."""
        try:
            import paho.mqtt.client as mqtt
            self.client = mqtt.Client(client_id="karbontarla-bridge", protocol=mqtt.MQTTv5)
            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
        except ImportError:
            logger.warning("paho-mqtt yüklü değil, MQTT devre dışı")
        except Exception as e:
            logger.warning(f"MQTT bağlantı hatası: {e}")

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        """Bağlantı başarılı olduğunda çağrılır."""
        if rc == 0:
            self.connected = True
            logger.info("MQTT broker'a bağlanıldı")
            client.subscribe("karbontarla/sensor/+/data")
        else:
            logger.error(f"MQTT bağlantı başarısız, kod: {rc}")

    def _on_message(self, client, userdata, msg):
        """Sensör verisi geldiğinde çağrılır."""
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            topic_parts = msg.topic.split("/")
            sensor_id = topic_parts[2] if len(topic_parts) >= 3 else "unknown"

            reading = {
                "sensor_id": sensor_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "soil_moisture": payload.get("soil_moisture"),
                "soil_temp_c": payload.get("soil_temp_c"),
                "soil_ph": payload.get("soil_ph"),
                "organic_matter": payload.get("organic_matter"),
                "co2_flux": payload.get("co2_flux"),
                "battery_pct": payload.get("battery_pct"),
                "signal_quality": payload.get("signal_quality"),
            }
            logger.info(f"Sensör verisi alındı: {sensor_id}")
            self._process_reading(reading)
        except json.JSONDecodeError:
            logger.error(f"Geçersiz JSON: {msg.payload}")
        except Exception as e:
            logger.error(f"Mesaj işleme hatası: {e}")

    def _process_reading(self, reading: dict):
        """Sensör okumalarını veritabanına kaydet.
        
        Async DB işlemleri burada senkron olarak yapılır.
        Üretim ortamında Celery task olarak yazılmalıdır.
        """
        logger.info(f"İşlenen sensör verisi: {reading['sensor_id']}")

    def disconnect(self):
        """Bağlantıyı kapat."""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False

    def publish_test_data(self, sensor_id: str, data: dict):
        """Test amaçlı sensör verisi gönder."""
        if self.client and self.connected:
            topic = f"karbontarla/sensor/{sensor_id}/data"
            self.client.publish(topic, json.dumps(data))

    @staticmethod
    def generate_mock_reading() -> dict:
        """Test için gerçekçi sensör verisi üretir."""
        import random
        return {
            "soil_moisture": round(random.uniform(15, 45), 2),
            "soil_temp_c": round(random.uniform(8, 32), 2),
            "soil_ph": round(random.uniform(5.5, 8.0), 2),
            "organic_matter": round(random.uniform(1.5, 5.5), 3),
            "co2_flux": round(random.uniform(0.5, 8.0), 4),
            "battery_pct": round(random.uniform(20, 100), 1),
            "signal_quality": random.randint(-90, -30),
        }
