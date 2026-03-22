"""
Agent authentication commands (API key connect and status).
"""
from evennia.commands.command import Command
from evennia.utils import create
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class CmdAgentConnect(Command):
    """
    Connect with an Agent API key.

    Usage:
        agent_connect <api_key>

    Keys look like claw_live_... or claw_test_...
    """

    key = "agent_connect"
    aliases = ["ac", "agent_login"]
    locks = "cmd:all()"  # Allow before account login
    help_category = "Authentication"

    def func(self):
        """Run agent_connect."""
        from world.agent_auth.auth import verify_api_key

        caller = self.caller
        session = self.session

        api_key = self.args.strip()

        if not api_key:
            caller.msg("Usage: agent_connect <api_key>")
            return

        if not api_key.startswith('claw_'):
            caller.msg("|rInvalid API key format. API keys start with 'claw_'|n")
            return

        agent = verify_api_key(api_key)

        if not agent:
            caller.msg("|rInvalid API key. Please check and try again.|n")
            logger.warning(f"Failed agent connect attempt with key prefix: {api_key[:20]}...")
            return

        if not agent.is_claimed:
            caller.msg("|rThis Agent has not been claimed yet.|n")
            caller.msg(f"Please visit {agent.claim_url} to claim this agent first.")
            return

        if agent.claim_expires_at and agent.claim_expires_at < timezone.now():
            caller.msg("|rThis Agent's claim link has expired.|n")
            return

        account = self._get_or_create_account(agent)

        if not account:
            caller.msg("|rFailed to create or retrieve account.|n")
            return

        session.sessionhandler.login(session, account)

        # Single active WS per Agent: MULTISESSION_MODE may be 1 for humans, but duplicate
        # agent_connect sessions cause duplicate broadcasts and "Sharing ... sessions".
        if getattr(account.db, "is_agent", False):
            session.sessionhandler.disconnect_duplicate_sessions(
                session,
                reason=(
                    "This Agent account opened a new connection (agent_connect). "
                    "Only one session is kept; this one was closed."
                ),
            )

        # Clear stale puppet on this session (e.g. character was deleted in a prior session).
        # Otherwise Evennia may emit "The Character does not exist." before we attach the Agent char.
        try:
            account.unpuppet_object(session)
        except (RuntimeError, TypeError, AttributeError):
            pass

        character = self._get_or_create_agent_character(account, agent)
        if not character:
            caller.msg("|rCould not create or load a character for this Agent.|n")
            session.sessionhandler.disconnect(session)
            return

        try:
            account.puppet_object(session, character)
        except RuntimeError as exc:
            logger.error("Agent puppet failed for %s: %s", agent.name, exc)
            caller.msg("|rCould not enter the game with your character.|n")
            session.sessionhandler.disconnect(session)
            return

        if session.get_puppet() is not character:
            logger.error(
                "Agent %s: puppet_object did not attach character %s to session",
                agent.name,
                character.key,
            )
            caller.msg("|rCould not enter the game with your character.|n")
            session.sessionhandler.disconnect(session)
            return

        agent.update_last_active()

        if agent.evennia_account != account:
            agent.evennia_account = account
            agent.save()

        self._create_session_record(agent, session)

        caller.msg(f"|gWelcome, Agent {agent.name}!|n")
        caller.msg(f"You are now connected to the Adventure as |c{character.key}|n.")
        
        logger.info(f"Agent {agent.name} (ID: {agent.id}) connected successfully")
    
    def _get_or_create_account(self, agent):
        """Return existing or new Evennia Account for this Agent."""
        from evennia.accounts.models import AccountDB

        if agent.evennia_account:
            return agent.evennia_account

        account_name = f"agent_{agent.name}"

        try:
            account = AccountDB.objects.get(username=account_name)
            return account
        except AccountDB.DoesNotExist:
            pass

        try:
            account = create.create_account(
                account_name,
                email=None,
                password=None,  # Agent accounts don't use passwords
                typeclass="typeclasses.accounts.Account"
            )
            account.db.is_agent = True
            account.db.agent_id = str(agent.id)
            account.save()
            
            logger.info(f"Created new account for Agent {agent.name}")
            return account
            
        except Exception as e:
            logger.error(f"Failed to create account for Agent {agent.name}: {e}")
            return None
    
    @staticmethod
    def _session_client_ip(session):
        """
        Normalize session.address for PostgreSQL inet (avoid str[0] -> first char bug).
        """
        addr = getattr(session, "address", None)
        if not addr:
            return None
        if isinstance(addr, str):
            host = addr.split(":")[0].split("%")[0].strip()
            return host or None
        if isinstance(addr, (list, tuple)) and len(addr) >= 1:
            return str(addr[0])
        return None

    def _create_session_record(self, agent, session):
        """Persist AgentSession row for auditing."""
        from world.agent_auth.models import AgentSession

        try:
            AgentSession.objects.create(
                agent=agent,
                ip_address=self._session_client_ip(session),
                user_agent="MCP Bridge",
            )
        except Exception as e:
            logger.error(f"Failed to create session record: {e}")

    def _get_or_create_agent_character(self, account, agent):
        """
        One stable Character per Agent: match db.claw_agent_id, else legacy key, else create.

        Evennia defaults to MAX_NR_CHARACTERS=1. Tutorial IntroRoom (etc.) may rename the
        character (e.g. LUCKY_*), so key may not match slug(agent.name). If the account
        already holds one character with no claw_agent_id, adopt it instead of create.
        """

        agent_id_str = str(agent.id)
        chars = account.characters.all()

        for char in chars:
            if getattr(char.db, "claw_agent_id", None) == agent_id_str:
                return char

        from world.agent_auth.in_world_snapshot import slug_character_key

        want_key = slug_character_key(agent.name, agent.id)
        for char in chars:
            if char.key == want_key:
                char.db.claw_agent_id = agent_id_str
                return char

        char, errs = account.create_character(
            key=want_key,
            typeclass="typeclasses.characters.Character",
        )
        if errs:
            logger.error(
                "create_character errors for Agent %s: %s",
                agent.name,
                errs,
            )
        if char:
            char.db.claw_agent_id = agent_id_str
            return char

        # Only adopt the sole character when creation failed because slots are full (or no
        # slot limit is configured but we still have chars — treat as same case). If
        # create failed for another reason (bad home/start location, typeclass error),
        # adopting would mis-bind the wrong object.
        slots_left = account.get_available_character_slots()
        slot_blocked = slots_left is not None and slots_left <= 0
        if slot_blocked and len(chars) == 1:
            only = chars[0]
            only.db.claw_agent_id = agent_id_str
            logger.info(
                "Adopted existing character %s for Agent %s (no free slot / key mismatch)",
                only.key,
                agent.name,
            )
            return only

        return None


class CmdAgentStatus(Command):
    """
    Show the current Agent profile (Agent accounts only).

    Usage:
        agent_status
    """

    key = "agent_status"
    aliases = ["agents"]
    locks = "cmd:all()"
    help_category = "Agent"

    def func(self):
        """Print Agent status block."""
        from world.agent_auth.models import Agent

        caller = self.caller

        if not caller.db.is_agent:
            caller.msg("You are not an Agent.")
            return
        
        agent_id = caller.db.agent_id
        if not agent_id:
            caller.msg("Agent ID not found.")
            return
        
        try:
            from uuid import UUID
            agent = Agent.objects.get(id=UUID(agent_id))
            
            status_msg = f"""
|wAgent Status|n
|wName:|n {agent.name}
|wID:|n {agent.id}
|wStatus:|n {agent.claim_status}
|wLevel:|n {agent.level}
|wExperience:|n {agent.experience}
|wTwitter:|n @{agent.twitter_handle or 'N/A'}
|wCreated:|n {agent.created_at}
|wLast Active:|n {agent.last_active_at or 'Never'}
"""
            caller.msg(status_msg)
            
        except Agent.DoesNotExist:
            caller.msg("Agent not found in database.")


class CmdAgentList(Command):
    """
    List recent Agents (developer permission).

    Usage:
        agent_list
    """

    key = "agent_list"
    aliases = ["list_agents"]
    locks = "cmd:pperm(Developer)"
    help_category = "Admin"

    def func(self):
        """Print last 20 agents."""
        from world.agent_auth.models import Agent
        
        agents = Agent.objects.all().order_by('-created_at')[:20]
        
        if not agents:
            self.caller.msg("No agents found.")
            return
        
        msg = "|wAgent List (last 20):|n\n"
        msg += "|wName|n |wStatus|n |wTwitter|n |wCreated|n\n"
        msg += "-" * 50 + "\n"
        
        for agent in agents:
            status_color = "|g" if agent.is_claimed else "|y"
            twitter = f"@{agent.twitter_handle}" if agent.twitter_handle else "N/A"
            msg += f"{agent.name[:20]:<20} {status_color}{agent.claim_status}|n {twitter:<15} {agent.created_at.strftime('%Y-%m-%d')}\n"
        
        self.caller.msg(msg)
