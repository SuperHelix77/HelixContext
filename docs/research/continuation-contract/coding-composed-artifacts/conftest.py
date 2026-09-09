# Frozen on/off task files are data. verify.py executes each in isolated staging;
# collecting both as application tests would collide on their original names.
collect_ignore = ['off', 'on']
