# generate_sounds.py - Creates all sound effect WAV files for plogging video
import numpy as np
import wave
import struct
import random

def create_wav(filename, samples, sample_rate=44100):
    """Save numpy array as WAV file."""
    f = wave.open(filename, 'w')
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(sample_rate)
    samples = np.clip(samples, -1, 1)
    samples = (samples * 32767).astype(np.int16)
    f.writeframes(samples.astype(np.int16).tostring())
    f.close()

def generate_footstep(duration=0.08, sr=44100):
    """Generate a short footstep sound (low thud)."""
    t = np.linspace(0, duration, int(sr * duration))
    envelope = np.exp(-t * 40)
    sound = np.sin(2 * np.pi * 80 * t) * envelope * 0.6
    sound += np.sin(2 * np.pi * 120 * t) * envelope * 0.3
    noise = np.random.normal(0, 1, len(t)) * envelope * 0.1
    return sound + noise

def generate_spot_ding(duration=0.15, sr=44100):
    """Generate a 'spotted litter' ding sound."""
    t = np.linspace(0, duration, int(sr * duration))
    envelope = np.exp(-t * 15)
    sound = np.sin(2 * np.pi * 880 * t) * envelope * 0.5
    sound += np.sin(2 * np.pi * 1100 * t) * envelope * 0.3
    sound += np.sin(2 * np.pi * 1320 * t) * envelope * 0.2
    return sound

def generate_pickup(duration=0.2, sr=44100):
    """Generate a 'litter picked up' swoosh+crunch."""
    t = np.linspace(0, duration, int(sr * duration))
    envelope = np.exp(-t * 12)
    freq = 200 + 600 * (t / duration)
    swoosh = np.sin(2 * np.pi * freq * t) * envelope * 0.4
    noise = np.random.normal(0, 1, len(t)) * envelope * 0.3
    click = np.sin(2 * np.pi * 1500 * t) * np.exp(-t * 30) * 0.5
    return swoosh + noise + click

def generate_celebration(duration=0.5, sr=44100):
    """Generate a short celebration jingle after picking up."""
    t = np.linspace(0, duration, int(sr * duration))
    envelope = np.exp(-t * 8)
    sound = np.sin(2 * np.pi * 523 * t) * envelope * 0.3
    sound += np.sin(2 * np.pi * 659 * t) * envelope * 0.3
    sound += np.sin(2 * np.pi * 784 * t) * envelope * 0.3
    return sound

def generate_ambient(duration=30.0, sr=44100):
    """Generate ambient nature background (birds, wind)."""
    t = np.linspace(0, duration, int(sr * duration))
    sound = np.zeros(len(t))
    wind = np.sin(2 * np.pi * 0.5 * t) * np.sin(2 * np.pi * 200 * t) * 0.03
    wind += np.random.normal(0, 0.02, len(t))
    sound += wind
    for chirp_time in np.arange(1, duration, random.uniform(3, 5)):
        chirp_idx = int(chirp_time * sr)
        chirp_len = int(0.1 * sr)
        if chirp_idx + chirp_len < len(t):
            chirp_t = np.linspace(0, 0.1, chirp_len)
            chirp_env = np.exp(-chirp_t * 30)
            chirp = np.sin(2 * np.pi * 2000 * chirp_t) * chirp_env * 0.1
            chirp += np.sin(2 * np.pi * 2500 * chirp_t) * chirp_env * 0.08
            sound[chirp_idx:chirp_idx+chirp_len] += chirp
    return sound * 0.5

print("Generating sound effects...")

create_wav("footstep.wav", generate_footstep())
print("  Done: footstep.wav")

create_wav("spot_ding.wav", generate_spot_ding())
print("  Done: spot_ding.wav")

create_wav("pickup.wav", generate_pickup())
print("  Done: pickup.wav")

create_wav("celebration.wav", generate_celebration())
print("  Done: celebration.wav")

create_wav("ambient.wav", generate_ambient())
print("  Done: ambient.wav (30s background)")

print("All sound effects generated!")
