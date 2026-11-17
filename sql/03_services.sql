USE SCHEMA LAUNCH_MYSTERY.DEMO;
USE WAREHOUSE LAUNCH_MYSTERY_WH;

CREATE OR REPLACE SEMANTIC VIEW CHECKOUT_FUNNEL
  TABLES (funnel AS CHECKOUT_EVENT_FUNNEL)
  DIMENSIONS (
    funnel.hour_utc AS WINDOW_START_UTC,
    funnel.release_phase AS RELEASE_PHASE,
    funnel.platform AS PLATFORM,
    funnel.cohort AS COHORT
  )
  METRICS (
    funnel.sessions AS SUM(STOREFRONT_SESSIONS),
    funnel.checkout_attempts AS SUM(CHECKOUT_STARTS),
    funnel.completed_orders AS SUM(ORDERS),
    funnel.address_validation_timeouts AS SUM(ADDRESS_TIMEOUTS),
    funnel.completion_rate AS DIV0(SUM(ORDERS), SUM(CHECKOUT_STARTS))
      COMMENT = 'Fraction of checkout starts that became orders. Multiply by 100 for percent.'
  )
  COMMENT = 'Synthetic June 4 incident. Before is 09:00 to 10:00 UTC, After is 10:00 to 11:00 UTC. Rollout and Holdout are stable iOS cohorts.';

CREATE CORTEX SEARCH SERVICE IF NOT EXISTS INCIDENT_SEARCH
  ON BODY
  ATTRIBUTES DOC_ID
  WAREHOUSE = LAUNCH_MYSTERY_WH
  TARGET_LAG = '1 hour'
  INITIALIZE = ON_CREATE
  AS (SELECT DOC_ID, TITLE, BODY FROM INCIDENT_NOTES);
