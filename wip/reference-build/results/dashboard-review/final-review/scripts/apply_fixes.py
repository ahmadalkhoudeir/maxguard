"""Apply all proposed fixes to a build folder (final tree or the AHM-03 stage).
Usage: python apply_fixes.py <root>"""
import sys
from pathlib import Path

root = Path(sys.argv[1])
done = []

def edit(rel, old, new, optional=False):
    p = root / rel
    s = p.read_text()
    if s.count(old) != 1:
        if optional:
            return
        raise SystemExit(f"{rel}: expected one match for {old[:60]!r}")
    p.write_text(s.replace(old, new))
    done.append(rel)

# A + B + C + D: app.js
edit("maxguard/web/static/app.js",
'''      form.querySelector("button").focus();  // it was disabled during the upload, which drops focus
''',
'''      // The button was disabled during the upload, which drops focus to the page.
      // Give it back, unless the person has moved on to something else meanwhile.
      if (!document.activeElement || document.activeElement === document.body) {
        form.querySelector("button").focus();
      }
''')
edit("maxguard/web/static/app.js",
'''  const modeSwitch = document.querySelector(".mode-switch");
  if (modeSwitch) {
    modeSwitch.addEventListener("submit", function () {
      modeSwitch.elements.next.value = location.pathname + location.search;
    });
  }

  document.body.addEventListener("htmx:sendError", statusNotSaved);''',
'''  // On the document, not on the form: Back and Forward between filter addresses
  // replace the page body (htmx history), and with it the form and its listeners.
  document.addEventListener("submit", function (event) {
    if (event.target.classList.contains("mode-switch")) {
      event.target.elements.next.value = location.pathname + location.search;
    }
  });

  // A filter answer goes into the table on the page now: a refresh that answered
  // first has already replaced the table the filter request was aimed at.
  const filters = document.getElementById("filters");
  if (filters) {
    filters.addEventListener("htmx:beforeOnLoad", function (event) {
      event.detail.target = document.getElementById("alerts");
    });
  }

  document.body.addEventListener("htmx:sendError", statusNotSaved);''')
edit("maxguard/web/static/app.js",
'''    : "Not saved: the MaxGuard server could not be reached.";''',
'''    : "No answer from the MaxGuard server: the change may not be saved. Reload the page to check.";''')
# E + F: _status.html
edit("maxguard/web/templates/_status.html",
'''<form id="status-form" class="card status-form"
      hx-patch=''', '''<form id="status-form" class="card status-form" autocomplete="off"
      hx-patch=''')
edit("maxguard/web/templates/_status.html",
'''<input id="actor" name="actor" type="text" maxlength="100" required autocomplete="name">''',
'''<input id="actor" name="actor" type="text" maxlength="100" required autocomplete="name"
         pattern=".*\\S.*" title="Your name, not only spaces">''')
# G: app.css
edit("maxguard/web/static/app.css",
".status-form, #upload-form { display: grid; grid-template-columns: minmax(0, 1fr); gap: 8px; max-width: 420px; }",
".status-form, #upload-form { display: grid; grid-template-columns: minmax(0, 1fr); gap: 8px; max-width: 420px; }\n"
".status-form, .stack td { overflow-wrap: anywhere; }  /* a long name or address never pushes the page sideways */")
edit("maxguard/web/static/app.css", "  font-size: 0.85rem;\n  white-space: nowrap;\n}", "  font-size: 0.85rem;\n}")
edit("maxguard/web/static/app.css", "  .stack td .sev { justify-self: start; white-space: normal; }",
     "  .stack td .sev { justify-self: start; }")
# I: routes.py, the assignee comparison as the browser sends a text field
edit("maxguard/web/routes.py",
'''    assignee = str(form.get("assignee", "")).strip()[:MAX_NAME_LENGTH]''',
'''    assignee = text_field(form.get("assignee", ""))[:MAX_NAME_LENGTH]''')
edit("maxguard/web/routes.py",
'''    if "shown_assignee" in form and assignee == str(form["shown_assignee"]).strip():''',
'''    if "shown_assignee" in form and assignee == text_field(form["shown_assignee"]):''')
edit("maxguard/web/routes.py",
'''def safe_next(path: str) -> str:''',
'''def text_field(value) -> str:
    """A form value as a text box holds it: browsers drop line breaks from text inputs
    (but not from hidden ones), so an assignee stored with one compares equal."""
    return str(value).replace("\\r", "").replace("\\n", "").strip()


def safe_next(path: str) -> str:''')
# H: routes.py + alert.html (final tree only: the timeline links arrive in AHM-06)
if "(alert.last_seen + 1) | int" in (root / "maxguard/web/templates/alert.html").read_text():
    edit("maxguard/web/routes.py", '''TEMPLATES.env.filters["utc_time"] = utc_time
''', '''TEMPLATES.env.filters["utc_time"] = utc_time


def timeline_end(ts: float) -> int | None:
    """end= for an alert page's timeline links: one second after last_seen, or None
    when last_seen is not a time the timeline accepts (inf or 1e12 from a hostile log)."""
    try:
        end = int(ts) + 1
    except (TypeError, ValueError, OverflowError):
        return None
    return end if 0 <= end <= LAST_TIME else None


TEMPLATES.env.filters["timeline_end"] = timeline_end
''')
    edit("maxguard/web/templates/alert.html",
'''  <dd class="mono"><a href="/timeline?ip={{ alert.src_ip | urlencode }}&amp;end={{ (alert.last_seen + 1) | int }}">{{ alert.src_ip }}</a>
    → <a href="/timeline?ip={{ alert.dst_ip | urlencode }}&amp;end={{ (alert.last_seen + 1) | int }}">''',
'''  {% set end = alert.last_seen | timeline_end %}
  <dd class="mono"><a href="/timeline?ip={{ alert.src_ip | urlencode }}{% if end is not none %}&amp;end={{ end }}{% endif %}">{{ alert.src_ip }}</a>
    → <a href="/timeline?ip={{ alert.dst_ip | urlencode }}{% if end is not none %}&amp;end={{ end }}{% endif %}">''')
# J: queue.html caption
edit("maxguard/web/templates/queue.html",
'''{% if more %}The {{ alerts | length }} most severe alerts. More alerts match: use the filters to see them.{% else %}''',
'''{% if more %}The {{ alerts | length }} most severe alerts, most recent first. More alerts match and are not shown{% if not (status and severity) %}: choose a status and a severity to see them{% endif %}.{% else %}''')
print("edited:", sorted(set(done)))
