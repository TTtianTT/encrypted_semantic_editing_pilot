# G15 actual cases

First12 worlds were fixed before inference, two per seed/split; supplementary failure examples use deterministic hash ordering within openly reported post-result categories. They do not affect training, cohorts, estimates or model choice. Absent categories remain absent.

## pre-inference hash fixed / seed42 / iid / g15_iid_recorded_plan_0003

F old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

F old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

F old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

F fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

F fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

F fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

F fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

F reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

F reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

F reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

F self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

F self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

F reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-26", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-24", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-26", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-26", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-24", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-26", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-24", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-26", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-26", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-20. My plan to send one parcel to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

## pre-inference hash fixed / seed42 / iid / g15_iid_recorded_plan_0083

F old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-09", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-07", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-09", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-09", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-07", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-09", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-07", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-09", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-09", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-03. My plan to send four tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

## pre-inference hash fixed / seed42 / template_ood / g15_template_ood_recorded_plan_0088

F old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

F old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

F old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

F fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

F fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

F fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

F fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

F reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

F reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

F reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

F self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

F self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

F reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

N old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

N old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

N old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

N fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

N fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-19", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

N fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-17", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

N fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-19", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

N reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

N reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

N reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

N self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

N self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-19", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

N reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

O old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

O old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

O old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

O fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

O fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

O fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-17", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

O fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

O reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

O reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

O reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

O self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

O self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

O reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

P old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

P old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

P old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

P fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

P fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-19", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

P fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated two days ago is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-17", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

P fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-19", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

P reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

P reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

P reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

P self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

P self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-19", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

P reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated today is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-13. What the record describes for an event dated yesterday is my plan to not deliver five books to Carol. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

## pre-inference hash fixed / seed42 / template_ood / g15_template_ood_recorded_plan_0078

F old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

F old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

F old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

F fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

F fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

F fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

F fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

F reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

F reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

F reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

F self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

F self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

F reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N self_second Q: joint=False; exact=False; full=False; C=True; error=parse_unresolved; date_delta=None
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to has the event dated today. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: null

N reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-11-28. As described in the record, my plan to not bring four sensors to Frank has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "bring", "object": "sensor", "quantity": 4, "record_date": "2026-11-28", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

## pre-inference hash fixed / seed43 / iid / g15_iid_recorded_plan_0010

F old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

F old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

F old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

F fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

F fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

F fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

F fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

F reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

F reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

F reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

F self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

F self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

F reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-07", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-07", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-09", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-09", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-07", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-07", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-09", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-07", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-03. According to the record, my plan to not bring six tickets to Carol concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 6, "record_date": "2026-10-03", "event_date": "2026-10-08", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

## pre-inference hash fixed / seed43 / iid / g15_iid_recorded_plan_0016

F old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

F old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

F old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

F fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

F fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

F fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

F fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

F reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

F reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

F reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

F self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

F self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

F reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-19", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-19", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-21", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-21", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

N reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-19", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

O reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-19", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-19", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-21", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-19", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

P reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-15. The record describes my plan to not give two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "David", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}

## pre-inference hash fixed / seed43 / template_ood / g15_template_ood_recorded_plan_0007

F old H0: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F old H1: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F old H2: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F fixed E: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F reset_fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F reset_fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F reset_fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F reset_self Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N old H0: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N old H1: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N old H2: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N fixed E: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N reset_fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N reset_fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N reset_fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N reset_self Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O old H0: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O old H1: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O old H2: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O fixed E: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O reset_fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O reset_fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O reset_fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O reset_self Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P old H0: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P old H1: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P old H2: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-03", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-29. The event date assigned in the record to my plan to give two tickets to Grace is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "give", "object": "ticket", "quantity": 2, "record_date": "2026-11-29", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

## pre-inference hash fixed / seed43 / template_ood / g15_template_ood_recorded_plan_0118

F old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

F old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

F old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

F fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

F fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

F fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

F fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

F reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

F reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

F reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

F self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

F self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

F reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

N old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

N old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

N old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

N fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

N fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-21", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

N fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-21", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

N fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-23", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

N reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

N reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

N reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

N self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

N self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-23", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

N reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

O old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

O old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

O old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

O fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

O fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

O fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

O fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

O reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

O reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

O reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

O self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

O self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

O reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

P old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

P old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

P old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

P fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

P fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-21", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

P fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-21", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

P fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-23", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

P reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

P reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

P reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

P self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

P self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-21", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

P reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated today. This record does not establish that the event occurred.
Output: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Frank. Record date: 2026-10-17. As described in the record, my plan to not bring four parcels to David has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Frank", "actor": "Frank", "recipient": "David", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

## pre-inference hash fixed / seed44 / iid / g15_iid_recorded_plan_0069

F old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-24", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-24", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-24", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-26", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-26", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-24", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-24", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-24", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-26", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-24", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-11-20. In the record, my plan to give one book to Alice has an event date of yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "give", "object": "book", "quantity": 1, "record_date": "2026-11-20", "event_date": "2026-11-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

## pre-inference hash fixed / seed44 / iid / g15_iid_recorded_plan_0099

F old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

F old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

F old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

F fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

F fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

F fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-12", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

F fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

F reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

F reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

F reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

F self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

F self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

F reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-12", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-12", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-14", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-14", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

N reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-12", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

O reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-12", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-12", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-14", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-12", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

P reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated today, is described in the record. This record does not establish that the event occurred.
Output: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold: Author: Henry. Record date: 2026-11-08. My plan to send three tickets to Frank, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Parsed: {"author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "send", "object": "ticket", "quantity": 3, "record_date": "2026-11-08", "event_date": "2026-11-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Henry", "perspective": "first"}

## pre-inference hash fixed / seed44 / template_ood / g15_template_ood_recorded_plan_0067

F old H0: joint=False; exact=False; full=NA; C=False; error=date_error; date_delta=2
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-15", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F old H1: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F old H2: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

F reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N old H0: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N old H1: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N old H2: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-12", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-12", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-14", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-14", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

N reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O old H0: joint=False; exact=False; full=NA; C=False; error=date_error; date_delta=2
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-15", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O old H1: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O old H2: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

O reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P old H0: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P old H1: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P old H2: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-12", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-12", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-14", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-12", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

P reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-08. The event date assigned in the record to my plan to give four sensors to Carol is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 4, "record_date": "2026-10-08", "event_date": "2026-10-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob", "perspective": "first"}

## pre-inference hash fixed / seed44 / template_ood / g15_template_ood_recorded_plan_0054

F old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

F old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

F old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

F fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

F fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

F fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-28", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

F fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

F reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

F reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

F reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

F self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

F self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

F reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-28", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-28", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-30", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-30", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

N reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-28", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

O reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-28", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-28", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-30", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-28", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

P reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated today. This record does not establish that the event occurred.
Output: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Grace. Record date: 2026-10-24. As described in the record, my plan to not send seven tickets to Bob has the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "ticket", "quantity": 7, "record_date": "2026-10-24", "event_date": "2026-10-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}

## self_failure first deterministic hash after failure classification / seed42 / iid / g15_iid_recorded_plan_0120

N old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

N old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

N old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

N fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

N fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-02", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

N fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-02", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

N fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-04", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

N reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

N reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

N reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

N self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

N self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-04", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

N reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

## heldout_failure first deterministic hash after failure classification / seed42 / iid / g15_iid_recorded_plan_0120

N old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

N old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

N old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

N fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

N fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-02", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

N fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-02", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

N fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-04", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

N reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

N reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

N reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

N self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

N self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-04", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

N reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated today. This record does not establish that the event occurred.
Output: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: David. Record date: 2026-10-29. The record describes my plan to not deliver one ticket to Frank, with the event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "David", "actor": "David", "recipient": "Frank", "action": "deliver", "object": "ticket", "quantity": 1, "record_date": "2026-10-29", "event_date": "2026-11-03", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}

## self_failure first deterministic hash after failure classification / seed44 / template_ood / g15_template_ood_recorded_plan_0143

N old H0: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is two days ago. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

N old H1: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is two days ago. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

N old H2: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is two days ago. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

N fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

N fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is two days ago. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-16", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

N fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is two days ago. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-16", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

N fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-18", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

N reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

N reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

N reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

N self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

N self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-18", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

N reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

## heldout_failure first deterministic hash after failure classification / seed44 / template_ood / g15_template_ood_recorded_plan_0143

N old H0: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is two days ago. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

N old H1: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is two days ago. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

N old H2: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is two days ago. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

N fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

N fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is two days ago. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-16", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

N fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is two days ago. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-16", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

N fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-18", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

N reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

N reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

N reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

N self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

N self_second Q: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=1
Current: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-18", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

N reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-12. The event date assigned in the record to my plan to send four tickets to David is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "David", "action": "send", "object": "ticket", "quantity": 4, "record_date": "2026-12-12", "event_date": "2026-12-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}

## heldout_failure first deterministic hash after failure classification / seed42 / template_ood / g15_template_ood_recorded_plan_0055

F old H0: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is two days ago. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

F old H1: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is two days ago. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

F old H2: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is two days ago. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

F fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

F fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

F fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

F fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=2
Current: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is tomorrow. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-10", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

F reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

F reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

F reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

F self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

F self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

F reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

## heldout_failure first deterministic hash after failure classification / seed42 / iid / g15_iid_recorded_plan_0050

O old H0: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated yesterday. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Bob", "action": "give", "object": "book", "quantity": 4, "record_date": "2026-11-30", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

O old H1: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated yesterday. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Bob", "action": "give", "object": "book", "quantity": 4, "record_date": "2026-11-30", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

O old H2: joint=True; exact=True; full=NA; C=True; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated yesterday. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Bob", "action": "give", "object": "book", "quantity": 4, "record_date": "2026-11-30", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

O fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Bob", "action": "give", "object": "book", "quantity": 4, "record_date": "2026-11-30", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

O fixed P: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Bob", "action": "give", "object": "book", "quantity": 4, "record_date": "2026-11-30", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

O fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Bob", "action": "give", "object": "book", "quantity": 4, "record_date": "2026-11-30", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

O fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Bob", "action": "give", "object": "book", "quantity": 4, "record_date": "2026-11-30", "event_date": "2026-12-04", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

O reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Bob", "action": "give", "object": "book", "quantity": 4, "record_date": "2026-11-30", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

O reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Bob", "action": "give", "object": "book", "quantity": 4, "record_date": "2026-11-30", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

O reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Bob", "action": "give", "object": "book", "quantity": 4, "record_date": "2026-11-30", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

O self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated today. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated today. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Bob", "action": "give", "object": "book", "quantity": 4, "record_date": "2026-11-30", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

O self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Bob", "action": "give", "object": "book", "quantity": 4, "record_date": "2026-11-30", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

O reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-11-30. According to the record, my plan to not give four books to Bob concerns an event dated yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Bob", "action": "give", "object": "book", "quantity": 4, "record_date": "2026-11-30", "event_date": "2026-12-05", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

## heldout_failure first deterministic hash after failure classification / seed42 / template_ood / g15_template_ood_recorded_plan_0055

O old H0: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is two days ago. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

O old H1: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is two days ago. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

O old H2: joint=True; exact=True; full=NA; C=False; error=success; date_delta=0
Current: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is two days ago. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is two days ago. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

O fixed E: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

O fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

O fixed G: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=-1
Current: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is two days ago. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-07", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

O fixed U: joint=False; exact=False; full=False; C=True; error=date_error; date_delta=2
Current: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is tomorrow. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-10", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

O reset_fixed P: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

O reset_fixed G: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

O reset_fixed U: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

O self_first Q: joint=True; exact=True; full=NA; C=NA; error=success; date_delta=0
Current: natural tomorrow for self first
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

O self_second Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

O reset_self Q: joint=True; exact=True; full=True; C=True; error=success; date_delta=0
Current: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-03. The event date assigned in the record to my plan to send eight parcels to Emma is yesterday. This record does not establish that the event occurred.
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

## Post-result boundary examples and category scope

Automatic maintenance-failure category is H2 only; its zero count does not describe H0/H1/all3. `case_categories.csv` now names that scope explicitly. Following examples are supplementary deterministic post-result descriptions, not the pre-inference12 cases, and do not change cohorts or estimates.

### atomic_F: seed44, iid, g15_iid_reported_cancelled_0030

Source/current: Author: Grace. Record date: 2026-10-07. The subject of the record is Grace's cancelled plan to not give one sensor to Carol, with the event dated in two days. This record does not establish that the event occurred.

Output: Author: Grace. Record date: 2026-10-07. The subject of the record is Grace's cancelled plan to not give one sensor to Carol, with the event dated in two days. This record does not establish that the event occurred.

Gold: Author: Grace. Record date: 2026-10-07. The subject of the record is Grace's cancelled plan to not give one sensor to Carol, with the event dated tomorrow. This record does not establish that the event occurred.

Joint=False; exact=False; error=date_error; relative_date=2; delta_days=1; first_failure=NA fixed next step. Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 1, "record_date": "2026-10-07", "event_date": "2026-10-13", "record_status": "reported_cancelled", "polarity": "negative", "attribution": "Grace", "perspective": "third"}

### atomic_O: seed44, iid, g15_iid_reported_cancelled_0030

Source/current: Author: Grace. Record date: 2026-10-07. The subject of the record is Grace's cancelled plan to not give one sensor to Carol, with the event dated in two days. This record does not establish that the event occurred.

Output: Author: Grace. Record date: 2026-10-07. The subject of the record is Grace's cancelled plan to not give one sensor to Carol, with the event dated in two days. This record does not establish that the event occurred.

Gold: Author: Grace. Record date: 2026-10-07. The subject of the record is Grace's cancelled plan to not give one sensor to Carol, with the event dated tomorrow. This record does not establish that the event occurred.

Joint=False; exact=False; error=date_error; relative_date=2; delta_days=1; first_failure=NA fixed next step. Parsed: {"author": "Grace", "actor": "Grace", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 1, "record_date": "2026-10-07", "event_date": "2026-10-13", "record_status": "reported_cancelled", "polarity": "negative", "attribution": "Grace", "perspective": "third"}

### heldout_O42: seed42, iid, g15_iid_recorded_plan_0098

Source/current: Author: Frank. Record date: 2026-11-13. According to the record, my plan to not send six books to Carol concerns an event dated today. This record does not establish that the event occurred.

Output: Author: Frank. Record date: 2026-11-13. According to the record, my plan to not send six books to Carol concerns an event dated two days ago. This record does not establish that the event occurred.

Gold: Author: Frank. Record date: 2026-11-13. According to the record, my plan to not send six books to Carol concerns an event dated yesterday. This record does not establish that the event occurred.

Joint=False; exact=False; error=date_error; relative_date=-2; delta_days=-1; first_failure=NA fixed next step. Parsed: {"author": "Frank", "actor": "Frank", "recipient": "Carol", "action": "send", "object": "book", "quantity": 6, "record_date": "2026-11-13", "event_date": "2026-11-17", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}

### maintenance_O44: seed44, template_ood, g15_template_ood_recorded_plan_0012

Source/current: Author: David. Record date: 2026-10-11. What the record describes for an event dated yesterday is my plan to not send nine sensors to Carol. This record does not establish that the event occurred.

Output: Author: David. Record date: 2026-10-11. What the record describes for an event dated four days ago is my plan to not send nine sensors to Carol. This record does not establish that the event occurred.

Gold: Author: David. Record date: 2026-10-11. What the record describes for an event dated two days ago is my plan to not send nine sensors to Carol. This record does not establish that the event occurred.

Joint=False; exact=False; error=date_error; relative_date=-4; delta_days=-2; first_failure=NA fixed next step. Parsed: {"author": "David", "actor": "David", "recipient": "Carol", "action": "send", "object": "sensor", "quantity": 9, "record_date": "2026-10-11", "event_date": "2026-10-14", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}
