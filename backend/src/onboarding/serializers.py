"""Django REST Framework serializers for Bienvenue à La Suite onboarding."""

from typing import Any, Dict, List, Optional
from rest_framework import serializers
from src.onboarding.models import (
    Template,
    Agent,
    AgentComment,
    Service,
    TodoItem,
    AgentTodoStatus,
    Colleague,
    Document,
    Training,
)


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for administrative department / service."""

    class Meta:
        model = Service
        fields = [
            "id",
            "name",
            "initials",
            "color",
            "logo_url",
            "manager_name",
            "manager_email",
        ]


class AgentCommentSerializer(serializers.ModelSerializer):
    """Serializer for HR / Manager notes on an agent."""

    class Meta:
        model = AgentComment
        fields = ["id", "date", "text"]


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
    service_name = serializers.CharField(source="service.name", read_only=True, default=None)
    service_initials = serializers.CharField(source="service.initials", read_only=True, default=None)
    service_color = serializers.CharField(source="service.color", read_only=True, default=None)
    service_logo_url = serializers.CharField(source="service.logo_url", read_only=True, default=None)
    manager_name = serializers.CharField(source="service.manager_name", read_only=True, default=None)
    manager_email = serializers.CharField(source="service.manager_email", read_only=True, default=None)

    class Meta:
        model = Agent
        fields = [
            "id",
            "email",
            "name",
            "job_title",
            "phone",
            "arrival_date",
            "departure_date",
            "service_name",
            "service_initials",
            "service_color",
            "service_logo_url",
            "manager_name",
            "manager_email",
            "role",
            "signature_accepted",
            "created_at",
            "progress",
        ]

    def get_progress(self, obj: Agent) -> Dict[str, int]:
        """Compute total tasks, completed tasks, and percentage."""
        if not obj.assigned_template and not obj.custom_todo_items.exists():
            return {"total_tasks": 0, "completed_tasks": 0, "percentage": 0}

        all_todos = obj.get_all_todos()
        total = all_todos.count()
        if total == 0:
            return {"total_tasks": 0, "completed_tasks": 0, "percentage": 100}

        completed = AgentTodoStatus.objects.filter(
            agent=obj,
            todo_item__in=all_todos,
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
    service_name = serializers.SerializerMethodField()

    class Meta:
        model = TodoItem
        fields = [
            "id",
            "order",
            "label",
            "description",
            "service_link",
            "service_name",
            "doc_url",
            "validation_type",
            "done",
            "done_at",
            "is_locked",
        ]

    def get_service_name(self, obj: TodoItem) -> str:
        """Resolve human-readable Suite service name from link or label."""
        mapping = [
            ("francetransfert", "France Transfert"),
            ("fichiers", "Fichiers"),
            ("tchap", "Tchap"),
            ("webinaire", "Webinaire"),
            ("visio", "Visio"),
            ("grist", "Grist"),
            ("docs", "Docs"),
        ]
        link = (obj.service_link or "").lower()
        for key, name in mapping:
            if key in link:
                return name

        label = (obj.label or "").lower()
        for key, name in mapping:
            if key in label:
                return name

        return "Service"

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
        if not agent:
            return False

        if "_completed_todo_ids" not in self.context:
            status_map = self._get_status_map()
            self.context["_completed_todo_ids"] = {
                todo_id for todo_id, s in status_map.items() if s.done
            }
        completed_ids = self.context["_completed_todo_ids"]

        if "_template_todos" not in self.context:
            self.context["_template_todos"] = list(
                agent.get_all_todos().values("id", "order")
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
        todos = obj.get_all_todos()
        return TodoItemWithStatusSerializer(
            todos,
            many=True,
            context={"agent": obj},
        ).data

    def get_colleagues(self, obj: Agent) -> List[Dict[str, Any]]:
        """Serialize dynamic contacts (colleagues_to_meet + service peers) and template colleagues."""
        colleagues_list = []
        seen_ids = set()

        for agent in obj.colleagues_to_meet.select_related("service").all():
            if agent.id not in seen_ids:
                seen_ids.add(agent.id)
                colleagues_list.append({
                    "id": str(agent.id),
                    "name": agent.name,
                    "role": agent.job_title or "Colleague",
                    "department": agent.service.name if agent.service else "General",
                    "tchap_link": f"https://www.tchap.gouv.fr/#/user/@{agent.email}:agent.finances.gouv.fr",
                    "team": bool(obj.service and agent.service_id == obj.service_id),
                })

        if obj.service:
            peers = obj.service.members.exclude(id=obj.id).select_related("service").all()
            for peer in peers:
                if peer.id not in seen_ids:
                    seen_ids.add(peer.id)
                    colleagues_list.append({
                        "id": str(peer.id),
                        "name": peer.name,
                        "role": peer.job_title or "Colleague",
                        "department": obj.service.name,
                        "tchap_link": f"https://www.tchap.gouv.fr/#/user/@{peer.email}:agent.finances.gouv.fr",
                        "team": True,
                    })

        tc_qs = obj.assigned_template.colleagues.all() if obj.assigned_template else Colleague.objects.none()
        if not tc_qs.exists():
            core_tpl = Template.objects.filter(grist_row_id="demo-template-core").first()
            if core_tpl:
                tc_qs = core_tpl.colleagues.all()

        for tc in tc_qs:
            if tc.id not in seen_ids:
                seen_ids.add(tc.id)
                colleagues_list.append({
                    "id": str(tc.id),
                    "name": tc.name,
                    "role": "Contact",
                    "department": "General",
                    "tchap_link": tc.tchap_link,
                    "team": False,
                })

        return colleagues_list

    def get_documents(self, obj: Agent) -> List[Dict[str, Any]]:
        """Serialize template documents with fallback to core documents."""
        docs = obj.assigned_template.documents.all() if obj.assigned_template else Document.objects.none()
        if not docs.exists():
            core_tpl = Template.objects.filter(grist_row_id="demo-template-core").first()
            if core_tpl:
                docs = core_tpl.documents.all()
        return DocumentSerializer(docs, many=True).data

    def get_trainings(self, obj: Agent) -> List[Dict[str, Any]]:
        """Serialize template trainings with fallback to core trainings."""
        trainings = obj.assigned_template.trainings.all() if obj.assigned_template else Training.objects.none()
        if not trainings.exists():
            core_tpl = Template.objects.filter(grist_row_id="demo-template-core").first()
            if core_tpl:
                trainings = core_tpl.trainings.all()
        return TrainingSerializer(trainings, many=True).data


class ManagerAgentOverviewSerializer(serializers.ModelSerializer):
    """Serializer for GET /api/manager/overview/ listing agent progress."""

    template_name = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    current_step = serializers.SerializerMethodField()
    service_name = serializers.CharField(source="service.name", read_only=True, default=None)
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Agent
        fields = [
            "id",
            "name",
            "email",
            "job_title",
            "phone",
            "arrival_date",
            "service_name",
            "template_name",
            "progress_percentage",
            "signature_accepted",
            "current_step",
            "comments",
            "created_at",
        ]

    def get_comments(self, obj: Agent) -> List[Dict[str, Any]]:
        """Serialize comments attached to the agent."""
        return AgentCommentSerializer(obj.comments.all(), many=True).data

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

        uncompleted = obj.get_all_todos().exclude(
            id__in=AgentTodoStatus.objects.filter(agent=obj, done=True).values_list("todo_item_id", flat=True)
        ).order_by("order").first()

        if uncompleted:
            return uncompleted.label
        return "All tasks completed"
