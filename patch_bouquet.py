import io, re

path = r"C:\Users\Administrator\Documents\GitHub\for_u\letter.py"
with io.open(path, "r", encoding="utf-8") as f:
    src = f.read()

start_marker = "        # Front blooms paint OVER back blooms: generate back-to-front"
end_marker = "            pts_list.extend(candidates)"

start = src.index(start_marker)
end = src.index(end_marker) + len(end_marker)

new_block = '''        # ------------------------------------------------------------------
        # 2. LILIES painted onto a shared cell grid with true occlusion:
        # back-to-front; each front bloom OVERWRITES cells of back blooms
        # so every bloom is a clean solid disc of its own palette.
        # ------------------------------------------------------------------
        rem_pts = self.total_points - len(pts_list)
        CW, CH = 7.0, 10.0                       # cell size (smooth, dense)
        cellmap = {}                             # cell key -> point dict

        area_w = sum(s["rad"] ** 2 for s in lily_specs)
        budgets = [rem_pts * s["rad"] ** 2 / area_w for s in lily_specs]
        paint_order = sorted(zip(lily_specs, budgets),
                             key=lambda t: t[0]["cy"])

        for l_spec, pts_per_lily in paint_order:
            if pts_per_lily <= 0:
                continue
            lcx = l_spec["cx"]
            lcy = l_spec["cy"]
            lrad = l_spec["rad"]
            lrot = l_spec["rot"]
            c_main = l_spec["col_main"]
            c_dark = l_spec["col_dark"]
            c_hi = l_spec["col_hi"]
            c_core = l_spec.get("col_core", None)
            bloom_order = l_spec["bloom_order"]

            # every cell whose centre lies inside the 6-lobe silhouette gets
            # painted with this bloom's palette (solid smooth disc look)
            gx0 = int((lcx - lrad * 1.15) / CW)
            gx1 = int((lcx + lrad * 1.15) / CW) + 1
            gy0 = int((lcy - lrad * 1.15) / CH)
            gy1 = int((lcy + lrad * 1.15) / CH) + 1
            cells = []
            for gy in range(gy0, gy1):
                py = gy * CH + CH * 0.5
                for gx in range(gx0, gx1):
                    px = gx * CW + CW * 0.5
                    dxc, dyc = px - lcx, py - lcy
                    r = math.hypot(dxc, dyc)
                    if r > lrad:
                        continue
                    ang = math.atan2(dyc, dxc) - lrot
                    k = (ang / (math.pi / 3.0)) % 1.0
                    lobe = 1.0 - abs(k - 0.5) * 2.0          # 0..1 triangle
                    r_max = lrad * (0.60 + 0.40 * lobe ** 0.5)
                    if r <= r_max:
                        cells.append((gx, gy, px, py, r / lrad))

            # smooth budget: if too many cells, drop evenly (every Nth)
            if len(cells) > pts_per_lily:
                keep = int(math.ceil(len(cells) / float(pts_per_lily)))
                cells = [c for i, c in enumerate(cells) if i % keep == 0]

            for (gx, gy, px, py, un) in cells:
                # radial shading: dark core -> main -> hi -> dark rim
                if un < 0.18:
                    col = c_core if c_core else c_dark
                    ch = "@"
                elif un < 0.40:
                    col = tuple(int(v * 0.80) for v in c_main)
                    ch = "%"
                elif un < 0.62:
                    col = c_main
                    ch = "a"
                elif un < 0.80:
                    col = c_hi
                    ch = "o"
                elif un < 0.93:
                    col = c_hi
                    ch = "-"
                else:
                    col = c_dark
                    ch = "~"
                cellmap[(gx, gy)] = {
                    "base_x": px,
                    "base_y": py,
                    "part": "lily",
                    "lcx": lcx, "lcy": lcy, "u": un,
                    "grow_delay": bloom_order,
                    "char": ch, "color": col
                }

        pts_list.extend(cellmap.values())'''

src = src[:start] + new_block + src[end:]
with io.open(path, "w", encoding="utf-8") as f:
    f.write(src)
print("patched OK")
