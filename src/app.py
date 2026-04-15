#!/usr/bin/env python3
import os, time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Try to load Waveshare EPD driver
try:
    from waveshare_epd import epd4in2_V2
    EPD_AVAILABLE = True
except Exception as e:
    print("[EPD_IMPORT_FAIL]", e)
    EPD_AVAILABLE = False

# Fetcher hits your HTTPS API with API key + HMAC
import fetcher as db

# --- Config via env ---
REFRESH_SECONDS = int(os.getenv("APP_REFRESH_SECONDS", "7200"))
FONT_PATH = os.getenv("APP_FONT_PATH", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
FORCE_REDRAW_ON_START = os.getenv("APP_FORCE_REDRAW_ON_START", "0") == "1"

# --- Fonts ---
def mk_fonts():
    try:
        return (
            ImageFont.truetype(FONT_PATH, 18),  # small
            ImageFont.truetype(FONT_PATH, 22),  # body
            ImageFont.truetype(FONT_PATH, 30),  # title
        )
    except Exception as e:
        print("[FONT_WARN] using default font:", e)
        f = ImageFont.load_default()
        return f, f, f

# --- Drawing helpers ---
def text_w_h(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return (bbox[2] - bbox[0], bbox[3] - bbox[1])

def draw_center(draw, text, y, font, width):
    w, h = text_w_h(draw, text, font)
    x = (width - w) // 2
    draw.text((x, y), text, font=font, fill=0)
    return h

def draw_right(draw, text, y, font, right_edge):
    w, h = text_w_h(draw, text, font)
    x = right_edge - w
    draw.text((x, y), text, font=font, fill=0)
    return h

def compact_date(iso_date: str) -> str:
    # "2025-09-07" -> "Sep 07"
    try:
        dt = datetime.strptime(iso_date, "%Y-%m-%d")
        return dt.strftime("%b %d")
    except Exception:
        return str(iso_date or "")

# --- Format lines for display ---
def format_summary_lines(person_totals, total_due):
    if person_totals is None:
        return ["Error:", "Could not fetch", "utility data."]
    total_due = float(total_due or 0)
    if total_due <= 0:
        return ["All bills are paid!"]
    lines = [f"Total Due: ${total_due:,.2f}"]
    for row in person_totals:
        name = row.get("personName", "?")
        amt = float(row.get("totalOwedByPerson") or 0)
        lines.append(f"{name}: ${amt:,.2f}")
    return lines

def format_due_soon_lines(detail_rows, max_items=4):
    """
    Build a small 'Due soon' section from detailed rows.
    We show unique bills in due-date order (already ordered by API).
    """
    if not detail_rows:
        return []

    # collapse by billID to avoid 3 duplicates (one per person)
    seen = set()
    items = []
    for r in detail_rows:
        bid = r.get("billID")
        if bid in seen:
            continue
        seen.add(bid)
        item = r.get("item", "?")
        due = compact_date(r.get("dueDate"))
        total = float(r.get("billTotal") or 0.0)
        items.append(f"{item} • {due} • ${total:,.2f}")
        if len(items) >= max_items:
            break
    return (["Due soon:"] + items) if items else []

# --- Render the full frame ---
def render_image(width, height, title_lines, due_lines):
    image = Image.new("1", (width, height), 255)
    draw = ImageDraw.Draw(image)
    f18, f22, f30 = mk_fonts()

    # Top row: left = full date, right = updated HH:MM
    now = datetime.now()
    date_str = now.strftime("%B %d, %Y")
    upd_str = "Updated " + now.strftime("%H:%M")
    draw.text((6, 6), date_str, font=f18, fill=0)
    draw_right(draw, upd_str, 6, f18, right_edge=width - 6)

    y = 46

    # Title+per-person block (centered)
    if not title_lines:
        title_lines = ["Error", "No data"]

    # First line as title
    y += draw_center(draw, title_lines[0], y, f30, width) + 12

    # Optional separator + remaining summary lines
    if len(title_lines) > 1:
        y += draw_center(draw, "—" * 18, y, f18, width) + 6
        for line in title_lines[1:]:
            y += draw_center(draw, line, y, f22, width) + 8

    # Space before the due-soon box
    y += 8

    # Due soon section (centered lines)
    if due_lines:
        y += draw_center(draw, "—" * 18, y, f18, width) + 4
        for line in due_lines:
            y += draw_center(draw, line, y, f18 if line.endswith(":") else f22, width) + 6

    return image

# --- Main loop ---
def main():
    epd = None
    width, height = 400, 300
    if EPD_AVAILABLE:
        try:
            epd = epd4in2_V2.EPD()
            width, height = epd.width, epd.height
            print(f"[INFO] EPD size: {width}x{height}")
        except Exception as e:
            print(f"[WARN] EPD init failed (deferred), sim mode until draw: {e}")
            epd = None

    last_payload = None
    first_loop = True

    while True:
        try:
            print("[INFO] Fetching unpaid bills (HTTPS)…")
            person_totals, total_due = db.get_unpaid_bills_summary()
            detail_rows = db.get_detailed_unpaid_bills()

            summary_lines = format_summary_lines(person_totals, total_due)
            due_lines = format_due_soon_lines(detail_rows, max_items=4)

            # payload used to decide if we need to redraw (ignore timestamp)
            payload = (tuple(summary_lines), tuple(due_lines))
            force = first_loop and FORCE_REDRAW_ON_START

            import hashlib, json
            raw = {"summary": summary_lines, "due": due_lines}
            digest = hashlib.sha256(json.dumps(raw, sort_keys=True).encode()).hexdigest()[:10]
            print(f"[INFO] Payload checksum: {digest}")

            if force or payload != last_payload:
                img = render_image(width, height, summary_lines, due_lines)

                # Try (re)create epd here so we wake each draw
                if EPD_AVAILABLE and epd is None:
                    try:
                        epd = epd4in2_V2.EPD()
                        width, height = epd.width, epd.height
                    except Exception as e:
                        print("[WARN] Late EPD create failed; sim draw:", e)

                if epd:
                    try:
                        epd.init()
                        epd.Clear()
                        epd.display(epd.getbuffer(img))
                        img.save("/home/aaronperkel/Room-Display-Sign/last_draw.png")
                        epd.sleep()
                        print("[INFO] Display updated.", "(forced)" if force else "")
                    except Exception as e:
                        print(f"[ERROR] EPD update failed: {e}. Writing display.png for inspection.")
                        img.save("display.png")
                else:
                    img.save("display.png")
                    print("[INFO] Wrote display.png (simulation)", "(forced)" if force else "")

                last_payload = payload
            else:
                print("[INFO] No change; skipping redraw.")

        except Exception as e:
            print(f"[ERROR] loop: {e}")

        first_loop = False
        time.sleep(REFRESH_SECONDS)

if __name__ == "__main__":
    main()
