"""
services/handoff_service.py
-----------------------------
Business service for simulating a live agent handoff.

This service has no database access — it returns a simulated transfer
message as defined in the assignment spec.  In a production system,
this would open a real-time chat channel or queue a ticket.
"""

import logging

from chatbot.schemas import ServiceResult

logger = logging.getLogger(__name__)


_HANDOFF_MESSAGE = """\
I'm connecting you to a **NorthStar support representative** right now 🎧

⏳ *Please hold for a moment...*

A member of our team will be with you shortly. Your conversation history has been shared with them so you won't need to repeat yourself.

Thank you for your patience! If no one is available right now, you can also reach us at **support@northstar-gear.com**."""


class HandoffService:
    """
    Simulates transferring the user to a live support agent.

    In the assignment demo, this returns a static confirmation message.
    A production implementation would integrate with a live chat platform
    (e.g. Intercom, Zendesk, Freshdesk) by replacing this class.
    """

    def simulate_handoff(self) -> ServiceResult:
        """
        Simulate a live agent transfer.

        Returns
        -------
        ServiceResult
            Always succeeds; ``data`` contains the transfer confirmation text.
        """
        logger.info("simulate_handoff: initiating simulated agent transfer.")
        return ServiceResult(success=True, data=_HANDOFF_MESSAGE)
