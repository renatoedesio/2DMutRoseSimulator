"""Sensor de localização observável, separado da posição verdadeira do Pygame."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import random


@dataclass(frozen=True)
class LocalizationMeasurement:
    """Observação em metros; não contém a posição verdadeira do robô."""

    x_m: float
    y_m: float
    sigma_m: float
    timestamp: str
    source: str = "simulator2d_localization_sensor"


class SimulatedLocalizationSensor:
    """Converte pixels em metros e aplica ruído gaussiano reprodutível."""

    def __init__(
        self,
        meters_per_pixel: float,
        *,
        sigma_m: float = 0.0,
        bias_m: tuple[float, float] = (0.0, 0.0),
        seed: int = 42,
    ) -> None:
        if meters_per_pixel <= 0:
            raise ValueError("meters_per_pixel deve ser maior que zero.")
        if sigma_m < 0:
            raise ValueError("sigma_m não pode ser negativo.")
        self.meters_per_pixel = meters_per_pixel
        self.sigma_m = sigma_m
        self.bias_m = bias_m
        self._random = random.Random(seed)

    def observe(self, position_pixels: tuple[float, float]) -> LocalizationMeasurement:
        """Gera uma medida; a posição recebida não é exposta no resultado."""
        true_x_m = position_pixels[0] * self.meters_per_pixel
        true_y_m = position_pixels[1] * self.meters_per_pixel
        return LocalizationMeasurement(
            x_m=true_x_m + self.bias_m[0] + self._random.gauss(0.0, self.sigma_m),
            y_m=true_y_m + self.bias_m[1] + self._random.gauss(0.0, self.sigma_m),
            sigma_m=self.sigma_m,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
