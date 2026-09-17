"""Database models for Bienvenue à La Suite onboarding."""

import uuid
from django.db import models
from django.db.models.functions import Lower


class RoleChoices(models.TextChoices):
    """User access roles."""

    MANAGER = "manager", "Manager"
    NEW_AGENT = "new_agent", "New Agent"


class ValidationTypeChoices(models.TextChoices):
    """Task validation mechanisms."""

    API_CHECK = "API_CHECK", "API Check (e.g. Fichiers)"
    MANUAL = "MANUAL", "Manual (Honor System)"
    GRIST = "GRIST", "Grist Task"
    SIGNATURE = "SIGNATURE", "Signature Validation"


class DocumentFormatChoices(models.TextChoices):
    """Supported document badge formats."""

    PDF = "pdf", "PDF Document"
    DOC = "doc", "Word / Text Document"
    LINK = "link", "Web Link"


class Template(models.Model):
    """Master onboarding template synced from Grist."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text="Descriptive template name.")
    grist_row_id = models.CharField(
        max_length=128,
        unique=True,
        help_text="Source row ID in Grist for webhook upsert.",
    )
    email_signature = models.TextField(
        blank=True,
        default="",
        help_text="Standardized email signature template.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "templates"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.grist_row_id})"


class Agent(models.Model):
    """Civil servant user profile (newcomer or manager)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        max_length=255,
        unique=True,
        help_text="Institutional email address, primary identity.",
    )
    name = models.CharField(max_length=255, help_text="Full display name.")
    role = models.CharField(
        max_length=32,
        choices=RoleChoices.choices,
        default=RoleChoices.NEW_AGENT,
    )
    assigned_template = models.ForeignKey(
        Template,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="agents",
        help_text="Assigned onboarding template.",
    )
    signature_accepted = models.BooleanField(
        default=False,
        help_text="Whether the agent has validated their email signature.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "agents"
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                name="idx_agents_email_lower",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} <{self.email}> ({self.role})"


class TodoItem(models.Model):
    """Individual checklist item inside a template."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name="todo_items",
    )
    label = models.CharField(max_length=512, help_text="Task action label.")
    description = models.TextField(
        blank=True,
        default="",
        help_text="Detailed instructions or explanation.",
    )
    service_link = models.URLField(
        max_length=1024,
        blank=True,
        null=True,
        help_text="Deep link to a relevant Suite service.",
    )
    doc_url = models.URLField(
        max_length=1024,
        blank=True,
        null=True,
        help_text="Documentation guide link.",
    )
    order = models.IntegerField(
        default=0,
        help_text="Sort order enforcing sequential unlocking.",
    )
    validation_type = models.CharField(
        max_length=32,
        choices=ValidationTypeChoices.choices,
        default=ValidationTypeChoices.MANUAL,
    )
    grist_row_id = models.CharField(
        max_length=128,
        unique=True,
        null=True,
        blank=True,
        help_text="Grist row ID for deterministic in-place sync.",
    )

    class Meta:
        db_table = "todo_items"
        ordering = ["order"]
        indexes = [
            models.Index(
                fields=["template", "order"],
                name="idx_todo_items_template_order",
            ),
        ]

    def __str__(self) -> str:
        return f"[{self.order}] {self.label} ({self.validation_type})"


class AgentTodoStatus(models.Model):
    """Completion status of an agent for a specific task."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name="todo_statuses",
    )
    todo_item = models.ForeignKey(
        TodoItem,
        on_delete=models.CASCADE,
        related_name="agent_statuses",
    )
    done = models.BooleanField(default=False)
    done_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "agent_todo_statuses"
        constraints = [
            models.UniqueConstraint(
                fields=["agent", "todo_item"],
                name="unique_agent_todo_status",
            )
        ]

    def __str__(self) -> str:
        status_str = "Done" if self.done else "Pending"
        return f"{self.agent.email} - {self.todo_item.label}: {status_str}"


class Colleague(models.Model):
    """Key contact or mentor in the department."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name="colleagues",
    )
    name = models.CharField(max_length=255, help_text="Full name and role.")
    tchap_link = models.URLField(
        max_length=1024,
        help_text="Direct link to start discussion on Tchap.",
    )
    grist_row_id = models.CharField(
        max_length=128,
        unique=True,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "colleagues"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Document(models.Model):
    """Official documentation or administrative guide."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=1024)
    format = models.CharField(
        max_length=32,
        choices=DocumentFormatChoices.choices,
        default=DocumentFormatChoices.PDF,
    )
    grist_row_id = models.CharField(
        max_length=128,
        unique=True,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "documents"
        ordering = ["title"]

    def __str__(self) -> str:
        return f"{self.title} ({self.format})"


class Training(models.Model):
    """Curated tutorial or training video."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name="trainings",
    )
    title = models.CharField(max_length=255)
    video_url = models.URLField(max_length=1024)
    duration_minutes = models.IntegerField(null=True, blank=True)
    grist_row_id = models.CharField(
        max_length=128,
        unique=True,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "trainings"
        ordering = ["title"]

    def __str__(self) -> str:
        duration_str = f" ({self.duration_minutes} min)" if self.duration_minutes else ""
        return f"{self.title}{duration_str}"
