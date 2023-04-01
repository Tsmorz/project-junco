import sys
k = 0
try:
   for line in sys.stdin:
      k = k + 1
      print(line)
except:
   sys.stdout.flush()
   pass
print(k)
    
"""
def auto(timestamp, recovery_x_error, wind_vector_x, wind_vector_y, recovery_y_error):
	lateral_airspeed = 0
	drop_package = 0
	padding[3]
	return lateral_airspeed, drop_package
"""
