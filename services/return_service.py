"""
services/return_service.py
---------------------------
Business service for return policy and shipping information.

These responses are static business rules — no database access is required
for the assignment version (per API_CONTRACT.md).

Responsibilities:
  - Return the return & exchange policy text.
  - Return shipping options and timelines.
"""

import logging

from chatbot.schemas import ServiceResult

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Static policy content
# Defined here (not in config) because these are business rules, not
# configuration parameters.  They would come from a CMS or REST API in
# a production system.
# ---------------------------------------------------------------------------

_RETURN_POLICY = """\
Here's our **Return & Exchange Policy** 📋

**Return Window**
• Items may be returned within **30 days** of purchase.

**Item Condition**
• Items must be **unused** and in **original packaging**.
• Damaged or worn items are not eligible for return.

**Exchange Policy**
• We offer direct exchanges for defective or incorrectly shipped items.
• Size exchanges are subject to stock availability.

**How to Return**
• Contact our support team with your **order number** to initiate a return.
• We'll provide a prepaid return label for eligible items.

Is there anything else I can help you with?"""

_SHIPPING_INFO = """\
Here are our **Shipping Options** 📬

| Option | Timeline |
|---|---|
| Standard shipping | 3–5 business days |
| Expedited shipping | 1–2 business days |

**Processing Time**
• All orders are processed within **24 hours** of placement.
• Orders placed after 3 PM are processed the next business day.

**Tracking**
• You will receive a tracking number by email once your order ships.

Is there anything else I can help you with?"""


class ReturnService:
    """
    Provides return policy and shipping information.

    No database access is required — these are static business rules.
    """

    def get_return_policy(self) -> ServiceResult:
        """
        Return the complete return and exchange policy.

        Returns
        -------
        ServiceResult
            Always succeeds; ``data`` contains the formatted policy text.
        """
        logger.info("get_return_policy: returning policy text.")
        return ServiceResult(success=True, data=_RETURN_POLICY)

    def get_shipping_info(self) -> ServiceResult:
        """
        Return shipping options and delivery timelines.

        Returns
        -------
        ServiceResult
            Always succeeds; ``data`` contains the formatted shipping text.
        """
        logger.info("get_shipping_info: returning shipping info.")
        return ServiceResult(success=True, data=_SHIPPING_INFO)
