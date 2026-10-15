# overhang-bench report

All print numbers are *estimates*: `proxy` = overhang-bench's vertical-column model; `PrusaSlicer` = PrusaSlicer-2.9.6 G-code estimates with scripts/prusaslicer_reference.ini. None of them is a measurement of a physical print.

## 1. Reproduction of Castro (2020), Table 4.2.1

Angular distance (degrees) between the build direction of Table 4.2.1 and the one found here.

| mesh | Table 4.2.1 (t1, t2) | objective | search | found (t1, t2) | angle to table (deg) |
|---|---|---|---|---|---|
| arm | (-2.7444, 0.0799) | castro-eq | grid | (-2.6878, 0.0873) | 3.26 |
| arm | (-2.7444, 0.0799) | castro-eq | mcd | (-2.7448, 0.0799) | 0.02 |
| arm | (-2.7444, 0.0799) | castro-eq | rcsp | (-2.7681, 0.0729) | 1.41 |
| arm | (-2.7444, 0.0799) | castro-eq | sphere | (-2.7276, 0.0820) | 0.97 |
| bunny | (-0.1788, 0.5579) | castro-eq | grid | (-0.1745, 0.5585) | 0.21 |
| bunny | (-0.1788, 0.5579) | castro-eq | mcd | (-0.1810, 0.5616) | 0.24 |
| bunny | (-0.1788, 0.5579) | castro-eq | rcsp | (-0.2070, 0.5977) | 2.65 |
| bunny | (-0.1788, 0.5579) | castro-eq | sphere | (-0.1705, 0.5437) | 0.91 |
| camel_b | (2.9598, -1.4669) | castro-eq | grid | (2.0944, -1.5184) | 4.61 |
| camel_b | (2.9598, -1.4669) | castro-eq | mcd | (2.7945, -1.4872) | 1.46 |
| camel_b | (2.9598, -1.4669) | castro-eq | rcsp | (2.8101, 1.4855) | 169.19 |
| camel_b | (2.9598, -1.4669) | castro-eq | sphere | (2.1572, -1.5172) | 4.41 |
| cow | (-1.5708, -0.0924) | castro-eq | grid | (-1.5708, -0.0873) | 0.29 |
| cow | (-1.5708, -0.0924) | castro-eq | mcd | (-1.5708, -0.0924) | 0.00 |
| cow | (-1.5708, -0.0924) | castro-eq | rcsp | (-1.5704, -0.0924) | 0.02 |
| cow | (-1.5708, -0.0924) | castro-eq | sphere | (-1.5708, -0.0924) | 0.00 |
| horse_quad | (-1.4316, 0.2639) | castro-eq | grid | (-1.4137, 0.2618) | 1.00 |
| horse_quad | (-1.4316, 0.2639) | castro-eq | mcd | (-1.4162, 0.2611) | 0.87 |
| horse_quad | (-1.4316, 0.2639) | castro-eq | rcsp | (-1.4384, 0.2665) | 0.40 |
| horse_quad | (-1.4316, 0.2639) | castro-eq | sphere | (-1.4265, 0.2630) | 0.29 |
| decimated-knight | (0.0982, 0.0074) | castro-eq | grid | (0.0873, 0.0000) | 0.76 |
| decimated-knight | (0.0982, 0.0074) | castro-eq | mcd | (0.0908, 0.0004) | 0.58 |
| decimated-knight | (0.0982, 0.0074) | castro-eq | rcsp | (0.0908, 0.0004) | 0.58 |
| decimated-knight | (0.0982, 0.0074) | castro-eq | sphere | (0.0908, 0.0004) | 0.58 |
| decimated-max | (-1.8040, 0.0235) | castro-eq | grid | (-1.7977, 0.0175) | 0.50 |
| decimated-max | (-1.8040, 0.0235) | castro-eq | mcd | (-1.8056, 0.0250) | 0.13 |
| decimated-max | (-1.8040, 0.0235) | castro-eq | rcsp | (-1.8056, 0.0250) | 0.13 |
| decimated-max | (-1.8040, 0.0235) | castro-eq | sphere | (-1.8056, 0.0250) | 0.13 |
| heart | (-2.6011, 0.0370) | castro-eq | grid | (-2.6005, 0.0349) | 0.12 |
| heart | (-2.6011, 0.0370) | castro-eq | mcd | (-2.5994, 0.0304) | 0.39 |
| heart | (-2.6011, 0.0370) | castro-eq | rcsp | (-2.6146, 0.0454) | 0.91 |
| heart | (-2.6011, 0.0370) | castro-eq | sphere | (-2.5994, 0.0304) | 0.39 |
| skull | (3.1004, -0.4287) | castro-eq | grid | (3.0718, -0.4887) | 3.74 |
| skull | (3.1004, -0.4287) | castro-eq | mcd | (3.0754, -0.4906) | 3.77 |
| skull | (3.1004, -0.4287) | castro-eq | rcsp | (3.0743, -0.4933) | 3.93 |
| skull | (3.1004, -0.4287) | castro-eq | sphere | (3.0757, -0.4900) | 3.73 |

## 2. Search strategies

f relative to the best value found by any strategy for that (mesh, objective); 0 % = found the best.

| mesh | objective | search | f − f* (%) | evaluations | time (s) |
|---|---|---|---|---|---|
| arm | castro-eq | grid | 1.31 | 65341 | 0.53 |
| arm | castro-eq | mcd | 0.00 | 12704 | 0.26 |
| arm | castro-eq | rcsp | 1.05 | 10022 | 0.21 |
| arm | castro-eq | sphere | 0.41 | 21810 | 0.18 |
| bunny | castro-eq | grid | 0.16 | 65341 | 0.41 |
| bunny | castro-eq | mcd | 0.10 | 7497 | 0.07 |
| bunny | castro-eq | rcsp | 0.69 | 4376 | 0.04 |
| bunny | castro-eq | sphere | 0.00 | 23415 | 0.15 |
| camel_b | castro-eq | grid | 0.00 | 65341 | 0.29 |
| camel_b | castro-eq | mcd | 0.07 | 13256 | 0.07 |
| camel_b | castro-eq | rcsp | 0.07 | 12259 | 0.06 |
| camel_b | castro-eq | sphere | 0.00 | 21981 | 0.08 |
| cow | castro-eq | grid | 1.01 | 65341 | 0.42 |
| cow | castro-eq | mcd | 0.00 | 57691 | 0.86 |
| cow | castro-eq | rcsp | 0.01 | 15416 | 0.23 |
| cow | castro-eq | sphere | 0.00 | 25060 | 0.18 |
| horse_quad | castro-eq | grid | 0.32 | 65341 | 0.33 |
| horse_quad | castro-eq | mcd | 0.13 | 7198 | 0.10 |
| horse_quad | castro-eq | rcsp | 0.06 | 4930 | 0.06 |
| horse_quad | castro-eq | sphere | 0.00 | 21250 | 0.12 |
| decimated-knight | castro-eq | grid | 0.29 | 65341 | 0.08 |
| decimated-knight | castro-eq | mcd | 0.00 | 32467 | 0.08 |
| decimated-knight | castro-eq | rcsp | 0.00 | 49707 | 0.17 |
| decimated-knight | castro-eq | sphere | 0.00 | 24004 | 0.04 |
| decimated-max | castro-eq | grid | 0.01 | 65341 | 0.67 |
| decimated-max | castro-eq | mcd | 0.00 | 18733 | 0.56 |
| decimated-max | castro-eq | rcsp | 0.00 | 17206 | 0.48 |
| decimated-max | castro-eq | sphere | 0.00 | 20393 | 0.22 |
| heart | castro-eq | grid | 0.26 | 65341 | 0.60 |
| heart | castro-eq | mcd | 0.00 | 15878 | 0.31 |
| heart | castro-eq | rcsp | 0.80 | 13281 | 0.25 |
| heart | castro-eq | sphere | 0.00 | 24792 | 0.25 |
| skull | castro-eq | grid | 0.26 | 65341 | 0.35 |
| skull | castro-eq | mcd | 0.01 | 16834 | 0.21 |
| skull | castro-eq | rcsp | 0.07 | 82081 | 1.43 |
| skull | castro-eq | sphere | 0.00 | 24814 | 0.16 |
| arm | ezair | ezair | 0.00 | 13973 | 21.44 |
| bunny | ezair | ezair | 0.00 | 11962 | 45.82 |
| camel_b | ezair | ezair | 0.00 | 12382 | 29.81 |
| cow | ezair | ezair | 0.00 | 9250 | 28.72 |
| horse_quad | ezair | ezair | 0.00 | 11695 | 22.03 |
| decimated-knight | ezair | ezair | 0.00 | 10508 | 26.89 |
| decimated-max | ezair | ezair | 0.00 | 11108 | 58.08 |
| heart | ezair | ezair | 0.00 | 11102 | 70.93 |
| skull | ezair | ezair | 0.00 | 10137 | 50.92 |
| arm | alexander | sphere | 0.00 | 4938 | 0.75 |
| arm | goguelin-len | sphere | 0.00 | 5282 | 0.66 |
| bunny | alexander | sphere | 0.00 | 4969 | 0.67 |
| bunny | goguelin-len | sphere | 0.00 | 5045 | 0.53 |
| camel_b | alexander | sphere | 0.00 | 4879 | 0.52 |
| camel_b | goguelin-len | sphere | 0.00 | 5176 | 1.12 |
| cow | alexander | sphere | 0.00 | 5083 | 1.27 |
| cow | goguelin-len | sphere | 0.00 | 4889 | 1.01 |
| horse_quad | alexander | sphere | 0.00 | 4922 | 1.20 |
| horse_quad | goguelin-len | sphere | 0.00 | 4992 | 0.74 |
| decimated-knight | alexander | sphere | 0.00 | 5524 | 0.23 |
| decimated-knight | goguelin-len | sphere | 0.00 | 4868 | 0.20 |
| decimated-max | alexander | sphere | 0.00 | 4860 | 2.53 |
| decimated-max | goguelin-len | sphere | 0.00 | 5012 | 1.69 |
| heart | alexander | sphere | 0.00 | 4893 | 10.82 |
| heart | goguelin-len | sphere | 0.00 | 5338 | 6.41 |
| skull | alexander | sphere | 0.00 | 4980 | 1.84 |
| skull | goguelin-len | sphere | 0.00 | 4840 | 1.01 |

## 3. Print estimates per pose

| mesh | pose | height (mm) | overhang area (mm²) | proxy support vol. (mm³) | proxy filament (m) | proxy time (min) | PrusaSlicer filament (m) | PrusaSlicer support filament (m) | PrusaSlicer time (min) |
|---|---|---|---|---|---|---|---|---|---|
| arm | initial | 13.8 | 281 | 1257 | 0.66 | 8 | 1.17 | 0.57 | 25 |
| arm | castro-eq | 13.2 | 331 | 241 | 0.59 | 8 | 0.84 | 0.22 | 20 |
| arm | ezair | 13.2 | 331 | 241 | 0.59 | 8 | 0.84 | 0.22 | 20 |
| arm | alexander | 55.8 | 35 | 22 | 0.58 | 13 | 0.96 | 0.22 | 31 |
| arm | goguelin-len | 52.6 | 36 | 21 | 0.58 | 12 | 0.83 | 0.09 | 27 |
| arm | tweaker3-vol | 18.4 | 264 | 514 | 0.61 | 8 | 1.00 | 0.37 | 23 |
| arm | tweaker3-sur | 18.4 | 264 | 514 | 0.61 | 8 | 1.00 | 0.37 | 23 |
| bunny | initial | 46.5 | 1629 | 22711 | 6.85 | 74 | 10.24 | 4.33 | 171 |
| bunny | castro-eq | 44.2 | 1264 | 7148 | 5.88 | 64 | 8.12 | 2.15 | 147 |
| bunny | ezair | 59.7 | 1430 | 6720 | 5.85 | 65 | 8.16 | 2.35 | 141 |
| bunny | alexander | 64.0 | 813 | 10591 | 6.09 | 68 | 9.82 | 3.97 | 166 |
| bunny | goguelin-len | 48.2 | 1077 | 6085 | 5.81 | 64 | 8.32 | 2.36 | 150 |
| bunny | tweaker3-vol | 60.3 | 1193 | 18286 | 6.57 | 73 | 10.23 | 4.44 | 167 |
| bunny | tweaker3-sur | 47.8 | 1558 | 16040 | 6.43 | 70 | 9.79 | 3.84 | 168 |
| camel_b | initial | 60.0 | 494 | 5386 | 2.38 | 31 | 4.51 | 2.37 | 87 |
| camel_b | castro-eq | 18.5 | 1147 | 3442 | 2.26 | 25 | 3.97 | 1.92 | 80 |
| camel_b | ezair | 18.5 | 1147 | 3448 | 2.26 | 25 | 3.94 | 1.89 | 80 |
| camel_b | alexander | 60.3 | 318 | 3510 | 2.26 | 30 | 4.26 | 2.03 | 95 |
| camel_b | goguelin-len | 18.5 | 1174 | 3649 | 2.27 | 25 | 3.95 | 1.90 | 81 |
| camel_b | tweaker3-vol | 58.5 | 437 | 9104 | 2.61 | 33 | 4.99 | 2.76 | 97 |
| camel_b | tweaker3-sur | 58.5 | 437 | 9104 | 2.61 | 33 | 4.99 | 2.76 | 97 |
| cow | initial | 19.5 | 977 | 3835 | 2.02 | 22 | 3.29 | 1.49 | 64 |
| cow | castro-eq | 34.9 | 409 | 1128 | 1.85 | 23 | 2.59 | 0.82 | 55 |
| cow | ezair | 34.9 | 409 | 1128 | 1.85 | 23 | 2.59 | 0.82 | 55 |
| cow | alexander | 46.6 | 198 | 2635 | 1.94 | 25 | 3.29 | 1.47 | 65 |
| cow | goguelin-len | 35.0 | 406 | 1115 | 1.85 | 23 | 2.57 | 0.80 | 54 |
| cow | tweaker3-vol | 36.7 | 471 | 5250 | 2.10 | 25 | 3.42 | 1.63 | 63 |
| cow | tweaker3-sur | 36.7 | 423 | 2057 | 1.90 | 23 | 2.70 | 0.91 | 57 |
| horse_quad | initial | 27.5 | 892 | 3973 | 2.02 | 23 | 3.54 | 1.62 | 70 |
| horse_quad | castro-eq | 44.7 | 463 | 1382 | 1.86 | 24 | 2.44 | 0.57 | 56 |
| horse_quad | ezair | 44.9 | 468 | 1476 | 1.86 | 24 | 2.44 | 0.58 | 56 |
| horse_quad | alexander | 73.3 | 226 | 4783 | 2.07 | 30 | 4.49 | 2.50 | 85 |
| horse_quad | goguelin-len | 44.7 | 456 | 1347 | 1.86 | 24 | 2.45 | 0.59 | 56 |
| horse_quad | tweaker3-vol | 27.5 | 892 | 3973 | 2.02 | 23 | 3.54 | 1.62 | 70 |
| horse_quad | tweaker3-sur | 50.5 | 397 | 3703 | 2.00 | 26 | 3.40 | 1.56 | 70 |
| decimated-knight | initial | 18.4 | 824 | 3435 | 1.95 | 22 | 3.31 | 1.42 | 70 |
| decimated-knight | castro-eq | 19.0 | 827 | 2464 | 1.89 | 21 | 3.09 | 1.21 | 67 |
| decimated-knight | ezair | 19.0 | 827 | 2465 | 1.89 | 21 | 3.09 | 1.21 | 67 |
| decimated-knight | alexander | 59.6 | 274 | 2112 | 1.87 | 26 | 3.65 | 1.43 | 91 |
| decimated-knight | goguelin-len | 18.9 | 822 | 2454 | 1.89 | 21 | 3.10 | 1.22 | 67 |
| decimated-knight | tweaker3-vol | 60.0 | 300 | 2983 | 1.93 | 27 | 4.51 | 2.29 | 102 |
| decimated-knight | tweaker3-sur | 60.0 | 300 | 2983 | 1.93 | 27 | 4.51 | 2.29 | 102 |
| decimated-max | initial | 43.1 | 854 | 8176 | 4.32 | 48 | 6.22 | 2.14 | 101 |
| decimated-max | castro-eq | 59.7 | 542 | 1203 | 3.88 | 46 | 4.65 | 0.71 | 75 |
| decimated-max | ezair | 33.2 | 1178 | 2494 | 3.97 | 43 | 5.10 | 1.03 | 88 |
| decimated-max | alexander | 59.1 | 385 | 3999 | 4.06 | 48 | 5.66 | 1.71 | 89 |
| decimated-max | goguelin-len | 59.5 | 523 | 1141 | 3.88 | 46 | 4.67 | 0.73 | 75 |
| decimated-max | tweaker3-vol | 57.6 | 588 | 1552 | 3.91 | 46 | 5.13 | 1.11 | 84 |
| decimated-max | tweaker3-sur | 57.6 | 588 | 1552 | 3.91 | 46 | 5.13 | 1.11 | 84 |
| heart | initial | 42.4 | 2797 | 35185 | 4.30 | 48 | 7.77 | 5.66 | 139 |
| heart | castro-eq | 34.8 | 2516 | 23379 | 3.57 | 40 | 6.46 | 4.35 | 122 |
| heart | ezair | 34.8 | 2516 | 23372 | 3.57 | 40 | 6.46 | 4.35 | 122 |
| heart | alexander | 60.2 | 1378 | 19308 | 3.31 | 40 | 6.66 | 4.61 | 126 |
| heart | goguelin-len | 39.4 | 2295 | 26591 | 3.77 | 42 | 7.01 | 4.92 | 130 |
| heart | tweaker3-vol | 49.6 | 2339 | 28196 | 3.87 | 44 | 7.58 | 5.50 | 138 |
| heart | tweaker3-sur | 49.6 | 2339 | 28196 | 3.87 | 44 | 7.58 | 5.50 | 138 |
| skull | initial | 53.7 | 1206 | 8337 | 6.90 | 75 | 11.02 | 3.89 | 197 |
| skull | castro-eq | 50.3 | 1303 | 6009 | 6.76 | 73 | 9.71 | 2.71 | 174 |
| skull | ezair | 60.1 | 1349 | 4732 | 6.68 | 74 | 10.78 | 3.35 | 199 |
| skull | alexander | 67.7 | 900 | 3426 | 6.59 | 74 | 8.49 | 1.92 | 157 |
| skull | goguelin-len | 50.5 | 1229 | 6028 | 6.76 | 73 | 9.14 | 2.59 | 163 |
| skull | tweaker3-vol | 56.2 | 1500 | 7758 | 6.86 | 75 | 10.26 | 3.34 | 182 |
| skull | tweaker3-sur | 47.7 | 1943 | 13685 | 7.24 | 78 | 12.52 | 4.80 | 223 |

## 3b. Summary per method (PrusaSlicer estimates)

Median over meshes of the reduction relative to the initial pose; in parentheses, the number of meshes where the method is the best of all poses (ties count for each tied method).

| method | support filament | print time | total filament |
|---|---|---|---|
| alexander | -14.4% (1/9) | +2.0% (1/9) | -5.5% (1/9) |
| castro-eq | -45.2% (4/9) | -14.0% (2/9) | -20.7% (3/9) |
| ezair | -45.2% (2/9) | -13.3% (4/9) | -18.0% (3/9) |
| goguelin-len | -45.5% (2/9) | -12.4% (2/9) | -18.7% (2/9) |
| tweaker3-sur | -3.7% (0/9) | -0.6% (0/9) | -4.1% (0/9) |
| tweaker3-vol | -0.0% (0/9) | -1.5% (0/9) | -0.1% (0/9) |

## 4. Does the proxy rank poses like the slicer?

Spearman rank correlation over all (mesh, pose) pairs, pooled; and per mesh the fraction of pose pairs ordered the same way (support).

- support: Spearman ρ = 0.960 (n = 63)
- total filament: Spearman ρ = 0.965 (n = 63)
- time: Spearman ρ = 0.919 (n = 63)
- within-mesh pairwise agreement on support: 155/189
