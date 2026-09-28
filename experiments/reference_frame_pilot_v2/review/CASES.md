# v2 解释性案例

以下19例是确定性便利抽样，用于解释覆盖收益、指定链修复、仍失败及事实损坏，不用于估计准确率；方法/路径不匿名，正式盲审另见blind_review.csv。判定为结构化自动检查，27例额外模型复核见model_review.md。

## 1. coverage_repair · v2_test_iid_0001 · G1 · plus_plus/decode_reencode

源：Author: Emma. Record date: 2026-11-29. The record describes my report of not bringing nine books to Carol, with the event dated two days ago.

各步框架：`[{"view_date": "2026-12-01", "perspective": "first"}, {"view_date": "2026-12-02", "perspective": "first"}, {"view_date": "2026-12-03", "perspective": "first"}]`

目标：Author: Emma. Record date: 2026-11-29. The record describes my report of not bringing nine books to Carol, with the event dated four days ago.

世界事实：`{"record_id": "v2_test_iid_0001", "author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "book", "quantity": 9, "record_date": "2026-11-29", "event_date": "2026-11-29", "record_status": "reported_completed", "polarity": "negative", "attribution": "Emma"}`

输出：Author: Emma. Record date: 2026-11-29. The record describes my report of not bringing nine books to Carol, with the event dated four days ago.

判定：joint=True，date=True，nondate=True，unresolved=False，normal_end=True。

配对对照 G0 输出：Author: Emma. Record date: 2026-11-29. The record describes my report of not bringing nine books to Carol, with the event dated three days ago.

配对对照joint=False。

## 2. coverage_repair · v2_test_iid_0004 · G1 · plus_plus/decode_reencode

源：Author: Henry. Record date: 2026-11-04. For an event dated two days ago, the record describes my report of delivering six books to Grace.

各步框架：`[{"view_date": "2026-11-06", "perspective": "first"}, {"view_date": "2026-11-07", "perspective": "first"}, {"view_date": "2026-11-08", "perspective": "first"}]`

目标：Author: Henry. Record date: 2026-11-04. For an event dated four days ago, the record describes my report of delivering six books to Grace.

世界事实：`{"record_id": "v2_test_iid_0004", "author": "Henry", "actor": "Henry", "recipient": "Grace", "action": "deliver", "object": "book", "quantity": 6, "record_date": "2026-11-04", "event_date": "2026-11-04", "record_status": "reported_completed", "polarity": "positive", "attribution": "Henry"}`

输出：Author: Henry. Record date: 2026-11-04. For an event dated four days ago, the record describes my report of delivering six books to Grace.

判定：joint=True，date=True，nondate=True，unresolved=False，normal_end=True。

配对对照 G0 输出：Author: Henry. Record date: 2026-11-04. For an event dated three days ago, the record describes my report of delivering six books to Grace.

配对对照joint=False。

## 3. coverage_repair · v2_test_iid_0012 · G1 · plus_plus/decode_reencode

源：Author: Grace. Record date: 2026-12-04. The record contains an account of my plan to not deliver three sensors to Emma, with the event dated two days ago. This record does not establish that the event occurred.

各步框架：`[{"view_date": "2026-12-11", "perspective": "first"}, {"view_date": "2026-12-12", "perspective": "first"}, {"view_date": "2026-12-13", "perspective": "first"}]`

目标：Author: Grace. Record date: 2026-12-04. The record contains an account of my plan to not deliver three sensors to Emma, with the event dated four days ago. This record does not establish that the event occurred.

世界事实：`{"record_id": "v2_test_iid_0012", "author": "Grace", "actor": "Grace", "recipient": "Emma", "action": "deliver", "object": "sensor", "quantity": 3, "record_date": "2026-12-04", "event_date": "2026-12-09", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace"}`

输出：Author: Grace. Record date: 2026-12-04. The record contains an account of my plan to not deliver three sensors to Emma, with the event dated four days ago. This record does not establish that the event occurred.

判定：joint=True，date=True，nondate=True，unresolved=False，normal_end=True。

配对对照 G0 输出：Author: Grace. Record date: 2026-12-04. The record contains an account of my plan to not deliver three sensors to Emma, with the event dated three days ago. This record does not establish that the event occurred.

配对对照joint=False。

## 4. coverage_repair · v2_test_iid_0013 · G1 · plus_plus/decode_reencode

源：Author: Alice. Record date: 2026-10-08. The record contains an account of my report of not bringing two parcels to Henry, with the event dated two days ago.

各步框架：`[{"view_date": "2026-10-10", "perspective": "first"}, {"view_date": "2026-10-11", "perspective": "first"}, {"view_date": "2026-10-12", "perspective": "first"}]`

目标：Author: Alice. Record date: 2026-10-08. The record contains an account of my report of not bringing two parcels to Henry, with the event dated four days ago.

世界事实：`{"record_id": "v2_test_iid_0013", "author": "Alice", "actor": "Alice", "recipient": "Henry", "action": "bring", "object": "parcel", "quantity": 2, "record_date": "2026-10-08", "event_date": "2026-10-08", "record_status": "reported_completed", "polarity": "negative", "attribution": "Alice"}`

输出：Author: Alice. Record date: 2026-10-08. The record contains an account of my report of not bringing two parcels to Henry, with the event dated four days ago.

判定：joint=True，date=True，nondate=True，unresolved=False，normal_end=True。

配对对照 G0 输出：Author: Alice. Record date: 2026-10-08. The record contains an account of my report of not bringing two parcels to Henry, with the event dated three days ago.

配对对照joint=False。

## 5. chain_repair · v2_test_iid_0000 · G2 · plus_plus/latent_chain

源：Author: Grace. Record date: 2026-11-23. The record describes my plan to not deliver five tickets to Carol, with the event dated today. This record does not establish that the event occurred.

各步框架：`[{"view_date": "2026-11-28", "perspective": "first"}, {"view_date": "2026-11-29", "perspective": "first"}, {"view_date": "2026-11-30", "perspective": "first"}]`

目标：Author: Grace. Record date: 2026-11-23. The record describes my plan to not deliver five tickets to Carol, with the event dated two days ago. This record does not establish that the event occurred.

世界事实：`{"record_id": "v2_test_iid_0000", "author": "Grace", "actor": "Grace", "recipient": "Carol", "action": "deliver", "object": "ticket", "quantity": 5, "record_date": "2026-11-23", "event_date": "2026-11-28", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace"}`

输出：Author: Grace. Record date: 2026-11-23. The record describes my plan to not deliver five tickets to Carol, with the event dated two days ago. This record does not establish that the event occurred.

判定：joint=True，date=True，nondate=True，unresolved=False，normal_end=True。

配对对照 G1 输出：Author: two three daysAuthor three two two two daysNone three days two two three two daysI three two three- daysComments three daysI two daysD three tomorrow4: tomorrow 4 four two daysSo four two tomorrowTRY three tomorrowI three days tomorrow

配对对照joint=False。

## 6. chain_repair · v2_test_iid_0001 · G2 · plus_plus/latent_chain

源：Author: Emma. Record date: 2026-11-29. The record describes my report of not bringing nine books to Carol, with the event dated two days ago.

各步框架：`[{"view_date": "2026-12-01", "perspective": "first"}, {"view_date": "2026-12-02", "perspective": "first"}, {"view_date": "2026-12-03", "perspective": "first"}]`

目标：Author: Emma. Record date: 2026-11-29. The record describes my report of not bringing nine books to Carol, with the event dated four days ago.

世界事实：`{"record_id": "v2_test_iid_0001", "author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "book", "quantity": 9, "record_date": "2026-11-29", "event_date": "2026-11-29", "record_status": "reported_completed", "polarity": "negative", "attribution": "Emma"}`

输出：Author: Emma. Record date: 2026-11-29. The record describes my report of not bringing nine books to Carol, with the event dated four days ago.

判定：joint=True，date=True，nondate=True，unresolved=False，normal_end=True。

配对对照 G1 输出：Author: two three three tomorrow three days are three days.

配对对照joint=False。

## 7. chain_repair · v2_test_iid_0002 · G2 · plus_plus/latent_chain

源：Author: Grace. Record date: 2026-10-25. The record describes my cancelled plan to not send four sensors to Bob, with the event dated tomorrow. This record does not establish that the event occurred.

各步框架：`[{"view_date": "2026-10-29", "perspective": "first"}, {"view_date": "2026-10-30", "perspective": "first"}, {"view_date": "2026-10-31", "perspective": "first"}]`

目标：Author: Grace. Record date: 2026-10-25. The record describes my cancelled plan to not send four sensors to Bob, with the event dated yesterday. This record does not establish that the event occurred.

世界事实：`{"record_id": "v2_test_iid_0002", "author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "sensor", "quantity": 4, "record_date": "2026-10-25", "event_date": "2026-10-30", "record_status": "reported_cancelled", "polarity": "negative", "attribution": "Grace"}`

输出：Author: Grace. Record date: 2026-10-25. The record describes my cancelled plan to not send four sensors to Bob, with the event dated yesterday. This record does not establish that the event occurred.

判定：joint=True，date=True，nondate=True，unresolved=False，normal_end=True。

配对对照 G1 输出：Author: two two two three two two days three two daysThree three two three three three two posts three four daysFour two three four two daysU daysNone4: This record does not not new three two levels does not separate three two more days tomorrowNone of two

配对对照joint=False。

## 8. chain_repair · v2_test_iid_0003 · G2 · plus_plus/latent_chain

源：Author: Alice. Record date: 2026-12-08. For an event dated yesterday, the record describes my plan to give one ticket to Carol. This record does not establish that the event occurred.

各步框架：`[{"view_date": "2026-12-14", "perspective": "first"}, {"view_date": "2026-12-15", "perspective": "first"}, {"view_date": "2026-12-16", "perspective": "first"}]`

目标：Author: Alice. Record date: 2026-12-08. For an event dated three days ago, the record describes my plan to give one ticket to Carol. This record does not establish that the event occurred.

世界事实：`{"record_id": "v2_test_iid_0003", "author": "Alice", "actor": "Alice", "recipient": "Carol", "action": "give", "object": "ticket", "quantity": 1, "record_date": "2026-12-08", "event_date": "2026-12-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice"}`

输出：Author: Alice. Record date: 2026-12-08. For an event dated three days ago, the record describes my plan to give one ticket to Carol. This record does not establish that the event occurred.

判定：joint=True，date=True，nondate=True，unresolved=False，normal_end=True。

配对对照 G1 输出：Author: Alice. Record four three three days two days two three two two days are two two two ground three two days,None three two three ground three three two things separate two days things separate days are not two days days are all sorts of two days more days are more three days

配对对照joint=False。

## 9. still_failed · v2_test_template_ood_0011 · G2 · plus_plus/latent_chain

源：Author: Henry. Record date: 2026-11-25. The event date assigned in the record to my cancelled plan to deliver four books to Frank is tomorrow. This record does not establish that the event occurred.

各步框架：`[{"view_date": "2026-11-29", "perspective": "first"}, {"view_date": "2026-11-30", "perspective": "first"}, {"view_date": "2026-12-01", "perspective": "first"}]`

目标：Author: Henry. Record date: 2026-11-25. The event date assigned in the record to my cancelled plan to deliver four books to Frank is yesterday. This record does not establish that the event occurred.

世界事实：`{"record_id": "v2_test_template_ood_0011", "author": "Henry", "actor": "Henry", "recipient": "Frank", "action": "deliver", "object": "book", "quantity": 4, "record_date": "2026-11-25", "event_date": "2026-11-30", "record_status": "reported_cancelled", "polarity": "positive", "attribution": "Henry"}`

输出：Author: Henry. Record date: 2026-11-25. The event date assigned in the record to my cancelled plan to deliver four books to Frank is today. This record does not establish that the event occurred.

判定：joint=False，date=False，nondate=True，unresolved=False，normal_end=True。

## 10. still_failed · v2_test_template_ood_0035 · G2 · plus_plus/latent_chain

源：Author: Alice. Record date: 2026-12-12. The event date assigned in the record to my cancelled plan to give one ticket to Henry is tomorrow. This record does not establish that the event occurred.

各步框架：`[{"view_date": "2026-12-16", "perspective": "first"}, {"view_date": "2026-12-17", "perspective": "first"}, {"view_date": "2026-12-18", "perspective": "first"}]`

目标：Author: Alice. Record date: 2026-12-12. The event date assigned in the record to my cancelled plan to give one ticket to Henry is yesterday. This record does not establish that the event occurred.

世界事实：`{"record_id": "v2_test_template_ood_0035", "author": "Alice", "actor": "Alice", "recipient": "Henry", "action": "give", "object": "ticket", "quantity": 1, "record_date": "2026-12-12", "event_date": "2026-12-17", "record_status": "reported_cancelled", "polarity": "positive", "attribution": "Alice"}`

输出：Author: Alice. Record date: 2026-12-12. The event date assigned in the record to my cancelled plan to give one ticket to Henry is today. This record does not establish that the event occurred.

判定：joint=False，date=False，nondate=True，unresolved=False，normal_end=True。

## 11. still_failed · v2_test_template_ood_0047 · G2 · plus_plus/latent_chain

源：Author: Bob. Record date: 2026-11-25. The event date assigned in the record to my cancelled plan to send eight parcels to Grace is tomorrow. This record does not establish that the event occurred.

各步框架：`[{"view_date": "2026-11-29", "perspective": "first"}, {"view_date": "2026-11-30", "perspective": "first"}, {"view_date": "2026-12-01", "perspective": "first"}]`

目标：Author: Bob. Record date: 2026-11-25. The event date assigned in the record to my cancelled plan to send eight parcels to Grace is yesterday. This record does not establish that the event occurred.

世界事实：`{"record_id": "v2_test_template_ood_0047", "author": "Bob", "actor": "Bob", "recipient": "Grace", "action": "send", "object": "parcel", "quantity": 8, "record_date": "2026-11-25", "event_date": "2026-11-30", "record_status": "reported_cancelled", "polarity": "positive", "attribution": "Bob"}`

输出：Author: Bob. Record date: 2026-11-25. The event date assigned in the record to my cancelled plan to send eight parcels to Grace is today. This record does not establish that the event occurred.

判定：joint=False，date=False，nondate=True，unresolved=False，normal_end=True。

## 12. still_failed · v2_test_template_ood_0057 · G2 · plus_plus/latent_chain

源：Author: Alice. Record date: 2026-11-07. The event date assigned in the record to my plan to send nine sensors to Emma is in two days. This record does not establish that the event occurred.

各步框架：`[{"view_date": "2026-11-10", "perspective": "first"}, {"view_date": "2026-11-11", "perspective": "first"}, {"view_date": "2026-11-12", "perspective": "first"}]`

目标：Author: Alice. Record date: 2026-11-07. The event date assigned in the record to my plan to send nine sensors to Emma is today. This record does not establish that the event occurred.

世界事实：`{"record_id": "v2_test_template_ood_0057", "author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "send", "object": "sensor", "quantity": 9, "record_date": "2026-11-07", "event_date": "2026-11-12", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice"}`

输出：Author: Alice. Record date: 2026-11-07. The event date assigned in the record to my plan to send nine sensors to Emma is in two days. This record does not establish that the event occurred.

判定：joint=False，date=False，nondate=True，unresolved=False，normal_end=True。

## 13. parsed_facts_damaged · v2_test_iid_0068 · G2 · plus_minus/latent_chain

源：Author: Bob. Record date: 2026-11-19. The subject of the record is my cancelled plan to not give seven parcels to Henry, with the event dated yesterday. This record does not establish that the event occurred.

各步框架：`[{"view_date": "2026-11-25", "perspective": "first"}, {"view_date": "2026-11-26", "perspective": "first"}, {"view_date": "2026-11-25", "perspective": "first"}]`

目标：Author: Bob. Record date: 2026-11-19. The subject of the record is my cancelled plan to not give seven parcels to Henry, with the event dated yesterday. This record does not establish that the event occurred.

世界事实：`{"record_id": "v2_test_iid_0068", "author": "Bob", "actor": "Bob", "recipient": "Henry", "action": "give", "object": "parcel", "quantity": 7, "record_date": "2026-11-19", "event_date": "2026-11-24", "record_status": "reported_cancelled", "polarity": "negative", "attribution": "Bob"}`

输出：Author: Bob. Record date: 2026-11-19. The subject of the record is my cancelled plan to not give four parcels to Henry, with the event dated yesterday. This record does not establish that the event occurred.

判定：joint=False，date=True，nondate=False，unresolved=False，normal_end=True。

## 14. parsed_facts_damaged · v2_test_iid_0026 · G2 · plus3/latent_chain

源：Author: Henry. Record date: 2026-12-05. The record describes my cancelled plan to not send two parcels to David, with the event dated yesterday. This record does not establish that the event occurred.

各步框架：`[{"view_date": "2026-12-11", "perspective": "first"}, {"view_date": "2026-12-12", "perspective": "first"}, {"view_date": "2026-12-13", "perspective": "first"}, {"view_date": "2026-12-14", "perspective": "first"}]`

目标：Author: Henry. Record date: 2026-12-05. The record describes my cancelled plan to not send two parcels to David, with the event dated four days ago. This record does not establish that the event occurred.

世界事实：`{"record_id": "v2_test_iid_0026", "author": "Henry", "actor": "Henry", "recipient": "David", "action": "send", "object": "parcel", "quantity": 2, "record_date": "2026-12-05", "event_date": "2026-12-10", "record_status": "reported_cancelled", "polarity": "negative", "attribution": "Henry"}`

输出：Author: Henry. Record date: 2026-12-05. The record describes my cancelled plan to not send four parcels to David, with the event dated three days ago. This record does not establish that the event occurred.

判定：joint=False，date=False，nondate=False，unresolved=False，normal_end=True。

## 15. parsed_facts_damaged · v2_test_template_ood_0064 · G2 · plus3/latent_chain

源：Author: Grace. Record date: 2026-11-20. It is my report of sending two books to Frank that the record describes for an event dated today.

各步框架：`[{"view_date": "2026-11-20", "perspective": "first"}, {"view_date": "2026-11-21", "perspective": "first"}, {"view_date": "2026-11-22", "perspective": "first"}, {"view_date": "2026-11-23", "perspective": "first"}]`

目标：Author: Grace. Record date: 2026-11-20. It is my report of sending two books to Frank that the record describes for an event dated three days ago.

世界事实：`{"record_id": "v2_test_template_ood_0064", "author": "Grace", "actor": "Grace", "recipient": "Frank", "action": "send", "object": "book", "quantity": 2, "record_date": "2026-11-20", "event_date": "2026-11-20", "record_status": "reported_completed", "polarity": "positive", "attribution": "Grace"}`

输出：Author: Grace. Record date: 2026-11-20. It is my report of sending four books to Frank that the record describes for an event dated two days ago.

判定：joint=False，date=False，nondate=False，unresolved=False，normal_end=True。

## 16. unresolved · v2_test_iid_0000 · G2 · minus_minus/latent_chain

源：Author: Grace. Record date: 2026-11-23. The record describes my plan to not deliver five tickets to Carol, with the event dated two days ago. This record does not establish that the event occurred.

各步框架：`[{"view_date": "2026-11-30", "perspective": "first"}, {"view_date": "2026-11-29", "perspective": "first"}, {"view_date": "2026-11-28", "perspective": "first"}]`

目标：Author: Grace. Record date: 2026-11-23. The record describes my plan to not deliver five tickets to Carol, with the event dated today. This record does not establish that the event occurred.

世界事实：`{"record_id": "v2_test_iid_0000", "author": "Grace", "actor": "Grace", "recipient": "Carol", "action": "deliver", "object": "ticket", "quantity": 5, "record_date": "2026-11-23", "event_date": "2026-11-28", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Grace"}`

输出：Author:

判定：joint=False，date=False，nondate=False，unresolved=True，normal_end=True。

## 17. unresolved · v2_test_iid_0001 · G2 · minus_minus/latent_chain

源：Author: Emma. Record date: 2026-11-29. The record describes my report of not bringing nine books to Carol, with the event dated two days ago.

各步框架：`[{"view_date": "2026-12-01", "perspective": "first"}, {"view_date": "2026-11-30", "perspective": "first"}, {"view_date": "2026-11-29", "perspective": "first"}]`

目标：Author: Emma. Record date: 2026-11-29. The record describes my report of not bringing nine books to Carol, with the event dated today.

世界事实：`{"record_id": "v2_test_iid_0001", "author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "bring", "object": "book", "quantity": 9, "record_date": "2026-11-29", "event_date": "2026-11-29", "record_status": "reported_completed", "polarity": "negative", "attribution": "Emma"}`

输出：

判定：joint=False，date=False，nondate=False，unresolved=True，normal_end=True。

## 18. unresolved · v2_test_iid_0002 · G2 · minus_minus/latent_chain

源：Author: Grace. Record date: 2026-10-25. The record describes my cancelled plan to not send four sensors to Bob, with the event dated today. This record does not establish that the event occurred.

各步框架：`[{"view_date": "2026-10-30", "perspective": "first"}, {"view_date": "2026-10-29", "perspective": "first"}, {"view_date": "2026-10-28", "perspective": "first"}]`

目标：Author: Grace. Record date: 2026-10-25. The record describes my cancelled plan to not send four sensors to Bob, with the event dated in two days. This record does not establish that the event occurred.

世界事实：`{"record_id": "v2_test_iid_0002", "author": "Grace", "actor": "Grace", "recipient": "Bob", "action": "send", "object": "sensor", "quantity": 4, "record_date": "2026-10-25", "event_date": "2026-10-30", "record_status": "reported_cancelled", "polarity": "negative", "attribution": "Grace"}`

输出：Author tomorrow

判定：joint=False，date=False，nondate=False，unresolved=True，normal_end=True。

## 19. unresolved · v2_test_iid_0003 · G2 · minus_minus/latent_chain

源：Author: Alice. Record date: 2026-12-08. For an event dated yesterday, the record describes my plan to give one ticket to Carol. This record does not establish that the event occurred.

各步框架：`[{"view_date": "2026-12-14", "perspective": "first"}, {"view_date": "2026-12-13", "perspective": "first"}, {"view_date": "2026-12-12", "perspective": "first"}]`

目标：Author: Alice. Record date: 2026-12-08. For an event dated tomorrow, the record describes my plan to give one ticket to Carol. This record does not establish that the event occurred.

世界事实：`{"record_id": "v2_test_iid_0003", "author": "Alice", "actor": "Alice", "recipient": "Carol", "action": "give", "object": "ticket", "quantity": 1, "record_date": "2026-12-08", "event_date": "2026-12-13", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice"}`

输出：Author: Alice. Record date: in two days

判定：joint=False，date=False，nondate=False，unresolved=True，normal_end=True。
