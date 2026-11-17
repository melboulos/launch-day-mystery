USE SCHEMA LAUNCH_MYSTERY.DEMO;
USE WAREHOUSE LAUNCH_MYSTERY_WH;

-- Expect 1,000 Before and 820 After.
SELECT RELEASE_PHASE, SUM(ORDERS) AS ORDERS
FROM CHECKOUT_HOURLY GROUP BY RELEASE_PHASE;

-- Expect Rollout 60% Before and 24% After. Holdout stays near 60.6%.
SELECT * FROM SEMANTIC_VIEW(
    CHECKOUT_FUNNEL
    DIMENSIONS funnel.release_phase, funnel.platform, funnel.cohort
    METRICS funnel.completed_orders, funnel.completion_rate
) ORDER BY PLATFORM, COHORT, RELEASE_PHASE;

-- Inspection only. The app uses the Cortex Search Python API.
SELECT PARSE_JSON(SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'LAUNCH_MYSTERY.DEMO.INCIDENT_SEARCH',
    '{"query":"elevated payment authorization latency","columns":["DOC_ID","TITLE"],"limit":3}'
));

SELECT AI_COMPLETE('claude-haiku-4-5', 'Reply with READY.');
