#!/usr/bin/env python
import re

# Read the file
with open('C:/Users/gmu_a/dev/BCP/BCP/GIF_and_CM/compute_parallel_transport_intrinsic.py', 'r') as f:
    code = f.read()

# Replace the problematic while True loop
old_code = '''    while True:
        i = 0
        try:
            angles_vertices_to_faces, middle_angle_time = compute_middle_angle(f, one_rings, integrated_angles, all_one_ring_angles)
            break
        except:
            print(f"Failed attempt number {i}")
            i += 1
            continue'''

new_code = '''    # Retry compute_middle_angle with a reasonable limit
    max_retries = 3
    angles_vertices_to_faces = None
    middle_angle_time = 0
    for attempt in range(max_retries):
        try:
            angles_vertices_to_faces, middle_angle_time = compute_middle_angle(f, one_rings, integrated_angles, all_one_ring_angles)
            break
        except Exception as e:
            print(f"Failed attempt number {attempt}: {e}")
            if attempt == max_retries - 1:
                print(f"All {max_retries} attempts failed. Using fallback (zeros).")
                angles_vertices_to_faces = np.zeros((f.shape[0], 3), dtype=np.float64)
                middle_angle_time = 0'''

if old_code in code:
    code = code.replace(old_code, new_code)
    with open('C:/Users/gmu_a/dev/BCP/BCP/GIF_and_CM/compute_parallel_transport_intrinsic.py', 'w') as f:
        f.write(code)
    print("File patched successfully")
else:
    print("Old code not found - already patched or file changed")
