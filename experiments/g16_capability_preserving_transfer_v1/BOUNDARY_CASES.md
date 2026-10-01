# G-today 边界的事后描述案例

每seed/split在F-guard的G-source失败中按上面公开hash取首例；不存在则absent。不改变12个事前固定案例、模型选择、分母或指标。每例保留同世界E/P/G/U与自身/真实输出重编码控制。

## seed42 / iid / g16_iid_recorded_plan_0108

old/H0, actual_updates=50, joint=True, exact=True, full=NA, error=success, first_failure=NA, date_delta=0
Current: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated two days ago. This record does not establish that the event occurred.
Mask SHA: 679192cc32ad78ba6afeeba01f2f623ba97a8dbd7c6cb59b1e9b4f046fcd87ea; length=48; memory SHA: aa6e7aeb1da19d13df5301d845841a481868a0586a7253f28608db81123575be
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Emma", "action": "give", "object": "book", "quantity": 5, "record_date": "2026-12-02", "event_date": "2026-12-07", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

old/H1, actual_updates=50, joint=True, exact=True, full=NA, error=success, first_failure=NA, date_delta=0
Current: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated two days ago. This record does not establish that the event occurred.
Mask SHA: 679192cc32ad78ba6afeeba01f2f623ba97a8dbd7c6cb59b1e9b4f046fcd87ea; length=48; memory SHA: b98520626b845eaf2d62f63b43754f2848333463e5f3cdf6461f074a91efa8bf
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Emma", "action": "give", "object": "book", "quantity": 5, "record_date": "2026-12-02", "event_date": "2026-12-07", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

old/H2, actual_updates=50, joint=True, exact=True, full=NA, error=success, first_failure=NA, date_delta=0
Current: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated two days ago. This record does not establish that the event occurred.
Mask SHA: 679192cc32ad78ba6afeeba01f2f623ba97a8dbd7c6cb59b1e9b4f046fcd87ea; length=48; memory SHA: f9afdcbda4947a4bcb3432b5947960737830ed1e773097050328bdcdd6233b58
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Emma", "action": "give", "object": "book", "quantity": 5, "record_date": "2026-12-02", "event_date": "2026-12-07", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

fixed/E, actual_updates=50, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated yesterday. This record does not establish that the event occurred.
Mask SHA: 679192cc32ad78ba6afeeba01f2f623ba97a8dbd7c6cb59b1e9b4f046fcd87ea; length=48; memory SHA: acb5cbc53afd23f85ba07508e40575ae66bb46e76653696b0d83dae501080497
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Emma", "action": "give", "object": "book", "quantity": 5, "record_date": "2026-12-02", "event_date": "2026-12-07", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

fixed/P, actual_updates=50, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated yesterday. This record does not establish that the event occurred.
Mask SHA: 679192cc32ad78ba6afeeba01f2f623ba97a8dbd7c6cb59b1e9b4f046fcd87ea; length=48; memory SHA: efc94b0009766ba6b7756f205dd8ed1c6df7cce8b381e8ed096d6e4081f68256
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Emma", "action": "give", "object": "book", "quantity": 5, "record_date": "2026-12-02", "event_date": "2026-12-07", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

fixed/G, actual_updates=50, joint=False, exact=False, full=False, error=date_error, first_failure=NA, date_delta=-1
Current: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated yesterday. This record does not establish that the event occurred.
Mask SHA: 679192cc32ad78ba6afeeba01f2f623ba97a8dbd7c6cb59b1e9b4f046fcd87ea; length=48; memory SHA: 627d71881e114d42c16ac5e23a97f03c8371496817c3abd6b48e81e9fc382958
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Emma", "action": "give", "object": "book", "quantity": 5, "record_date": "2026-12-02", "event_date": "2026-12-06", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

fixed/U, actual_updates=50, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated yesterday. This record does not establish that the event occurred.
Mask SHA: 679192cc32ad78ba6afeeba01f2f623ba97a8dbd7c6cb59b1e9b4f046fcd87ea; length=48; memory SHA: 28c5089200f7e66c91370fccaf55f2efd3095199ac74311d46c6dd710b43f76e
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Emma", "action": "give", "object": "book", "quantity": 5, "record_date": "2026-12-02", "event_date": "2026-12-07", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

reset_fixed/P, actual_updates=50, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated yesterday. This record does not establish that the event occurred.
Mask SHA: 679192cc32ad78ba6afeeba01f2f623ba97a8dbd7c6cb59b1e9b4f046fcd87ea; length=48; memory SHA: acb5cbc53afd23f85ba07508e40575ae66bb46e76653696b0d83dae501080497
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Emma", "action": "give", "object": "book", "quantity": 5, "record_date": "2026-12-02", "event_date": "2026-12-07", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

reset_fixed/G, actual_updates=50, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated yesterday. This record does not establish that the event occurred.
Mask SHA: 679192cc32ad78ba6afeeba01f2f623ba97a8dbd7c6cb59b1e9b4f046fcd87ea; length=48; memory SHA: acb5cbc53afd23f85ba07508e40575ae66bb46e76653696b0d83dae501080497
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Emma", "action": "give", "object": "book", "quantity": 5, "record_date": "2026-12-02", "event_date": "2026-12-07", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

reset_fixed/U, actual_updates=50, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated yesterday. This record does not establish that the event occurred.
Mask SHA: 679192cc32ad78ba6afeeba01f2f623ba97a8dbd7c6cb59b1e9b4f046fcd87ea; length=48; memory SHA: acb5cbc53afd23f85ba07508e40575ae66bb46e76653696b0d83dae501080497
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Emma", "action": "give", "object": "book", "quantity": 5, "record_date": "2026-12-02", "event_date": "2026-12-07", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

self_first/Q, actual_updates=50, joint=True, exact=True, full=NA, error=success, first_failure=NA, date_delta=0
Current: natural tomorrow
Output: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated today. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated today. This record does not establish that the event occurred.
Mask SHA: 679192cc32ad78ba6afeeba01f2f623ba97a8dbd7c6cb59b1e9b4f046fcd87ea; length=48; memory SHA: 00cbc9068241f696b4be197931157488ba0994b73710f96c26757d01e4ede75c
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Emma", "action": "give", "object": "book", "quantity": 5, "record_date": "2026-12-02", "event_date": "2026-12-07", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

self_second/Q, actual_updates=50, joint=True, exact=True, full=True, error=success, first_failure=None, date_delta=0
Current: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated yesterday. This record does not establish that the event occurred.
Mask SHA: 679192cc32ad78ba6afeeba01f2f623ba97a8dbd7c6cb59b1e9b4f046fcd87ea; length=48; memory SHA: 3e3b49eaf58aeaf1e59248e99e2c136dabb7b8dd2e3e719dbf49f3945c4745e8
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Emma", "action": "give", "object": "book", "quantity": 5, "record_date": "2026-12-02", "event_date": "2026-12-07", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

reset_self/Q, actual_updates=50, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated today. This record does not establish that the event occurred.
Output: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Carol. Record date: 2026-12-02. The record contains an account of my plan to not give five books to Emma, with the event dated yesterday. This record does not establish that the event occurred.
Mask SHA: 679192cc32ad78ba6afeeba01f2f623ba97a8dbd7c6cb59b1e9b4f046fcd87ea; length=48; memory SHA: acb5cbc53afd23f85ba07508e40575ae66bb46e76653696b0d83dae501080497
Parsed: {"author": "Carol", "actor": "Carol", "recipient": "Emma", "action": "give", "object": "book", "quantity": 5, "record_date": "2026-12-02", "event_date": "2026-12-07", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Carol", "perspective": "first"}

## seed42 / template_ood / g16_template_ood_recorded_plan_0017

old/H0, actual_updates=50, joint=True, exact=True, full=NA, error=success, first_failure=NA, date_delta=0
Current: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated two days ago. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: 20fdebf8e81506960d68755dc7c9603b9f3384ea994c457c1e4ebdd9858c53f9
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "send", "object": "book", "quantity": 7, "record_date": "2026-10-12", "event_date": "2026-10-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

old/H1, actual_updates=50, joint=True, exact=True, full=NA, error=success, first_failure=NA, date_delta=0
Current: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated two days ago. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: af30e9cabc40321d6a507881775ecbde609853b1575b9389fde9bca2ea412007
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "send", "object": "book", "quantity": 7, "record_date": "2026-10-12", "event_date": "2026-10-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

old/H2, actual_updates=50, joint=True, exact=True, full=NA, error=success, first_failure=NA, date_delta=0
Current: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes today. This record does not establish that the event occurred. This track does not indicate that the three event occurred
Output: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated two days ago. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: 387def886262e37220812abf99166d3a8a7fa1eddef7d0d8ef4644bd4aedac28
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "send", "object": "book", "quantity": 7, "record_date": "2026-10-12", "event_date": "2026-10-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

fixed/E, actual_updates=50, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: d0ba68f476ffe1e59330b6005d32f3c4b350525dd3bb75abd1e33b2a514b7269
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "send", "object": "book", "quantity": 7, "record_date": "2026-10-12", "event_date": "2026-10-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

fixed/P, actual_updates=50, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: 613d973e2114b8c25b68f03ac08008b3f668e4495c1b6bec4bf979e5a5b3e0b7
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "send", "object": "book", "quantity": 7, "record_date": "2026-10-12", "event_date": "2026-10-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

fixed/G, actual_updates=50, joint=False, exact=False, full=False, error=date_error, first_failure=NA, date_delta=-1
Current: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: d8fcc3d3be2808685dca4baa479baf2ed7b137d5c041201bf0975b49f004a48e
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "send", "object": "book", "quantity": 7, "record_date": "2026-10-12", "event_date": "2026-10-16", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

fixed/U, actual_updates=50, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: bc09a6f5dd071b71779baba7617fb2646a5ab5d0ca668a24719cbe3cd003f16b
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "send", "object": "book", "quantity": 7, "record_date": "2026-10-12", "event_date": "2026-10-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

reset_fixed/P, actual_updates=50, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: d0ba68f476ffe1e59330b6005d32f3c4b350525dd3bb75abd1e33b2a514b7269
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "send", "object": "book", "quantity": 7, "record_date": "2026-10-12", "event_date": "2026-10-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

reset_fixed/G, actual_updates=50, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: d0ba68f476ffe1e59330b6005d32f3c4b350525dd3bb75abd1e33b2a514b7269
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "send", "object": "book", "quantity": 7, "record_date": "2026-10-12", "event_date": "2026-10-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

reset_fixed/U, actual_updates=50, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: d0ba68f476ffe1e59330b6005d32f3c4b350525dd3bb75abd1e33b2a514b7269
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "send", "object": "book", "quantity": 7, "record_date": "2026-10-12", "event_date": "2026-10-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

self_first/Q, actual_updates=50, joint=True, exact=True, full=NA, error=success, first_failure=NA, date_delta=0
Current: natural tomorrow
Output: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated today. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated today. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: e27d3d2bc7bf45c35f48340351b3ca9c12fb0acbdf6efc5ff2fe9d5fccb6b9ef
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "send", "object": "book", "quantity": 7, "record_date": "2026-10-12", "event_date": "2026-10-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

self_second/Q, actual_updates=50, joint=True, exact=True, full=True, error=success, first_failure=None, date_delta=0
Current: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: 8d67763cc276ce586ed5aa9a073fa661ea8287eb928701ff06b5f1225f1eab45
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "send", "object": "book", "quantity": 7, "record_date": "2026-10-12", "event_date": "2026-10-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

reset_self/Q, actual_updates=50, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-10-12. It is my plan to send seven books to Carol that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: d0ba68f476ffe1e59330b6005d32f3c4b350525dd3bb75abd1e33b2a514b7269
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "send", "object": "book", "quantity": 7, "record_date": "2026-10-12", "event_date": "2026-10-17", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

## seed43 / iid / g16_iid_recorded_plan_0096

old/H0, actual_updates=25, joint=True, exact=True, full=NA, error=success, first_failure=NA, date_delta=0
Current: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated two days ago. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: cbb5167ec3a19d4c6034727df5e2e53cedb29189b35869f0f84ea0126c35d94a
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "send", "object": "parcel", "quantity": 3, "record_date": "2026-10-10", "event_date": "2026-10-15", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

old/H1, actual_updates=25, joint=True, exact=True, full=NA, error=success, first_failure=NA, date_delta=0
Current: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated two days ago. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: e08e4e09e2f1984222e57468c197db05f122aab5a2601c93562f5b21ee090942
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "send", "object": "parcel", "quantity": 3, "record_date": "2026-10-10", "event_date": "2026-10-15", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

old/H2, actual_updates=25, joint=True, exact=True, full=NA, error=success, first_failure=NA, date_delta=0
Current: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated yesterday. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated two days ago. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: 857525781068cb3acb32552318d7eb98700feb0d38f08ce53c3e6df18c964ce8
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "send", "object": "parcel", "quantity": 3, "record_date": "2026-10-10", "event_date": "2026-10-15", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

fixed/E, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: fb09ee09553ec8a8a598d46bc474618f1eb864586a5c13fa863513184700b91b
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "send", "object": "parcel", "quantity": 3, "record_date": "2026-10-10", "event_date": "2026-10-15", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

fixed/P, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: c5a2169dfb087c45d577afcb642d667e1cc4aba9ec48b5811ef775b9c0c7cd82
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "send", "object": "parcel", "quantity": 3, "record_date": "2026-10-10", "event_date": "2026-10-15", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

fixed/G, actual_updates=25, joint=False, exact=False, full=False, error=date_error, first_failure=NA, date_delta=-1
Current: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: 84b5960240f8834d186a193a3335ee52e069f075061672563f40ef03e9416816
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "send", "object": "parcel", "quantity": 3, "record_date": "2026-10-10", "event_date": "2026-10-14", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

fixed/U, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: cae6462b50c66be0fb79e893e663cbf6c6c5b96708e62ceb233713db2d6e6cff
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "send", "object": "parcel", "quantity": 3, "record_date": "2026-10-10", "event_date": "2026-10-15", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

reset_fixed/P, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: fb09ee09553ec8a8a598d46bc474618f1eb864586a5c13fa863513184700b91b
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "send", "object": "parcel", "quantity": 3, "record_date": "2026-10-10", "event_date": "2026-10-15", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

reset_fixed/G, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: fb09ee09553ec8a8a598d46bc474618f1eb864586a5c13fa863513184700b91b
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "send", "object": "parcel", "quantity": 3, "record_date": "2026-10-10", "event_date": "2026-10-15", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

reset_fixed/U, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: fb09ee09553ec8a8a598d46bc474618f1eb864586a5c13fa863513184700b91b
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "send", "object": "parcel", "quantity": 3, "record_date": "2026-10-10", "event_date": "2026-10-15", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

self_first/Q, actual_updates=25, joint=True, exact=True, full=NA, error=success, first_failure=NA, date_delta=0
Current: natural tomorrow
Output: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated today. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated today. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: 2ec74d5a6f060fa38c154f4e7dc26e24c192862889b2aad1590c9e3b9d91185f
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "send", "object": "parcel", "quantity": 3, "record_date": "2026-10-10", "event_date": "2026-10-15", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

self_second/Q, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=None, date_delta=0
Current: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: a5e248e4d7975656986d6fe67e7c27efc6e3c6f65d2a385b768e53f613674ab4
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "send", "object": "parcel", "quantity": 3, "record_date": "2026-10-10", "event_date": "2026-10-15", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

reset_self/Q, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated today. This record does not establish that the event occurred.
Output: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Bob. Record date: 2026-10-10. The record describes my plan to not send three parcels to Carol, with the event dated yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: fb09ee09553ec8a8a598d46bc474618f1eb864586a5c13fa863513184700b91b
Parsed: {"author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "send", "object": "parcel", "quantity": 3, "record_date": "2026-10-10", "event_date": "2026-10-15", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob", "perspective": "first"}

## seed43 / template_ood / g16_template_ood_recorded_plan_0077

old/H0, actual_updates=25, joint=True, exact=True, full=NA, error=success, first_failure=NA, date_delta=0
Current: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated two days ago. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: 7f9187571bd7aaaeb7815b82ba93b924cab8cad33605329087d41d55c248e07e
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "deliver", "object": "book", "quantity": 9, "record_date": "2026-11-19", "event_date": "2026-11-24", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

old/H1, actual_updates=25, joint=True, exact=True, full=NA, error=success, first_failure=NA, date_delta=0
Current: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated two days ago. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: 0ddd87e538553dcd20fc65173463f207f8dc57a33b2ddb88ac3b3c8035ddd5ff
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "deliver", "object": "book", "quantity": 9, "record_date": "2026-11-19", "event_date": "2026-11-24", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

old/H2, actual_updates=25, joint=True, exact=True, full=NA, error=success, first_failure=NA, date_delta=0
Current: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated two days ago. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: 06729841bfe4660b20c618bfdac2d8612f674d9e3097405bca9aaf6bc59413a0
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "deliver", "object": "book", "quantity": 9, "record_date": "2026-11-19", "event_date": "2026-11-24", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

fixed/E, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: c7268fbf24eeb6066c8f5c3bd37246e761b2d1def98b371a3f918ebae2e858d0
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "deliver", "object": "book", "quantity": 9, "record_date": "2026-11-19", "event_date": "2026-11-24", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

fixed/P, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: 45f10710c5e53af88e2b3f614540d411f38998856fd2dd83f0e9a539c9b7d84f
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "deliver", "object": "book", "quantity": 9, "record_date": "2026-11-19", "event_date": "2026-11-24", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

fixed/G, actual_updates=25, joint=False, exact=False, full=False, error=date_error, first_failure=NA, date_delta=-1
Current: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated two days ago. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: a0bce60dff8bcbeaa8788a7c9e9e9dc9f66cacc5827d5aec373adc9a4879befc
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "deliver", "object": "book", "quantity": 9, "record_date": "2026-11-19", "event_date": "2026-11-23", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

fixed/U, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: ecac350a6a7519ba6dbd368e3c624a8a75da02d058b600e8bda66bce929bbfc9
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "deliver", "object": "book", "quantity": 9, "record_date": "2026-11-19", "event_date": "2026-11-24", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

reset_fixed/P, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: c7268fbf24eeb6066c8f5c3bd37246e761b2d1def98b371a3f918ebae2e858d0
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "deliver", "object": "book", "quantity": 9, "record_date": "2026-11-19", "event_date": "2026-11-24", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

reset_fixed/G, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: c7268fbf24eeb6066c8f5c3bd37246e761b2d1def98b371a3f918ebae2e858d0
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "deliver", "object": "book", "quantity": 9, "record_date": "2026-11-19", "event_date": "2026-11-24", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

reset_fixed/U, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: c7268fbf24eeb6066c8f5c3bd37246e761b2d1def98b371a3f918ebae2e858d0
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "deliver", "object": "book", "quantity": 9, "record_date": "2026-11-19", "event_date": "2026-11-24", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

self_first/Q, actual_updates=25, joint=True, exact=True, full=NA, error=success, first_failure=NA, date_delta=0
Current: natural tomorrow
Output: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated today. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated today. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: 263672d67351d933fe7d12d307df670817348655d9d26d893bc723c72c15ca65
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "deliver", "object": "book", "quantity": 9, "record_date": "2026-11-19", "event_date": "2026-11-24", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

self_second/Q, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=None, date_delta=0
Current: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: ded7e374bf5696cbc626facc8f6e4f60e874e2e9f5e9603b1f7db5d511ce6a03
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "deliver", "object": "book", "quantity": 9, "record_date": "2026-11-19", "event_date": "2026-11-24", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

reset_self/Q, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated today. This record does not establish that the event occurred.
Output: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Gold: Author: Emma. Record date: 2026-11-19. It is my plan to deliver nine books to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.
Mask SHA: c7f3b80272e39b0c3b9d780c0cee314a2931f39cdbacb84a0ee9fb6976ee9efd; length=46; memory SHA: c7268fbf24eeb6066c8f5c3bd37246e761b2d1def98b371a3f918ebae2e858d0
Parsed: {"author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "deliver", "object": "book", "quantity": 9, "record_date": "2026-11-19", "event_date": "2026-11-24", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma", "perspective": "first"}

## seed44 / iid / g16_iid_recorded_plan_0053

old/H0, actual_updates=25, joint=True, exact=True, full=NA, error=success, first_failure=NA, date_delta=0
Current: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of yesterday. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of two days ago. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of two days ago. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: 2f78faf13e3c5dd7d575004617d67707b6987de0254114542f8f28bc9e538ea1
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 7, "record_date": "2026-12-11", "event_date": "2026-12-16", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

old/H1, actual_updates=25, joint=True, exact=True, full=NA, error=success, first_failure=NA, date_delta=0
Current: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of yesterday. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of two days ago. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of two days ago. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: b281a8cf35430f1271144e35d9f8decaaaea337693a28f8c50b86abfa1a26597
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 7, "record_date": "2026-12-11", "event_date": "2026-12-16", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

old/H2, actual_updates=25, joint=True, exact=True, full=NA, error=success, first_failure=NA, date_delta=0
Current: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of yesterday. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of two days ago. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of two days ago. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: 7d827e9b09721ad20bd62ab367304381f045e8938440eb1c85c8892347aaf944
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 7, "record_date": "2026-12-11", "event_date": "2026-12-16", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

fixed/E, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: a724bc198e243a4a78c69d7901edcd9459af53e701d906715be0321928f6b1a0
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 7, "record_date": "2026-12-11", "event_date": "2026-12-16", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

fixed/P, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: f7df487cb12386515812c9e6945ab6560fa9d9795ddf4a9a2e1254fabc00348e
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 7, "record_date": "2026-12-11", "event_date": "2026-12-16", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

fixed/G, actual_updates=25, joint=False, exact=False, full=False, error=date_error, first_failure=NA, date_delta=-1
Current: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of two days ago. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: 00a3cc68cee980986f5deb2aed91cbbee5647fae68e8ab3029b90732aa6e11ad
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 7, "record_date": "2026-12-11", "event_date": "2026-12-15", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

fixed/U, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: ecf4d66c3ac7e6c502ccea94c46ffb419735a3c0b0713c78dbb7e08c27593f29
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 7, "record_date": "2026-12-11", "event_date": "2026-12-16", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

reset_fixed/P, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: a724bc198e243a4a78c69d7901edcd9459af53e701d906715be0321928f6b1a0
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 7, "record_date": "2026-12-11", "event_date": "2026-12-16", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

reset_fixed/G, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: a724bc198e243a4a78c69d7901edcd9459af53e701d906715be0321928f6b1a0
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 7, "record_date": "2026-12-11", "event_date": "2026-12-16", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

reset_fixed/U, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: a724bc198e243a4a78c69d7901edcd9459af53e701d906715be0321928f6b1a0
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 7, "record_date": "2026-12-11", "event_date": "2026-12-16", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

self_first/Q, actual_updates=25, joint=True, exact=True, full=NA, error=success, first_failure=NA, date_delta=0
Current: natural tomorrow
Output: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of today. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of today. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: d8d9ddc35de7b5f9ee465bc03f9e6dd7ec4f0413746c84df9ef7318b1974c88a
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 7, "record_date": "2026-12-11", "event_date": "2026-12-16", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

self_second/Q, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=None, date_delta=0
Current: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: 54abd04ed36b7e488c32fe005cdaaec088f832c52135f53a4a39617628a55dde
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 7, "record_date": "2026-12-11", "event_date": "2026-12-16", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

reset_self/Q, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-12-11. In the record, my plan to bring seven tickets to Carol has an event date of yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: a724bc198e243a4a78c69d7901edcd9459af53e701d906715be0321928f6b1a0
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Carol", "action": "bring", "object": "ticket", "quantity": 7, "record_date": "2026-12-11", "event_date": "2026-12-16", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

## seed44 / template_ood / g16_template_ood_recorded_plan_0019

old/H0, actual_updates=25, joint=False, exact=False, full=NA, error=date_error, first_failure=NA, date_delta=2
Current: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is yesterday. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is today. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is two days ago. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: 79a80398553831c8cbcf92c7a674e7c12e5aa53464fb36c497a0077d00ee87c1
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Grace", "action": "send", "object": "sensor", "quantity": 4, "record_date": "2026-10-23", "event_date": "2026-10-30", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

old/H1, actual_updates=25, joint=True, exact=True, full=NA, error=success, first_failure=NA, date_delta=0
Current: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is two days ago. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is two days ago. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: fd12caaa6a7ff513ad79bc731b50a4379a3b6edd3638d27d37a3d81edcf057ae
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Grace", "action": "send", "object": "sensor", "quantity": 4, "record_date": "2026-10-23", "event_date": "2026-10-28", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

old/H2, actual_updates=25, joint=True, exact=True, full=NA, error=success, first_failure=NA, date_delta=0
Current: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is two days ago. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is two days ago. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: 37bf64c7400e7b9ad25b74ce7d6c04e256e5fb66e981bd7ef074a7b58ada7218
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Grace", "action": "send", "object": "sensor", "quantity": 4, "record_date": "2026-10-23", "event_date": "2026-10-28", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

fixed/E, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: 372deddfd0af78809b56add641552e0f8371440058d47e8f1562cce1d3d716f5
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Grace", "action": "send", "object": "sensor", "quantity": 4, "record_date": "2026-10-23", "event_date": "2026-10-28", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

fixed/P, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: 2c1700f97f60a140a2745730d857731cb143d76c229c0a78b65c79fffae57536
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Grace", "action": "send", "object": "sensor", "quantity": 4, "record_date": "2026-10-23", "event_date": "2026-10-28", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

fixed/G, actual_updates=25, joint=False, exact=False, full=False, error=date_error, first_failure=NA, date_delta=-1
Current: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is two days ago. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: 443f33929e9789464000c4c3acebe4229e0571f657987cfcfed707a36df96331
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Grace", "action": "send", "object": "sensor", "quantity": 4, "record_date": "2026-10-23", "event_date": "2026-10-27", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

fixed/U, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: 53dce90fa20bac7b2c1f0a7866bca5b7cfe34e40c96b1bc6817993012862aa51
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Grace", "action": "send", "object": "sensor", "quantity": 4, "record_date": "2026-10-23", "event_date": "2026-10-28", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

reset_fixed/P, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: 372deddfd0af78809b56add641552e0f8371440058d47e8f1562cce1d3d716f5
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Grace", "action": "send", "object": "sensor", "quantity": 4, "record_date": "2026-10-23", "event_date": "2026-10-28", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

reset_fixed/G, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: 372deddfd0af78809b56add641552e0f8371440058d47e8f1562cce1d3d716f5
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Grace", "action": "send", "object": "sensor", "quantity": 4, "record_date": "2026-10-23", "event_date": "2026-10-28", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

reset_fixed/U, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: 372deddfd0af78809b56add641552e0f8371440058d47e8f1562cce1d3d716f5
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Grace", "action": "send", "object": "sensor", "quantity": 4, "record_date": "2026-10-23", "event_date": "2026-10-28", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

self_first/Q, actual_updates=25, joint=True, exact=True, full=NA, error=success, first_failure=NA, date_delta=0
Current: natural tomorrow
Output: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is today. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is today. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: 1ebdf924f635f75aa6b9ff95ce176123f0c9f43207f3848b16016a493d00c67b
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Grace", "action": "send", "object": "sensor", "quantity": 4, "record_date": "2026-10-23", "event_date": "2026-10-28", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

self_second/Q, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=None, date_delta=0
Current: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: 2f5b8f3d3b5a3e363c02ba8c1dd159a655570340c93b6fd1c27fbfd60c2e1afd
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Grace", "action": "send", "object": "sensor", "quantity": 4, "record_date": "2026-10-23", "event_date": "2026-10-28", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}

reset_self/Q, actual_updates=25, joint=True, exact=True, full=True, error=success, first_failure=NA, date_delta=0
Current: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is today. This record does not establish that the event occurred.
Output: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is yesterday. This record does not establish that the event occurred.
Gold: Author: Alice. Record date: 2026-10-23. The event date assigned in the record to my plan to send four sensors to Grace is yesterday. This record does not establish that the event occurred.
Mask SHA: f8471d776a8df02b40adf57335c6a0b4979cee533a9e16242b9954dab378da17; length=45; memory SHA: 372deddfd0af78809b56add641552e0f8371440058d47e8f1562cce1d3d716f5
Parsed: {"author": "Alice", "actor": "Alice", "recipient": "Grace", "action": "send", "object": "sensor", "quantity": 4, "record_date": "2026-10-23", "event_date": "2026-10-28", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice", "perspective": "first"}
