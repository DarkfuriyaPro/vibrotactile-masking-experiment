import calibration_level
import calibration_response

input("Place the accelerometer on channel 1. Press Enter to continue...")
calibration_level.calibrate_level(0,False)
calibration_response.calibrate_response(0)
calibration_level.calibrate_level(0)
input("Place the accelerometer on channel 2. Press Enter to continue...")
calibration_level.calibrate_level(1,False)
calibration_response.calibrate_response(1)
calibration_level.calibrate_level(1)

print("calibration finished.")