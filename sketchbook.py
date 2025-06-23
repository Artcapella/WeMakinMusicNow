from isobar import *
from scamp import *
import sched, time

scheduler = sched.scheduler(time.time, time.sleep)

def play_scamp_note():
    # call into SCAMP to play something
    session = Session()  # your active Session
    flute = session.new_part("Flute")
    flute.play_note(72, length=1.0, volume=0.6)
    # re-schedule the same event
    scheduler.enter(1.0, 1, play_scamp_note)

scheduler.enter(1.0, 1, play_scamp_note)
scheduler.run()