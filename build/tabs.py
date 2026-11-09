"""Build give.json, drives.json, meals.json and hmeals.json from the sheet's
Give Back, Holiday Drives and Meal Kitchens tabs.

Usage: python3 tabs.py <tabs_dump.json>
The dump is {"give": {"values": [...]}, "drives": {...}, "meals": {...}}.
Any tab missing from the dump keeps its current JSON file.
"""
import json, re, sys
from datetime import date

src = open('build_data.py').read()
exec(src[src.index('REGION='):src.index('\n', src.index('A2R='))])   # REGION, A2R

MON = {m: i + 1 for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split())}
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
CONFIRMED = re.compile(r'^(Confirmed|Listed|Ongoing|Year-round)', re.I)
SEASON_END = "2027-01-10"


def cell(r, i):
    return (r[i] if i < len(r) else "").strip()


def pad(rows, n):
    return [r + [""] * (n - len(r)) for r in rows]


def area_region(a):
    a = re.split(r' / |\(|,', a)[0].strip()
    return a, A2R.get(a, "")


def parse_date(s):
    m = re.search(r'([A-Za-z]{3})[a-z]*\.?\s+(\d{1,2}),?\s+(20\d\d)', s or "")
    if not m or m.group(1).lower() not in MON:
        return ""
    return date(int(m.group(3)), MON[m.group(1).lower()], int(m.group(2))).isoformat()


def first_minutes(t):
    """Minutes after midnight of the first clock time in a text like 'Lunch 11:30am-12:30pm'."""
    s = t.lower().replace("noon", "12pm")
    if "evening" in s and not re.search(r'\d', s):
        return 1140
    m = re.search(r'(\d{1,2})(?::(\d\d))?\s*(am|pm)?', s)
    if not m:
        return 0
    h, mi, ap = int(m.group(1)), int(m.group(2) or 0), m.group(3)
    if not ap:
        n = re.search(r'(\d{1,2})(?::\d\d)?\s*(am|pm)', s[m.end():])
        if n:
            ap = n.group(2)
            if ap == "pm" and h != 12 and h > int(n.group(1)) and int(n.group(1)) < 12:
                ap = "am"
    if ap == "pm" and h < 12:
        h += 12
    if ap == "am" and h == 12:
        h = 0
    if not ap and 1 <= h <= 7:
        h += 12
    return h * 60 + mi


def split_details(d):
    """'Anyone. Hot lunch... Phone 206-...' -> (who, rest, phone)."""
    phone = ""
    m = re.search(r'\s*Phone:?\s*([\d\-\(\) ]{10,})\.?', d)
    if m:
        phone = m.group(1).strip().rstrip(".")
        d = (d[:m.start()] + d[m.end():]).strip()
    parts = re.split(r'(?<=\.)\s+', d, maxsplit=1)
    first = parts[0].rstrip(".")
    if re.match(r'^(Anyone|Adults|Ages|Women|Men|Youth|LGBTQ|Homeless|American Indian|Seniors|Residents|Eastside|Families|Kids)', first):
        return first, (parts[1] if len(parts) > 1 else ""), phone
    return "Anyone", d, phone


# ---------- Give Back ----------
def build_give(rows, extra_drives):
    out = []
    for i, r in enumerate(pad(rows[1:], 15)):
        n = cell(r, 0)
        if not n:
            continue
        kinds = [k.strip() for k in cell(r, 1).split(",") if k.strip() and k.strip() != "Event"]
        a, reg = area_region(cell(r, 2))
        hours = [cell(r, 4 + d) for d in range(7)]
        link = cell(r, 12)
        nth = None
        for d, h in enumerate(hours):
            m = re.search(r'\s*\((1st|2nd|3rd|4th)( and (1st|2nd|3rd|4th))? \w+\)', h)
            if m:
                nth = [int(x[0]) for x in re.findall(r'(1st|2nd|3rd|4th)', m.group(0))]
                hours[d] = h[:m.start()].strip()
        if not any(hours):
            # no drop-off hours: volunteer-from-anywhere items become "anytime" listings
            if link and kinds:
                virtual = re.search(r'virtual|from home', cell(r, 2), re.I)
                extra_drives.append({"id": 1000 + i, "n": n, "k": kinds, "a": re.sub(r'\s*\(.*', '', cell(r, 2)),
                                     "loc": cell(r, 3), "s": "", "e": "",
                                     "sch": "Any time, from home" if virtual else "Check their site for times",
                                     "v": cell(r, 11), "u": link})
            continue
        if not link:
            continue
        out.append({"id": i, "n": n, "k": kinds, "a": a, "r": reg, "loc": cell(r, 3), "h": hours,
                    "v": cell(r, 11), "u": link, "nth": nth})
    return out


# ---------- Holiday Drives ----------
def build_drives(rows):
    out = []
    for i, r in enumerate(pad(rows[1:], 13)):
        n = cell(r, 0)
        if not n or not CONFIRMED.match(cell(r, 10)):
            continue
        kinds = [k.strip() for k in cell(r, 1).split(",") if k.strip() and k.strip() != "Event"]
        if not kinds:
            continue
        s, e = parse_date(cell(r, 5)), parse_date(cell(r, 6))
        if cell(r, 6) and not e:            # "Through the season" and the like
            e = SEASON_END
        if s and not e:
            # one day if it is an event, a one-day holiday, or the schedule names that date; otherwise it runs all season
            mo, dy = int(s[5:7]), int(s[8:10])
            day_txt = re.compile(r'\b' + list(MON)[mo - 1] + r'[a-z]*\.?\s+' + str(dy) + r'\b', re.I)
            one_day = ("Event" in cell(r, 1) or re.match(r'(Thanksgiving|Christmas Eve|Christmas Day|New Year)', cell(r, 2))
                       or day_txt.search(cell(r, 7)) or re.match(r'(Thanksgiving|Christmas) Day', cell(r, 7)))
            e = s if one_day else SEASON_END
        if e and not s:
            s = ""
        out.append({"id": i, "n": n, "k": kinds, "a": cell(r, 3), "loc": cell(r, 4), "s": s, "e": e if s else "",
                    "sch": cell(r, 7), "v": cell(r, 8), "u": cell(r, 9)})
    return out


# ---------- Meal Kitchens ----------
def week_hours(text):
    h = [""] * 7
    for part in text.split(";"):
        part = part.strip()
        m = re.match(r'(Daily|(?:Sun|Mon|Tue|Wed|Thu|Fri|Sat)(?:\s*-\s*(?:Sun|Mon|Tue|Wed|Thu|Fri|Sat))?)\s+(.*)', part)
        if not m:
            continue
        span, what = m.group(1), m.group(2)
        what = re.sub(r'\s*\((last|1st|first)[^)]*\)', '', what).strip()
        if span == "Daily":
            idx = range(7)
        elif "-" in span:
            a, b = [DAYS.index(x.strip().lower()[:3]) for x in span.split("-")]
            idx = range(a, b + 1) if a <= b else list(range(a, 7)) + list(range(0, b + 1))
        else:
            idx = [DAYS.index(span.lower()[:3])]
        for d in idx:
            h[d] = what[0].upper() + what[1:] if what else what
    return h


def build_meals(rows):
    rows = pad(rows, 8)
    weekly, holiday = [], []
    mode = "weekly"
    for r in rows[1:]:
        n = cell(r, 0)
        if not any(r):
            if mode == "holiday":
                mode = "done"
            continue
        if cell(r, 3) == "Date and time":
            mode = "holiday"
            continue
        if n and not cell(r, 2) and not cell(r, 3):     # a block title row
            if mode == "weekly" and weekly:
                mode = "between"
            continue
        if mode == "weekly":
            who, v, phone = split_details(cell(r, 4))
            hours = week_hours(cell(r, 3))
            if not any(hours) or not cell(r, 7):
                continue
            a, reg = area_region(cell(r, 1))
            m = {"n": n, "a": a, "r": reg, "loc": cell(r, 2), "h": hours, "t": [first_minutes(x) if x else 0 for x in hours],
                 "who": who, "v": v, "u": cell(r, 7), "src": cell(r, 5), "id": len(weekly)}
            if phone:
                m["phone"] = phone
            if re.search(r'last \w+ of the month', cell(r, 3), re.I):
                m["last"] = True
            if re.search(r'no \w+ the last week of december', cell(r, 4), re.I):
                y = date.today().year
                m["skip"] = [date(y, 12, d).isoformat() for d in range(25, 32) if hours[date(y, 12, d).weekday()]]
            if re.search(r'\$\d', cell(r, 4)):
                m["cost"] = re.search(r'\$\d+(\.\d\d)?( per meal)?', cell(r, 4)).group(0)
            weekly.append(m)
        elif mode == "holiday":
            d = parse_date(cell(r, 3))
            if not d:
                continue
            tm = cell(r, 3).split(str(int(d[:4])), 1)[-1].lstrip(", ").strip()
            who, v, phone = split_details(cell(r, 4))
            a, reg = area_region(cell(r, 1))
            holiday.append({"n": n, "a": a, "r": reg, "loc": cell(r, 2), "d": d, "tm": tm or "time not posted",
                            "who": who, "v": v, "u": cell(r, 7), "phone": phone})
    return weekly, holiday


if __name__ == "__main__":
    dump = json.load(open(sys.argv[1]))
    extra = []
    if "give" in dump:
        g = build_give(dump["give"]["values"], extra)
        json.dump(g, open("give.json", "w"), ensure_ascii=False)
        print("give", len(g))
    if "drives" in dump:
        dr = build_drives(dump["drives"]["values"]) + extra
        json.dump(dr, open("drives.json", "w"), ensure_ascii=False)
        print("drives", len(dr))
    if "meals" in dump:
        w, h = build_meals(dump["meals"]["values"])
        json.dump(w, open("meals.json", "w"), ensure_ascii=False)
        json.dump(h, open("hmeals.json", "w"), ensure_ascii=False)
        print("meals", len(w), "holiday meals", len(h))
