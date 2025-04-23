# … [all your imports and calibration code stay identical] …

OUTPUT = "/home/rickg/LEGARD/Tests/HeatMap/coordinates.txt"  # <– match viewer
open(OUTPUT, "w").close()   # start with a clean slate (optional)

while True:
    # ----- your existing reading / validation loop (unchanged) -----
    if all_valid and len(scaled_weights) == 4:
        x_val, y_val = calculate_xy(scaled_weights)
        print(f"X: {x_val:.3f}, Y: {y_val:.3f}")

        # append point + force it onto disk immediately
        with open(OUTPUT, "a", buffering=1) as f:      # line-buffered
            f.write(f"{x_val:.3f}, {y_val:.3f}\n")
            # f.flush() is automatic with buffering=1
    else:
        print("Skipping calculations due to invalid sensor data.")

