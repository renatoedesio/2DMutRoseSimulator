import unittest

from src.platforms.simulator2d.localization_sensor import SimulatedLocalizationSensor


class SimulatedLocalizationSensorTests(unittest.TestCase):
    def test_converts_pixels_to_meters_without_exposing_truth(self) -> None:
        sensor = SimulatedLocalizationSensor(0.01, sigma_m=0.0, seed=42)

        measurement = sensor.observe((320.0, 150.0))

        self.assertEqual(3.2, measurement.x_m)
        self.assertEqual(1.5, measurement.y_m)
        self.assertEqual(0.0, measurement.sigma_m)

    def test_noise_is_reproducible_for_a_seed(self) -> None:
        first = SimulatedLocalizationSensor(0.01, sigma_m=0.2, seed=7).observe((0.0, 0.0))
        second = SimulatedLocalizationSensor(0.01, sigma_m=0.2, seed=7).observe((0.0, 0.0))

        self.assertEqual((first.x_m, first.y_m), (second.x_m, second.y_m))
        self.assertNotEqual((0.0, 0.0), (first.x_m, first.y_m))


if __name__ == "__main__":
    unittest.main()
