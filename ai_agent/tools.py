# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tools for the ADK AlloyDB-only Data Science Agent."""

import logging

from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool
from .sub_agents.analytics import alloydb_agent
logger = logging.getLogger(__name__)


async def call_alloydb_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call AlloyDB database (NL2SQL) agent."""
    logger.debug("call_alloydb_agent: %s", question)

    # Replace None with your actual AlloyDB agent if you have one
    agent_tool = AgentTool(agent=alloydb_agent)

    alloydb_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["alloydb_agent_output"] = alloydb_agent_output
    return alloydb_agent_output
