"""Orchestrator — coordinates Planner → Executor → Reviewer pipeline."""
import json
import logging
import re
from typing import AsyncGenerator
from app.agents.planner import PlannerAgent
from app.agents.executor import ExecutorAgent
from app.agents.reviewer import ReviewerAgent
from app.core.knowledge import knowledge_base

logger = logging.getLogger(__name__)


class Orchestrator:
    """Orchestrates the multi-agent pipeline: Plan → Execute → Review."""

    def __init__(self):
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.reviewer = ReviewerAgent()

    def _extract_json(self, text: str) -> dict:
        """Extract JSON from text, trying multiple approaches."""
        # Direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # JSON block
        match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Brace-delimited
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        return {}

    async def process(
        self,
        task: str,
        kb_query: str = "",
        stream_callback=None,
    ) -> dict:
        """Run the full Plan → Execute → Review pipeline.

        Returns a dict with: plan, execution_result, review, final_output
        """
        result = {
            "task": task,
            "plan": None,
            "execution_result": None,
            "review": None,
            "final_output": None,
            "status": "running",
        }

        # Phase 1: Knowledge Retrieval
        context = ""
        if kb_query:
            context = knowledge_base.get_context_for_prompt(kb_query)

        # Phase 2: Planning
        if stream_callback:
            await stream_callback("phase", "Planning — analyzing task...")

        plan_raw = await self.planner.run(task, context)
        plan = self._extract_json(plan_raw)
        result["plan"] = plan if plan else {"raw": plan_raw}

        if stream_callback:
            await stream_callback("phase", f"Plan created: {len(plan.get('steps', []))} steps")

        # Phase 3: Execution
        if stream_callback:
            await stream_callback("phase", "Executing — carrying out plan...")

        exec_prompt = f"""Execute the following plan:

**Goal**: {plan.get('goal', task)}

**Steps**:
{json.dumps(plan.get('steps', []), indent=2)}

Execute each step and report results. Be thorough and use available tools.
"""
        execution_raw = await self.executor.run(exec_prompt)
        result["execution_result"] = execution_raw

        if stream_callback:
            await stream_callback("phase", "Execution complete — reviewing output...")

        # Phase 4: Review
        review_prompt = f"""Review the following execution:

**Original Task**: {task}

**Plan**:
{json.dumps(plan, indent=2)}

**Execution Result**:
{execution_raw[:3000]}

Evaluate quality and provide feedback.
"""
        review_raw = await self.reviewer.run(review_prompt)
        review = self._extract_json(review_raw)
        result["review"] = review if review else {"raw": review_raw}

        # Determine final output
        verdict = review.get("verdict", "pass")
        if verdict == "pass":
            result["final_output"] = execution_raw
            result["status"] = "completed"
        elif verdict == "needs_revision":
            result["final_output"] = review.get("revised_output", execution_raw)
            result["status"] = "completed_with_revisions"
        else:
            result["final_output"] = execution_raw
            result["status"] = "failed_review"

        if stream_callback:
            await stream_callback("phase", f"Pipeline complete — status: {result['status']}")

        return result

    async def direct_chat(self, message: str) -> str:
        """Direct chat with the executor agent (bypass pipeline)."""
        return await self.executor.run(message)

    async def direct_chat_stream(self, message: str) -> AsyncGenerator[str, None]:
        """Streaming direct chat."""
        async for chunk in self.executor.run_stream(message):
            yield chunk


# Singleton
orchestrator = Orchestrator()
