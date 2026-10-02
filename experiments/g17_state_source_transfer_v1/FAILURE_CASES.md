# Post-hoc descriptive failures

First2 by predetermined SHA order in each observed error class among F handoffs. These do not affect any cohort/primary. Empty classes stated.

## date_error: 2 displayed

seed43 template_ood g17_template_ood_0087, a=2, G→F, C=True

Current: Author: Bob. Record date: 2026-11-28. The event date assigned in the record to my plan to give six sensors to Grace is in two days. This record does not establish that the event occurred.

Gold: Author: Bob. Record date: 2026-11-28. The event date assigned in the record to my plan to give six sensors to Grace is tomorrow. This record does not establish that the event occurred.

Output: Author: Bob. Record date: 2026-11-28. The event date assigned in the record to my plan to give six sensors to Grace is in two days. This record does not establish that the event occurred.

seed42 iid g17_iid_0123, a=-2, U→F, C=True

Current: Author: Alice. Record date: 2026-10-16. My plan to give four sensors to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

Gold: Author: Alice. Record date: 2026-10-16. My plan to give four sensors to David, with the event dated three days ago, is described in the record. This record does not establish that the event occurred.

Output: Author: Alice. Record date: 2026-10-16. My plan to give four sensors to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

## fact_error: 0 displayed
No observed cases.

## date_and_fact_error: 0 displayed
No observed cases.

## parse_unresolved: 2 displayed

seed43 template_ood g17_template_ood_0039, a=-2, G→F, C=True

Current: Author: Bob. Record date: 2026-11-25. The event date assigned in the record to my plan to deliver four books to Carol is two days ago. This record does not establish that the event occurred.

Gold: Author: Bob. Record date: 2026-11-25. The event date assigned in the record to my plan to deliver four books to Carol is three days ago. This record does not establish that the event occurred.

Output: Author: Bob. Record date: 2026-11-25. The event date assigned in the record to my plan to deliver four books to Carol is 2026. This record does not establish that the event occurred.

seed42 template_ood g17_template_ood_0006, a=2, U→F, C=True

Current: Author: Emma. Record date: 2026-10-20. As described in the record, my plan to not give five sensors to Henry has the event dated in two days. This record does not establish that the event occurred.

Gold: Author: Emma. Record date: 2026-10-20. As described in the record, my plan to not give five sensors to Henry has the event dated tomorrow. This record does not establish that the event occurred.

Output: Author: Emma. Record date: 2026-10-20. As described in the record, my plan to not give five sensors to Henry has the event dated tomorrow in the three days. This record does not establish that the event occurred.

## perspective_error: 0 displayed
No observed cases.

## length_limit: 0 displayed
No observed cases.
