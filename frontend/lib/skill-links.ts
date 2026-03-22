/**
 * Agent skill pack lives in the monorepo at repository root skill/.
 * Keep URLs in sync with skill/README.md and docs/ECOSYSTEM.md.
 */
export const GAME_REPO_URL = 'https://github.com/Fankouzu/claw-adventure'

/** Browse SKILL.md and references on GitHub */
export const SKILL_TREE_URL = `${GAME_REPO_URL}/tree/main/skill`

/** Primary agent skill document (rendered on GitHub) */
export const SKILL_MD_URL = `${GAME_REPO_URL}/blob/main/skill/SKILL.md`

/**
 * Rolling zip published by repo workflows (skill-latest pre-release).
 */
export const SKILL_ZIP_LATEST_URL = `${GAME_REPO_URL}/releases/download/skill-latest/claw-adventure-skill-latest.zip`

/**
 * Install via Skills CLI using the same zip asset (portable across hosts).
 */
export const SKILL_CLI_COMMAND = `npx skills add ${SKILL_ZIP_LATEST_URL}`
