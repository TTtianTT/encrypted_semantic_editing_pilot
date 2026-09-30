# Fixed diagnostic cases

Category absence is explicit: {"natural_only": 6, "edited_only": 6, "all3": 6, "fixed_success_rollout_failure": 6}. Fallback cases do not claim an absent category. Unresolved parse is a conservative failure, not a confirmed fact error.

## 1. natural_only: F2/43/iid/g13_iid_recorded_plan_0078

Current: Author: Grace. Record date: 2026-11-13. The subject of the record is my plan to not give seven sensors to Bob, with the event dated yesterday. This record does not establish that the event occurred.
Gold next: Author: Grace. Record date: 2026-11-13. The subject of the record is my plan to not give seven sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.
Own rollout first failure: 2

H0: Author: Grace. Record date: 2026-11-13. The subject of the record is my plan to not give seven sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "give", "object": "sensor", "quantity": 7, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H1: Author: Grace. Record date: 2026-11-13. The subject of the record is my plan to not give seven sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "give", "object": "sensor", "quantity": 7, "record_date": "2026-11-13", "event_date": "2026-11-18", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H2: Author: Grace. Record date: 2026-11-13. The subject of the record is my plan to not give seven sensors to Bob, with the event dated days ago. This record does not establish that the event occurred.
joint=False; parsed=null; unresolved=True; date error=False; other fact error=False

Own step5:  - - -To - -About - - To - - than - -' - - about - -IB - - nearly - - mother - -Did - - own - - Medical - - of - -284 - - In - -
Gold step5: Author: Grace. Record date: 2026-11-13. The subject of the record is my plan to not give seven sensors to Bob, with the event dated four days ago. This record does not establish that the event occurred.

## 2. natural_only: F2/44/iid/g13_iid_recorded_plan_0152

Current: Author: Frank. Record date: 2026-12-10. The record describes my plan to not deliver seven tickets to Henry, with the event dated yesterday. This record does not establish that the event occurred.
Gold next: Author: Frank. Record date: 2026-12-10. The record describes my plan to not deliver seven tickets to Henry, with the event dated two days ago. This record does not establish that the event occurred.
Own rollout first failure: 2

H0: Author: Frank. Record date: 2026-12-10. The record describes my plan to not deliver seven tickets to Henry, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Frank", "actor": "Frank", "recipient": "Henry", "action": "deliver", "object": "ticket", "quantity": 7, "record_date": "2026-12-10", "event_date": "2026-12-15", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H1: Author: Frank. Record date: 2026-12-10. The record describes my plan to not deliver seven tickets to Henry, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Frank", "actor": "Frank", "recipient": "Henry", "action": "deliver", "object": "ticket", "quantity": 7, "record_date": "2026-12-10", "event_date": "2026-12-15", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H2: Author: Frank. Record date: 2026-12-10. The record describes my plan to not deliver seven tickets to Henry, with the event dated three days ago. This record does not establish that the event occurred.
joint=False; parsed={"author": "Frank", "actor": "Frank", "recipient": "Henry", "action": "deliver", "object": "ticket", "quantity": 7, "record_date": "2026-12-10", "event_date": "2026-12-14", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}; unresolved=False; date error=True; other fact error=False

Own step5: ToToToThreeToTo threeToTo 3 3 3-3ToTo wipe threeTo three ToToTo twoTo three 3 3To three pairTo three days ToTo three -3 threeTo two ToTo two 3 3 ToTo 3To two Two ToToThreeTwoTo two
Gold step5: Author: Frank. Record date: 2026-12-10. The record describes my plan to not deliver seven tickets to Henry, with the event dated four days ago. This record does not establish that the event occurred.

## 3. natural_only: F2/42/template_ood/g13_template_ood_recorded_plan_0129

Current: Author: Grace. Record date: 2026-10-18. It is my plan to give five tickets to Carol that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Gold next: Author: Grace. Record date: 2026-10-18. It is my plan to give five tickets to Carol that the record describes for an event dated two days ago. This record does not establish that the event occurred.
Own rollout first failure: 2

H0: Author: Grace. Record date: 2026-10-18. It is my plan to give five tickets to Carol that the record describes for an event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Grace", "actor": "Grace", "recipient": "Carol", "action": "give", "object": "ticket", "quantity": 5, "record_date": "2026-10-18", "event_date": "2026-10-23", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Grace", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H1: Author: Grace. Record date: 2026-10-18. It is my plan to give five tickets to Carol that the record describes for an event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Grace", "actor": "Grace", "recipient": "Carol", "action": "give", "object": "ticket", "quantity": 5, "record_date": "2026-10-18", "event_date": "2026-10-23", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Grace", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H2: Author: Grace. Record date: 2026-10-18. It is my plan tomorrow three days ago. These three days three days days three three days old. This record does not establish that the event occurred.
joint=False; parsed=null; unresolved=True; date error=False; other fact error=False

Own step5:  three three threeThree three three days three three four three three five three three nine three three rules three three
Gold step5: Author: Grace. Record date: 2026-10-18. It is my plan to give five tickets to Carol that the record describes for an event dated four days ago. This record does not establish that the event occurred.

## 4. natural_only: F2/44/iid/g13_iid_recorded_plan_0046

Current: Author: Bob. Record date: 2026-10-17. The subject of the record is my plan to not deliver six tickets to Grace, with the event dated yesterday. This record does not establish that the event occurred.
Gold next: Author: Bob. Record date: 2026-10-17. The subject of the record is my plan to not deliver six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.
Own rollout first failure: 2

H0: Author: Bob. Record date: 2026-10-17. The subject of the record is my plan to not deliver six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "deliver", "object": "ticket", "quantity": 6, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H1: Author: Bob. Record date: 2026-10-17. The subject of the record is my plan to not deliver six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "deliver", "object": "ticket", "quantity": 6, "record_date": "2026-10-17", "event_date": "2026-10-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H2: Author: Bob. Record date: 2026-10-17. The subject of the record is my plan to not deliver six tickets to Grace, with the event dated three days ago. This record does not establish that the event occurred.
joint=False; parsed={"author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "deliver", "object": "ticket", "quantity": 6, "record_date": "2026-10-17", "event_date": "2026-10-21", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}; unresolved=False; date error=True; other fact error=False

Own step5: ToToToThreeToTo threeToTo 3 3 3ToTo twoToTo pairToToBiToTo3ToToTwoTo two ToToTo
Gold step5: Author: Bob. Record date: 2026-10-17. The subject of the record is my plan to not deliver six tickets to Grace, with the event dated four days ago. This record does not establish that the event occurred.

## 5. natural_only: F2/44/iid/g13_iid_recorded_plan_0142

Current: Author: Emma. Record date: 2026-11-12. The subject of the record is my plan to not bring two tickets to Henry, with the event dated yesterday. This record does not establish that the event occurred.
Gold next: Author: Emma. Record date: 2026-11-12. The subject of the record is my plan to not bring two tickets to Henry, with the event dated two days ago. This record does not establish that the event occurred.
Own rollout first failure: 2

H0: Author: Emma. Record date: 2026-11-12. The subject of the record is my plan to not bring two tickets to Henry, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "bring", "object": "ticket", "quantity": 2, "record_date": "2026-11-12", "event_date": "2026-11-17", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H1: Author: Emma. Record date: 2026-11-12. The subject of the record is my plan to not bring two tickets to Henry, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "bring", "object": "ticket", "quantity": 2, "record_date": "2026-11-12", "event_date": "2026-11-17", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H2: Author: Emma. Record date: 2026-11-12. The subject of the record is my plan to not bring two tickets to Henry, with the event dated three days ago. This record does not establish that the event occurred.
joint=False; parsed={"author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "bring", "object": "ticket", "quantity": 2, "record_date": "2026-11-12", "event_date": "2026-11-16", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}; unresolved=False; date error=True; other fact error=False

Own step5: ToToToThreeTo three three three daysTo threeTo three days three three-ToTo three ToToTo pairToTo twoToTo 3ToToBiToTo3ToToTwoToToRTo two ToTo twoThreeToTo
Gold step5: Author: Emma. Record date: 2026-11-12. The subject of the record is my plan to not bring two tickets to Henry, with the event dated four days ago. This record does not establish that the event occurred.

## 6. natural_only: F2/44/iid/g13_iid_recorded_plan_0068

Current: Author: Emma. Record date: 2026-11-17. The record contains an account of my plan to not bring two books to Henry, with the event dated yesterday. This record does not establish that the event occurred.
Gold next: Author: Emma. Record date: 2026-11-17. The record contains an account of my plan to not bring two books to Henry, with the event dated two days ago. This record does not establish that the event occurred.
Own rollout first failure: 2

H0: Author: Emma. Record date: 2026-11-17. The record contains an account of my plan to not bring two books to Henry, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "bring", "object": "book", "quantity": 2, "record_date": "2026-11-17", "event_date": "2026-11-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H1: Author: Emma. Record date: 2026-11-17. The record contains an account of my plan to not bring two books to Henry, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "bring", "object": "book", "quantity": 2, "record_date": "2026-11-17", "event_date": "2026-11-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H2: Author: Emma. Record date: 2026-11-17. The record contains an account of my plan to not bring two books to Henry, with the event dated three days ago. This record does not establish that the event occurred.
joint=False; parsed={"author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "bring", "object": "book", "quantity": 2, "record_date": "2026-11-17", "event_date": "2026-11-21", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}; unresolved=False; date error=True; other fact error=False

Own step5: ToToToThreeTo three three daysTo threeTo three days three three threeToTo three ToTo threeThreeToTo twoTo three'To pairTo three84To three -To two To pairTo two respectiveTo two'To two84To two405 twoTo twoAbout twoTo
Gold step5: Author: Emma. Record date: 2026-11-17. The record contains an account of my plan to not bring two books to Henry, with the event dated four days ago. This record does not establish that the event occurred.

## 7. edited_only: F0/42/iid/g13_iid_recorded_plan_0027

Current: Author: Grace. Record date: 2026-12-02. My plan to give two parcels to Emma, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold next: Author: Grace. Record date: 2026-12-02. My plan to give two parcels to Emma, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Own rollout first failure: 1

H0: Author: Grace. Record date: 2026-12-02. My plan to give two parcels to Emma, with the event dated two parcels, is described in the record. This record does not establish that the event occurred.
joint=False; parsed=null; unresolved=True; date error=False; other fact error=False

H1: Author: Grace. Record date: 2026-12-02. My plan to give two parcels to Emma, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
joint=True; parsed={"author": "Grace", "actor": "Grace", "recipient": "Emma", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-12-02", "event_date": "2026-12-07", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Grace", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H2: Author: Grace. Record date: 2026-12-02. My plan to give two parcels to Emma, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
joint=True; parsed={"author": "Grace", "actor": "Grace", "recipient": "Emma", "action": "give", "object": "parcel", "quantity": 2, "record_date": "2026-12-02", "event_date": "2026-12-07", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Grace", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

Own step5: Author: Grace. Record date: 2026-12-02. My plan to give two parcels to Emma, with the event dated two days ago, is described in the record. This record does not establish that the record did not establish two days days ago two days two days
Gold step5: Author: Grace. Record date: 2026-12-02. My plan to give two parcels to Emma, with the event dated four days ago, is described in the record. This record does not establish that the event occurred.

## 8. edited_only: F0/42/iid/g13_iid_recorded_plan_0024

Current: Author: Frank. Record date: 2026-11-24. The record describes my plan to not give two books to Bob, with the event dated yesterday. This record does not establish that the event occurred.
Gold next: Author: Frank. Record date: 2026-11-24. The record describes my plan to not give two books to Bob, with the event dated two days ago. This record does not establish that the event occurred.
Own rollout first failure: 2

H0: Author: Frank. Record date: 2026-11-24. The record describes my plan to not give two books to Bob, with the event dated two books. This record does not establish that the event occurred.
joint=False; parsed=null; unresolved=True; date error=False; other fact error=False

H1: Author: Frank. Record date: 2026-11-24. The record describes my plan to not give two books to Bob, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Frank", "actor": "Frank", "recipient": "Bob", "action": "give", "object": "book", "quantity": 2, "record_date": "2026-11-24", "event_date": "2026-11-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H2: Author: Frank. Record date: 2026-11-24. The record describes my plan to not give two books to Bob, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Frank", "actor": "Frank", "recipient": "Bob", "action": "give", "object": "book", "quantity": 2, "record_date": "2026-11-24", "event_date": "2026-11-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

Own step5: Author: Frank. Record date: 2026-11-24. The record describes my plan to not give two books to Bob, with the event dated two days ago. This record does not establish that the event occurred two days days ago
Gold step5: Author: Frank. Record date: 2026-11-24. The record describes my plan to not give two books to Bob, with the event dated four days ago. This record does not establish that the event occurred.

## 9. edited_only: F0/42/iid/g13_iid_recorded_plan_0092

Current: Author: Grace. Record date: 2026-11-23. The record contains an account of my plan to not deliver two books to Alice, with the event dated yesterday. This record does not establish that the event occurred.
Gold next: Author: Grace. Record date: 2026-11-23. The record contains an account of my plan to not deliver two books to Alice, with the event dated two days ago. This record does not establish that the event occurred.
Own rollout first failure: 2

H0: Author: Grace. Record date: 2026-11-23. The record contains an account of my plan to not deliver two books to Alice, with the event dated two books. This record does not establish that the event occurred.
joint=False; parsed=null; unresolved=True; date error=False; other fact error=False

H1: Author: Grace. Record date: 2026-11-23. The record contains an account of my plan to not deliver two books to Alice, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Grace", "actor": "Grace", "recipient": "Alice", "action": "deliver", "object": "book", "quantity": 2, "record_date": "2026-11-23", "event_date": "2026-11-28", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H2: Author: Grace. Record date: 2026-11-23. The record contains an account of my plan to not deliver two books to Alice, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Grace", "actor": "Grace", "recipient": "Alice", "action": "deliver", "object": "book", "quantity": 2, "record_date": "2026-11-23", "event_date": "2026-11-28", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

Own step5: Author: Grace. Record date: 2026-11-23. The record contains an account of my plan to not deliver two books to Alice, with the event dated two days ago. This record does not establish that the event occurred.
Gold step5: Author: Grace. Record date: 2026-11-23. The record contains an account of my plan to not deliver two books to Alice, with the event dated four days ago. This record does not establish that the event occurred.

## 10. edited_only: F0/42/iid/g13_iid_recorded_plan_0019

Current: Author: Grace. Record date: 2026-10-18. My plan to send seven books to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold next: Author: Grace. Record date: 2026-10-18. My plan to send seven books to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Own rollout first failure: 2

H0: Author: Grace. Record date: 2026-10-18. My plan to send seven books to David, with the event dated two books to Mike, is described in the record. This record does not establish that the event occurred.
joint=False; parsed=null; unresolved=True; date error=False; other fact error=False

H1: Author: Grace. Record date: 2026-10-18. My plan to send seven books to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
joint=True; parsed={"author": "Grace", "actor": "Grace", "recipient": "David", "action": "send", "object": "book", "quantity": 7, "record_date": "2026-10-18", "event_date": "2026-10-23", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Grace", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H2: Author: Grace. Record date: 2026-10-18. My plan to send seven books to David, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
joint=True; parsed={"author": "Grace", "actor": "Grace", "recipient": "David", "action": "send", "object": "book", "quantity": 7, "record_date": "2026-10-18", "event_date": "2026-10-23", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Grace", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

Own step5: Author: Grace. Record date: 2026-10-18. My plan to send seven books to David, with the record dated two days ago, is described in the record. This record does not establish that the record two days days ago did not establish two days two days
Gold step5: Author: Grace. Record date: 2026-10-18. My plan to send seven books to David, with the event dated four days ago, is described in the record. This record does not establish that the event occurred.

## 11. edited_only: F0/42/template_ood/g13_template_ood_recorded_plan_0104

Current: Author: Emma. Record date: 2026-10-26. What the record describes for an event dated yesterday is my plan to not send two books to Henry. This record does not establish that the event occurred.
Gold next: Author: Emma. Record date: 2026-10-26. What the record describes for an event dated two days ago is my plan to not send two books to Henry. This record does not establish that the event occurred.
Own rollout first failure: 1

H0: Author: Emma. Record date: 2026-10-26. What the record describes for an event dated two books is my plan to not send two books to Henry. This record does not establish that the event occurred.
joint=False; parsed=null; unresolved=True; date error=False; other fact error=False

H1: Author: Emma. Record date: 2026-10-26. What the record describes for an event dated two days ago is my plan to not send two books to Henry. This record does not establish that the event occurred.
joint=True; parsed={"author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "send", "object": "book", "quantity": 2, "record_date": "2026-10-26", "event_date": "2026-10-31", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H2: Author: Emma. Record date: 2026-10-26. What the record describes for an event dated two days ago is my plan to not send two books to Henry. This record does not establish that the event occurred.
joint=True; parsed={"author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "send", "object": "book", "quantity": 2, "record_date": "2026-10-26", "event_date": "2026-10-31", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

Own step5: Author: Emma. Record date: 2026-10-26. What the record describes for an event dated two days ago is my plan to not send two books to Henry. This record does not establish that the event occurred two days days ago.
Gold step5: Author: Emma. Record date: 2026-10-26. What the record describes for an event dated four days ago is my plan to not send two books to Henry. This record does not establish that the event occurred.

## 12. edited_only: F0/42/iid/g13_iid_recorded_plan_0016

Current: Author: Henry. Record date: 2026-10-11. The record describes my plan to not send eight books to Bob, with the event dated yesterday. This record does not establish that the event occurred.
Gold next: Author: Henry. Record date: 2026-10-11. The record describes my plan to not send eight books to Bob, with the event dated two days ago. This record does not establish that the event occurred.
Own rollout first failure: 2

H0: Author: Henry. Record date: 2026-10-11. The record describes my plan to not send eight books to Bob, with the event dated two books to Dylan, with this record does not establish that the event occurred.
joint=False; parsed=null; unresolved=True; date error=False; other fact error=False

H1: Author: Henry. Record date: 2026-10-11. The record describes my plan to not send eight books to Bob, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Henry", "actor": "Henry", "recipient": "Bob", "action": "send", "object": "book", "quantity": 8, "record_date": "2026-10-11", "event_date": "2026-10-16", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Henry", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H2: Author: Henry. Record date: 2026-10-11. The record describes my plan to not send eight books to Bob, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Henry", "actor": "Henry", "recipient": "Bob", "action": "send", "object": "book", "quantity": 8, "record_date": "2026-10-11", "event_date": "2026-10-16", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Henry", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

Own step5: Author: Henry. Record date: 2026-10-11. The record describes my plan to not send eight books to Bob, with the event dated two days ago. This record does not establish that the event occurred two days days ago
Gold step5: Author: Henry. Record date: 2026-10-11. The record describes my plan to not send eight books to Bob, with the event dated four days ago. This record does not establish that the event occurred.

## 13. all3: F3/43/template_ood/g13_template_ood_recorded_plan_0132

Current: Author: Alice. Record date: 2026-12-11. What the record describes for an event dated yesterday is my plan to not send four parcels to Grace. This record does not establish that the event occurred.
Gold next: Author: Alice. Record date: 2026-12-11. What the record describes for an event dated two days ago is my plan to not send four parcels to Grace. This record does not establish that the event occurred.
Own rollout first failure: 2

H0: Author: Alice. Record date: 2026-12-11. What the record describes for an event dated two days ago is my plan to not send four parcels to Grace. This record does not establish that the event occurred.
joint=True; parsed={"author": "Alice", "actor": "Alice", "recipient": "Grace", "action": "send", "object": "parcel", "quantity": 4, "record_date": "2026-12-11", "event_date": "2026-12-16", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Alice", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H1: Author: Alice. Record date: 2026-12-11. What the record describes for an event dated two days ago is my plan to not send four parcels to Grace. This record does not establish that the event occurred.
joint=True; parsed={"author": "Alice", "actor": "Alice", "recipient": "Grace", "action": "send", "object": "parcel", "quantity": 4, "record_date": "2026-12-11", "event_date": "2026-12-16", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Alice", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H2: Author: Alice. Record date: 2026-12-11. What the record describes for an event dated two days ago is my plan to not send four parcels to Grace. This record does not establish that the event occurred.
joint=True; parsed={"author": "Alice", "actor": "Alice", "recipient": "Grace", "action": "send", "object": "parcel", "quantity": 4, "record_date": "2026-12-11", "event_date": "2026-12-16", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Alice", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

Own step5: Author: Alice. Record date 2 days two days two daysTwo days days 2 days ago - two days ago 2
Gold step5: Author: Alice. Record date: 2026-12-11. What the record describes for an event dated four days ago is my plan to not send four parcels to Grace. This record does not establish that the event occurred.

## 14. all3: F0/44/iid/g13_iid_recorded_plan_0112

Current: Author: Alice. Record date: 2026-12-01. The record describes my plan to not bring two tickets to Henry, with the event dated yesterday. This record does not establish that the event occurred.
Gold next: Author: Alice. Record date: 2026-12-01. The record describes my plan to not bring two tickets to Henry, with the event dated two days ago. This record does not establish that the event occurred.
Own rollout first failure: 2

H0: Author: Alice. Record date: 2026-12-01. The record describes my plan to not bring two tickets to Henry, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Alice", "actor": "Alice", "recipient": "Henry", "action": "bring", "object": "ticket", "quantity": 2, "record_date": "2026-12-01", "event_date": "2026-12-06", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Alice", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H1: Author: Alice. Record date: 2026-12-01. The record describes my plan to not bring two tickets to Henry, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Alice", "actor": "Alice", "recipient": "Henry", "action": "bring", "object": "ticket", "quantity": 2, "record_date": "2026-12-01", "event_date": "2026-12-06", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Alice", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H2: Author: Alice. Record date: 2026-12-01. The record describes my plan to not bring two tickets to Henry, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Alice", "actor": "Alice", "recipient": "Henry", "action": "bring", "object": "ticket", "quantity": 2, "record_date": "2026-12-01", "event_date": "2026-12-06", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Alice", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

Own step5: Author: Alice. Record date: 20 two 2 2 2 two days two days 2 two two days ago. Two days two two two 2 two 2 days ago two days days ago 2 2 days 2 2. This record does not establish that the event occurred two days
Gold step5: Author: Alice. Record date: 2026-12-01. The record describes my plan to not bring two tickets to Henry, with the event dated four days ago. This record does not establish that the event occurred.

## 15. all3: F0/44/iid/g13_iid_recorded_plan_0130

Current: Author: David. Record date: 2026-11-24. According to the record, my plan to not send two tickets to Alice concerns an event dated yesterday. This record does not establish that the event occurred.
Gold next: Author: David. Record date: 2026-11-24. According to the record, my plan to not send two tickets to Alice concerns an event dated two days ago. This record does not establish that the event occurred.
Own rollout first failure: 2

H0: Author: David. Record date: 2026-11-24. According to the record, my plan to not send two tickets to Alice concerns an event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "David", "actor": "David", "recipient": "Alice", "action": "send", "object": "ticket", "quantity": 2, "record_date": "2026-11-24", "event_date": "2026-11-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H1: Author: David. Record date: 2026-11-24. According to the record, my plan to not send two tickets to Alice concerns an event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "David", "actor": "David", "recipient": "Alice", "action": "send", "object": "ticket", "quantity": 2, "record_date": "2026-11-24", "event_date": "2026-11-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H2: Author: David. Record date: 2026-11-24. According to the record, my plan to not send two tickets to Alice concerns an event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "David", "actor": "David", "recipient": "Alice", "action": "send", "object": "ticket", "quantity": 2, "record_date": "2026-11-24", "event_date": "2026-11-29", "record_status": "recorded_plan", "polarity": "negative", "attribution": "David", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

Own step5: Author: David. Record date: 20 two 2 2 2 two days two days ago 2 2 days two two days 2 two two two 2 days ago. This record 2 22 2 2. This two days
Gold step5: Author: David. Record date: 2026-11-24. According to the record, my plan to not send two tickets to Alice concerns an event dated four days ago. This record does not establish that the event occurred.

## 16. all3: F1/44/template_ood/g13_template_ood_recorded_plan_0085

Current: Author: David. Record date: 2026-10-12. It is my plan to give three books to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Gold next: Author: David. Record date: 2026-10-12. It is my plan to give three books to Henry that the record describes for an event dated two days ago. This record does not establish that the event occurred.
Own rollout first failure: 2

H0: Author: David. Record date: 2026-10-12. It is my plan to give three books to Henry that the record describes for an event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "David", "actor": "David", "recipient": "Henry", "action": "give", "object": "book", "quantity": 3, "record_date": "2026-10-12", "event_date": "2026-10-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "David", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H1: Author: David. Record date: 2026-10-12. It is my plan to give three books to Henry that the record describes for an event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "David", "actor": "David", "recipient": "Henry", "action": "give", "object": "book", "quantity": 3, "record_date": "2026-10-12", "event_date": "2026-10-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "David", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H2: Author: David. Record date: 2026-10-12. It is my plan to give three books to Henry that the record describes for an event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "David", "actor": "David", "recipient": "Henry", "action": "give", "object": "book", "quantity": 3, "record_date": "2026-10-12", "event_date": "2026-10-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "David", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

Own step5: Author: David. Record date: 2026-2-2. It is two days two two daysTwo days two days ago, two days 2 days ago. This record 2
Gold step5: Author: David. Record date: 2026-10-12. It is my plan to give three books to Henry that the record describes for an event dated four days ago. This record does not establish that the event occurred.

## 17. all3: F3/44/iid/g13_iid_recorded_plan_0091

Current: Author: Grace. Record date: 2026-10-20. My plan to send eight tickets to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.
Gold next: Author: Grace. Record date: 2026-10-20. My plan to send eight tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
Own rollout first failure: 2

H0: Author: Grace. Record date: 2026-10-20. My plan to send eight tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
joint=True; parsed={"author": "Grace", "actor": "Grace", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 8, "record_date": "2026-10-20", "event_date": "2026-10-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Grace", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H1: Author: Grace. Record date: 2026-10-20. My plan to send eight tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
joint=True; parsed={"author": "Grace", "actor": "Grace", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 8, "record_date": "2026-10-20", "event_date": "2026-10-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Grace", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H2: Author: Grace. Record date: 2026-10-20. My plan to send eight tickets to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.
joint=True; parsed={"author": "Grace", "actor": "Grace", "recipient": "Henry", "action": "send", "object": "ticket", "quantity": 8, "record_date": "2026-10-20", "event_date": "2026-10-25", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Grace", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

Own step5: Author: 2 days ago 2 2 days two days two - two days ago. Two days 2 2 2 - two - days ago: 2 2-2. Two - days two two days days days 2
Gold step5: Author: Grace. Record date: 2026-10-20. My plan to send eight tickets to Henry, with the event dated four days ago, is described in the record. This record does not establish that the event occurred.

## 18. all3: F3/42/template_ood/g13_template_ood_recorded_plan_0092

Current: Author: Emma. Record date: 2026-10-15. What the record describes for an event dated yesterday is my plan to not bring eight tickets to Grace. This record does not establish that the event occurred.
Gold next: Author: Emma. Record date: 2026-10-15. What the record describes for an event dated two days ago is my plan to not bring eight tickets to Grace. This record does not establish that the event occurred.
Own rollout first failure: 2

H0: Author: Emma. Record date: 2026-10-15. What the record describes for an event dated two days ago is my plan to not bring eight tickets to Grace. This record does not establish that the event occurred.
joint=True; parsed={"author": "Emma", "actor": "Emma", "recipient": "Grace", "action": "bring", "object": "ticket", "quantity": 8, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H1: Author: Emma. Record date: 2026-10-15. What the record describes for an event dated two days ago is my plan to not bring eight tickets to Grace. This record does not establish that the event occurred.
joint=True; parsed={"author": "Emma", "actor": "Emma", "recipient": "Grace", "action": "bring", "object": "ticket", "quantity": 8, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H2: Author: Emma. Record date: 2026-10-15. What the record describes for an event dated two days ago is my plan to not bring eight tickets to Grace. This record does not establish that the event occurred.
joint=True; parsed={"author": "Emma", "actor": "Emma", "recipient": "Grace", "action": "bring", "object": "ticket", "quantity": 8, "record_date": "2026-10-15", "event_date": "2026-10-20", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

Own step5: Author: Emma. Record date: 2026-10-15. What the record describes for an event dated two days ago is my plan to not bring eight tickets to Grace. This record does not establish that the record three days days days
Gold step5: Author: Emma. Record date: 2026-10-15. What the record describes for an event dated four days ago is my plan to not bring eight tickets to Grace. This record does not establish that the event occurred.

## 19. fixed_success_rollout_failure: F1/43/template_ood/g13_template_ood_recorded_plan_0017

Current: Author: Carol. Record date: 2026-12-03. It is my plan to send four sensors to Grace that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Gold next: Author: Carol. Record date: 2026-12-03. It is my plan to send four sensors to Grace that the record describes for an event dated two days ago. This record does not establish that the event occurred.
Own rollout first failure: 2

H0: Author: Carol. Record date: 2026-12-03. It is my plan to send four sensors to Grace that the record describes for an event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Carol", "actor": "Carol", "recipient": "Grace", "action": "send", "object": "sensor", "quantity": 4, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H1: Author: Carol. Record date: 2026-12-03. It is my plan to send four sensors to Grace that the record describes two days ago. This record does not establish that the event occurred.
joint=False; parsed=null; unresolved=True; date error=False; other fact error=False

H2: Author: Carol. Record date: 2026-12-03. It is my plan to send four sensors to Grace that the record describes for an event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Carol", "actor": "Carol", "recipient": "Grace", "action": "send", "object": "sensor", "quantity": 4, "record_date": "2026-12-03", "event_date": "2026-12-08", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Carol", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

Own step5: Author: two days two days ago. Record date: 2026-two-two. It is my plan to send four sensors to two days days ago that the record describes two days that the two days pair of two days 2-two days ago2
Gold step5: Author: Carol. Record date: 2026-12-03. It is my plan to send four sensors to Grace that the record describes for an event dated four days ago. This record does not establish that the event occurred.

## 20. fixed_success_rollout_failure: F3/43/template_ood/g13_template_ood_recorded_plan_0136

Current: Author: Emma. Record date: 2026-12-06. What the record describes for an event dated yesterday is my plan to not bring two books to Henry. This record does not establish that the event occurred.
Gold next: Author: Emma. Record date: 2026-12-06. What the record describes for an event dated two days ago is my plan to not bring two books to Henry. This record does not establish that the event occurred.
Own rollout first failure: 2

H0: Author: Emma. Record date: 2026-12-06. What the record describes for an event dated two days ago is my plan to not bring two books to Henry. This record does not establish that the event occurred.
joint=True; parsed={"author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "bring", "object": "book", "quantity": 2, "record_date": "2026-12-06", "event_date": "2026-12-11", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H1: Author: Emma. Record date: 2026-12-06. What the record describes for an event dated two days ago is my plan to not bring two books to Henry. This record does not establish that the event occurred.
joint=True; parsed={"author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "bring", "object": "book", "quantity": 2, "record_date": "2026-12-06", "event_date": "2026-12-11", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H2: Author: Emma. Record date: 2026-12-06. What the record describes for an event dated two days ago is my plan to not bring two books to Henry. This record does not establish that the event occurred.
joint=True; parsed={"author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "bring", "object": "book", "quantity": 2, "record_date": "2026-12-06", "event_date": "2026-12-11", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

Own step5: Author: Emma. Record date 2 days two days two daysTwo days days 2 days ago - two days ago 2
Gold step5: Author: Emma. Record date: 2026-12-06. What the record describes for an event dated four days ago is my plan to not bring two books to Henry. This record does not establish that the event occurred.

## 21. fixed_success_rollout_failure: F0/43/template_ood/g13_template_ood_recorded_plan_0129

Current: Author: Grace. Record date: 2026-10-18. It is my plan to give five tickets to Carol that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Gold next: Author: Grace. Record date: 2026-10-18. It is my plan to give five tickets to Carol that the record describes for an event dated two days ago. This record does not establish that the event occurred.
Own rollout first failure: 1

H0: Author: Grace. Record date: 2026-10-18. It is my plan to give five tickets to Carol that the record describes for an event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Grace", "actor": "Grace", "recipient": "Carol", "action": "give", "object": "ticket", "quantity": 5, "record_date": "2026-10-18", "event_date": "2026-10-23", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Grace", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H1: Author: Grace. Record date: 2026-10-18. It is my plan to give five tickets to Carol that the record describes for an event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Grace", "actor": "Grace", "recipient": "Carol", "action": "give", "object": "ticket", "quantity": 5, "record_date": "2026-10-18", "event_date": "2026-10-23", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Grace", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H2: Author: Grace. Record date: 2026-10-18. It is my plan to give five tickets to Carol that the record describes for an event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Grace", "actor": "Grace", "recipient": "Carol", "action": "give", "object": "ticket", "quantity": 5, "record_date": "2026-10-18", "event_date": "2026-10-23", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Grace", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

Own step5: Author: Grace. Record date: 20 two days ago. Record two two days two days days ago two two two-day two days back two tickets to two that the record describes for an event dated two days that the two two posts two days. This record does not establish that the event occurred
Gold step5: Author: Grace. Record date: 2026-10-18. It is my plan to give five tickets to Carol that the record describes for an event dated four days ago. This record does not establish that the event occurred.

## 22. fixed_success_rollout_failure: F0/42/template_ood/g13_template_ood_recorded_plan_0014

Current: Author: Frank. Record date: 2026-10-11. As described in the record, my plan to not deliver five books to Bob has the event dated yesterday. This record does not establish that the event occurred.
Gold next: Author: Frank. Record date: 2026-10-11. As described in the record, my plan to not deliver five books to Bob has the event dated two days ago. This record does not establish that the event occurred.
Own rollout first failure: 1

H0: Author: Frank. Record date: 2026-10-11. As described in the record, my plan to not deliver five books to Bob has the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Frank", "actor": "Frank", "recipient": "Bob", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-10-11", "event_date": "2026-10-16", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H1: Author: Frank. Record date: 2026-10-11. As described in the record, my plan to not deliver five books to Bob has the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Frank", "actor": "Frank", "recipient": "Bob", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-10-11", "event_date": "2026-10-16", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H2: Author: Frank. Record date: 2026-10-11. As described in the record, my plan to not deliver five books to Bob has the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Frank", "actor": "Frank", "recipient": "Bob", "action": "deliver", "object": "book", "quantity": 5, "record_date": "2026-10-11", "event_date": "2026-10-16", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Frank", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

Own step5: Author: Frank. Record date: 2026-10-11. As described in two books, my plan to not deliver five books to Bob has the event dated two days ago. This record does not establish that the event occurred.
Gold step5: Author: Frank. Record date: 2026-10-11. As described in the record, my plan to not deliver five books to Bob has the event dated four days ago. This record does not establish that the event occurred.

## 23. fixed_success_rollout_failure: F0/42/iid/g13_iid_recorded_plan_0118

Current: Author: Carol. Record date: 2026-11-11. The subject of the record is my plan to not bring five sensors to Emma, with the event dated yesterday. This record does not establish that the event occurred.
Gold next: Author: Carol. Record date: 2026-11-11. The subject of the record is my plan to not bring five sensors to Emma, with the event dated two days ago. This record does not establish that the event occurred.
Own rollout first failure: 2

H0: Author: Carol. Record date: 2026-11-11. The subject of the record is my plan to not bring five sensors to Emma, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Carol", "actor": "Carol", "recipient": "Emma", "action": "bring", "object": "sensor", "quantity": 5, "record_date": "2026-11-11", "event_date": "2026-11-16", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H1: Author: Carol. Record date: 2026-11-11. The subject of the record is my plan to not bring five sensors to Emma, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Carol", "actor": "Carol", "recipient": "Emma", "action": "bring", "object": "sensor", "quantity": 5, "record_date": "2026-11-11", "event_date": "2026-11-16", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H2: Author: Carol. Record date: 2026-11-11. The subject of the record is my plan to not bring five sensors to Emma, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Carol", "actor": "Carol", "recipient": "Emma", "action": "bring", "object": "sensor", "quantity": 5, "record_date": "2026-11-11", "event_date": "2026-11-16", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

Own step5: Author: Carol. Record date: 2026-11-11. The subject of the record is my plan to not bring five sensors to Emma, with the event dated two days ago. This record does not establish that the event occurred.
Gold step5: Author: Carol. Record date: 2026-11-11. The subject of the record is my plan to not bring five sensors to Emma, with the event dated four days ago. This record does not establish that the event occurred.

## 24. fixed_success_rollout_failure: F3/43/iid/g13_iid_recorded_plan_0000

Current: Author: Emma. Record date: 2026-11-25. The record describes my plan to not deliver six sensors to Alice, with the event dated yesterday. This record does not establish that the event occurred.
Gold next: Author: Emma. Record date: 2026-11-25. The record describes my plan to not deliver six sensors to Alice, with the event dated two days ago. This record does not establish that the event occurred.
Own rollout first failure: 2

H0: Author: Emma. Record date: 2026-11-25. The record describes my plan to not deliver six sensors to Alice, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Emma", "actor": "Emma", "recipient": "Alice", "action": "deliver", "object": "sensor", "quantity": 6, "record_date": "2026-11-25", "event_date": "2026-11-30", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H1: Author: Emma. Record date: 2026-11-25. The record describes my plan to not deliver six sensors to Alice, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Emma", "actor": "Emma", "recipient": "Alice", "action": "deliver", "object": "sensor", "quantity": 6, "record_date": "2026-11-25", "event_date": "2026-11-30", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

H2: Author: Emma. Record date: 2026-11-25. The record describes my plan to not deliver six sensors to Alice, with the event dated two days ago. This record does not establish that the event occurred.
joint=True; parsed={"author": "Emma", "actor": "Emma", "recipient": "Alice", "action": "deliver", "object": "sensor", "quantity": 6, "record_date": "2026-11-25", "event_date": "2026-11-30", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma", "perspective": "first"}; unresolved=False; date error=False; other fact error=False

Own step5: Author: Emma. Record date: 2026-11-two. The record describes my two days days ago 2 2 days ago - - 2 days days ago Dis
Gold step5: Author: Emma. Record date: 2026-11-25. The record describes my plan to not deliver six sensors to Alice, with the event dated four days ago. This record does not establish that the event occurred.
