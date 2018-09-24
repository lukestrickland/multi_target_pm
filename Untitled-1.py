import csv
from pprint import pprint
with open('stop_trials.csv', 'rb') as f:
    reader = csv.reader(f)
    headers = reader.next()
    column = {h:[] for h in headers}
    for row in reader:
        for h, v in zip(headers, row):
            column[h].append(v)
  
print(column['correct_response'])