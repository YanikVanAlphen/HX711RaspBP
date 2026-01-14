import time
import json
from pathlib import Path
from HX711_LoadCellAmplifier.hx711v0_5_1 import HX711

# ========================== CONFIG FILE SETUP ==========================
CONFIG_FILE = Path(__file__).parent / "scale_config.json"

class LoadCellScale:
    def __init__(self, dat_pin=23, clk_pin=24, gain=128, auto_tare=True):
        """
        Initialize the load cell scale class.
        
        Args:
            dat_pin: Data pin
            clk_pin: Clock pin
            gain: Amplifier gain (default 128)
            auto_tare: Automatically tare on initialization (default True)
        """
        self.hx = HX711(dat_pin, clk_pin, gain=gain)
        self.hx.setReadingFormat("MSB", "MSB")
        
        self.current_weight = 0.0
        self._is_reading = False
        
        # load saved calibration if exists
        self._load_config()
        
        if auto_tare:
            self.tare()

    def _save_config(self):
        """Save calibration to config file"""
        config = {
            "offset_a": self.hx.getOffset('A'),
            "reference_unit_a": self.hx.getReferenceUnit('A')
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)

    def _load_config(self):
        """Load calibration from config file"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE) as f:
                    config = json.load(f)
                self.hx.setOffset(config.get("offset_a", 0), 'A')
                self.hx.setReferenceUnit(config.get("reference_unit_a", 1), 'A')
            except Exception:
                pass

    def tare(self):
        """Zero the scale (assumes no weight on scale)"""
        self.hx.autosetOffset('A')
        self._save_config()

    def calibrate(self, known_weight_grams: float):
        """
        Calibrate the scale with a known weight.
        
        Args:
            known_weight_grams: The weight in grams currently on the scale
        
        Note: Ensure the known weight is stable on the scale before calling.
        """
        # average multiple readings for stability
        total = 0
        count = 20
        for _ in range(count):
            val = self.hx.getLongWithOffset('A')
            if val is not None:
                total += val
            time.sleep(0.05)
        
        average_offset_value = total / count
        # reference unit calculation from hx711py python library usage example (example_hx711v0_5_1.py)
        reference_unit = average_offset_value / known_weight_grams
        
        self.hx.setReferenceUnit(reference_unit, 'A')
        self._save_config()

    def start_reading(self):
        """Start continuous weight monitoring"""
        if self._is_reading:
            return
        
        def update_weight(raw_bytes):
            if raw_bytes:
                weight = self.hx.rawBytesToWeight(raw_bytes, 'A')
                if weight is not None:
                    self.current_weight = weight

        self.hx.enableReadyCallback(update_weight)
        self._is_reading = True

    def stop_reading(self):
        """Stop continuous weight monitoring"""
        if not self._is_reading:
            return
        
        self.hx.disableReadyCallback()
        self._is_reading = False

    def get_weight(self):
        """
        Get the current weight in grams.
        
        Returns:
            float: Current weight in grams
        """
        return self.current_weight

    def is_reading(self):
        """Check if currently in reading mode"""
        return self._is_reading