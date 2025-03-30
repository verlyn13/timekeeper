"""
Helper script to fix the test_task_scheduler_integration.py file.
It copies the content from test_temporal_adaptation_effect.py into the right spot.
"""

import re

# Read the original file
with open("test_task_scheduler_integration.py", "r") as f:
    content = f.read()

# Read the fixed method
with open("test_temporal_adaptation_effect.py", "r") as f:
    fixed_method = f.read()
    # Skip the docstring at the top
    fixed_method = "\n".join(fixed_method.split("\n")[3:])

# Find the beginning of the problematic method
start_pattern = r"def test_temporal_adaptation_effect\(self, adaptive_scheduler, adaptive_temporal\):"
start_match = re.search(start_pattern, content)
if not start_match:
    print("Couldn't find the method to replace")
    exit(1)

start_pos = start_match.start()

# Find the beginning of the next method
next_pattern = (
    r"def test_scheduling_with_adapted_temporal_system\(self, adaptive_temporal\):"
)
next_match = re.search(next_pattern, content)
if not next_match:
    print("Couldn't find the next method")
    exit(1)

end_pos = next_match.start()

# Replace the method
new_content = content[:start_pos] + fixed_method + content[end_pos:]

# Write back to the file
with open("test_task_scheduler_integration.py", "w") as f:
    f.write(new_content)

print("Successfully fixed the test file!")
