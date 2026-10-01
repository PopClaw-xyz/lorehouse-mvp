/* PopClaw Ranger Map — vanilla JS.
 *
 * Reads the local read-only API, renders one comic marker per ranger on an
 * equirectangular world map, and refreshes conditionally every 5 seconds
 * while the page is visible. All user-supplied text goes through
 * textContent — never innerHTML. No external requests of any kind.
 */
(function () {
  "use strict";

  var MAP_URL = "/ranger-map/v1/map";
  var HISTORY_URL = "/ranger-map/v1/footprints";
  var REFRESH_MS = 5000;

  var world = document.getElementById("world");
  var canvas = document.getElementById("map-canvas");
  var markersEl = document.getElementById("markers");
  var anchorsEl = document.getElementById("anchors");
  var leadersEl = document.getElementById("leaders");
  var loadState = document.getElementById("load-state");
  var emptyState = document.getElementById("empty-state");
  var errorState = document.getElementById("error-state");
  var errorDetail = document.getElementById("error-detail");
  var retryButton = document.getElementById("retry");
  var countRangers = document.getElementById("count-rangers");
  var countFootprints = document.getElementById("count-footprints");
  var selectedEl = document.getElementById("selected");
  var trailButton = document.getElementById("button-trail");
  var rosterButton = document.getElementById("button-roster");
  var helpButton = document.getElementById("button-help");

  var drawerTrail = document.getElementById("drawer-trail");
  var drawerRoster = document.getElementById("drawer-roster");
  var drawerHelp = document.getElementById("drawer-help");
  var trailTitle = document.getElementById("trail-title");
  var trailList = document.getElementById("trail-list");
  var trailEarlier = document.getElementById("trail-earlier");
  var rosterList = document.getElementById("roster-list");

  var snapshot = null;        // {items, byRanger}
  var previousByRanger = {};
  var selectedRangerId = null;
  var trailBefore = null;
  var refreshTimer = null;
  var cycleId = 0;
  var currentAbort = null;
  var lastGoodAt = null;
  var firstPageEtag = null;

  /* ------------------------------------------------------------------ *
   * Deterministic illustrated portraits                                 *
   * ------------------------------------------------------------------ */

  var FACE_COLORS = ["#ED2925", "#2B2B2B", "#3E8E8C", "#E8A13B", "#E58BA0", "#7BA05B", "#5E9BD1", "#F5E6C8"];

  function hashCode(text) {
    var h = 2166136261;
    for (var i = 0; i < text.length; i++) {
      h ^= text.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return h >>> 0;
  }

  function portraitMarkup(rangerId) {
    var h = hashCode(rangerId);
    var face = FACE_COLORS[h % FACE_COLORS.length];
    var pale = (h >> 3) & 1;
    var eyes = (h >> 4) % 3;           // 0 dots, 1 happy arcs, 2 wink
    var mouth = (h >> 6) % 4;          // 0 smile, 1 open, 2 cat, 3 flat
    var top = (h >> 8) % 4;            // tuft, cap, band, antenna
    var ink = "#2B2B2B";
    var eye = pale ? "#2B2B2B" : "#FFFFFF";
    var lip = pale ? "#2B2B2B" : "#FFFFFF";

    var eyesSvg = [
      '<circle cx="33" cy="42" r="3.4" fill="' + eye + '"/>' +
        '<circle cx="47" cy="42" r="3.4" fill="' + eye + '"/>',
      '<path d="M29 43 q4 -5 8 0" stroke="' + eye + '" stroke-width="2.4" fill="none" stroke-linecap="round"/>' +
        '<path d="M43 43 q4 -5 8 0" stroke="' + eye + '" stroke-width="2.4" fill="none" stroke-linecap="round"/>',
      '<path d="M29 43 q4 -5 8 0" stroke="' + eye + '" stroke-width="2.4" fill="none" stroke-linecap="round"/>' +
        '<circle cx="47" cy="42" r="3.4" fill="' + eye + '"/>'
    ][eyes];

    var mouthSvg = [
      '<path d="M34 52 q6 5 12 0" stroke="' + lip + '" stroke-width="2.6" fill="none" stroke-linecap="round"/>',
      '<path d="M36 51 q4 7 8 0 z" fill="' + lip + '"/>',
      '<path d="M33 51 q3 4 6 0 q3 4 6 0" stroke="' + lip + '" stroke-width="2.4" fill="none" stroke-linecap="round"/>',
      '<path d="M35 53 h10" stroke="' + lip + '" stroke-width="2.6" stroke-linecap="round"/>'
    ][mouth];

    var topSvg = [
      '<path d="M40 22 q-2 -8 3 -10 q1 6 4 7" stroke="' + ink + '" stroke-width="3" fill="none" stroke-linecap="round"/>',
      '<path d="M28 28 q12 -14 24 0 z" fill="' + (pale ? "#ED2925" : "#FFFFFF") + '" stroke="' + ink + '" stroke-width="2.4" stroke-linejoin="round"/>',
      '<path d="M27 26 h26" stroke="' + ink + '" stroke-width="4" stroke-linecap="round"/>',
      '<line x1="40" y1="20" x2="40" y2="10" stroke="' + ink + '" stroke-width="2.6" stroke-linecap="round"/>' +
        '<circle cx="40" cy="8" r="3" fill="#ED2925" stroke="' + ink + '" stroke-width="1.6"/>'
    ][top];

    return (
      '<svg viewBox="0 0 80 76" aria-hidden="true" focusable="false">' +
      '<ellipse cx="40" cy="44" rx="26" ry="28" fill="' + face + '" stroke="' + ink + '" stroke-width="3"/>' +
      '<ellipse cx="18" cy="46" rx="5" ry="8" fill="' + face + '" stroke="' + ink + '" stroke-width="2.4"/>' +
      '<ellipse cx="62" cy="46" rx="5" ry="8" fill="' + face + '" stroke="' + ink + '" stroke-width="2.4"/>' +
      topSvg + eyesSvg + mouthSvg +
      '<path d="M28 33 q5 -3 10 0" stroke="' + ink + '" stroke-width="2" fill="none" opacity="0.35"/>' +
      "</svg>"
    );
  }

  function portraitElement(rangerId) {
    var holder = document.createElement("span");
    holder.className = "portrait";
    // Static template built only from constants; no user data involved.
    holder.innerHTML = portraitMarkup(rangerId);
    return holder;
  }

  /* ------------------------------------------------------------------ *
   * Time formatting                                                     *
   * ------------------------------------------------------------------ */

  function shortTime(iso) {
    var d = new Date(iso);
    if (isNaN(d)) return "";
    var now = new Date();
    var hh = String(d.getHours()).padStart(2, "0");
    var mm = String(d.getMinutes()).padStart(2, "0");
    if (d.toDateString() === now.toDateString()) return hh + ":" + mm;
    return d.toLocaleDateString(undefined, { month: "short", day: "numeric" }) + " " + hh + ":" + mm;
  }

  function fullTime(iso) {
    var d = new Date(iso);
    if (isNaN(d)) return "";
    return d.toLocaleString() + " (" + iso + ")";
  }

  /* ------------------------------------------------------------------ *
   * Projection and marker layout                                        *
   * ------------------------------------------------------------------ */

  function project(lonStr, latStr) {
    var lon = Number(lonStr);
    var lat = Number(latStr);
    var norm = (((lon + 180) % 360) + 360) % 360; // 180 === -180 on the map
    return { x: (norm / 360) * 100, y: ((90 - lat) / 180) * 100 };
  }

  function worldSize() {
    var rect = world.getBoundingClientRect();
    return { w: rect.width, h: rect.height };
  }

  function buildMarker(item, changed) {
    var button = document.createElement("button");
    button.type = "button";
    button.className = "ranger" + (changed ? " enter" : "");
    button.dataset.ranger = item.ranger_id;

    var inner = document.createElement("span");
    inner.className = "ranger-inner";

    var bubble = document.createElement("span");
    bubble.className = "bubble";
    var status = document.createElement("p");
    status.className = "bubble-status";
    status.textContent = item.status;
    var meta = document.createElement("p");
    meta.className = "bubble-meta";
    meta.textContent = item.place + " · last check-in " + shortTime(item.accepted_at);
    bubble.appendChild(status);
    bubble.appendChild(meta);

    var name = document.createElement("span");
    name.className = "ranger-name";
    var nick = document.createElement("span");
    nick.className = "nick";
    nick.textContent = item.nickname;
    var short = document.createElement("span");
    short.className = "short";
    short.textContent = item.ranger_id.slice(0, 6) + "…";
    name.appendChild(nick);
    name.appendChild(short);

    var place = document.createElement("span");
    place.className = "place-tag";
    place.textContent = item.place;

    inner.appendChild(bubble);
    inner.appendChild(portraitElement(item.ranger_id));
    inner.appendChild(name);
    inner.appendChild(place);
    button.appendChild(inner);

    button.setAttribute(
      "aria-label",
      item.nickname + " at " + item.place + " — " + item.status +
        " (checked in " + shortTime(item.accepted_at) + ")"
    );
    button.addEventListener("click", function () {
      selectRanger(item.ranger_id, true);
    });
    return button;
  }

  function findSpot(placed, ax, ay, w, h, size) {
    var margin = 6;
    // Presentation boxes stay fully inside the canvas; the true coordinate
    // remains the anchor dot, and any shift draws a leader line back to it.
    function clamp(x, y) {
      return {
        x: Math.min(Math.max(x, margin), Math.max(margin, size.w - w - margin)),
        y: Math.min(Math.max(y, margin), Math.max(margin, size.h - h - margin))
      };
    }
    var desired = clamp(ax - w / 2, ay - h);
    function free(x, y) {
      return placed.every(function (r) {
        return x + w < r.x + 6 || r.x + r.w + 6 < x ||
               y + h < r.y + 6 || r.y + r.h + 6 < y;
      });
    }
    function spot(x, y, displaced) {
      return { x: x, y: y, w: w, h: h, displaced: displaced };
    }
    if (free(desired.x, desired.y)) {
      var shifted = Math.abs(desired.x - (ax - w / 2)) > 18 ||
                    Math.abs(desired.y - (ay - h)) > 18;
      return spot(desired.x, desired.y, shifted);
    }
    // Spiral outward around the anchor; portrait keeps its leader short.
    for (var radius = 60; radius <= 420; radius += 52) {
      for (var i = 0; i < 8; i++) {
        var angle = (i / 8) * Math.PI * 2 + (radius / 52) * 0.4;
        var candidate = clamp(ax + Math.cos(angle) * radius - w / 2,
                              ay + Math.sin(angle) * radius * 0.7 - h / 2);
        if (free(candidate.x, candidate.y)) {
          return spot(candidate.x, candidate.y, true);
        }
      }
    }
    return spot(desired.x, desired.y, true); // overlap as last resort
  }

  function layoutMarkers(items, changed) {
    markersEl.replaceChildren();
    anchorsEl.replaceChildren();
    leadersEl.replaceChildren();

    var size = worldSize();
    if (!size.w || !size.h || !items) return;

    var ordered = items.slice().sort(function (a, b) {
      return Number(b.seq) - Number(a.seq);
    });
    var placed = [];

    ordered.forEach(function (item) {
      var anchor = project(item.longitude, item.latitude);
      var ax = (anchor.x / 100) * size.w;
      var ay = (anchor.y / 100) * size.h;

      var approxW = 240;
      var approxH = 165;
      var spot = findSpot(placed, ax, ay, approxW, approxH, size);
      placed.push(spot);

      var button = buildMarker(item, !!(changed && changed[item.ranger_id]));
      button.style.left = (((spot.x + approxW / 2) / size.w) * 100).toFixed(3) + "%";
      button.style.top = (((spot.y + approxH) / size.h) * 100).toFixed(3) + "%";
      if (item.ranger_id === selectedRangerId) button.classList.add("selected");
      markersEl.appendChild(button);

      var dot = document.createElement("span");
      dot.className = "anchor-dot";
      dot.style.left = anchor.x.toFixed(3) + "%";
      dot.style.top = anchor.y.toFixed(3) + "%";
      anchorsEl.appendChild(dot);

      if (spot.displaced) {
        var line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", ((ax / size.w) * 1000).toFixed(1));
        line.setAttribute("y1", ((ay / size.h) * 500).toFixed(1));
        line.setAttribute("x2", (((spot.x + approxW / 2) / size.w) * 1000).toFixed(1));
        line.setAttribute("y2", (((spot.y + approxH) / size.h) * 500).toFixed(1));
        leadersEl.appendChild(line);
      }
    });
  }

  /* ------------------------------------------------------------------ *
   * Snapshot loading (conditional refresh, stale-response safety)       *
   * ------------------------------------------------------------------ */

  function setLoadState(text) {
    loadState.textContent = text;
  }

  function showError() {
    var message = "The map service did not answer.";
    if (lastGoodAt) message += " Showing the last good map from " + shortTime(lastGoodAt) + ".";
    errorDetail.textContent = message;
    errorState.hidden = false;
  }

  function clearError() {
    errorState.hidden = true;
    errorDetail.textContent = "";
  }

  function scheduleRefresh() {
    if (refreshTimer) clearTimeout(refreshTimer);
    refreshTimer = setTimeout(function () {
      if (!document.hidden) loadSnapshot();
    }, REFRESH_MS);
  }

  function loadSnapshot() {
    var myCycle = ++cycleId;
    if (currentAbort) currentAbort.abort();
    var controller = new AbortController();
    currentAbort = controller;

    setLoadState("Loading rangers…");
    var headers = {};
    if (firstPageEtag) headers["If-None-Match"] = firstPageEtag;

    fetch(MAP_URL + "?limit=200", { headers: headers, signal: controller.signal })
      .then(function (first) {
        if (myCycle !== cycleId) throw { stale: true };
        if (first.status === 304) {
          setLoadState("");
          clearError();
          lastGoodAt = new Date().toISOString();
          scheduleRefresh();
          return null;
        }
        if (!first.ok) throw new Error("map request failed (" + first.status + ")");
        firstPageEtag = first.headers.get("ETag");
        return first.json().then(function (firstBody) {
          var allItems = firstBody.items.slice();
          var nextCursor = firstBody.next_cursor;
          var page = 1;
          function next() {
            if (!nextCursor) return Promise.resolve(null);
            page += 1;
            setLoadState("Loading rangers · page " + page + "…");
            var url = MAP_URL + "?limit=200&cursor=" + encodeURIComponent(nextCursor);
            return fetch(url, { signal: controller.signal })
              .then(function (response) {
                if (myCycle !== cycleId) throw { stale: true };
                if (!response.ok) throw new Error("map page failed (" + response.status + ")");
                return response.json();
              })
              .then(function (body) {
                allItems.push.apply(allItems, body.items);
                nextCursor = body.next_cursor;
                return next();
              });
          }
          return next().then(function () {
            firstBody.items = allItems;
            return firstBody;
          });
        });
      })
      .then(function (body) {
        if (myCycle !== cycleId || body === null) return;
        applySnapshot(body);
      })
      .catch(function (error) {
        if (error && (error.stale || error.name === "AbortError")) return;
        setLoadState("");
        showError();
        scheduleRefresh();
      });
  }

  function applySnapshot(body) {
    setLoadState("");
    clearError();
    lastGoodAt = new Date().toISOString();

    countRangers.textContent = String(body.ranger_count);
    countFootprints.textContent = String(body.footprint_count);

    var items = body.items || [];
    var byRanger = {};
    items.forEach(function (item) { byRanger[item.ranger_id] = item; });

    if (!items.length) {
      snapshot = { items: [], byRanger: {} };
      previousByRanger = {};
      selectedRangerId = null;
      layoutMarkers([], {});
      emptyState.hidden = false;
      updateSelectedPanel();
      scheduleRefresh();
      return;
    }
    emptyState.hidden = true;

    // Animate only genuinely new or re-positioned rangers (real updates).
    var changed = {};
    Object.keys(byRanger).forEach(function (id) {
      var prev = previousByRanger[id];
      if (!prev || prev.seq !== byRanger[id].seq) changed[id] = true;
    });
    previousByRanger = byRanger;
    snapshot = { items: items, byRanger: byRanger };

    layoutMarkers(items, changed);
    if (selectedRangerId && !byRanger[selectedRangerId]) {
      selectedRangerId = null;
      updateSelectedPanel();
    }
    scheduleRefresh();
  }

  /* ------------------------------------------------------------------ *
   * Selection, panels and drawers                                       *
   * ------------------------------------------------------------------ */

  function cssEscape(value) {
    if (window.CSS && CSS.escape) return CSS.escape(value);
    return value.replace(/[^a-zA-Z0-9_]/g, "\\$&");
  }

  function selectRanger(rangerId, focus) {
    selectedRangerId = rangerId;
    Array.prototype.forEach.call(markersEl.children, function (el) {
      el.classList.toggle("selected", el.dataset.ranger === rangerId);
    });
    updateSelectedPanel();
    if (focus) {
      var el = markersEl.querySelector('[data-ranger="' + cssEscape(rangerId) + '"]');
      if (el) el.focus({ preventScroll: true });
    }
  }

  function updateSelectedPanel() {
    selectedEl.replaceChildren();
    var item = snapshot && selectedRangerId && snapshot.byRanger[selectedRangerId];
    if (!item) {
      var hint = document.createElement("p");
      hint.className = "selected-hint";
      hint.textContent = "Click a ranger on the map to read their latest trace.";
      selectedEl.appendChild(hint);
      trailButton.hidden = true;
      closeDrawer(drawerTrail);
      return;
    }

    var line = document.createElement("p");
    line.className = "selected-line";
    var name = document.createElement("span");
    name.className = "selected-name";
    name.textContent = item.nickname + " ";
    var short = document.createElement("span");
    short.textContent = "(" + item.ranger_id.slice(0, 8) + "…)";
    short.style.color = "var(--muted)";
    short.style.fontSize = "12px";
    var place = document.createElement("span");
    place.className = "selected-place";
    place.textContent = item.place;
    var status = document.createElement("span");
    status.className = "selected-status";
    status.textContent = item.status + " · " + shortTime(item.accepted_at);
    line.appendChild(name);
    line.appendChild(short);
    line.appendChild(place);
    line.appendChild(status);

    var idLine = document.createElement("p");
    idLine.className = "selected-id";
    idLine.textContent = item.ranger_id;

    var copyButton = document.createElement("button");
    copyButton.type = "button";
    copyButton.className = "chip";
    copyButton.style.marginLeft = "8px";
    copyButton.textContent = "Copy identity";
    copyButton.addEventListener("click", function () {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(item.ranger_id).then(function () {
          copyButton.textContent = "Copied!";
          setTimeout(function () { copyButton.textContent = "Copy identity"; }, 1500);
        }).catch(function () { /* identity text stays selectable */ });
      }
    });

    selectedEl.appendChild(line);
    selectedEl.appendChild(idLine);
    selectedEl.appendChild(copyButton);
    trailButton.hidden = false;
  }

  function openDrawer(drawer) {
    [drawerTrail, drawerRoster, drawerHelp].forEach(function (d) {
      if (d !== drawer) closeDrawer(d);
    });
    drawer.hidden = false;
    syncDrawerButtons();
  }

  function closeDrawer(drawer) {
    drawer.hidden = true;
    syncDrawerButtons();
  }

  function toggleDrawer(drawer) {
    if (drawer.hidden) openDrawer(drawer); else closeDrawer(drawer);
  }

  function syncDrawerButtons() {
    rosterButton.setAttribute("aria-expanded", String(!drawerRoster.hidden));
    rosterButton.classList.toggle("chip-red", !drawerRoster.hidden);
    helpButton.setAttribute("aria-expanded", String(!drawerHelp.hidden));
    trailButton.setAttribute("aria-expanded", String(!drawerTrail.hidden));
  }

  function renderRoster() {
    rosterList.replaceChildren();
    if (!snapshot) return;
    var items = snapshot.items.slice().sort(function (a, b) {
      return a.nickname.localeCompare(b.nickname);
    });
    if (!items.length) {
      var empty = document.createElement("li");
      empty.className = "roster-sub";
      empty.textContent = "No rangers have checked in yet.";
      rosterList.appendChild(empty);
      return;
    }
    items.forEach(function (item) {
      var li = document.createElement("li");
      var row = document.createElement("button");
      row.type = "button";
      row.className = "roster-item";
      row.appendChild(portraitElement(item.ranger_id));

      var textCol = document.createElement("span");
      var name = document.createElement("span");
      name.className = "roster-name";
      name.textContent = item.nickname + " (" + item.ranger_id.slice(0, 8) + "…)";
      var sub = document.createElement("span");
      sub.className = "roster-sub";
      sub.textContent = item.place + " · " + shortTime(item.accepted_at) + " · " + item.status;
      textCol.appendChild(name);
      textCol.appendChild(sub);

      var link = document.createElement("span");
      link.className = "roster-trail-link";
      link.textContent = "Trail →";

      row.appendChild(textCol);
      row.appendChild(link);
      row.addEventListener("click", function () {
        selectRanger(item.ranger_id, true);
        closeDrawer(drawerRoster);
      });
      li.appendChild(row);
      rosterList.appendChild(li);
    });
  }

  function renderTrailPage(items, append) {
    if (!append) trailList.replaceChildren();
    items.forEach(function (item) {
      var li = document.createElement("li");
      li.className = "trail-item";
      var when = document.createElement("span");
      when.className = "trail-when";
      when.textContent = shortTime(item.accepted_at);
      when.title = fullTime(item.accepted_at);
      var place = document.createElement("span");
      place.className = "trail-place";
      place.textContent = item.place;
      var coords = document.createElement("span");
      coords.className = "coords";
      coords.textContent = item.latitude + ", " + item.longitude;
      place.appendChild(coords);
      var status = document.createElement("p");
      status.className = "trail-status";
      status.textContent = item.status;
      li.appendChild(when);
      li.appendChild(place);
      li.appendChild(status);
      trailList.appendChild(li);
    });
  }

  function loadTrail(rangerId) {
    trailBefore = null;
    var item = snapshot && snapshot.byRanger[rangerId];
    trailTitle.textContent = item ? item.nickname + "'s trail" : "Trail";
    trailList.replaceChildren();
    trailEarlier.hidden = true;
    var loading = document.createElement("li");
    loading.className = "trail-when";
    loading.textContent = "Loading…";
    trailList.appendChild(loading);
    fetch(HISTORY_URL + "?ranger_id=" + encodeURIComponent(rangerId) + "&limit=20")
      .then(function (response) {
        if (!response.ok) throw new Error("history failed");
        return response.json();
      })
      .then(function (body) {
        renderTrailPage(body.items, false);
        trailBefore = body.next_before;
        trailEarlier.hidden = !body.next_before;
      })
      .catch(function () {
        trailList.replaceChildren();
        var err = document.createElement("li");
        err.className = "trail-status";
        err.textContent = "Couldn't load the trail.";
        trailList.appendChild(err);
      });
  }

  trailEarlier.addEventListener("click", function () {
    if (!selectedRangerId || !trailBefore) return;
    fetch(HISTORY_URL + "?ranger_id=" + encodeURIComponent(selectedRangerId) +
          "&limit=20&before=" + encodeURIComponent(trailBefore))
      .then(function (response) {
        if (!response.ok) throw new Error("history failed");
        return response.json();
      })
      .then(function (body) {
        renderTrailPage(body.items, true);
        trailBefore = body.next_before;
        trailEarlier.hidden = !body.next_before;
      })
      .catch(function () { /* keep current pages; the button stays */ });
  });

  trailButton.addEventListener("click", function () {
    if (!selectedRangerId) return;
    loadTrail(selectedRangerId);
    openDrawer(drawerTrail);
  });

  rosterButton.addEventListener("click", function () {
    if (drawerRoster.hidden) renderRoster();
    toggleDrawer(drawerRoster);
  });

  helpButton.addEventListener("click", function () { toggleDrawer(drawerHelp); });

  Array.prototype.forEach.call(
    document.querySelectorAll("[data-close-drawer]"),
    function (button) {
      button.addEventListener("click", function () {
        closeDrawer(button.closest(".drawer"));
      });
    }
  );

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      [drawerTrail, drawerRoster, drawerHelp].forEach(closeDrawer);
    }
  });

  retryButton.addEventListener("click", loadSnapshot);

  document.addEventListener("visibilitychange", function () {
    if (document.hidden) {
      if (refreshTimer) clearTimeout(refreshTimer);
    } else {
      loadSnapshot(); // immediate refresh when returning to the page
    }
  });

  /* ------------------------------------------------------------------ *
   * Pan & zoom                                                          *
   * The canvas keeps a fixed 2:1 aspect (equirectangular); the transform *
   * covers, then pans and zooms the world.                              *
   * ------------------------------------------------------------------ */

  var view = { x: 0, y: 0, k: 1 };
  var minK = 1;

  function baseSize() {
    var rect = world.getBoundingClientRect();
    return { w: rect.width, h: rect.width / 2 };
  }

  function applyView() {
    canvas.style.transform =
      "translate(" + view.x + "px," + view.y + "px) scale(" + view.k + ")";
  }

  function clampView() {
    var rect = world.getBoundingClientRect();
    var base = baseSize();
    var cw = base.w * view.k;
    var ch = base.h * view.k;
    if (cw <= rect.width) view.x = (rect.width - cw) / 2;
    else view.x = Math.min(0, Math.max(rect.width - cw, view.x));
    if (ch <= rect.height) view.y = (rect.height - ch) / 2;
    else view.y = Math.min(0, Math.max(rect.height - ch, view.y));
  }

  function fitView() {
    var rect = world.getBoundingClientRect();
    var base = baseSize();
    minK = Math.max(1, rect.height / base.h);
    view.k = minK;
    clampView();
    applyView();
  }

  function zoomAt(clientX, clientY, factor) {
    var rect = world.getBoundingClientRect();
    var cx = clientX - rect.left;
    var cy = clientY - rect.top;
    var newK = Math.min(6, Math.max(minK, view.k * factor));
    if (newK === view.k) return;
    var ratio = newK / view.k;
    view.x = cx - (cx - view.x) * ratio;
    view.y = cy - (cy - view.y) * ratio;
    view.k = newK;
    clampView();
    applyView();
  }

  document.getElementById("zoom-in").addEventListener("click", function () {
    var r = world.getBoundingClientRect();
    zoomAt(r.left + r.width / 2, r.top + r.height / 2, 1.35);
  });
  document.getElementById("zoom-out").addEventListener("click", function () {
    var r = world.getBoundingClientRect();
    zoomAt(r.left + r.width / 2, r.top + r.height / 2, 1 / 1.35);
  });
  document.getElementById("zoom-reset").addEventListener("click", function () {
    view = { x: 0, y: 0, k: 1 };
    fitView();
  });

  world.addEventListener("wheel", function (event) {
    event.preventDefault();
    zoomAt(event.clientX, event.clientY, event.deltaY < 0 ? 1.15 : 1 / 1.15);
  }, { passive: false });

  var pointers = new Map();
  var pinchBase = null;

  world.addEventListener("pointerdown", function (event) {
    if (event.target.closest("button") || event.target.closest(".drawer")) return;
    pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
    try { world.setPointerCapture(event.pointerId); } catch (err) { /* ok */ }
    if (pointers.size === 2) {
      var pts = Array.from(pointers.values());
      pinchBase = {
        dist: Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y),
        k: view.k
      };
    }
  });

  world.addEventListener("pointermove", function (event) {
    if (!pointers.has(event.pointerId)) return;
    var prev = pointers.get(event.pointerId);
    pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
    if (pointers.size === 1) {
      view.x += event.clientX - prev.x;
      view.y += event.clientY - prev.y;
      clampView();
      applyView();
    } else if (pointers.size === 2 && pinchBase && pinchBase.dist > 0) {
      var pts = Array.from(pointers.values());
      var dist = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);
      var target = Math.min(6, Math.max(minK, pinchBase.k * (dist / pinchBase.dist)));
      var r = world.getBoundingClientRect();
      zoomAt(r.left + r.width / 2, r.top + r.height / 2, target / view.k);
    }
  });

  function releasePointer(event) {
    pointers.delete(event.pointerId);
    if (pointers.size < 2) pinchBase = null;
  }
  world.addEventListener("pointerup", releasePointer);
  world.addEventListener("pointercancel", releasePointer);

  var resizeTimer = null;
  window.addEventListener("resize", function () {
    if (resizeTimer) clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      fitView();
      if (snapshot) layoutMarkers(snapshot.items);
    }, 120);
  });

  /* ------------------------------------------------------------------ *
   * Keyboard navigation between markers                                 *
   * ------------------------------------------------------------------ */

  markersEl.addEventListener("keydown", function (event) {
    if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;
    var buttons = Array.prototype.slice.call(markersEl.children);
    if (!buttons.length) return;
    var index = buttons.indexOf(document.activeElement);
    if (index === -1) return;
    event.preventDefault();
    var next = event.key === "ArrowRight" ? index + 1 : index - 1;
    buttons[(next + buttons.length) % buttons.length].focus();
  });

  /* ------------------------------------------------------------------ *
   * Boot                                                                *
   * ------------------------------------------------------------------ */

  syncDrawerButtons();
  updateSelectedPanel();
  fitView();
  loadSnapshot();
})();
