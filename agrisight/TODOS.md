# AgriSight TODOS

Deferred work from /plan-ceo-review session (2026-04-18).
Approach A = conflict-aware report generator (current). Approach B = full analyst workspace.

---

## Tech Debt (new, found 2026-07-30)

### ~~[P2] ISSUE-004: Dashboard shows "Connection Error" on GeoJSON-wrapped API responses~~
~~Fixed 2026-07-30. Root cause: `/api/v1/geospatial/regions/` (and the stress-event
/conflict-event summary endpoints) are served by `GeoFeatureModelSerializer`, so
list data comes back as a GeoJSON `FeatureCollection` ({type, features: [...]})
with each item's fields nested under `.properties` — not a plain array as
`Dashboard.jsx` assumed. This wasn't a zero-rows edge case as originally
suspected — it would reproduce with any amount of region data, since the
response shape is always GeoJSON-wrapped. Only became visible once ISSUE-003's
blank-page bug was fixed and the dashboard could render at all. Fixed by adding
`toFlatFeatureList()` in `Dashboard.jsx` — normalizes either a plain array or a
FeatureCollection into flat objects, applied at all three call sites (regions,
recent stress events, recent conflict events). 5 new unit tests. Verified via
Vite dev server: dashboard now renders full stat cards/charts/activity feed
instead of crashing. Commit: 5fac612.~~

**New finding surfaced by this fix (not investigated further):** once the
dashboard rendered end-to-end for the first time, React logged `Maximum update
depth exceeded` originating from the Dashboard's data-fetch `useEffect`
(dependency array `[hasPermission]`). `hasPermission` in `AuthContext.jsx` is a
plain arrow function recreated on every `AuthProvider` render (not wrapped in
`useCallback`), which is the same "unstable reference in a dependency array"
pattern as ISSUE-003's WebSocketContext bug. Did not visibly break rendering in
this session (dashboard displayed correctly despite the warning), but worth
fixing before it does — see the new tech-debt item below.

### [P2] `hasPermission` (AuthContext) is recreated every render, likely causing an effect re-fire loop
**What:** `AuthContext.jsx`'s `hasPermission` is a plain `const hasPermission = (permission) => {...}`
inside `AuthProvider`, not memoized with `useCallback`. `Dashboard.jsx`'s
data-fetch `useEffect` depends on `[hasPermission]`, so it re-fires (and
re-fetches) every time `AuthProvider` re-renders, regardless of whether
anything relevant to auth actually changed. React logs `Maximum update depth
exceeded` from this during normal dashboard use (found 2026-07-30, while
verifying the ISSUE-004 fix).
**Why:** Same shape as the ISSUE-003 WebSocketContext bug (unstable callback
reference in a dependency array) — worth checking whether other consumers of
`hasPermission` have the same problem before it causes a visible hang like
ISSUE-003 did.
**Context:** Wrap `hasPermission` in `useCallback` in `AuthContext.jsx`; check
`PermissionRoute` in `App.jsx` and any other `useEffect`/`useMemo` that
depends on it.
**Effort:** XS (CC: ~15 min)

---

## Approach B: Core Features

### [P1] Road access degradation layer
**What:** OSM road network + ACLED conflict event proximity → access score per district.
ST_DWithin(district_centroid, conflict_event_cluster, distance_threshold) in PostGIS.
**Why:** This is what makes AgriSight categorically different from FEWS NET. FEWS NET
cannot assess physical access in M23-controlled territory. AgriSight can.
**Pros:** Completes the conflict-aware thesis; adds a dimension no incumbent provides.
**Cons:** OSM road coverage in rural DRC is uneven — need a quality threshold (e.g.,
skip districts where OSM road density < X km per 100km²).
**Context:** Start with paved road network only (more reliable in OSM for DRC). Add
unpaved tracks in a second pass after validating quality.
**Effort:** M (human: 1 week / CC: ~1-2 hours)
**Depends on:** Approach A validated with at least one analyst.

### [P1] Composite score weight adjustment via config
**What:** Move the NDVI/conflict/displacement/rainfall weights (currently 30/35/25/10)
from hardcoded values to a config table or Django admin panel.
**Why:** First analyst feedback will tell you whether the weights are calibrated correctly.
You need to adjust without a code deploy.
**Effort:** S (human: 1 day / CC: 15 min)
**Depends on:** First analyst feedback session.

### [P1] Activate ML anomaly detection with conflict data as input
**What:** `apps/ml_models/` exists with scikit-learn anomaly detection but is not
wired to conflict data. For Approach B, conflict event density and displacement
figures should be input features alongside vegetation indices.
**Why:** The ML layer becomes meaningful once conflict data is in the pipeline.
**Context:** Check existing model interface in `apps/ml_models/` before designing
the new input schema.
**Effort:** M (human: 1 week / CC: 2 hours)

### [P2] Multi-org RBAC activation
**What:** The RBAC infrastructure is built (`apps/organizations/`, `apps/users/`,
permission checks in AuthContext). Approach B activates it for multi-INGO deployment.
**Why:** Scaling to multiple INGO pilots requires org-scoped data access.
**Effort:** S (human: 3 days / CC: 30 min — most work is already done)

### [P2] CHIRPS dekadal anomaly (10-day resolution)
**What:** Approach A uses monthly rainfall deviation. Approach B needs dekadal (10-day)
anomaly vs. 20-year climatology baseline for more precise early-warning signals.
**Why:** Monthly data can miss a 10-day drought that destroys a planting window.
**Effort:** S (human: 2 days / CC: 30 min)

### [P2] Complete `monitor_batch_jobs` Celery task
**What:** `backend/apps/satellite_processing/tasks.py` — `monitor_batch_jobs()` function
has incomplete monitoring loop logic (TODO comment). Currently abandoned mid-implementation.
**Why:** Approach B reactivates Celery for async report generation. This task needs
to be complete before that happens.
**Context:** The batch processing flow: Create → Analyse → Monitor → Start. The task
currently stops after Analyse. Need to implement the Monitor → Start state machine.
**Effort:** S (human: 1 day / CC: 30 min)

### ~~[P1] ISSUE-003 (found by /qa on 2026-07-30): WebSocket reconnect storm hangs the app blank immediately after login~~
~~Fixed 2026-07-30. Root cause was two bugs: (1) `useWebSocket.js`'s `connect`
callback depended on the whole `options` object WebSocketContext recreated every
render, causing a teardown/reopen loop on every render — fixed by reading
onMessage/authToken through refs and depending only on primitive values. (2) the
backend/infra half — `nginx.conf` had no `location /ws/` block (upgrades fell
through to the static frontend container), `backend` ran gunicorn+WSGI (can't
serve Channels regardless of nginx routing), and `asgi.py`'s own comment
described the correct import order but the code didn't follow it (ORM-touching
imports ran before `get_asgi_application()`, raising `AppRegistryNotReady` the
first time anything actually served the ASGI app). Also bumped haproxy's 50s
timeouts to 1h (would've silently killed idle WS connections) and added
`AgriSightConsumerTests` (apps/core/tests.py). This also completes the
"Real-time WebSocket alerts" P2 item below — the infrastructure is now actually
live, not just present. Verified end-to-end: login shows one clean "WebSocket
connected" + subscription_success, no reconnect storm, dashboard renders.
Commits: 2c01532 (frontend), 7fae568 (backend/infra).~~

### ~~[P2] Real-time WebSocket alerts~~
~~Activation completed as part of fixing ISSUE-003 above (2026-07-30) — same
underlying infrastructure, same commits.~~

---

## Approach B: Expansion

### [P3] South Sudan and Horn of Africa geographies
**What:** Add South Sudan and Ethiopia/Horn of Africa as supported geographies.
**Why:** Same crisis profile as DRC, same INGO buyers, same FEWS NET gaps.
**Effort:** S per geography (boundary data + ACLED region filter — mostly config)
**Depends on:** DRC pilot validated.

### [P3] Government ministry buyer track
**What:** Engage DRC Ministry of Agriculture and/or South Sudan Ministry of Agriculture.
**Why:** Government contracts are larger and longer-term than INGO pilots.
**Effort:** Business development, not engineering. Procurement cycles are 6-18 months.
**Depends on:** At least 2 successful INGO pilots.

---

## Tech Debt

### [P2] DRY: get_queryset() duplication across views
**What:** `get_queryset()` is copy-pasted in `ReportListCreateView`, `ReportDetailView`,
`AlertListCreateView`, `AlertDetailView`, and at least 3 other apps. Same pattern:
admin sees all, org user sees own org.
**Why:** Approach B will add 5+ more view classes. Without a shared mixin, this
duplication will compound and create inconsistent access control across views.
**Effort:** XS (human: 2 hours / CC: 10 min — extract to `OrgScopedQuerySetMixin`)
**Depends on:** Approach A shipped.

### [P2] Auth layer stabilization
**What:** The auth layer has had 3 refactors in git history (JWT → session → refactor).
The current implementation is well-commented and correct, but the history suggests
unclear requirements. Write an explicit auth decision record before Approach B.
**Why:** A 4th auth refactor during Approach B deployment would be disruptive.
**Effort:** XS (30 min to write the decision doc)

### ~~[P2] Composite score unit test table~~
~~Brought into Approach A scope during /plan-eng-review (2026-04-18). Tests for all-null,
partial-null, and boundary threshold cases are in conflict_reports/tests.py.~~
