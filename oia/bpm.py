import chrono

def measure_bpm():
    c = chrono.Chrono()
    input("appui sur entree pour commencer...")
    c.start()
    for i in range(4):
        input("appui sur entree encore %d fois:" % (4-i))
        c.start_new_laps()
    c.stop()
    print(c.get_all_laps_duration())
    print(c.get_average_time_per_laps())
    print("bpm: %5.2f" % (60/c.get_average_time_per_laps()))


measure_bpm()