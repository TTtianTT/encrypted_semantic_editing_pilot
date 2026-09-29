# 配对案例（便利抽样；不是准确率估计）

human_label为空，尚无真人审核。


## 1. reconstruction_failure / flan-t5-base

源：Author: Bob. Record date: 2026-11-01. The record describes my plan to not give one book to Emma, with the event dated four days ago. This record does not establish that the event occurred.

输出：No

判定：{"frame_ok": false, "content_ok": false, "readable": false, "joint_ok": false, "collateral_error": false, "plan_to_completed": false, "parse_unresolved": true, "uncertain_reason": "header_or_extra_text", "parsed": null, "hit_length_limit": false, "date_ok": false, "perspective_ok": false, "nondate_facts_ok": false, "normal_end": true, "parsed_nondate_error": false, "parsed_date_error": false}


## 2. reconstruction_failure / t5gemma-2-270m-270m

源：Author: Bob. Record date: 2026-11-01. The record describes my plan to not give one book to Emma, with the event dated four days ago. This record does not establish that the event occurred.

输出：
<unused6236>
Record: 11/01/2026
Record date: 11/01/2026
Record: 11/01/2026
Record: 11/01/2026
Record: 11

判定：{"frame_ok": false, "content_ok": false, "readable": false, "joint_ok": false, "collateral_error": false, "plan_to_completed": false, "parse_unresolved": true, "uncertain_reason": "header_or_extra_text", "parsed": null, "hit_length_limit": true, "date_ok": false, "perspective_ok": false, "nondate_facts_ok": false, "normal_end": false, "parsed_nondate_error": false, "parsed_date_error": false}


## 3. reconstruction_failure / flan-t5-large

源：Author: Bob. Record date: 2026-11-08. It is Bob's cancelled plan to bring three books to Grace that the record describes for an event dated four days ago. This record does not establish that the event occurred.

输出：Author: Bob. Record date: 2026-11-08 It is Bob's cancelled plan to bring three books to Grace that the record describes for an event dated four days ago. This record does not establish that the event occurred.

判定：{"frame_ok": false, "content_ok": false, "readable": false, "joint_ok": false, "collateral_error": false, "plan_to_completed": false, "parse_unresolved": true, "uncertain_reason": "header_or_extra_text", "parsed": null, "hit_length_limit": false, "date_ok": false, "perspective_ok": false, "nondate_facts_ok": false, "normal_end": true, "parsed_nondate_error": false, "parsed_date_error": false}


## 4. single_success_chain_failure / BART

源：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated two days ago. This record does not establish that the event occurred.

框架：[{"view_date": "2026-12-13", "perspective": "first"}, {"view_date": "2026-12-14", "perspective": "first"}, {"view_date": "2026-12-15", "perspective": "first"}]

G1 / latent_chain

第1步目标：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated three days ago. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated three days ago. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated four days ago. This record does not establish that the event occurred.

实际：Author: two twoAuthor three three three days four days days daysAuthor two three three two three four days four four days three days days are three days are two three days three three four four four three days things are three straight days days four three two days days three four three three are

joint=False, unresolved=True

G3 / latent_chain

第1步目标：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated three days ago. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated three days ago. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated four days ago. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated four days ago. This record does not establish that the event occurred.

joint=True, unresolved=False

G1 / decode_reencode

第1步目标：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated three days ago. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated three days ago. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated four days ago. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated four days ago. This record does not establish that the event occurred.

joint=True, unresolved=False


## 5. single_success_chain_failure / t5gemma-2b-2b-ul2-it

源：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated two days ago. This record does not establish that the event occurred.

框架：[{"view_date": "2026-12-13", "perspective": "first"}, {"view_date": "2026-12-14", "perspective": "first"}, {"view_date": "2026-12-15", "perspective": "first"}]

G1 / latent_chain

第1步目标：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated three days ago. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated three days ago. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated four days ago. This record does not establish that the event occurred.

实际：Author:

joint=False, unresolved=True

G3 / latent_chain

第1步目标：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated three days ago. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated three days ago. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated four days ago. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated four days ago. This record does not establish that the event occurred.

joint=True, unresolved=False

G1 / decode_reencode

第1步目标：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated three days ago. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated three days ago. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated four days ago. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated four days ago. This record does not establish that the event occurred.

joint=True, unresolved=False


## 6. reencode_recovers / BART

源：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated today.

框架：[{"view_date": "2026-10-28", "perspective": "first"}, {"view_date": "2026-10-29", "perspective": "first"}, {"view_date": "2026-10-30", "perspective": "first"}]

G1 / latent_chain

第1步目标：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated yesterday.

实际：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated yesterday.

joint=True, unresolved=False

第2步目标：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated two days ago.

实际：Author: two three daysAuthor three todayAuthor two todayThree three tomorrowAuthor four tomorrowNone three days three days two daysNone two days three three days tomorrowThree four two two two three two two more days tomorrowI two days tomorrow

joint=False, unresolved=True

G3 / latent_chain

第1步目标：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated yesterday.

实际：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated yesterday.

joint=True, unresolved=False

第2步目标：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated two days ago.

实际：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated two days ago.

joint=True, unresolved=False

G1 / decode_reencode

第1步目标：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated yesterday.

实际：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated yesterday.

joint=True, unresolved=False

第2步目标：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated two days ago.

实际：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated two days ago.

joint=True, unresolved=False


## 7. reencode_recovers / t5gemma-2b-2b-ul2-it

源：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated today.

框架：[{"view_date": "2026-10-28", "perspective": "first"}, {"view_date": "2026-10-29", "perspective": "first"}, {"view_date": "2026-10-30", "perspective": "first"}]

G1 / latent_chain

第1步目标：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated yesterday.

实际：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated yesterday.

joint=True, unresolved=False

第2步目标：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated two days ago.

实际：Author:

joint=False, unresolved=True

G3 / latent_chain

第1步目标：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated yesterday.

实际：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated yesterday.

joint=True, unresolved=False

第2步目标：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated two days ago.

实际：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated two days ago.

joint=True, unresolved=False

G1 / decode_reencode

第1步目标：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated yesterday.

实际：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated yesterday.

joint=True, unresolved=False

第2步目标：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated two days ago.

实际：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated two days ago.

joint=True, unresolved=False


## 8. G3_local_repair / BART

源：Author: Grace. Record date: 2026-11-20. The record describes my cancelled plan to not give one parcel to Carol, with the event dated two days ago. This record does not establish that the event occurred.

框架：[{"view_date": "2026-11-27", "perspective": "first"}, {"view_date": "2026-11-28", "perspective": "first"}, {"view_date": "2026-11-29", "perspective": "first"}]

G3 / latent_chain

第1步目标：Author: Grace. Record date: 2026-11-20. The record describes my cancelled plan to not give one parcel to Carol, with the event dated three days ago. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-11-20. The record describes my cancelled plan to not give one parcel to Carol, with the event dated three days ago. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: Grace. Record date: 2026-11-20. The record describes my cancelled plan to not give one parcel to Carol, with the event dated four days ago. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-11-20. The record describes my cancelled plan to not give one parcel to Carol, with the event dated four days ago. This record does not establish that the event occurred.

joint=True, unresolved=False

G1 / latent_chain

第1步目标：Author: Grace. Record date: 2026-11-20. The record describes my cancelled plan to not give one parcel to Carol, with the event dated three days ago. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-11-20. The record describes my cancelled plan to not give one parcel to Carol, with the event dated three days ago. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: Grace. Record date: 2026-11-20. The record describes my cancelled plan to not give one parcel to Carol, with the event dated four days ago. This record does not establish that the event occurred.

实际：Author: two threeAuthor three three three twoAuthor two three three four threeNone three three days four three three 3Author four three days two days three days three three levels three days days four four three four two days four days four two two two days days days three four four

joint=False, unresolved=True

G3 / decode_reencode

第1步目标：Author: Grace. Record date: 2026-11-20. The record describes my cancelled plan to not give one parcel to Carol, with the event dated three days ago. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-11-20. The record describes my cancelled plan to not give one parcel to Carol, with the event dated three days ago. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: Grace. Record date: 2026-11-20. The record describes my cancelled plan to not give one parcel to Carol, with the event dated four days ago. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-11-20. The record describes my cancelled plan to not give one parcel to Carol, with the event dated four days ago. This record does not establish that the event occurred.

joint=True, unresolved=False


## 9. G3_local_repair / t5gemma-2b-2b-ul2-it

源：Author: Grace. Record date: 2026-11-20. The record describes my cancelled plan to not give one parcel to Carol, with the event dated two days ago. This record does not establish that the event occurred.

框架：[{"view_date": "2026-11-27", "perspective": "first"}, {"view_date": "2026-11-28", "perspective": "first"}, {"view_date": "2026-11-29", "perspective": "first"}]

G3 / latent_chain

第1步目标：Author: Grace. Record date: 2026-11-20. The record describes my cancelled plan to not give one parcel to Carol, with the event dated three days ago. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-11-20. The record describes my cancelled plan to not give one parcel to Carol, with the event dated three days ago. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: Grace. Record date: 2026-11-20. The record describes my cancelled plan to not give one parcel to Carol, with the event dated four days ago. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-11-20. The record describes my cancelled plan to not give one parcel to Carol, with the event dated four days ago. This record does not establish that the event occurred.

joint=True, unresolved=False

G1 / latent_chain

第1步目标：Author: Grace. Record date: 2026-11-20. The record describes my cancelled plan to not give one parcel to Carol, with the event dated three days ago. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-11-20. The record describes my cancelled plan to not give one parcel to Carol, with the event dated three days ago. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: Grace. Record date: 2026-11-20. The record describes my cancelled plan to not give one parcel to Carol, with the event dated four days ago. This record does not establish that the event occurred.

实际：Author:

joint=False, unresolved=True

G3 / decode_reencode

第1步目标：Author: Grace. Record date: 2026-11-20. The record describes my cancelled plan to not give one parcel to Carol, with the event dated three days ago. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-11-20. The record describes my cancelled plan to not give one parcel to Carol, with the event dated three days ago. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: Grace. Record date: 2026-11-20. The record describes my cancelled plan to not give one parcel to Carol, with the event dated four days ago. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-11-20. The record describes my cancelled plan to not give one parcel to Carol, with the event dated four days ago. This record does not establish that the event occurred.

joint=True, unresolved=False


## 10. G3_tradeoff / BART

源：Author: David. Record date: 2026-11-08. It is my cancelled plan to bring nine parcels to Emma that the record describes for an event dated in two days. This record does not establish that the event occurred.

框架：[{"view_date": "2026-11-11", "perspective": "first"}, {"view_date": "2026-11-12", "perspective": "first"}, {"view_date": "2026-11-12", "perspective": "third"}]

G3 / latent_chain

第1步目标：Author: David. Record date: 2026-11-08. It is my cancelled plan to bring nine parcels to Emma that the record describes for an event dated tomorrow. This record does not establish that the event occurred.

实际：Author: David. Record date: 2026-11-08. It is my cancelled plan to bring nine parcels to Emma that the record describes for an event dated tomorrow that the note does not establish that the event occurred.

joint=False, unresolved=True

第2步目标：Author: David. Record date: 2026-11-08. It is David's cancelled plan to bring nine parcels to Emma that the record describes for an event dated tomorrow. This record does not establish that the event occurred.

实际：Author: David. Record date: 2026-11-08. It is David's cancelled plan to bring nine parcels to Emma that the record describes for an event dated tomorrow that the Record does not establish that the event occurred. This record does not indicate that the Event occurred.

joint=False, unresolved=True

G1 / latent_chain

第1步目标：Author: David. Record date: 2026-11-08. It is my cancelled plan to bring nine parcels to Emma that the record describes for an event dated tomorrow. This record does not establish that the event occurred.

实际：Author: David. Record date: 2026-11-08. It is my cancelled plan to bring nine parcels to Emma that the record describes for an event dated tomorrow. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: David. Record date: 2026-11-08. It is David's cancelled plan to bring nine parcels to Emma that the record describes for an event dated tomorrow. This record does not establish that the event occurred.

实际：Author: David. Record date: 2026-11-08. It is David's cancelled plan to bring nine parcels to Emma that the record describes for an event dated tomorrow. This record does not establish that the event occurred.

joint=True, unresolved=False

G3 / decode_reencode

第1步目标：Author: David. Record date: 2026-11-08. It is my cancelled plan to bring nine parcels to Emma that the record describes for an event dated tomorrow. This record does not establish that the event occurred.

实际：Author: David. Record date: 2026-11-08. It is my cancelled plan to bring nine parcels to Emma that the record describes for an event dated tomorrow that the note does not establish that the event occurred.

joint=False, unresolved=True

第2步目标：Author: David. Record date: 2026-11-08. It is David's cancelled plan to bring nine parcels to Emma that the record describes for an event dated tomorrow. This record does not establish that the event occurred.

实际：Author: David. Record date: 2026-11-08. It is David's cancelled plan to bring nine parcels to Emma that the record describes for an event dated tomorrow that the note does not establish that the event occurred.

joint=False, unresolved=True


## 11. G3_tradeoff / t5gemma-2b-2b-ul2-it

源：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated today. This record does not establish that the event occurred.

框架：[{"view_date": "2026-12-11", "perspective": "first"}, {"view_date": "2026-12-12", "perspective": "first"}, {"view_date": "2026-12-12", "perspective": "third"}]

G3 / latent_chain

第1步目标：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated yesterday. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated yesterday. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: Grace. Record date: 2026-12-06. The record describes Grace's plan to not bring eight parcels to Emma, with the event dated yesterday. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-12-06. The record describes Grace's plan to not bring eight parcels to Emma, with the event dated today. This record does not establish that the event occurred.

joint=False, unresolved=False

G1 / latent_chain

第1步目标：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated yesterday. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated yesterday. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: Grace. Record date: 2026-12-06. The record describes Grace's plan to not bring eight parcels to Emma, with the event dated yesterday. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-12-06. The record describes Grace's plan to not bring eight parcels to Emma, with the event dated yesterday. This record does not establish that the event occurred.

joint=True, unresolved=False

G3 / decode_reencode

第1步目标：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated yesterday. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated yesterday. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: Grace. Record date: 2026-12-06. The record describes Grace's plan to not bring eight parcels to Emma, with the event dated yesterday. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-12-06. The record describes Grace's plan to not bring eight parcels to Emma, with the event dated yesterday. This record does not establish that the event occurred.

joint=True, unresolved=False


## 12. untrained_three_failure / BART

源：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated yesterday.

框架：[{"view_date": "2026-10-29", "perspective": "first"}, {"view_date": "2026-10-30", "perspective": "first"}, {"view_date": "2026-10-31", "perspective": "first"}, {"view_date": "2026-11-01", "perspective": "first"}]

G3 / latent_chain

第1步目标：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated two days ago.

实际：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated two days ago.

joint=True, unresolved=False

第2步目标：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated three days ago.

实际：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated three days ago.

joint=True, unresolved=False

第3步目标：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated four days ago.

实际：Author: Carol. Record date: 2026-10-28. The record describes my report of four days ago four days days ago three days ago.

joint=False, unresolved=True

G1 / latent_chain

第1步目标：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated two days ago.

实际：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated two days ago.

joint=True, unresolved=False

第2步目标：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated three days ago.

实际：Author: Carol. The three two days two days three three two three two are three three days three days two three days are three two two days are two two are two three ground two two things three days and more days three two four two are more

joint=False, unresolved=True

第3步目标：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated four days ago.

实际： two twoSoScroll twoScrollScrollScrollSoScrollSoSoScroll twoSoSoHereHereScrollHereHereScrollFineButThreeFour four fourScroll twoScroll twoSo

joint=False, unresolved=True

G3 / decode_reencode

第1步目标：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated two days ago.

实际：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated two days ago.

joint=True, unresolved=False

第2步目标：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated three days ago.

实际：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated three days ago.

joint=True, unresolved=False

第3步目标：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated four days ago.

实际：Author: Carol. Record date: 2026-10-28. The record describes my report of not delivering nine tickets to Frank, with the event dated four days ago.

joint=True, unresolved=False


## 13. untrained_three_failure / t5gemma-2b-2b-ul2-it

源：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated tomorrow. This record does not establish that the event occurred.

框架：[{"view_date": "2026-12-10", "perspective": "first"}, {"view_date": "2026-12-11", "perspective": "first"}, {"view_date": "2026-12-12", "perspective": "first"}, {"view_date": "2026-12-13", "perspective": "first"}]

G3 / latent_chain

第1步目标：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated today. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated today. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated yesterday. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated yesterday. This record does not establish that the event occurred.

joint=True, unresolved=False

第3步目标：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated two days ago. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated yesterday. This record does not establish that the event occurred.

joint=False, unresolved=False

G1 / latent_chain

第1步目标：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated today. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated today. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated yesterday. This record does not establish that the event occurred.

实际：Author:

joint=False, unresolved=True

第3步目标：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated two days ago. This record does not establish that the event occurred.

实际：Author

joint=False, unresolved=True

G3 / decode_reencode

第1步目标：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated today. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated today. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated yesterday. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated yesterday. This record does not establish that the event occurred.

joint=True, unresolved=False

第3步目标：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated two days ago. This record does not establish that the event occurred.

实际：Author: Grace. Record date: 2026-12-06. The record describes my plan to not bring eight parcels to Emma, with the event dated two days ago. This record does not establish that the event occurred.

joint=True, unresolved=False


## 14. fact_damage / t5gemma-2b-2b-ul2-it

源：Author: Grace. Record date: 2026-11-21. In the record, my report of sending seven books to David has an event date of two days ago.

框架：[{"view_date": "2026-11-23", "perspective": "first"}, {"view_date": "2026-11-22", "perspective": "first"}, {"view_date": "2026-11-21", "perspective": "first"}]

G1 / latent_chain

第1步目标：Author: Grace. Record date: 2026-11-21. In the record, my report of sending seven books to David has an event date of yesterday.

实际：Author: Grace. Record date: 2026-11-21. In the record, my report of sending seven books to David has an event date of yesterday.

joint=True, unresolved=False

第2步目标：Author: Grace. Record date: 2026-11-21. In the record, my report of sending seven books to David has an event date of today.

实际：Author: Grace. Record date: 2026-11-21. In the record, my report of sending eight books to David has an event date of three days ago.

joint=False, unresolved=False

G3 / latent_chain

第1步目标：Author: Grace. Record date: 2026-11-21. In the record, my report of sending seven books to David has an event date of yesterday.

实际：Author: Grace. Record date: 2026-11-21. In the record, my report of sending seven books to David has an event date of yesterday.

joint=True, unresolved=False

第2步目标：Author: Grace. Record date: 2026-11-21. In the record, my report of sending seven books to David has an event date of today.

实际：Author: Grace. Record date: 2026-11-21. In the record, my report of sending eight books to David has an event date of three days ago.

joint=False, unresolved=False

G1 / decode_reencode

第1步目标：Author: Grace. Record date: 2026-11-21. In the record, my report of sending seven books to David has an event date of yesterday.

实际：Author: Grace. Record date: 2026-11-21. In the record, my report of sending seven books to David has an event date of yesterday.

joint=True, unresolved=False

第2步目标：Author: Grace. Record date: 2026-11-21. In the record, my report of sending seven books to David has an event date of today.

实际：Author: Grace. Record date: 2026-11-21. In the record, my report of sending seven books to David has an event date of today.

joint=True, unresolved=False


## 15. unresolved / BART

源：Author: David. Record date: 2026-12-05. For an event dated in two days, the record describes my plan to send four tickets to Frank. This record does not establish that the event occurred.

框架：[{"view_date": "2026-12-08", "perspective": "first"}, {"view_date": "2026-12-09", "perspective": "first"}, {"view_date": "2026-12-10", "perspective": "first"}]

G1 / latent_chain

第1步目标：Author: David. Record date: 2026-12-05. For an event dated tomorrow, the record describes my plan to send four tickets to Frank. This record does not establish that the event occurred.

实际：Author: David. Record date: 2026-12-05. For an event dated tomorrow, the record describes my plan to send four tickets to Frank. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: David. Record date: 2026-12-05. For an event dated today, the record describes my plan to send four tickets to Frank. This record does not establish that the event occurred.

实际： threeThree threeONEAuthor threeFour threeThreeONEThreeSo threeSo newThreeScrollThreeREAD twoThreeYesterdayThree three three three three three daysThree days three daysONE daysFour four three daysSoThree

joint=False, unresolved=True

G3 / latent_chain

第1步目标：Author: David. Record date: 2026-12-05. For an event dated tomorrow, the record describes my plan to send four tickets to Frank. This record does not establish that the event occurred.

实际：Author: David. Record date: 2026-12-05. For an event dated tomorrow, the record describes my plan to send four tickets to Frank. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: David. Record date: 2026-12-05. For an event dated today, the record describes my plan to send four tickets to Frank. This record does not establish that the event occurred.

实际：Author: David. Record date: 2026-12-05. For an event dated today, the record describes my plan to send four tickets to Frank. This record does not establish that the event occurred.

joint=True, unresolved=False

G1 / decode_reencode

第1步目标：Author: David. Record date: 2026-12-05. For an event dated tomorrow, the record describes my plan to send four tickets to Frank. This record does not establish that the event occurred.

实际：Author: David. Record date: 2026-12-05. For an event dated tomorrow, the record describes my plan to send four tickets to Frank. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: David. Record date: 2026-12-05. For an event dated today, the record describes my plan to send four tickets to Frank. This record does not establish that the event occurred.

实际：Author: David. Record date: 2026-12-05. For an event dated today, the record describes my plan to send four tickets to Frank. This record does not establish that the event occurred.

joint=True, unresolved=False


## 16. unresolved / t5gemma-2b-2b-ul2-it

源：Author: David. Record date: 2026-12-05. For an event dated in two days, the record describes my plan to send four tickets to Frank. This record does not establish that the event occurred.

框架：[{"view_date": "2026-12-08", "perspective": "first"}, {"view_date": "2026-12-09", "perspective": "first"}, {"view_date": "2026-12-10", "perspective": "first"}]

G1 / latent_chain

第1步目标：Author: David. Record date: 2026-12-05. For an event dated tomorrow, the record describes my plan to send four tickets to Frank. This record does not establish that the event occurred.

实际：Author: David. Record date: 2026-12-05. For an event dated tomorrow, the record describes my plan to send four tickets to Frank. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: David. Record date: 2026-12-05. For an event dated today, the record describes my plan to send four tickets to Frank. This record does not establish that the event occurred.

实际：Author:

joint=False, unresolved=True

G3 / latent_chain

第1步目标：Author: David. Record date: 2026-12-05. For an event dated tomorrow, the record describes my plan to send four tickets to Frank. This record does not establish that the event occurred.

实际：Author: David. Record date: 2026-12-05. For an event dated tomorrow, the record describes my plan to send four tickets to Frank. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: David. Record date: 2026-12-05. For an event dated today, the record describes my plan to send four tickets to Frank. This record does not establish that the event occurred.

实际：Author: David. Record date: 2026-12-05. For an event dated today, the record describes my plan to send four tickets to Frank. This record does not establish that the event occurred.

joint=True, unresolved=False

G1 / decode_reencode

第1步目标：Author: David. Record date: 2026-12-05. For an event dated tomorrow, the record describes my plan to send four tickets to Frank. This record does not establish that the event occurred.

实际：Author: David. Record date: 2026-12-05. For an event dated tomorrow, the record describes my plan to send four tickets to Frank. This record does not establish that the event occurred.

joint=True, unresolved=False

第2步目标：Author: David. Record date: 2026-12-05. For an event dated today, the record describes my plan to send four tickets to Frank. This record does not establish that the event occurred.

实际：Author: David. Record date: 2026-12-05. For an event dated today, the record describes my plan to send four tickets to Frank. This record does not establish that the event occurred.

joint=True, unresolved=False
