USE SCHEMA LAUNCH_MYSTERY.DEMO;
USE WAREHOUSE LAUNCH_MYSTERY_WH;

-- One row per hour, platform, and cohort. The iOS cohort assignment is stable.
BEGIN;
DELETE FROM CHECKOUT_HOURLY;
INSERT INTO CHECKOUT_HOURLY VALUES
  ('2026-06-04 09:00:00', 'Before', 'iOS',     'Rollout',  2000, 500, 300),
  ('2026-06-04 09:00:00', 'Before', 'iOS',     'Holdout',   700, 165, 100),
  ('2026-06-04 09:00:00', 'Before', 'Android', 'Standard', 2000, 500, 300),
  ('2026-06-04 09:00:00', 'Before', 'Web',     'Standard', 2300, 500, 300),
  ('2026-06-04 10:00:00', 'After',  'iOS',     'Rollout',  2000, 500, 120),
  ('2026-06-04 10:00:00', 'After',  'iOS',     'Holdout',   700, 165, 100),
  ('2026-06-04 10:00:00', 'After',  'Android', 'Standard', 2000, 500, 300),
  ('2026-06-04 10:00:00', 'After',  'Web',     'Standard', 2300, 500, 300);

DELETE FROM INCIDENT_NOTES;
INSERT INTO INCIDENT_NOTES VALUES
  ('REL-041', 'iOS checkout rollout at 10:00 UTC',
   'On June 4 at 10:00 UTC, the one-tap checkout flag was enabled for the iOS rollout cohort. The iOS holdout stayed on the previous flow. Android and Web were unchanged.'),
  ('PAY-017', 'Payment provider latency at 11:20 UTC',
   'The payment provider reported elevated authorization latency beginning at 11:20 UTC on June 4. Its first affected authorization occurred after the 10:00 to 11:00 UTC investigation window.'),
  ('OBS-032', 'iOS rollout telemetry',
   'The 10:06 UTC mobile log sample shows repeated address-validation timeouts in the one-tap checkout flow. The sample does not establish how many failed orders had this error.'),
  ('OPS-005', 'Checkout feature flag runbook',
   'The incident lead can disable the one-tap flag for the iOS rollout cohort. After disabling it, compare checkout completion with the holdout and watch overall order volume before closing the incident.'),
  ('MKT-008', 'Launch campaign schedule',
   'The launch email went out at 09:00 UTC. The paid campaign schedule remained unchanged between 09:00 and 11:00 UTC.');
COMMIT;
