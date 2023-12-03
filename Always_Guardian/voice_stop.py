import psutil


def kill_guardian():
    for proc in psutil.process_iter():
        if proc.name() == "voice_start.exe":
            proc.kill()


kill_guardian()
