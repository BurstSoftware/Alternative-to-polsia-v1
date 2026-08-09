from pathlib import Path

content = r'''"""
project-md.py

Polsia-style Autonomous Company Operating System
================================================

This file compiles the previously defined condition logic into one Python
project scaffold.

Important:
- This is an implementation-oriented reconstruction inspired by publicly
  described Polsia concepts.
- It is NOT Polsia's proprietary production source code.
- The design models:
    Goal -> Observe -> Gap -> Hypothesis -> Action -> Result -> Measurement
    -> Learning -> New State -> New Priority -> New Action
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import time


# ============================================================
# 1. ENUMS / CORE STATES
# ============================================================

class CompanyStatus(Enum):
    ACTIVE = auto()
    PAUSED = auto()
    STOPPED = auto()


class TriggerType(Enum):
    USER_REQUEST = auto()
    CRITICAL_EVENT = auto()
    EXTERNAL_EVENT = auto()
    SCHEDULE = auto()
    TASK_CONTINUATION = auto()
    EXPERIMENT_RESULT = auto()
    METRIC_CHANGE = auto()
    PERIODIC_REVIEW = auto()


class Domain(Enum):
    ORCHESTRATOR = auto()
    STRATEGY = auto()
    RESEARCH = auto()
    SOCIAL = auto()
    OUTREACH = auto()
    SUPPORT = auto()
    ADS = auto()
    ENGINEERING = auto()
    FINANCE = auto()
    GROWTH = auto()


class GoalStatus(Enum):
    ON_TARGET = auto()
    AT_RISK = auto()
    OFF_TARGET = auto()
    CRITICAL = auto()


class TaskStatus(Enum):
    PENDING = auto()
    READY = auto()
    RUNNING = auto()
    BLOCKED = auto()
    AWAITING_EXTERNAL_EVENT = auto()
    AWAITING_HUMAN = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


class ResultStatus(Enum):
    SUCCESS = auto()
    PARTIAL_SUCCESS = auto()
    RETRYABLE_FAILURE = auto()
    PERMANENT_FAILURE = auto()
    BLOCKED = auto()
    AWAITING_EXTERNAL_EVENT = auto()
    AWAITING_HUMAN = auto()
    CANCELLED = auto()


class Bottleneck(Enum):
    ACQUISITION = auto()
    CONVERSION = auto()
    ACTIVATION = auto()
    RETENTION = auto()
    MONETIZATION = auto()
    OPERATIONS = auto()
    EXPANSION = auto()
    NONE = auto()


class ActionType(Enum):
    SEARCH = auto()
    SEND_EMAIL = auto()
    SOCIAL_POST = auto()
    CREATE_AD_CAMPAIGN = auto()
    CODE_CHANGE = auto()
    DEPLOY = auto()
    QUERY_FINANCE = auto()
    CUSTOMER_SUPPORT = auto()
    UPDATE_STATE = auto()
    LLM_ONLY = auto()


# ============================================================
# 2. DATA MODELS
# ============================================================

@dataclass
class Metric:
    name: str
    value: float
    target: Optional[float] = None
    direction: str = "increase"  # "increase" or "decrease"


@dataclass
class Goal:
    id: str
    name: str
    metric_name: str
    target: float
    direction: str = "increase"
    warning_threshold: float = 0.0
    critical_threshold: float = 0.0
    status: GoalStatus = GoalStatus.OFF_TARGET


@dataclass
class Event:
    id: str
    type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    priority: int = 50


@dataclass
class Experiment:
    id: str
    hypothesis: str
    baseline: float
    target: float
    variant: str
    started_at: datetime = field(default_factory=datetime.utcnow)
    sample_size: int = 0
    result: Optional[Dict[str, Any]] = None
    complete: bool = False


@dataclass
class MemoryItem:
    situation: str
    action: str
    result: str
    expected: Optional[str] = None
    actual: Optional[str] = None
    lesson: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Action:
    id: str
    name: str
    action_type: ActionType
    domain: Domain
    description: str

    impact: float = 1.0
    confidence: float = 1.0
    urgency: float = 1.0
    alignment: float = 1.0
    reversibility: float = 1.0

    cost: float = 1.0
    risk: float = 1.0
    execution_time: float = 1.0

    required_permission: Optional[str] = None
    required_integration: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)

    estimated_cost_dollars: float = 0.0
    priority: int = 50

    @property
    def score(self) -> float:
        numerator = (
            self.impact
            * self.confidence
            * self.urgency
            * self.alignment
            * self.reversibility
        )

        denominator = (
            max(self.cost, 1.0)
            * max(self.risk, 1.0)
            * max(self.execution_time, 1.0)
        )

        return numerator / denominator


@dataclass
class ExecutionResult:
    status: ResultStatus
    output: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    error: Optional[str] = None
    business_success: Optional[bool] = None
    execution_success: Optional[bool] = None


@dataclass
class Task:
    id: str
    objective: str
    domain: Domain
    action: Optional[Action] = None
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    priority: int = 50
    memory: List[ExecutionResult] = field(default_factory=list)


@dataclass
class CompanyState:
    company_id: str
    status: CompanyStatus = CompanyStatus.ACTIVE
    sandbox_mode: bool = True

    mission: str = ""
    goals: List[Goal] = field(default_factory=list)
    strategy: List[str] = field(default_factory=list)
    products: List[Dict[str, Any]] = field(default_factory=list)
    customers: List[Dict[str, Any]] = field(default_factory=list)
    leads: List[Dict[str, Any]] = field(default_factory=list)

    metrics: Dict[str, float] = field(default_factory=dict)
    budgets: Dict[str, float] = field(default_factory=dict)
    budget_spent: Dict[str, float] = field(default_factory=dict)

    permissions: Dict[str, bool] = field(default_factory=dict)
    integrations: Dict[str, bool] = field(default_factory=dict)

    active_tasks: List[Task] = field(default_factory=list)
    blocked_tasks: List[Task] = field(default_factory=list)
    completed_tasks: List[Task] = field(default_factory=list)

    experiments: List[Experiment] = field(default_factory=list)
    events: List[Event] = field(default_factory=list)
    memory: List[MemoryItem] = field(default_factory=list)


# ============================================================
# 3. PRIORITY / INTERRUPT LOGIC
# ============================================================

PRIORITY = {
    "SECURITY": 100,
    "OUTAGE": 95,
    "PAYMENT_FAILURE": 90,
    "CUSTOMER_CRITICAL": 85,
    "REVENUE_OPPORTUNITY": 70,
    "ACTIVE_EXPERIMENT": 60,
    "SCHEDULED_TASK": 50,
    "CONTENT": 30,
    "MAINTENANCE": 20,
}


def should_interrupt(active_task: Optional[Task], incoming_priority: int) -> bool:
    if active_task is None:
        return True
    return incoming_priority > active_task.priority


# ============================================================
# 4. TRIGGER DETECTION
# ============================================================

class TriggerDetector:
    def detect(self, state: CompanyState) -> Optional[TriggerType]:
        if state.status != CompanyStatus.ACTIVE:
            return None

        if self.user_message_pending(state):
            return TriggerType.USER_REQUEST

        if self.critical_event_pending(state):
            return TriggerType.CRITICAL_EVENT

        if self.external_event_pending(state):
            return TriggerType.EXTERNAL_EVENT

        if self.scheduled_agent_due(state):
            return TriggerType.SCHEDULE

        if self.unfinished_task_ready(state):
            return TriggerType.TASK_CONTINUATION

        if self.experiment_completed(state):
            return TriggerType.EXPERIMENT_RESULT

        if self.metric_threshold_crossed(state):
            return TriggerType.METRIC_CHANGE

        return TriggerType.PERIODIC_REVIEW

    def user_message_pending(self, state: CompanyState) -> bool:
        return any(event.type == "user_request" for event in state.events)

    def critical_event_pending(self, state: CompanyState) -> bool:
        critical_types = {"security", "outage", "payment_failure", "customer_critical"}
        return any(event.type in critical_types for event in state.events)

    def external_event_pending(self, state: CompanyState) -> bool:
        external_types = {
            "customer_message",
            "new_lead",
            "campaign_finished",
            "competitor_change",
            "deployment_failure",
        }
        return any(event.type in external_types for event in state.events)

    def scheduled_agent_due(self, state: CompanyState) -> bool:
        # Replace with real scheduler logic.
        return False

    def unfinished_task_ready(self, state: CompanyState) -> bool:
        return any(task.status == TaskStatus.READY for task in state.active_tasks)

    def experiment_completed(self, state: CompanyState) -> bool:
        return any(exp.complete for exp in state.experiments)

    def metric_threshold_crossed(self, state: CompanyState) -> bool:
        # Replace with metric-change event tracking.
        return False


# ============================================================
# 5. EVENT CLASSIFICATION
# ============================================================

def classify_event(event: Event) -> Domain:
    mapping = {
        "customer_message": Domain.SUPPORT,
        "customer_critical": Domain.SUPPORT,
        "new_lead": Domain.OUTREACH,
        "conversion_drop": Domain.GROWTH,
        "bug": Domain.ENGINEERING,
        "deployment_failure": Domain.ENGINEERING,
        "outage": Domain.ENGINEERING,
        "security": Domain.ENGINEERING,
        "campaign_finished": Domain.ADS,
        "cash_warning": Domain.FINANCE,
        "payment_failure": Domain.FINANCE,
        "competitor_change": Domain.RESEARCH,
        "strategy_review": Domain.STRATEGY,
    }
    return mapping.get(event.type, Domain.ORCHESTRATOR)


# ============================================================
# 6. GOAL EVALUATION
# ============================================================

def evaluate_goal(goal: Goal, state: CompanyState) -> GoalStatus:
    actual = state.metrics.get(goal.metric_name, 0.0)
    target = goal.target

    if goal.direction == "increase":
        if actual >= target:
            return GoalStatus.ON_TARGET

        gap = target - actual

    elif goal.direction == "decrease":
        if actual <= target:
            return GoalStatus.ON_TARGET

        gap = actual - target

    else:
        raise ValueError(f"Unknown goal direction: {goal.direction}")

    if goal.critical_threshold and gap >= goal.critical_threshold:
        return GoalStatus.CRITICAL

    if goal.warning_threshold and gap <= goal.warning_threshold:
        return GoalStatus.AT_RISK

    return GoalStatus.OFF_TARGET


def evaluate_all_goals(state: CompanyState) -> List[Goal]:
    for goal in state.goals:
        goal.status = evaluate_goal(goal, state)
    return state.goals


# ============================================================
# 7. BOTTLENECK DETECTION
# ============================================================

def detect_bottleneck(state: CompanyState) -> Bottleneck:
    traffic = state.metrics.get("traffic", 0)
    minimum_traffic = state.metrics.get("minimum_traffic", 1000)

    signup_conversion = state.metrics.get("signup_conversion", 0)
    target_conversion = state.metrics.get("target_conversion", 0.05)

    activation_rate = state.metrics.get("activation_rate", 0)
    target_activation = state.metrics.get("target_activation", 0.4)

    retention = state.metrics.get("retention", 0)
    target_retention = state.metrics.get("target_retention", 0.6)

    revenue_per_user = state.metrics.get("revenue_per_user", 0)
    target_arpu = state.metrics.get("target_arpu", 20)

    support_backlog = state.metrics.get("support_backlog", 0)
    support_threshold = state.metrics.get("support_backlog_threshold", 50)

    if traffic < minimum_traffic:
        return Bottleneck.ACQUISITION

    if signup_conversion < target_conversion:
        return Bottleneck.CONVERSION

    if activation_rate < target_activation:
        return Bottleneck.ACTIVATION

    if retention < target_retention:
        return Bottleneck.RETENTION

    if revenue_per_user < target_arpu:
        return Bottleneck.MONETIZATION

    if support_backlog > support_threshold:
        return Bottleneck.OPERATIONS

    return Bottleneck.EXPANSION


# ============================================================
# 8. CANDIDATE ACTION GENERATION
# ============================================================

def generate_actions(
    state: CompanyState,
    bottleneck: Bottleneck,
    goals: List[Goal],
) -> List[Action]:

    actions: List[Action] = []

    if bottleneck == Bottleneck.ACQUISITION:
        actions.extend([
            Action(
                id="acq_social",
                name="Publish Social Content",
                action_type=ActionType.SOCIAL_POST,
                domain=Domain.SOCIAL,
                description="Create and publish content to increase qualified traffic.",
                impact=5,
                confidence=3,
                urgency=3,
                alignment=4,
                reversibility=5,
                cost=1,
                risk=1,
                execution_time=1,
                required_permission="social_posting",
                required_integration="social",
            ),
            Action(
                id="acq_outreach",
                name="Run Lead Outreach",
                action_type=ActionType.SEND_EMAIL,
                domain=Domain.OUTREACH,
                description="Generate prospects and start targeted outbound outreach.",
                impact=5,
                confidence=4,
                urgency=4,
                alignment=5,
                reversibility=3,
                cost=2,
                risk=2,
                execution_time=2,
                required_permission="send_email",
                required_integration="email",
            ),
        ])

    elif bottleneck == Bottleneck.CONVERSION:
        actions.append(
            Action(
                id="conv_landing",
                name="Improve Landing Page",
                action_type=ActionType.CODE_CHANGE,
                domain=Domain.ENGINEERING,
                description="Improve landing-page clarity, offer presentation, and conversion flow.",
                impact=5,
                confidence=4,
                urgency=4,
                alignment=5,
                reversibility=4,
                cost=2,
                risk=2,
                execution_time=2,
                required_permission="code_changes",
                required_integration="code_repository",
            )
        )

    elif bottleneck == Bottleneck.ACTIVATION:
        actions.append(
            Action(
                id="activation_onboarding",
                name="Improve Onboarding",
                action_type=ActionType.CODE_CHANGE,
                domain=Domain.ENGINEERING,
                description="Reduce friction between signup and first successful user outcome.",
                impact=5,
                confidence=4,
                urgency=4,
                alignment=5,
                reversibility=4,
                cost=2,
                risk=2,
                execution_time=3,
                required_permission="code_changes",
                required_integration="code_repository",
            )
        )

    elif bottleneck == Bottleneck.RETENTION:
        actions.extend([
            Action(
                id="ret_support",
                name="Analyze Support Friction",
                action_type=ActionType.CUSTOMER_SUPPORT,
                domain=Domain.SUPPORT,
                description="Analyze support interactions to discover recurring churn drivers.",
                impact=4,
                confidence=4,
                urgency=4,
                alignment=5,
                reversibility=5,
                cost=1,
                risk=1,
                execution_time=2,
            ),
            Action(
                id="ret_product",
                name="Fix Retention Issue",
                action_type=ActionType.CODE_CHANGE,
                domain=Domain.ENGINEERING,
                description="Implement product changes addressing the highest-confidence retention problem.",
                impact=5,
                confidence=3,
                urgency=4,
                alignment=5,
                reversibility=3,
                cost=3,
                risk=3,
                execution_time=4,
                required_permission="code_changes",
                required_integration="code_repository",
            ),
        ])

    elif bottleneck == Bottleneck.MONETIZATION:
        actions.append(
            Action(
                id="monetization_analysis",
                name="Analyze Monetization",
                action_type=ActionType.QUERY_FINANCE,
                domain=Domain.FINANCE,
                description="Analyze pricing, ARPU, plans, payment behavior, and revenue opportunities.",
                impact=4,
                confidence=4,
                urgency=3,
                alignment=5,
                reversibility=5,
                cost=1,
                risk=1,
                execution_time=2,
                required_permission="finance_read",
                required_integration="payments",
            )
        )

    elif bottleneck == Bottleneck.OPERATIONS:
        actions.append(
            Action(
                id="ops_support",
                name="Clear Support Backlog",
                action_type=ActionType.CUSTOMER_SUPPORT,
                domain=Domain.SUPPORT,
                description="Prioritize and process high-impact support issues.",
                impact=4,
                confidence=5,
                urgency=5,
                alignment=5,
                reversibility=5,
                cost=1,
                risk=1,
                execution_time=2,
            )
        )

    elif bottleneck == Bottleneck.EXPANSION:
        actions.extend([
            Action(
                id="exp_research",
                name="Research Growth Opportunities",
                action_type=ActionType.SEARCH,
                domain=Domain.RESEARCH,
                description="Research new markets, segments, channels, competitors, and product opportunities.",
                impact=4,
                confidence=3,
                urgency=2,
                alignment=4,
                reversibility=5,
                cost=1,
                risk=1,
                execution_time=2,
            ),
            Action(
                id="exp_ads",
                name="Scale Paid Acquisition",
                action_type=ActionType.CREATE_AD_CAMPAIGN,
                domain=Domain.ADS,
                description="Increase qualified acquisition through controlled paid experiments.",
                impact=5,
                confidence=3,
                urgency=3,
                alignment=4,
                reversibility=3,
                cost=4,
                risk=3,
                execution_time=2,
                required_permission="ad_spend",
                required_integration="ads",
                estimated_cost_dollars=100.0,
            ),
        ])

    return actions


def rank_actions(actions: List[Action]) -> List[Action]:
    return sorted(actions, key=lambda action: action.score, reverse=True)


# ============================================================
# 9. ELIGIBILITY / HARD CONDITION GATES
# ============================================================

def permission_allowed(action: Action, state: CompanyState) -> bool:
    if not action.required_permission:
        return True
    return state.permissions.get(action.required_permission, False)


def integration_available(action: Action, state: CompanyState) -> bool:
    if not action.required_integration:
        return True
    return state.integrations.get(action.required_integration, False)


def within_budget(action: Action, state: CompanyState) -> bool:
    if action.estimated_cost_dollars <= 0:
        return True

    budget_limit = state.budgets.get(action.domain.name.lower(), 0.0)
    spent = state.budget_spent.get(action.domain.name.lower(), 0.0)
    remaining = budget_limit - spent

    return action.estimated_cost_dollars <= remaining


def dependency_ready(action: Action, state: CompanyState) -> bool:
    completed_ids = {task.id for task in state.completed_tasks}
    return all(dep in completed_ids for dep in action.dependencies)


def conflicts_with_active_task(action: Action, state: CompanyState) -> bool:
    for task in state.active_tasks:
        if (
            task.status == TaskStatus.RUNNING
            and task.domain == action.domain
            and task.action
            and task.action.action_type == action.action_type
        ):
            return True
    return False


def exceeds_risk_threshold(action: Action, risk_threshold: float = 5.0) -> bool:
    return action.risk > risk_threshold


def eligible(action: Action, state: CompanyState) -> Tuple[bool, Optional[str]]:
    if not permission_allowed(action, state):
        return False, "PERMISSION"

    if not within_budget(action, state):
        return False, "BUDGET"

    if not dependency_ready(action, state):
        return False, "DEPENDENCY"

    if not integration_available(action, state):
        return False, "INTEGRATION"

    if conflicts_with_active_task(action, state):
        return False, "CONFLICT"

    if exceeds_risk_threshold(action):
        return False, "RISK"

    return True, None


# ============================================================
# 10. AGENT ROUTER
# ============================================================

AGENT_ROUTER = {
    Domain.STRATEGY: "planning_agent",
    Domain.RESEARCH: "research_agent",
    Domain.SOCIAL: "social_agent",
    Domain.OUTREACH: "outreach_agent",
    Domain.SUPPORT: "support_agent",
    Domain.ADS: "ads_agent",
    Domain.ENGINEERING: "engineering_agent",
    Domain.FINANCE: "finance_agent",
    Domain.GROWTH: "growth_agent",
    Domain.ORCHESTRATOR: "orchestrator",
}


def route_agent(action: Action) -> str:
    return AGENT_ROUTER.get(action.domain, "orchestrator")


# ============================================================
# 11. TOOL SELECTION
# ============================================================

def select_tool(action: Action) -> str:
    mapping = {
        ActionType.SEARCH: "SEARCH",
        ActionType.CODE_CHANGE: "CODE",
        ActionType.SEND_EMAIL: "EMAIL",
        ActionType.SOCIAL_POST: "SOCIAL",
        ActionType.QUERY_FINANCE: "PAYMENTS",
        ActionType.CREATE_AD_CAMPAIGN: "ADS",
        ActionType.CUSTOMER_SUPPORT: "SUPPORT",
        ActionType.DEPLOY: "DEPLOY",
        ActionType.UPDATE_STATE: "STATE",
        ActionType.LLM_ONLY: "LLM",
    }
    return mapping[action.action_type]


# ============================================================
# 12. EXECUTION LAYER
# ============================================================

class ToolExecutor:
    """
    Replace these placeholder methods with real tool/API integrations.
    """

    def execute(self, action: Action, state: CompanyState) -> ExecutionResult:
        if state.sandbox_mode:
            return self.simulate(action)

        return self.execute_real(action)

    def simulate(self, action: Action) -> ExecutionResult:
        return ExecutionResult(
            status=ResultStatus.SUCCESS,
            output={
                "mode": "sandbox",
                "action": action.name,
                "message": "Action simulated successfully."
            },
            execution_success=True,
        )

    def execute_real(self, action: Action) -> ExecutionResult:
        tool = select_tool(action)

        # Stub. Replace with real integrations.
        return ExecutionResult(
            status=ResultStatus.SUCCESS,
            output={
                "mode": "live",
                "tool": tool,
                "action": action.name,
                "message": "Real-action placeholder executed."
            },
            execution_success=True,
        )


# ============================================================
# 13. RESULT VALIDATION
# ============================================================

def validate_business_result(
    task: Task,
    result: ExecutionResult,
    state: CompanyState,
) -> ExecutionResult:
    """
    Technical execution success != business success.

    Replace this placeholder with task-specific success criteria.
    """

    if result.status == ResultStatus.SUCCESS:
        result.execution_success = True

        # Placeholder: actual implementations should compare KPI
        # deltas against a baseline or task-specific objective.
        result.business_success = True

    return result


# ============================================================
# 14. RETRY / FAILURE LOGIC
# ============================================================

def retry_delay(retry_count: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    return min(base_delay * (2 ** retry_count), max_delay)


def handle_result(task: Task, result: ExecutionResult) -> TaskStatus:
    if result.status == ResultStatus.SUCCESS:
        return TaskStatus.COMPLETED

    if result.status == ResultStatus.PARTIAL_SUCCESS:
        return TaskStatus.READY

    if result.status == ResultStatus.RETRYABLE_FAILURE:
        if task.retry_count < task.max_retries:
            task.retry_count += 1
            time.sleep(retry_delay(task.retry_count))
            return TaskStatus.READY
        return TaskStatus.FAILED

    if result.status == ResultStatus.BLOCKED:
        return TaskStatus.BLOCKED

    if result.status == ResultStatus.AWAITING_EXTERNAL_EVENT:
        return TaskStatus.AWAITING_EXTERNAL_EVENT

    if result.status == ResultStatus.AWAITING_HUMAN:
        return TaskStatus.AWAITING_HUMAN

    if result.status == ResultStatus.CANCELLED:
        return TaskStatus.CANCELLED

    return TaskStatus.FAILED


# ============================================================
# 15. MEMORY / LEARNING
# ============================================================

def record_memory(
    state: CompanyState,
    situation: str,
    action: Action,
    result: ExecutionResult,
    expected: Optional[str] = None,
    lesson: Optional[str] = None,
) -> None:
    state.memory.append(
        MemoryItem(
            situation=situation,
            action=action.name,
            result=result.status.name,
            expected=expected,
            actual=str(result.output),
            lesson=lesson,
        )
    )


# ============================================================
# 16. EXPERIMENT LOGIC
# ============================================================

def evaluate_experiment(experiment: Experiment) -> str:
    if not experiment.complete:
        return "CONTINUE_COLLECTING"

    if not experiment.result:
        return "NO_RESULT"

    actual = experiment.result.get("actual", experiment.baseline)

    if actual >= experiment.target:
        return "PROMOTE_WINNER"

    if actual <= experiment.baseline:
        return "REVERT"

    return "REVIEW"


# ============================================================
# 17. TASK CREATION
# ============================================================

def create_task_from_action(action: Action) -> Task:
    return Task(
        id=f"task_{action.id}_{int(time.time())}",
        objective=action.description,
        domain=action.domain,
        action=action,
        status=TaskStatus.READY,
        dependencies=list(action.dependencies),
        priority=action.priority,
    )


# ============================================================
# 18. AGENT EXECUTION LOOP
# ============================================================

class Agent:
    def __init__(self, name: str, executor: ToolExecutor):
        self.name = name
        self.executor = executor

    def gather_context(self, task: Task, state: CompanyState) -> Dict[str, Any]:
        return {
            "objective": task.objective,
            "metrics": state.metrics,
            "goals": [
                {
                    "id": goal.id,
                    "name": goal.name,
                    "status": goal.status.name,
                    "target": goal.target,
                }
                for goal in state.goals
            ],
            "recent_memory": state.memory[-10:],
        }

    def plan(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        if not task.action:
            raise ValueError("Task has no action.")

        return {
            "objective": task.objective,
            "next_step": task.action.name,
            "tool": select_tool(task.action),
        }

    def run(self, task: Task, state: CompanyState) -> ExecutionResult:
        task.status = TaskStatus.RUNNING

        context = self.gather_context(task, state)
        _plan = self.plan(task, context)

        if not task.action:
            result = ExecutionResult(
                status=ResultStatus.PERMANENT_FAILURE,
                error="Task has no executable action.",
            )
            task.status = TaskStatus.FAILED
            return result

        result = self.executor.execute(task.action, state)
        result = validate_business_result(task, result, state)

        task.memory.append(result)
        task.status = handle_result(task, result)

        return result


# ============================================================
# 19. ORCHESTRATOR
# ============================================================

class Orchestrator:
    """
    Company-level loop:

        Observe
          ->
        Diagnose
          ->
        Prioritize
          ->
        Delegate
          ->
        Execute
          ->
        Validate
          ->
        Learn
          ->
        Replan
    """

    def __init__(self):
        self.trigger_detector = TriggerDetector()
        self.executor = ToolExecutor()

    def detect_problems(self, state: CompanyState) -> Dict[str, Any]:
        evaluate_all_goals(state)
        bottleneck = detect_bottleneck(state)

        critical_goals = [
            goal for goal in state.goals
            if goal.status == GoalStatus.CRITICAL
        ]

        return {
            "bottleneck": bottleneck,
            "critical_goals": critical_goals,
        }

    def detect_opportunities(self, state: CompanyState) -> List[str]:
        opportunities = []

        if detect_bottleneck(state) == Bottleneck.EXPANSION:
            opportunities.append("Explore new growth channels")

        if state.metrics.get("revenue_growth", 0) > 0.20:
            opportunities.append("Scale proven revenue channel")

        return opportunities

    def create_candidate_actions(self, state: CompanyState) -> List[Action]:
        bottleneck = detect_bottleneck(state)
        return generate_actions(
            state=state,
            bottleneck=bottleneck,
            goals=state.goals,
        )

    def select_action(self, state: CompanyState) -> Optional[Action]:
        candidates = rank_actions(self.create_candidate_actions(state))

        for action in candidates:
            allowed, reason = eligible(action, state)

            if allowed:
                return action

            # In a production system, blocked actions should create
            # prerequisite/configuration tasks when appropriate.
            print(f"[blocked] {action.name}: {reason}")

        return None

    def dispatch(self, task: Task, state: CompanyState) -> ExecutionResult:
        if not task.action:
            return ExecutionResult(
                status=ResultStatus.PERMANENT_FAILURE,
                error="Cannot dispatch a task without an action."
            )

        agent_name = route_agent(task.action)
        agent = Agent(agent_name, self.executor)

        print(f"[dispatch] {agent_name} <- {task.objective}")

        return agent.run(task, state)

    def update_state_after_task(
        self,
        state: CompanyState,
        task: Task,
        result: ExecutionResult,
    ) -> None:
        if task in state.active_tasks:
            state.active_tasks.remove(task)

        if task.status == TaskStatus.COMPLETED:
            state.completed_tasks.append(task)

        elif task.status == TaskStatus.BLOCKED:
            state.blocked_tasks.append(task)

        elif task.status in {
            TaskStatus.READY,
            TaskStatus.RUNNING,
            TaskStatus.AWAITING_EXTERNAL_EVENT,
            TaskStatus.AWAITING_HUMAN,
        }:
            state.active_tasks.append(task)

        if task.action:
            record_memory(
                state=state,
                situation=f"Company bottleneck: {detect_bottleneck(state).name}",
                action=task.action,
                result=result,
                expected=task.objective,
                lesson="Use outcome data to improve future prioritization.",
            )

    def run_cycle(self, state: CompanyState) -> Dict[str, Any]:
        """
        One full company decision cycle.
        """

        # 1. Company active?
        if state.status != CompanyStatus.ACTIVE:
            return {"status": "STOPPED"}

        # 2. Detect trigger.
        trigger = self.trigger_detector.detect(state)

        # 3. Observe + diagnose.
        problems = self.detect_problems(state)
        opportunities = self.detect_opportunities(state)

        # 4. Prioritize/select highest-value eligible action.
        action = self.select_action(state)

        if not action:
            return {
                "status": "NO_ELIGIBLE_ACTION",
                "trigger": trigger.name if trigger else None,
                "problems": problems,
                "opportunities": opportunities,
            }

        # 5. Create task.
        task = create_task_from_action(action)
        state.active_tasks.append(task)

        # 6. Delegate + execute.
        result = self.dispatch(task, state)

        # 7. Update state + memory.
        self.update_state_after_task(state, task, result)

        # 8. Re-evaluate after resulting state change.
        evaluate_all_goals(state)

        return {
            "status": "CYCLE_COMPLETE",
            "trigger": trigger.name if trigger else None,
            "action": action.name,
            "agent": route_agent(action),
            "result": result.status.name,
            "task_status": task.status.name,
            "bottleneck": detect_bottleneck(state).name,
        }


# ============================================================
# 20. CROSS-AGENT EVENT BUS
# ============================================================

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List] = {}

    def subscribe(self, event_type: str, handler) -> None:
        self.subscribers.setdefault(event_type, []).append(handler)

    def emit(self, event_type: str, payload: Dict[str, Any]) -> None:
        for handler in self.subscribers.get(event_type, []):
            handler(payload)


# Example feature-deployment event propagation.

def social_feature_handler(payload: Dict[str, Any]) -> None:
    print(f"[social] Announce feature: {payload}")


def support_feature_handler(payload: Dict[str, Any]) -> None:
    print(f"[support] Update support knowledge: {payload}")


def outreach_feature_handler(payload: Dict[str, Any]) -> None:
    print(f"[outreach] Notify relevant prospects: {payload}")


def planning_feature_handler(payload: Dict[str, Any]) -> None:
    print(f"[planning] Monitor feature adoption: {payload}")


# ============================================================
# 21. SELF-HEALING / SELF-IMPROVEMENT CONDITION TREE
# ============================================================

def self_healing_flow(issue: Dict[str, Any]) -> str:
    """
    SYSTEM PROBLEM
        ->
    Detect anomaly
        ->
    Create issue
        ->
    Diagnose root cause
        ->
    Can agent repair?
       NO -> escalate
       YES
        ->
    Generate fix
        ->
    Run tests
        ->
    Tests pass?
       NO -> revise
       YES
        ->
    Deploy
        ->
    Monitor
        ->
    Resolved?
       NO -> rollback/replan
       YES -> close issue
    """

    if not issue.get("detected"):
        return "NO_ISSUE"

    if not issue.get("agent_can_repair"):
        return "ESCALATE"

    if not issue.get("tests_pass"):
        return "REVISE_FIX"

    if not issue.get("deployed"):
        return "DEPLOY_FIX"

    if not issue.get("resolved"):
        return "ROLLBACK_OR_REPLAN"

    return "CLOSE_ISSUE"


# ============================================================
# 22. FULL CONDITION LOGIC REFERENCE
# ============================================================

CONDITION_TREE = r"""
COMPANY LOOP
|
+-- Is company active?
|     +-- No -> stop / sleep
|     +-- Yes
|
+-- Critical event?
|     +-- security
|     +-- outage
|     +-- payment failure
|     +-- urgent customer
|
+-- User request?
|
+-- Agent schedule due?
|
+-- Existing task ready?
|
+-- Otherwise -> strategic review
      |
      +-- Load business state
      |
      +-- Compare goals vs metrics
      |
      +-- Detect bottleneck
      |
      +-- Detect opportunities
      |
      +-- Generate candidate actions
      |
      +-- Score candidates
      |
      +-- For highest-ranked candidate:
            |
            +-- Permission allowed?
            |
            +-- Budget available?
            |
            +-- Integration connected?
            |
            +-- Dependencies complete?
            |
            +-- Conflicting active task?
            |
            +-- Risk acceptable?
            |
            +-- Select specialized agent
            |
            +-- Agent gathers context
            |
            +-- Agent creates plan
            |
            +-- Agent selects tool
            |
            +-- Sandbox/live check
            |
            +-- Execute
            |
            +-- Observe result
            |
            +-- Validate technical success
            |
            +-- Validate business success
            |
            +-- Result:
            |      +-- SUCCESS -> update state
            |      +-- PARTIAL -> continue
            |      +-- RETRYABLE -> exponential retry
            |      +-- BLOCKED -> create prerequisite
            |      +-- AWAIT_EXTERNAL -> suspend
            |      +-- AWAIT_HUMAN -> request approval/input
            |      +-- PERMANENT_FAILURE -> fail/escalate
            |
            +-- Record memory
            |
            +-- Update metrics
            |
            +-- Recalculate goals
            |
            +-- Reprioritize company
            |
            +-- LOOP
"""


DEEPER_LOOP = r"""
GOAL
  |
OBSERVE
  |
GAP
  |
HYPOTHESIS
  |
ACTION
  |
RESULT
  |
MEASUREMENT
  |
LEARNING
  |
NEW STATE
  |
NEW PRIORITY
  |
NEW ACTION
"""


# ============================================================
# 23. SAMPLE COMPANY
# ============================================================

def build_sample_company() -> CompanyState:
    return CompanyState(
        company_id="demo-company",
        sandbox_mode=True,
        mission="Build and grow an autonomous AI-operated software company.",
        metrics={
            "traffic": 500,
            "minimum_traffic": 1000,
            "signup_conversion": 0.03,
            "target_conversion": 0.05,
            "activation_rate": 0.30,
            "target_activation": 0.40,
            "retention": 0.50,
            "target_retention": 0.60,
            "revenue_per_user": 15.0,
            "target_arpu": 20.0,
            "support_backlog": 10,
            "support_backlog_threshold": 50,
            "mrr": 7300,
            "revenue_growth": 0.10,
        },
        budgets={
            "ads": 1000.0,
            "outreach": 500.0,
            "social": 250.0,
            "engineering": 5000.0,
            "finance": 250.0,
        },
        budget_spent={
            "ads": 100.0,
            "outreach": 0.0,
            "social": 0.0,
            "engineering": 0.0,
            "finance": 0.0,
        },
        permissions={
            "social_posting": True,
            "send_email": True,
            "code_changes": True,
            "finance_read": True,
            "ad_spend": True,
        },
        integrations={
            "social": True,
            "email": True,
            "code_repository": True,
            "payments": True,
            "ads": True,
        },
        goals=[
            Goal(
                id="goal_mrr_10k",
                name="Reach $10k MRR",
                metric_name="mrr",
                target=10000.0,
                direction="increase",
                warning_threshold=1500.0,
                critical_threshold=5000.0,
            )
        ],
    )


# ============================================================
# 24. SAMPLE RUNTIME
# ============================================================

def main() -> None:
    state = build_sample_company()

    bus = EventBus()
    bus.subscribe("FEATURE_DEPLOYED", social_feature_handler)
    bus.subscribe("FEATURE_DEPLOYED", support_feature_handler)
    bus.subscribe("FEATURE_DEPLOYED", outreach_feature_handler)
    bus.subscribe("FEATURE_DEPLOYED", planning_feature_handler)

    orchestrator = Orchestrator()

    print("=" * 70)
    print("POLSIA-STYLE AUTONOMOUS COMPANY OPERATING SYSTEM")
    print("=" * 70)

    print("\nCondition Tree:")
    print(CONDITION_TREE)

    print("\nDeeper Recursive Loop:")
    print(DEEPER_LOOP)

    print("\nRunning one orchestration cycle...")
    result = orchestrator.run_cycle(state)

    print("\nCycle Result:")
    for key, value in result.items():
        print(f"{key}: {value}")

    print("\nExample cross-agent event:")
    bus.emit(
        "FEATURE_DEPLOYED",
        {
            "feature": "AI onboarding assistant",
            "target_segment": "new customers",
        },
    )


if __name__ == "__main__":
    main()
'''

path = Path("/mnt/data/project-md.py")
path.write_text(content, encoding="utf-8")

print(f"Created: {path}")
print(f"Lines: {len(content.splitlines())}")
