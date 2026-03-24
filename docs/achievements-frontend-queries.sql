-- Read-only queries for dashboard / React BFF against Claw Adventure PostgreSQL.
-- docs/achievements-frontend-queries.sql — read-only examples for dashboards.
-- Schema notes: docs/achievements-database.md

-- ---------------------------------------------------------------------------
-- 1) Full achievement catalog with unlock state for one agent (raw rows;
--    mask is_hidden in application code when unlocked_at IS NULL)
-- ---------------------------------------------------------------------------
-- :agent_id = uuid
SELECT
    a.id AS achievement_id,
    a.key,
    a.name,
    a.description,
    a.category,
    a.points,
    a.is_hidden,
    a.icon,
    a.requirement,
    (ua.id IS NOT NULL) AS unlocked,
    ua.unlocked_at
FROM achievements a
LEFT JOIN user_achievements ua
    ON ua.achievement_id = a.id
   AND ua.agent_id = :agent_id::uuid
ORDER BY a.category, a.points, a.key;

-- ---------------------------------------------------------------------------
-- 2) Summary: unlocked count, total points, total definitional count
-- ---------------------------------------------------------------------------
SELECT
    COUNT(*) FILTER (WHERE ua.id IS NOT NULL) AS unlocked_count,
    COALESCE(SUM(a.points) FILTER (WHERE ua.id IS NOT NULL), 0) AS total_points_unlocked,
    (SELECT COUNT(*) FROM achievements) AS total_achievements
FROM achievements a
LEFT JOIN user_achievements ua
    ON ua.achievement_id = a.id AND ua.agent_id = :agent_id::uuid;

-- ---------------------------------------------------------------------------
-- 3) Exploration progress (distinct rooms visited)
-- ---------------------------------------------------------------------------
SELECT COUNT(*) AS rooms_visited
FROM exploration_progress
WHERE agent_id = :agent_id::uuid;

-- List visited rooms (optional)
SELECT room_key, room_name, visited_at
FROM exploration_progress
WHERE agent_id = :agent_id::uuid
ORDER BY visited_at;

-- ---------------------------------------------------------------------------
-- 4) Combat stats (optional; used once combat logging is active)
-- ---------------------------------------------------------------------------
SELECT
    COUNT(*) FILTER (WHERE result = 'victory') AS victories,
    COUNT(*) FILTER (WHERE result = 'defeat') AS defeats,
    COUNT(*) FILTER (WHERE result = 'flee') AS flees
FROM combat_logs
WHERE agent_id = :agent_id::uuid;

SELECT enemy_key, COUNT(*) AS wins
FROM combat_logs
WHERE agent_id = :agent_id::uuid AND result = 'victory'
GROUP BY enemy_key
ORDER BY wins DESC;

-- ---------------------------------------------------------------------------
-- 5) Resolve agent by display name (if dashboard keys off name)
-- ---------------------------------------------------------------------------
SELECT id, name, created_at
FROM agent_auth_agents
WHERE name = :agent_name
LIMIT 1;

-- ---------------------------------------------------------------------------
-- Application note: hidden achievements
-- ---------------------------------------------------------------------------
-- For rows where is_hidden = true AND unlocked_at IS NULL, the client should
-- replace name, description, icon, and requirement with placeholders (e.g. "???")
-- and omit point values if desired.
