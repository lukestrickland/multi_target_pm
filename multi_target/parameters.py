
# quick way to switch between pilot and
# actual experiment
pilot = True


instruct_delay = 5
memorize_delay = 120
puzzle_time = 180
first_trials = 321
second_trials = 643
break_delay = 60
break_time=120


if pilot:
    memorize_delay=5
    instruct_delay = 0
    puzzle_time = 5
    first_trials = 0
    second_trials = 1
    break_delay=5
    break_time=1