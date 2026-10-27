// MaxGuard dashboard script (Ahmad, AHM-02). Everything else is htmx.
// 1) Live refresh: the server sends "alerts-changed" on /api/stream; the alert
//    table reloads itself on "refresh" (it also polls every 30 s as a fallback).
//    A browser keeps at most 6 connections open to one site, and each open
//    stream holds one, so six queue tabs would leave none for loading pages.
//    Only one tab opens the stream: the tab holding the "maxguard-stream" lock.
//    It passes each change to the other tabs over a BroadcastChannel. When that
//    tab closes, another queue tab gets the lock and opens the stream.
// 2) Upload: /api/analyses answers JSON; show it as plain text (textContent,
//    never innerHTML, because an error message can contain a file name).
// 3) The filters change the address without loading a page (hx-push-url), so the
//    Analyst/Home switch sends the address as it is now.
// 4) The status form is replaced only when the server answers; when it does not,
//    say "Not saved" instead of leaving an earlier "Saved." on the screen.
"use strict";

document.addEventListener("DOMContentLoaded", function () {
  if (document.getElementById("alerts") && window.EventSource) {
    liveRefresh();
  }

  const form = document.getElementById("upload-form");
  if (form) {
    form.addEventListener("htmx:afterRequest", function (event) {
      document.getElementById("upload-result").textContent = uploadMessage(event.detail.xhr);
      // The button was disabled during the upload, which drops focus to the page.
      // Give it back, unless the person has moved on to something else meanwhile.
      if (!document.activeElement || document.activeElement === document.body) {
        form.querySelector("button").focus();
      }
    });
  }

  const modeSwitch = document.querySelector(".mode-switch");
  if (modeSwitch) {
    modeSwitch.addEventListener("submit", function () {
      modeSwitch.elements.next.value = location.pathname + location.search;
    });
  }

  // A filter answer goes into the table on the page now: a refresh that answered
  // first has already replaced the table the filter request was aimed at.
  const filters = document.getElementById("filters");
  if (filters) {
    filters.addEventListener("htmx:beforeOnLoad", function (event) {
      event.detail.target = document.getElementById("alerts");
    });
  }
  // Only a queue page may replace the table. An error page has no #alerts in it, and
  // swapping it in removes the table, its polling and the filters' target for good.
  document.body.addEventListener("htmx:beforeSwap", function (event) {
    const target = event.detail.target;
    if (target && target.id === "alerts" && event.detail.xhr.status !== 200) {
      event.detail.shouldSwap = false;
    }
  });

  document.body.addEventListener("htmx:sendError", statusNotSaved);
  document.body.addEventListener("htmx:responseError", statusNotSaved);
});

function liveRefresh() {
  let again = false;
  const refresh = function () {
    const alerts = document.getElementById("alerts");
    if (!alerts) {
      return;  // no table on this page any more: nothing to refresh
    }
    // htmx ignores a refresh asked for while the table is loading or settling:
    // remember it and ask again once the new table has settled.
    if (alerts.classList.contains("htmx-request") || alerts.classList.contains("htmx-settling")) {
      again = true;
      return;
    }
    htmx.trigger(alerts, "refresh");
  };
  document.addEventListener("htmx:afterSettle", function (event) {
    if (again && event.target.id === "alerts") {
      again = false;
      refresh();
    }
  });
  if (!navigator.locks || !window.BroadcastChannel) {
    // Older browsers, and plain-http addresses other than localhost: one stream per tab.
    new EventSource("/api/stream").addEventListener("alerts-changed", refresh);
    return;
  }
  const channel = new BroadcastChannel("maxguard-alerts");
  channel.addEventListener("message", refresh);
  let waiting = null;  // this tab's place in line for the lock (an AbortController)
  const openStream = function () {
    const stream = new EventSource("/api/stream");
    stream.addEventListener("alerts-changed", function () {
      refresh();
      channel.postMessage("alerts-changed");
    });
    stream.addEventListener("error", function () {
      // An error answer (a proxy's 502) makes EventSource give up for good, and this
      // tab keeps the lock, so it must try again itself.
      if (stream.readyState === EventSource.CLOSED) {
        setTimeout(openStream, 5000);
      }
    });
  };
  const hold = function () {
    waiting = null;
    openStream();
    return new Promise(function () {});  // never settles: keep the lock until the tab closes
  };
  const join = function () {
    navigator.locks.request("maxguard-stream", { ifAvailable: true }, function (lock) {
      if (lock) {
        return hold();
      }
      // Another tab has the stream, and its first event (sent on connect) went to that
      // tab only. Catch up once: this page may be an old copy shown by the Back button.
      refresh();
      waiting = new AbortController();
      navigator.locks.request("maxguard-stream", { signal: waiting.signal }, hold)
        .catch(function () {});  // aborted on pagehide, below
      return null;
    });
  };
  join();
  // A page in the back/forward cache cannot run. If it stayed in line it could get
  // the lock there, and then no tab would open the stream.
  window.addEventListener("pagehide", function (event) {
    if (event.persisted && waiting) {
      waiting.abort();
    }
  });
  window.addEventListener("pageshow", function (event) {
    if (event.persisted && waiting) {
      join();
    }
  });
}

function statusNotSaved(event) {
  const form = event.detail.elt;
  if (!form || form.id !== "status-form") {
    return;
  }
  let message = form.querySelector(".message");
  if (!message) {
    message = document.createElement("p");
    message.className = "message";
    message.setAttribute("role", "status");
    form.appendChild(message);
  }
  const xhr = event.detail.xhr;
  message.textContent = xhr && xhr.status
    ? "Not saved: the MaxGuard server answered with error " + xhr.status + "."
    : "No answer from the MaxGuard server: the change may not be saved. Reload the page to check.";
}

function uploadMessage(xhr) {
  let body = {};
  try {
    body = JSON.parse(xhr.responseText);
  } catch (error) {
    body = {};
  }
  if (xhr.status === 200) {
    const n = body.findings;
    return "Done: " + n + " finding" + (n === 1 ? "" : "s") + ". They are in the alert queue.";
  }
  if (xhr.status === 0) {
    return "Upload failed: the MaxGuard server could not be reached.";
  }
  const detail = typeof body.detail === "string" ? body.detail : "error " + xhr.status;
  return "Upload failed: " + detail;
}
