from scale import LoadCellScale

# 1. init without auto-tare
scale = LoadCellScale(dat_pin=23, clk_pin=24, auto_tare=False)

# 2. remove all weight from scale, then tare
scale.tare()

# 3. place a known weight on the scale, e.g. 750g
input("Place 750g weight and press Enter...")

# 4. calibrate with the known weight
scale.calibrate(750.0)

# 5. start normal operation
scale.start_reading()