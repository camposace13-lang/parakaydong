import time
import sys

class RestaurantClock:
    def __init__(self):
        # 3600 game seconds (1 hour) / 10 real seconds = 360x speed
        self.time_dilation = 360 
        self.start_real_time = time.time()

    def get_game_time(self):
        # Calculate how many real seconds have passed
        elapsed_real_seconds = time.time() - self.start_real_time
        
        # Multiply by dilation to get total game seconds passed
        total_game_seconds = elapsed_real_seconds * self.time_dilation
        
        # Convert to HH:MM format (looping every 24 hours)
        total_game_minutes = int(total_game_seconds // 60)
        hours = (total_game_minutes // 60) % 24
        minutes = total_game_minutes % 60
        
        return hours, minutes

    def get_phase(self, hour):
        if 5 <= hour < 12: return "MORNING 🌅"
        if 12 <= hour < 19: return "AFTERNOON ☀️"
        if 19 <= hour < 21: return "EVENING 🌆"
        return "NIGHT 🌙"

# --- RUNNING THE LIVE CLOCK ---
clock = RestaurantClock()

try:
    while True:
        h, m = clock.get_game_time()
        phase = clock.get_phase(h)
        
        # \r moves the cursor back to the start of the line
        # :02d ensures it always shows two digits (e.g., 09:05)
        sys.stdout.write(f"\r[Current Time: {h:02d}:{m:02d}] - Phase: {phase}  ")
        sys.stdout.flush()
        
        # We sleep for a tiny bit so the CPU doesn't melt
        time.sleep(0.1) 

except KeyboardInterrupt:
    print("\n\nGame Saved. See you tomorrow!")
