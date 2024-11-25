import os
import time

# ==================== Function 4: Music to my ears  =================================
# ====================================================================================
# List of available sounds with their paths
sounds = {
    "1": "/usr/share/sounds/freedesktop/stereo/complete.oga",
    "2": "/usr/share/sounds/freedesktop/stereo/service-logout.oga",
    "3": "/usr/share/sounds/freedesktop/stereo/bell.oga",
    "4": "/usr/share/sounds/freedesktop/stereo/dialog-warning.oga",
    "5": "/usr/share/sounds/freedesktop/stereo/message-new-instant.oga",
}

def play_sequence():
    """Plays a specific sequence of sounds."""
    def play_sound(sound_key):
        """Plays the sound corresponding to the given key."""
        if sound_key in sounds:
            sound_path = sounds[sound_key]
            os.system(f"paplay {sound_path}")
        else:
            print(f"Sound key {sound_key} not found.")

    print("Playing number 2 (once)...")
    play_sound("2")
    time.sleep(0.1)  # Optional delay between sounds

    print("Playing number 4 (10 times)...")
    for _ in range(10):
        play_sound("4")
        time.sleep(0.1)  # Optional delay between repetitions

    print("Playing number 2 (once)...")
    play_sound("2")

    print("Finished playing sounds.")
