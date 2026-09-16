"""Django REST Framework serializers for Bienvenue à La Suite onboarding."""

from typing import Any, Dict, List, Optional
from rest_framework import serializers
from src.onboarding.models import (
    Template,
    Agent,
    TodoItem,
    AgentTodoStatus,
    Colleague,
    Document,
    Training,
)


class TemplateSerializer(serializers.ModelSerializer):
    """Serializer for Template master metadata."""

    class Meta:
        model = Template
        fields = [
            "id",
            "name",
            "email_signature",
            "created_at",
            "updated_at",
        ]


class ColleagueSerializer(serializers.ModelSerializer):
    """Serializer for team colleague cards."""

    class Meta:
        model = Colleague
        fields = [
            "id",
            "name",
            "tchap_link",
        ]


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for official documents and guides."""

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "url",
            "format",
        ]


class TrainingSerializer(serializers.ModelSerializer):
    """Serializer for video tutorials and trainings."""

    class Meta:
        model = Training
        fields = [
            "id",
            "title",
            "video_url",
            "duration_minutes",
        ]


class AgentSerializer(serializers.ModelSerializer):
    """Serializer for Agent user profile with computed progress."""

    progress = serializers.SerializerMethodField()

    class Meta:
        model = Agent
        fields = [
            "id",
            "email",
            "name",
            "role",
            "signature_accepted",
            "created_at",
            "progress",
        ]

    def get_progress(self, obj: Agent) -> Dict[str, int]:
        """Compute total tasks, completed tasks, and percentage."""
        if not obj.assigned_template:
            return {"total_tasks": 0, "completed_tasks": 0, "percentage": 0}

        total = obj.assigned_template.todo_items.count()
        if total == 0:
            return {"total_tasks": 0, "completed_tasks": 0, "percentage": 100}

        completed = AgentTodoStatus.objects.filter(
            agent=obj,
            todo_item__template=obj.assigned_template,
            done=True,
        ).count()

        percentage = int((completed / total) * 100)
        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "percentage": percentage,
        }


class TodoItemWithStatusSerializer(serializers.ModelSerializer):
    """Serializer for a task item combined with agent completion and lock status."""

    done = serializers.SerializerMethodField()
    done_at = serializers.SerializerMethodField()
    is_locked = serializers.SerializerMethodField()

    class Meta:
        model = TodoItem
        fields = [
            "id",
            "order",
            "label",
            "service_link",
            "validation_type",
            "done",
            "done_at",
            "is_locked",
        ]

    def _get_agent(self) -> Optional[Agent]:
        """Resolve current agent from serializer context."""
        return self.context.get("agent")

    def _get_status_map(self) -> Dict[Any, AgentTodoStatus]:
        """Fetch and cache map of todo_item_id -> AgentTodoStatus for current agent."""
        agent = self._get_agent()
        if not agent:
            return {}
        if "_status_map" not in self.context:
            statuses = AgentTodoStatus.objects.filter(agent=agent)
            self.context["_status_map"] = {s.todo_item_id: s for s in statuses}
        return self.context["_status_map"]

    def _get_status_record(self, obj: TodoItem) -> Optional[AgentTodoStatus]:
        """Fetch status record from cached context map."""
        return self._get_status_map().get(obj.id)

    def get_done(self, obj: TodoItem) -> bool:
        """Return task completion boolean."""
        status = self._get_status_record(obj)
        return status.done if status else False

    def get_done_at(self, obj: TodoItem) -> Optional[str]:
        """Return ISO timestamp when completed."""
        status = self._get_status_record(obj)
        return status.done_at.isoformat() if status and status.done_at else None

    def get_is_locked(self, obj: TodoItem) -> bool:
        """Determine sequential lock state based on prior task completions."""
        agent = self._get_agent()
        if not agent or not agent.assigned_template:
            return False

        if "_completed_todo_ids" not in self.context:
            status_map = self._get_status_map()
            self.context["_completed_todo_ids"] = {
                todo_id for todo_id, s in status_map.items() if s.done
            }
        completed_ids = self.context["_completed_todo_ids"]

        if "_template_todos" not in self.context:
            self.context["_template_todos"] = list(
                TodoItem.objects.filter(template=agent.assigned_template).values("id", "order")
            )
        template_todos = self.context["_template_todos"]

        return any(
            t["order"] < obj.order and t["id"] not in completed_ids
            for t in template_todos
        )


class OnboardingBundleSerializer(serializers.Serializer):
    """Composite bundle serializer powering GET /api/onboarding/me/."""

    agent = serializers.SerializerMethodField()
    template = serializers.SerializerMethodField()
    todos = serializers.SerializerMethodField()
    colleagues = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    trainings = serializers.SerializerMethodField()

    def get_agent(self, obj: Agent) -> Dict[str, Any]:
        """Serialize current agent profile."""
        return AgentSerializer(obj).data

    def get_template(self, obj: Agent) -> Optional[Dict[str, Any]]:
        """Serialize assigned template metadata."""
        if not obj.assigned_template:
            return None
        return TemplateSerializer(obj.assigned_template).data

    def get_todos(self, obj: Agent) -> List[Dict[str, Any]]:
        """Serialize sequential tasks with completion statuses."""
        if not obj.assigned_template:
            return []
        todos = obj.assigned_template.todo_items.all().order_by("order")
        return TodoItemWithStatusSerializer(
            todos,
            many=True,
            context={"agent": obj},
        ).data

    def get_colleagues(self, obj: Agent) -> List[Dict[str, Any]]:
        """Serialize template colleagues."""
        if not obj.assigned_template:
            return []
        return ColleagueSerializer(obj.assigned_template.colleagues.all(), many=True).data

    def get_documents(self, obj: Agent) -> List[Dict[str, Any]]:
        """Serialize template documents."""
        if not obj.assigned_template:
            return []
        return DocumentSerializer(obj.assigned_template.documents.all(), many=True).data

    def get_trainings(self, obj: Agent) -> List[Dict[str, Any]]:
        """Serialize template trainings."""
        if not obj.assigned_template:
            return []
        return TrainingSerializer(obj.assigned_template.trainings.all(), many=True).data


class ManagerAgentOverviewSerializer(serializers.ModelSerializer):
    """Serializer for GET /api/manager/overview/ listing agent progress."""

    template_name = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    current_step = serializers.SerializerMethodField()

    class Meta:
        model = Agent
        fields = [
            "id",
            "name",
            "email",
            "template_name",
            "progress_percentage",
            "signature_accepted",
            "current_step",
            "created_at",
        ]

    def get_template_name(self, obj: Agent) -> Optional[str]:
        """Return assigned template name."""
        return obj.assigned_template.name if obj.assigned_template else None

    def get_progress_percentage(self, obj: Agent) -> int:
        """Calculate progress percentage."""
        return AgentSerializer(obj).get_progress(obj)["percentage"]

    def get_current_step(self, obj: Agent) -> str:
        """Find label of first uncompleted task or Done."""
        if not obj.assigned_template:
            return "No template assigned"

        uncompleted = obj.assigned_template.todo_items.exclude(
            id__in=AgentTodoStatus.objects.filter(agent=obj, done=True).values_list("todo_item_id", flat=True)
        ).order_by("order").first()

        if uncompleted:
            return uncompleted.label
        return "All tasks completed"
