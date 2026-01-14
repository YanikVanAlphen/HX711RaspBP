from scale import LoadCellScale
import time

# init scale object (auto-tares on startup)
scale = LoadCellScale(dat_pin=23, clk_pin=24, auto_tare=True)

# start continuous read
scale.start_reading()

try:
    while True:
        # get current weight reading
        weight = scale.get_weight()
        print(f"Weight: {weight:7.2f} g", end="\r")
        time.sleep(0.1)
            
except KeyboardInterrupt:
    scale.stop_reading()
    print("\nStopped scale reading.")