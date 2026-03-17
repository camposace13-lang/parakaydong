import time


# ═════════════════════════════════════════════
# RESTAURANT CLOCK
# 1 real second = 6 game minutes (360x speed)
# Full 24-hr game day = 4 real minutes
# ═════════════════════════════════════════════
class RestaurantClock:
    def __init__(self, start_hour=7):
        self.time_dilation = 360
        self.start_real_time = time.time()
        # Offset so the clock starts at start_hour instead of 00:00
        self._start_offset_seconds = start_hour * 3600

    def get_game_time(self):
        elapsed_real = time.time() - self.start_real_time
        total_game_seconds = (elapsed_real * self.time_dilation) + self._start_offset_seconds
        total_game_minutes = int(total_game_seconds // 60)
        hours   = (total_game_minutes // 60) % 24
        minutes = total_game_minutes % 60
        return hours, minutes

    def get_phase(self, hour):
        if 5  <= hour < 12: return "MORNING 🌅"
        if 12 <= hour < 17: return "AFTERNOON ☀️"
        if 17 <= hour < 20: return "EVENING 🌆"
        return "NIGHT 🌙"

    def time_str(self):
        h, m = self.get_game_time()
        return f"{h:02d}:{m:02d}"
