"""Management command to reset agent onboarding tasks and signature status."""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from src.onboarding.models import Agent, AgentTodoStatus, RoleChoices


class Command(BaseCommand):
    """Resets onboarding checklist progress and signature confirmation."""

    help = "Resets all onboarding tasks and signature status to enable testing from scratch."

    def add_arguments(self, parser):
        """Register CLI flags for targeting specific agents or all."""
        parser.add_argument(
            "--agent",
            type=str,
            help="Email address of a specific agent to reset. If omitted, all new agents are reset.",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Reset all agents including managers.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """Execute reset operations on target agents."""
        agent_email = options.get("agent")
        reset_all = options.get("all", False)

        if agent_email:
            agents = Agent.objects.filter(email=agent_email.strip().lower())
            if not agents.exists():
                raise CommandError(f"Agent with email '{agent_email}' not found.")
        elif reset_all:
            agents = Agent.objects.all()
        else:
            agents = Agent.objects.filter(role=RoleChoices.NEW_AGENT)

        if not agents.exists():
            self.stdout.write(self.style.WARNING("No matching agents found to reset."))
            return

        total_tasks_reset = 0
        for agent in agents:
            agent.signature_accepted = False
            agent.save(update_fields=["signature_accepted"])

            # Reset existing statuses to done=False
            updated = AgentTodoStatus.objects.filter(agent=agent).update(
                done=False,
                done_at=None,
            )
            total_tasks_reset += updated

            # Ensure all tasks have a status row
            all_todos = agent.get_all_todos()
            for todo in all_todos:
                _, created = AgentTodoStatus.objects.get_or_create(
                    agent=agent,
                    todo_item=todo,
                    defaults={"done": False, "done_at": None},
                )
                if created:
                    total_tasks_reset += 1

            self.stdout.write(
                f" - Reset {agent.email} (signature_accepted=False)"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully reset onboarding progress for {agents.count()} agent(s) ({total_tasks_reset} task statuses)."
            )
        )
