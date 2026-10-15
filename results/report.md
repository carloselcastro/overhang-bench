# overhang-bench report

All print numbers are *estimates*: `proxy` = overhang-bench's vertical-column model; `PrusaSlicer` = PrusaSlicer-2.9.6 G-code estimates with scripts/prusaslicer_reference.ini. None of them is a measurement of a physical print.

## 1. Reproduction of Castro (2020), Table 4.2.1

Angular distance (degrees) between the build direction of Table 4.2.1 and the one found here.

| mesh | Table 4.2.1 (t1, t2) | objective | search | found (t1, t2) | angle to table (deg) |
|---|---|---|---|---|---|
| arm | (-2.7444, 0.0799) | castro-code | grid | (-2.7053, 0.0873) | 2.27 |
| arm | (-2.7444, 0.0799) | castro-code | mcd-asrun | (-2.7440, 0.0799) | 0.02 |
| arm | (-2.7444, 0.0799) | castro-code | mcd | (-2.7416, 0.0802) | 0.16 |
| arm | (-2.7444, 0.0799) | castro-code | rcsp | (-2.7443, 0.0799) | 0.01 |
| arm | (-2.7444, 0.0799) | castro-code | sphere | (-2.7276, 0.0822) | 0.97 |
| arm | (-2.7444, 0.0799) | castro-eq | grid | (-2.6878, 0.0873) | 3.26 |
| arm | (-2.7444, 0.0799) | castro-eq | mcd-asrun | (-2.7447, 0.0799) | 0.02 |
| arm | (-2.7444, 0.0799) | castro-eq | mcd | (-2.7448, 0.0799) | 0.02 |
| arm | (-2.7444, 0.0799) | castro-eq | rcsp | (-2.7681, 0.0729) | 1.41 |
| arm | (-2.7444, 0.0799) | castro-eq | sphere | (-2.7276, 0.0820) | 0.97 |
| bunny | (-0.1788, 0.5579) | castro-code | grid | (-0.1745, 0.5585) | 0.21 |
| bunny | (-0.1788, 0.5579) | castro-code | mcd-asrun | (-0.1677, 0.5386) | 1.23 |
| bunny | (-0.1788, 0.5579) | castro-code | mcd | (-0.1677, 0.5386) | 1.23 |
| bunny | (-0.1788, 0.5579) | castro-code | rcsp | (-0.1767, 0.5544) | 0.23 |
| bunny | (-0.1788, 0.5579) | castro-code | sphere | (-0.1685, 0.5400) | 1.14 |
| bunny | (-0.1788, 0.5579) | castro-eq | grid | (-0.1745, 0.5585) | 0.21 |
| bunny | (-0.1788, 0.5579) | castro-eq | mcd-asrun | (-0.1693, 0.5412) | 1.06 |
| bunny | (-0.1788, 0.5579) | castro-eq | mcd | (-0.1810, 0.5616) | 0.24 |
| bunny | (-0.1788, 0.5579) | castro-eq | rcsp | (-0.2070, 0.5977) | 2.65 |
| bunny | (-0.1788, 0.5579) | castro-eq | sphere | (-0.1705, 0.5437) | 0.91 |
| camel_b | (2.9598, -1.4669) | castro-code | grid | (2.8623, -1.4835) | 1.09 |
| camel_b | (2.9598, -1.4669) | castro-code | mcd-asrun | (2.9189, -1.4744) | 0.49 |
| camel_b | (2.9598, -1.4669) | castro-code | mcd | (2.8045, -1.4902) | 1.56 |
| camel_b | (2.9598, -1.4669) | castro-code | rcsp | (2.9812, -1.4623) | 0.29 |
| camel_b | (2.9598, -1.4669) | castro-code | sphere | (2.8706, -1.4819) | 0.99 |
| camel_b | (2.9598, -1.4669) | castro-eq | grid | (2.0944, -1.5184) | 4.61 |
| camel_b | (2.9598, -1.4669) | castro-eq | mcd-asrun | (2.9182, -1.4688) | 0.27 |
| camel_b | (2.9598, -1.4669) | castro-eq | mcd | (2.7945, -1.4872) | 1.46 |
| camel_b | (2.9598, -1.4669) | castro-eq | rcsp | (2.8101, 1.4855) | 169.19 |
| camel_b | (2.9598, -1.4669) | castro-eq | sphere | (2.1572, -1.5172) | 4.41 |
| cow | (-1.5708, -0.0924) | castro-code | grid | (-1.5708, -0.0873) | 0.29 |
| cow | (-1.5708, -0.0924) | castro-code | mcd-asrun | (-1.5708, -0.0924) | 0.00 |
| cow | (-1.5708, -0.0924) | castro-code | mcd | (-1.5708, -0.0924) | 0.00 |
| cow | (-1.5708, -0.0924) | castro-code | rcsp | (-1.5708, -0.0924) | 0.00 |
| cow | (-1.5708, -0.0924) | castro-code | sphere | (-1.5708, -0.0924) | 0.00 |
| cow | (-1.5708, -0.0924) | castro-eq | grid | (-1.5708, -0.0873) | 0.29 |
| cow | (-1.5708, -0.0924) | castro-eq | mcd-asrun | (-1.5708, -0.0924) | 0.00 |
| cow | (-1.5708, -0.0924) | castro-eq | mcd | (-1.5708, -0.0924) | 0.00 |
| cow | (-1.5708, -0.0924) | castro-eq | rcsp | (-1.5704, -0.0924) | 0.02 |
| cow | (-1.5708, -0.0924) | castro-eq | sphere | (-1.5708, -0.0924) | 0.00 |
| horse_quad | (-1.4316, 0.2639) | castro-code | grid | (-1.4137, 0.2618) | 1.00 |
| horse_quad | (-1.4316, 0.2639) | castro-code | mcd-asrun | (-1.4392, 0.2664) | 0.44 |
| horse_quad | (-1.4316, 0.2639) | castro-code | mcd | (-1.4392, 0.2664) | 0.44 |
| horse_quad | (-1.4316, 0.2639) | castro-code | rcsp | (-1.4426, 0.2676) | 0.65 |
| horse_quad | (-1.4316, 0.2639) | castro-code | sphere | (-1.4352, 0.2651) | 0.21 |
| horse_quad | (-1.4316, 0.2639) | castro-eq | grid | (-1.4137, 0.2618) | 1.00 |
| horse_quad | (-1.4316, 0.2639) | castro-eq | mcd-asrun | (-1.4301, 0.2637) | 0.08 |
| horse_quad | (-1.4316, 0.2639) | castro-eq | mcd | (-1.4162, 0.2611) | 0.87 |
| horse_quad | (-1.4316, 0.2639) | castro-eq | rcsp | (-1.4384, 0.2665) | 0.40 |
| horse_quad | (-1.4316, 0.2639) | castro-eq | sphere | (-1.4265, 0.2630) | 0.29 |
| decimated-knight | (0.0982, 0.0074) | castro-code | grid | (0.0873, 0.0000) | 0.76 |
| decimated-knight | (0.0982, 0.0074) | castro-code | mcd-asrun | (0.0982, 0.0074) | 0.00 |
| decimated-knight | (0.0982, 0.0074) | castro-code | mcd | (0.0982, 0.0075) | 0.01 |
| decimated-knight | (0.0982, 0.0074) | castro-code | rcsp | (0.0982, 0.0074) | 0.00 |
| decimated-knight | (0.0982, 0.0074) | castro-code | sphere | (0.0982, 0.0074) | 0.00 |
| decimated-knight | (0.0982, 0.0074) | castro-eq | grid | (0.0873, 0.0000) | 0.76 |
| decimated-knight | (0.0982, 0.0074) | castro-eq | mcd-asrun | (0.0908, 0.0004) | 0.58 |
| decimated-knight | (0.0982, 0.0074) | castro-eq | mcd | (0.0908, 0.0004) | 0.58 |
| decimated-knight | (0.0982, 0.0074) | castro-eq | rcsp | (0.0908, 0.0004) | 0.58 |
| decimated-knight | (0.0982, 0.0074) | castro-eq | sphere | (0.0908, 0.0004) | 0.58 |
| decimated-max | (-1.8040, 0.0235) | castro-code | grid | (-1.7977, 0.0175) | 0.50 |
| decimated-max | (-1.8040, 0.0235) | castro-code | mcd-asrun | (-1.8040, 0.0235) | 0.00 |
| decimated-max | (-1.8040, 0.0235) | castro-code | mcd | (-1.8040, 0.0235) | 0.00 |
| decimated-max | (-1.8040, 0.0235) | castro-code | rcsp | (-1.8040, 0.0235) | 0.00 |
| decimated-max | (-1.8040, 0.0235) | castro-code | sphere | (-1.8040, 0.0235) | 0.00 |
| decimated-max | (-1.8040, 0.0235) | castro-eq | grid | (-1.7977, 0.0175) | 0.50 |
| decimated-max | (-1.8040, 0.0235) | castro-eq | mcd-asrun | (-1.8056, 0.0250) | 0.13 |
| decimated-max | (-1.8040, 0.0235) | castro-eq | mcd | (-1.8056, 0.0250) | 0.13 |
| decimated-max | (-1.8040, 0.0235) | castro-eq | rcsp | (-1.8056, 0.0250) | 0.13 |
| decimated-max | (-1.8040, 0.0235) | castro-eq | sphere | (-1.8056, 0.0250) | 0.13 |
| heart | (-2.6011, 0.0370) | castro-code | grid | (-2.6005, 0.0349) | 0.12 |
| heart | (-2.6011, 0.0370) | castro-code | mcd-asrun | (-2.6015, 0.0372) | 0.03 |
| heart | (-2.6011, 0.0370) | castro-code | mcd | (-2.6010, 0.0364) | 0.03 |
| heart | (-2.6011, 0.0370) | castro-code | rcsp | (-2.5997, 0.0216) | 0.89 |
| heart | (-2.6011, 0.0370) | castro-code | sphere | (-2.6011, 0.0370) | 0.00 |
| heart | (-2.6011, 0.0370) | castro-eq | grid | (-2.6005, 0.0349) | 0.12 |
| heart | (-2.6011, 0.0370) | castro-eq | mcd-asrun | (-2.5994, 0.0304) | 0.39 |
| heart | (-2.6011, 0.0370) | castro-eq | mcd | (-2.5994, 0.0304) | 0.39 |
| heart | (-2.6011, 0.0370) | castro-eq | rcsp | (-2.6146, 0.0454) | 0.91 |
| heart | (-2.6011, 0.0370) | castro-eq | sphere | (-2.5994, 0.0304) | 0.39 |
| skull | (3.1004, -0.4287) | castro-code | grid | (3.1067, -0.4189) | 0.65 |
| skull | (3.1004, -0.4287) | castro-code | mcd-asrun | (3.1132, -0.4177) | 0.92 |
| skull | (3.1004, -0.4287) | castro-code | mcd | (3.1003, -0.4289) | 0.01 |
| skull | (3.1004, -0.4287) | castro-code | rcsp | (3.1267, 0.4029) | 47.67 |
| skull | (3.1004, -0.4287) | castro-code | sphere | (3.1004, -0.4287) | 0.00 |
| skull | (3.1004, -0.4287) | castro-eq | grid | (3.0718, -0.4887) | 3.74 |
| skull | (3.1004, -0.4287) | castro-eq | mcd-asrun | (3.0597, -0.5284) | 6.08 |
| skull | (3.1004, -0.4287) | castro-eq | mcd | (3.0754, -0.4906) | 3.77 |
| skull | (3.1004, -0.4287) | castro-eq | rcsp | (3.0743, -0.4933) | 3.93 |
| skull | (3.1004, -0.4287) | castro-eq | sphere | (3.0757, -0.4900) | 3.73 |

## 2. Search strategies

f relative to the best value found by any strategy for that (mesh, objective); 0 % = found the best.

| mesh | objective | search | f − f* (%) | evaluations | time (s) |
|---|---|---|---|---|---|
| arm | castro-code | grid | 1.44 | 65341 | 0.44 |
| arm | castro-code | mcd-asrun | 0.01 | 13947 | 0.28 |
| arm | castro-code | mcd | 0.06 | 8732 | 0.17 |
| arm | castro-code | rcsp | 0.00 | 9053 | 0.19 |
| arm | castro-code | sphere | 0.37 | 22293 | 0.15 |
| arm | castro-eq | grid | 1.31 | 65341 | 0.41 |
| arm | castro-eq | mcd-asrun | 0.00 | 16465 | 0.33 |
| arm | castro-eq | mcd | 0.00 | 12704 | 0.26 |
| arm | castro-eq | rcsp | 1.05 | 10022 | 0.21 |
| arm | castro-eq | sphere | 0.41 | 21810 | 0.16 |
| arm | alexander | grid | 0.61 | 65341 | 32.99 |
| arm | alexander | mcd-asrun | 0.42 | 4892 | 7.12 |
| arm | alexander | mcd | 0.03 | 4808 | 3.82 |
| arm | alexander | rcsp | 0.03 | 4616 | 3.30 |
| arm | alexander | sphere | 0.00 | 21131 | 3.28 |
| bunny | castro-code | grid | 0.19 | 65341 | 0.28 |
| bunny | castro-code | mcd-asrun | 0.00 | 8066 | 0.07 |
| bunny | castro-code | mcd | 0.00 | 7862 | 0.07 |
| bunny | castro-code | rcsp | 0.09 | 4558 | 0.04 |
| bunny | castro-code | sphere | 0.01 | 22249 | 0.09 |
| bunny | castro-eq | grid | 0.17 | 65341 | 0.40 |
| bunny | castro-eq | mcd-asrun | 0.00 | 7918 | 0.08 |
| bunny | castro-eq | mcd | 0.10 | 7497 | 0.07 |
| bunny | castro-eq | rcsp | 0.69 | 4376 | 0.04 |
| bunny | castro-eq | sphere | 0.00 | 23415 | 0.14 |
| bunny | alexander | grid | 0.82 | 65341 | 4.43 |
| bunny | alexander | mcd-asrun | 0.44 | 4645 | 2.19 |
| bunny | alexander | mcd | 0.73 | 5335 | 2.42 |
| bunny | alexander | rcsp | 1.30 | 4477 | 2.18 |
| bunny | alexander | sphere | 0.00 | 21295 | 1.93 |
| camel_b | castro-code | grid | 0.08 | 65341 | 0.29 |
| camel_b | castro-code | mcd-asrun | 0.15 | 13070 | 0.06 |
| camel_b | castro-code | mcd | 0.00 | 14272 | 0.07 |
| camel_b | castro-code | rcsp | 0.21 | 11447 | 0.05 |
| camel_b | castro-code | sphere | 0.09 | 23238 | 0.07 |
| camel_b | castro-eq | grid | 0.00 | 65341 | 0.30 |
| camel_b | castro-eq | mcd-asrun | 0.37 | 13864 | 0.07 |
| camel_b | castro-eq | mcd | 0.07 | 13256 | 0.07 |
| camel_b | castro-eq | rcsp | 0.07 | 12259 | 0.06 |
| camel_b | castro-eq | sphere | 0.00 | 21981 | 0.08 |
| camel_b | alexander | grid | 1.74 | 65341 | 2.89 |
| camel_b | alexander | mcd-asrun | 3.99 | 4344 | 1.00 |
| camel_b | alexander | mcd | 2.94 | 4692 | 1.14 |
| camel_b | alexander | rcsp | 3.26 | 4630 | 1.13 |
| camel_b | alexander | sphere | 0.00 | 20835 | 0.88 |
| cow | castro-code | grid | 1.01 | 65341 | 0.31 |
| cow | castro-code | mcd-asrun | 0.00 | 14473 | 0.10 |
| cow | castro-code | mcd | 0.00 | 12719 | 0.09 |
| cow | castro-code | rcsp | 0.00 | 14186 | 0.10 |
| cow | castro-code | sphere | 0.00 | 26024 | 0.12 |
| cow | castro-eq | grid | 1.01 | 65341 | 0.42 |
| cow | castro-eq | mcd-asrun | 0.00 | 23439 | 0.17 |
| cow | castro-eq | mcd | 0.00 | 57691 | 0.40 |
| cow | castro-eq | rcsp | 0.01 | 15416 | 0.11 |
| cow | castro-eq | sphere | 0.00 | 25060 | 0.16 |
| cow | alexander | grid | 1.74 | 65341 | 5.24 |
| cow | alexander | mcd-asrun | 0.87 | 4811 | 4.46 |
| cow | alexander | mcd | 0.00 | 4747 | 4.28 |
| cow | alexander | rcsp | 0.00 | 5525 | 5.48 |
| cow | alexander | sphere | 0.00 | 20999 | 2.33 |
| horse_quad | castro-code | grid | 0.33 | 65341 | 0.32 |
| horse_quad | castro-code | mcd-asrun | 0.05 | 6125 | 0.06 |
| horse_quad | castro-code | mcd | 0.05 | 6855 | 0.07 |
| horse_quad | castro-code | rcsp | 0.09 | 5541 | 0.05 |
| horse_quad | castro-code | sphere | 0.00 | 21571 | 0.11 |
| horse_quad | castro-eq | grid | 0.36 | 65341 | 0.34 |
| horse_quad | castro-eq | mcd-asrun | 0.00 | 7180 | 0.09 |
| horse_quad | castro-eq | mcd | 0.16 | 7198 | 0.10 |
| horse_quad | castro-eq | rcsp | 0.09 | 4930 | 0.05 |
| horse_quad | castro-eq | sphere | 0.03 | 21250 | 0.13 |
| horse_quad | alexander | grid | 3.05 | 65341 | 10.21 |
| horse_quad | alexander | mcd-asrun | 9.81 | 4501 | 3.21 |
| horse_quad | alexander | mcd | 4.24 | 4761 | 4.06 |
| horse_quad | alexander | rcsp | 0.00 | 4592 | 4.22 |
| horse_quad | alexander | sphere | 0.00 | 20906 | 3.76 |
| decimated-knight | castro-code | grid | 1.99 | 65341 | 0.07 |
| decimated-knight | castro-code | mcd-asrun | 0.00 | 20389 | 0.05 |
| decimated-knight | castro-code | mcd | 0.01 | 14855 | 0.04 |
| decimated-knight | castro-code | rcsp | 0.00 | 65101 | 0.20 |
| decimated-knight | castro-code | sphere | 0.00 | 23114 | 0.03 |
| decimated-knight | castro-eq | grid | 0.29 | 65341 | 0.07 |
| decimated-knight | castro-eq | mcd-asrun | 0.00 | 24267 | 0.06 |
| decimated-knight | castro-eq | mcd | 0.00 | 32467 | 0.17 |
| decimated-knight | castro-eq | rcsp | 0.00 | 49707 | 0.17 |
| decimated-knight | castro-eq | sphere | 0.00 | 24004 | 0.04 |
| decimated-knight | alexander | grid | 0.02 | 65341 | 2.52 |
| decimated-knight | alexander | mcd-asrun | 0.00 | 4757 | 0.60 |
| decimated-knight | alexander | mcd | 0.00 | 5044 | 0.69 |
| decimated-knight | alexander | rcsp | 0.00 | 5184 | 0.86 |
| decimated-knight | alexander | sphere | 0.00 | 21273 | 0.79 |
| decimated-max | castro-code | grid | 0.00 | 65341 | 0.60 |
| decimated-max | castro-code | mcd-asrun | 0.00 | 15550 | 0.39 |
| decimated-max | castro-code | mcd | 0.00 | 15482 | 0.41 |
| decimated-max | castro-code | rcsp | 0.00 | 16544 | 0.43 |
| decimated-max | castro-code | sphere | 0.00 | 20383 | 0.19 |
| decimated-max | castro-eq | grid | 0.01 | 65341 | 0.65 |
| decimated-max | castro-eq | mcd-asrun | 0.00 | 17147 | 0.53 |
| decimated-max | castro-eq | mcd | 0.00 | 18733 | 0.65 |
| decimated-max | castro-eq | rcsp | 0.00 | 17206 | 0.58 |
| decimated-max | castro-eq | sphere | 0.00 | 20393 | 0.22 |
| decimated-max | alexander | grid | 0.43 | 65341 | 25.43 |
| decimated-max | alexander | mcd-asrun | 0.00 | 4321 | 6.23 |
| decimated-max | alexander | mcd | 0.00 | 4587 | 6.26 |
| decimated-max | alexander | rcsp | 0.10 | 4867 | 7.08 |
| decimated-max | alexander | sphere | 0.14 | 20921 | 8.58 |
| heart | castro-code | grid | 0.07 | 65341 | 0.98 |
| heart | castro-code | mcd-asrun | 0.02 | 16138 | 0.55 |
| heart | castro-code | mcd | 0.01 | 14401 | 0.50 |
| heart | castro-code | rcsp | 0.25 | 21445 | 0.76 |
| heart | castro-code | sphere | 0.00 | 24811 | 0.45 |
| heart | castro-eq | grid | 0.26 | 65341 | 1.10 |
| heart | castro-eq | mcd-asrun | 0.00 | 15565 | 0.63 |
| heart | castro-eq | mcd | 0.00 | 15878 | 0.78 |
| heart | castro-eq | rcsp | 0.80 | 13281 | 0.53 |
| heart | castro-eq | sphere | 0.00 | 24792 | 0.52 |
| heart | alexander | grid | 0.83 | 65341 | 87.77 |
| heart | alexander | mcd-asrun | 0.27 | 3825 | 12.25 |
| heart | alexander | mcd | 0.27 | 4056 | 12.78 |
| heart | alexander | rcsp | 0.30 | 3958 | 11.78 |
| heart | alexander | sphere | 0.00 | 20819 | 9.82 |
| skull | castro-code | grid | 0.23 | 65341 | 0.32 |
| skull | castro-code | mcd-asrun | 0.28 | 19770 | 0.13 |
| skull | castro-code | mcd | 0.00 | 16737 | 0.10 |
| skull | castro-code | rcsp | 0.68 | 22518 | 0.14 |
| skull | castro-code | sphere | 0.00 | 22927 | 0.11 |
| skull | castro-eq | grid | 0.26 | 65341 | 0.43 |
| skull | castro-eq | mcd-asrun | 0.73 | 22195 | 0.14 |
| skull | castro-eq | mcd | 0.01 | 16834 | 0.11 |
| skull | castro-eq | rcsp | 0.07 | 82081 | 0.52 |
| skull | castro-eq | sphere | 0.00 | 24814 | 0.13 |
| skull | alexander | grid | 0.55 | 65341 | 4.17 |
| skull | alexander | mcd-asrun | 0.40 | 4184 | 1.74 |
| skull | alexander | mcd | 0.00 | 4118 | 4.33 |
| skull | alexander | rcsp | 0.15 | 4602 | 4.57 |
| skull | alexander | sphere | 0.22 | 20935 | 2.77 |
| arm | ezair | ezair | 0.00 | 14058 | 7.64 |
| arm | support-volume | ezair | 0.00 | 9966 | 15.68 |
| bunny | ezair | ezair | 0.00 | 11957 | 11.59 |
| bunny | support-volume | ezair | 0.00 | 9941 | 31.78 |
| camel_b | ezair | ezair | 0.00 | 12292 | 8.50 |
| camel_b | support-volume | ezair | 0.00 | 10730 | 27.95 |
| cow | ezair | ezair | 0.00 | 9250 | 7.04 |
| cow | support-volume | ezair | 0.00 | 10685 | 13.91 |
| horse_quad | ezair | ezair | 0.00 | 11685 | 5.76 |
| horse_quad | support-volume | ezair | 0.00 | 10926 | 14.99 |
| decimated-knight | ezair | ezair | 0.00 | 10517 | 7.47 |
| decimated-knight | support-volume | ezair | 0.00 | 10147 | 8.31 |
| decimated-max | ezair | ezair | 0.00 | 11108 | 29.84 |
| decimated-max | support-volume | ezair | 0.00 | 11063 | 37.46 |
| heart | ezair | ezair | 0.00 | 11096 | 22.51 |
| heart | support-volume | ezair | 0.00 | 10525 | 47.53 |
| skull | ezair | ezair | 0.00 | 10137 | 13.77 |
| skull | support-volume | ezair | 0.00 | 9149 | 25.84 |
| arm | goguelin-len | sphere | 0.00 | 21241 | 2.82 |
| arm | goguelin-vol | sphere | 0.00 | 20977 | 6.80 |
| bunny | goguelin-len | sphere | 0.00 | 21039 | 1.50 |
| bunny | goguelin-vol | sphere | 0.00 | 21010 | 3.83 |
| camel_b | goguelin-len | sphere | 0.00 | 21272 | 1.07 |
| camel_b | goguelin-vol | sphere | 0.00 | 21013 | 1.70 |
| cow | goguelin-len | sphere | 0.00 | 20941 | 1.14 |
| cow | goguelin-vol | sphere | 0.00 | 20849 | 2.98 |
| horse_quad | goguelin-len | sphere | 0.00 | 20877 | 0.84 |
| horse_quad | goguelin-vol | sphere | 0.00 | 20936 | 2.14 |
| decimated-knight | goguelin-len | sphere | 0.00 | 20856 | 0.20 |
| decimated-knight | goguelin-vol | sphere | 0.00 | 20831 | 0.51 |
| decimated-max | goguelin-len | sphere | 0.00 | 20951 | 2.00 |
| decimated-max | goguelin-vol | sphere | 0.00 | 20943 | 5.18 |
| heart | goguelin-len | sphere | 0.00 | 20806 | 4.89 |
| heart | goguelin-vol | sphere | 0.00 | 20928 | 12.43 |
| skull | goguelin-len | sphere | 0.00 | 20794 | 1.01 |
| skull | goguelin-vol | sphere | 0.00 | 20975 | 2.98 |

## 3. Print estimates per pose

| mesh | pose | height (mm) | overhang area (mm²) | proxy support vol. (mm³) | proxy filament (m) | proxy time (min) | PrusaSlicer filament (m) | PrusaSlicer support filament (m) | PrusaSlicer time (min) |
|---|---|---|---|---|---|---|---|---|---|
| arm | initial | 13.8 | 281 | 1257 | 0.66 | 8 | 1.17 | 0.57 | 25 |
| arm | castro-code | 13.2 | 331 | 241 | 0.59 | 8 | 0.84 | 0.22 | 20 |
| arm | castro-eq | 13.2 | 331 | 241 | 0.59 | 8 | 0.84 | 0.22 | 20 |
| arm | alexander | 56.1 | 35 | 21 | 0.58 | 13 | 0.96 | 0.22 | 31 |
| arm | ezair | 13.2 | 331 | 241 | 0.59 | 8 | 0.84 | 0.22 | 20 |
| arm | support-volume | 55.8 | 35 | 21 | 0.58 | 13 | 0.98 | 0.23 | 32 |
| arm | goguelin-len | 52.6 | 36 | 21 | 0.58 | 12 | 0.83 | 0.09 | 27 |
| arm | goguelin-vol | 52.6 | 36 | 21 | 0.58 | 12 | 0.83 | 0.09 | 27 |
| arm | tweaker3-vol | 18.4 | 264 | 514 | 0.61 | 8 | 1.00 | 0.37 | 23 |
| arm | tweaker3-sur | 18.4 | 264 | 514 | 0.61 | 8 | 1.00 | 0.37 | 23 |
| bunny | initial | 46.5 | 1629 | 22711 | 6.85 | 74 | 10.24 | 4.33 | 171 |
| bunny | castro-code | 43.8 | 1281 | 7142 | 5.88 | 64 | 8.12 | 2.14 | 147 |
| bunny | castro-eq | 43.9 | 1279 | 7140 | 5.88 | 64 | 8.09 | 2.12 | 147 |
| bunny | alexander | 64.0 | 813 | 10612 | 6.09 | 68 | 9.82 | 3.98 | 166 |
| bunny | ezair | 59.7 | 1430 | 6720 | 5.85 | 65 | 8.16 | 2.35 | 141 |
| bunny | support-volume | 47.2 | 1064 | 5986 | 5.80 | 63 | 8.23 | 2.27 | 151 |
| bunny | goguelin-len | 48.2 | 1078 | 6084 | 5.81 | 64 | 8.32 | 2.36 | 150 |
| bunny | goguelin-vol | 47.2 | 1062 | 5939 | 5.80 | 63 | 8.20 | 2.24 | 150 |
| bunny | tweaker3-vol | 60.3 | 1193 | 18286 | 6.57 | 73 | 10.23 | 4.44 | 167 |
| bunny | tweaker3-sur | 47.8 | 1558 | 16040 | 6.43 | 70 | 9.79 | 3.84 | 168 |
| camel_b | initial | 60.0 | 494 | 5386 | 2.38 | 31 | 4.51 | 2.37 | 87 |
| camel_b | castro-code | 18.5 | 1147 | 3418 | 2.26 | 25 | 3.96 | 1.91 | 80 |
| camel_b | castro-eq | 18.5 | 1175 | 3590 | 2.27 | 25 | 3.99 | 1.94 | 82 |
| camel_b | alexander | 60.5 | 312 | 3430 | 2.26 | 30 | 4.23 | 2.00 | 94 |
| camel_b | ezair | 18.5 | 1147 | 3448 | 2.26 | 25 | 3.94 | 1.89 | 80 |
| camel_b | support-volume | 57.9 | 340 | 2586 | 2.21 | 29 | 4.12 | 1.94 | 91 |
| camel_b | goguelin-len | 18.5 | 1174 | 3578 | 2.27 | 25 | 3.95 | 1.90 | 81 |
| camel_b | goguelin-vol | 58.0 | 334 | 2614 | 2.21 | 29 | 4.23 | 2.05 | 93 |
| camel_b | tweaker3-vol | 58.5 | 437 | 9104 | 2.61 | 33 | 4.99 | 2.76 | 97 |
| camel_b | tweaker3-sur | 58.5 | 437 | 9104 | 2.61 | 33 | 4.99 | 2.76 | 97 |
| cow | initial | 19.5 | 977 | 3835 | 2.02 | 22 | 3.29 | 1.49 | 64 |
| cow | castro-code | 34.9 | 409 | 1128 | 1.85 | 23 | 2.59 | 0.82 | 55 |
| cow | castro-eq | 34.9 | 409 | 1128 | 1.85 | 23 | 2.59 | 0.82 | 55 |
| cow | alexander | 46.6 | 198 | 2635 | 1.94 | 25 | 3.29 | 1.47 | 65 |
| cow | ezair | 34.9 | 409 | 1128 | 1.85 | 23 | 2.59 | 0.82 | 55 |
| cow | support-volume | 35.2 | 401 | 1093 | 1.84 | 23 | 2.48 | 0.71 | 53 |
| cow | goguelin-len | 35.0 | 404 | 1102 | 1.84 | 23 | 2.54 | 0.77 | 53 |
| cow | goguelin-vol | 35.1 | 401 | 1107 | 1.85 | 23 | 2.51 | 0.75 | 53 |
| cow | tweaker3-vol | 36.7 | 471 | 5250 | 2.10 | 25 | 3.42 | 1.63 | 63 |
| cow | tweaker3-sur | 36.7 | 423 | 2057 | 1.90 | 23 | 2.70 | 0.91 | 57 |
| horse_quad | initial | 27.5 | 892 | 3973 | 2.02 | 23 | 3.54 | 1.62 | 70 |
| horse_quad | castro-code | 44.7 | 460 | 1367 | 1.86 | 24 | 2.44 | 0.57 | 56 |
| horse_quad | castro-eq | 44.7 | 462 | 1357 | 1.86 | 24 | 2.43 | 0.57 | 55 |
| horse_quad | alexander | 73.0 | 224 | 4506 | 2.05 | 29 | 4.40 | 2.40 | 84 |
| horse_quad | ezair | 44.9 | 468 | 1476 | 1.86 | 24 | 2.44 | 0.58 | 56 |
| horse_quad | support-volume | 44.7 | 459 | 1360 | 1.86 | 24 | 2.44 | 0.58 | 56 |
| horse_quad | goguelin-len | 44.7 | 456 | 1347 | 1.86 | 24 | 2.45 | 0.59 | 56 |
| horse_quad | goguelin-vol | 44.7 | 457 | 1350 | 1.86 | 24 | 2.44 | 0.58 | 56 |
| horse_quad | tweaker3-vol | 27.5 | 892 | 3973 | 2.02 | 23 | 3.54 | 1.62 | 70 |
| horse_quad | tweaker3-sur | 50.5 | 397 | 3703 | 2.00 | 26 | 3.40 | 1.56 | 70 |
| decimated-knight | initial | 18.4 | 824 | 3435 | 1.95 | 22 | 3.31 | 1.42 | 70 |
| decimated-knight | castro-code | 19.3 | 824 | 2591 | 1.90 | 21 | 3.14 | 1.26 | 68 |
| decimated-knight | castro-eq | 19.0 | 827 | 2464 | 1.89 | 21 | 3.09 | 1.21 | 67 |
| decimated-knight | alexander | 59.5 | 280 | 2230 | 1.88 | 26 | 3.59 | 1.39 | 90 |
| decimated-knight | ezair | 19.0 | 827 | 2465 | 1.89 | 21 | 3.09 | 1.21 | 67 |
| decimated-knight | support-volume | 59.7 | 283 | 2124 | 1.87 | 26 | 3.61 | 1.39 | 92 |
| decimated-knight | goguelin-len | 18.9 | 822 | 2454 | 1.89 | 21 | 3.10 | 1.22 | 67 |
| decimated-knight | goguelin-vol | 18.9 | 822 | 2454 | 1.89 | 21 | 3.10 | 1.22 | 67 |
| decimated-knight | tweaker3-vol | 60.0 | 300 | 2983 | 1.93 | 27 | 4.51 | 2.29 | 102 |
| decimated-knight | tweaker3-sur | 42.1 | 619 | 4844 | 2.04 | 25 | 4.33 | 2.14 | 98 |
| decimated-max | initial | 43.1 | 854 | 8176 | 4.32 | 48 | 6.22 | 2.14 | 101 |
| decimated-max | castro-code | 59.7 | 542 | 1208 | 3.89 | 46 | 4.65 | 0.71 | 75 |
| decimated-max | castro-eq | 59.7 | 542 | 1203 | 3.88 | 46 | 4.65 | 0.71 | 75 |
| decimated-max | alexander | 59.1 | 385 | 3999 | 4.06 | 48 | 5.66 | 1.71 | 89 |
| decimated-max | ezair | 33.2 | 1178 | 2494 | 3.97 | 43 | 5.10 | 1.03 | 88 |
| decimated-max | support-volume | 59.8 | 527 | 1063 | 3.88 | 46 | 4.68 | 0.72 | 75 |
| decimated-max | goguelin-len | 59.5 | 524 | 1145 | 3.88 | 46 | 4.67 | 0.73 | 75 |
| decimated-max | goguelin-vol | 59.5 | 531 | 1087 | 3.88 | 46 | 4.71 | 0.75 | 76 |
| decimated-max | tweaker3-vol | 57.6 | 588 | 1552 | 3.91 | 46 | 5.13 | 1.11 | 84 |
| decimated-max | tweaker3-sur | 57.6 | 588 | 1552 | 3.91 | 46 | 5.13 | 1.11 | 84 |
| heart | initial | 42.4 | 2797 | 35185 | 4.30 | 48 | 7.77 | 5.66 | 139 |
| heart | castro-code | 34.8 | 2520 | 23529 | 3.58 | 40 | 6.50 | 4.38 | 123 |
| heart | castro-eq | 34.8 | 2516 | 23379 | 3.57 | 40 | 6.46 | 4.35 | 122 |
| heart | alexander | 60.4 | 1371 | 19273 | 3.31 | 40 | 6.76 | 4.71 | 126 |
| heart | ezair | 34.8 | 2516 | 23372 | 3.57 | 40 | 6.46 | 4.35 | 122 |
| heart | support-volume | 60.9 | 1444 | 15838 | 3.10 | 38 | 7.70 | 5.65 | 146 |
| heart | goguelin-len | 39.4 | 2295 | 26591 | 3.77 | 42 | 7.01 | 4.92 | 130 |
| heart | goguelin-vol | 56.4 | 1505 | 18284 | 3.25 | 39 | 6.67 | 4.61 | 128 |
| heart | tweaker3-vol | 49.6 | 2339 | 28196 | 3.87 | 44 | 7.58 | 5.50 | 138 |
| heart | tweaker3-sur | 49.6 | 2339 | 28196 | 3.87 | 44 | 7.58 | 5.50 | 138 |
| skull | initial | 53.7 | 1206 | 8337 | 6.90 | 75 | 10.99 | 3.93 | 196 |
| skull | castro-code | 51.0 | 1221 | 6208 | 6.77 | 73 | 9.85 | 2.83 | 176 |
| skull | castro-eq | 50.3 | 1301 | 5984 | 6.76 | 73 | 9.18 | 2.64 | 164 |
| skull | alexander | 67.7 | 894 | 3513 | 6.60 | 74 | 8.44 | 1.87 | 157 |
| skull | ezair | 60.1 | 1349 | 4732 | 6.68 | 74 | 10.78 | 3.35 | 199 |
| skull | support-volume | 68.6 | 913 | 3414 | 6.59 | 74 | 8.49 | 1.91 | 158 |
| skull | goguelin-len | 50.5 | 1229 | 6012 | 6.76 | 73 | 9.14 | 2.59 | 164 |
| skull | goguelin-vol | 50.5 | 1229 | 5961 | 6.76 | 73 | 10.90 | 3.53 | 195 |
| skull | tweaker3-vol | 56.2 | 1500 | 7758 | 6.86 | 75 | 10.26 | 3.34 | 182 |
| skull | tweaker3-sur | 47.7 | 1943 | 13685 | 7.24 | 78 | 12.51 | 4.80 | 222 |

## 3b. Summary per method (PrusaSlicer estimates)

Median over meshes of the reduction relative to the initial pose; in parentheses, the number of meshes where the method is the best of all poses (ties count for each tied method).

| method | support filament | print time | total filament |
|---|---|---|---|
| alexander | -15.6% (1/9) | +2.0% (1/9) | -6.1% (1/9) |
| castro-code | -45.2% (0/9) | -14.0% (2/9) | -20.7% (0/9) |
| castro-eq | -45.2% (4/9) | -14.3% (2/9) | -21.0% (3/9) |
| ezair | -45.2% (2/9) | -13.3% (4/9) | -18.0% (3/9) |
| goguelin-len | -45.5% (1/9) | -12.4% (1/9) | -18.8% (1/9) |
| goguelin-vol | -48.3% (0/9) | -8.2% (0/9) | -19.9% (0/9) |
| support-volume | -51.5% (1/9) | -12.0% (1/9) | -19.6% (1/9) |
| tweaker3-sur | -3.7% (0/9) | -0.6% (0/9) | -4.1% (0/9) |
| tweaker3-vol | -0.0% (0/9) | -1.5% (0/9) | -0.1% (0/9) |

## 4. Does the proxy rank poses like the slicer?

Spearman rank correlation over all (mesh, pose) pairs, pooled; and per mesh the fraction of pose pairs ordered the same way (support).

- support: Spearman ρ = 0.958 (n = 90)
- total filament: Spearman ρ = 0.967 (n = 90)
- time: Spearman ρ = 0.911 (n = 90)
- within-mesh pairwise agreement on support: 302/405
