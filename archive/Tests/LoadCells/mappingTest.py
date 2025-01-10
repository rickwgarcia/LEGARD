# Function re-maps a number from one range to another.
def scale_to(val, fromLow, fromHigh, toLow, toHigh):

    return (val - fromLow) * (toHigh - toLow) / (fromHigh - fromLow) + toLow
    
    
    
analog_value = 512  # Example analog reading
scaled_value = scale_to(analog_value, 0, 1023, 0, 255)
print(scaled_value) 

