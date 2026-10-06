// MaxGuard dashboard script (Ahmad, AHM-02). Everything else is htmx.
// 1) Live refresh: the server sends "alerts-changed" on /api/stream; the alert
//    table reloads itself on "refresh" (it also polls every 30 s as a fallback).
// 2) Upload: /api/analyses answers JSON; show it as plain text (textContent,
//    never innerHTML, because an error message can contain a file name).
"use strict";

document.addEventListener("DOMContentLoaded", function () {
  if (document.getElementById("alerts") && window.EventSource) {
    const stream = new EventSource("/api/stream");
    stream.addEventListener("alerts-changed", function () {
      htmx.trigger("#alerts", "refresh");
    });
  }

  const form = document.getElementById("upload-form");
  if (form) {
    form.addEventListener("htmx:afterRequest", function (event) {
      document.getElementById("upload-result").textContent = uploadMessage(event.detail.xhr);
    });
  }
});

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
