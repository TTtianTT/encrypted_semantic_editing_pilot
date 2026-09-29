# 预选20个世界的配对案例

训练前随机固定IID/OOD各10个世界；没有挑选成功例。human_label为空，尚无真人审核。折叠输出完整保存于JSONL和匿名CSV；本页展示四种主要方法。

## 1. joint_v1_test_iid_0006

源frame：{"view_date": "2026-10-20", "perspective": "first"}

Author: Grace. Record date: 2026-10-17. According to the record, my plan to not send seven sensors to Bob concerns an event dated in two days. This record does not establish that the event occurred.

目标frame：{"view_date": "2026-10-21", "perspective": "third"}

Author: Grace. Record date: 2026-10-17. According to the record, Grace's plan to not send seven sensors to Bob concerns an event dated tomorrow. This record does not establish that the event occurred.

**Joint16**

第1步：Author: Grace. Record date: 2026-10-17. According to the record, Grace's plan to not send seven sensors to Bob concerns an event dated tomorrow. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Joint32**

第1步：Author: Grace. Record date: 2026-10-17. According to the record, Grace's plan to not send seven sensors to Bob concerns an event dated tomorrow. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_T_then_P**

第1步：Author: Grace. Record date: 2026-10-17. According to the record, my plan to not send seven sensors to Bob concerns an event dated tomorrow. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Grace. Record date: 2026-10-17. According to the record, Grace's plan to not send seven sensors to Bob concerns an event dated in three days. This record does not establish that the event occurred.

joint=False，date=False，person=True，非日期事实=True，未决=False

**Sequential_P_then_T**

第1步：Author: Grace. Record date: 2026-10-17. According to the record, Grace's plan to not send seven sensors to Bob concerns an event dated in two days. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Grace. Record date: 2026-10-17. According to the record, Grace's plan to not send seven sensors to Bob concerns an event dated tomorrow. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

## 2. joint_v1_test_iid_0033

源frame：{"view_date": "2026-10-25", "perspective": "first"}

Author: Henry. Record date: 2026-10-20. My plan to bring six parcels to David, with the event dated today, is described in the record. This record does not establish that the event occurred.

目标frame：{"view_date": "2026-10-26", "perspective": "third"}

Author: Henry. Record date: 2026-10-20. Henry's plan to bring six parcels to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

**Joint16**

第1步：Author: Henry. Record date: 2026-10-20. Henry's plan to bring six parcels to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Joint32**

第1步：Author: Henry. Record date: 2026-10-20. Henry's plan to bring six parcels to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_T_then_P**

第1步：Author: Henry. Record date: 2026-10-20. My plan to bring six parcels to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Henry. Record date: 2026-10-20. Henry's plan to bring six parcels to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_P_then_T**

第1步：Author: Henry. Record date: 2026-10-20. Henry's plan to bring six parcels to David, with the event dated today, is described in the record. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Henry. Record date: 2026-10-20. Henry's plan to bring six parcels to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

## 3. joint_v1_test_iid_0075

源frame：{"view_date": "2026-11-07", "perspective": "first"}

Author: Alice. Record date: 2026-11-04. For an event dated in two days, the record describes my plan to bring eight books to Carol. This record does not establish that the event occurred.

目标frame：{"view_date": "2026-11-08", "perspective": "third"}

Author: Alice. Record date: 2026-11-04. For an event dated tomorrow, the record describes Alice's plan to bring eight books to Carol. This record does not establish that the event occurred.

**Joint16**

第1步：Author: Alice. Record date: 2026-11-04. For an event dated tomorrow, the record describes Alice's plan to bring eight books to Carol. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Joint32**

第1步：Author: Alice. Record date: 2026-11-04. For an event dated tomorrow, the record describes Alice's plan to bring eight books to Carol. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_T_then_P**

第1步：Author: Alice. Record date: 2026-11-04. For an event dated tomorrow, the record describes my plan to bring eight books to Carol. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Alice. Record date: 2026-11-04. For an event dated tomorrow, the record describes Alice's plan to bring eight books to Carol. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_P_then_T**

第1步：Author: Alice. Record date: 2026-11-04. For an event dated in two days, the record describes Alice's plan to bring eight books to Carol. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Alice. Record date: 2026-11-04. For an event dated tomorrow, the record describes Alice's plan to bring eight books to Carol. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

## 4. joint_v1_test_iid_0009

源frame：{"view_date": "2026-10-22", "perspective": "first"}

Author: Bob. Record date: 2026-10-18. My plan to give seven books to Henry, with the event dated tomorrow, is described in the record. This record does not establish that the event occurred.

目标frame：{"view_date": "2026-10-23", "perspective": "third"}

Author: Bob. Record date: 2026-10-18. Bob's plan to give seven books to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.

**Joint16**

第1步：Author: Bob. Record date: 2026-10-18. Bob's plan to give seven books to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Joint32**

第1步：Author: Bob. Record date: 2026-10-18. Bob's plan to give seven books to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_T_then_P**

第1步：Author: Bob. Record date: 2026-10-18. My plan to give seven books to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Bob. Record date: 2026-10-18. Bob's plan to give seven books to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

joint=False，date=False，person=True，非日期事实=True，未决=False

**Sequential_P_then_T**

第1步：Author: Bob. Record date: 2026-10-18. Bob's plan to give seven books to Henry, with the event dated tomorrow, is described in the record. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Bob. Record date: 2026-10-18. Bob's plan to give seven books to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

joint=False，date=False，person=True，非日期事实=True，未决=False

## 5. joint_v1_test_iid_0025

源frame：{"view_date": "2026-12-14", "perspective": "first"}

Author: Henry. Record date: 2026-12-13. The record describes my report of not sending nine parcels to David, with the event dated yesterday.

目标frame：{"view_date": "2026-12-15", "perspective": "third"}

Author: Henry. Record date: 2026-12-13. The record describes Henry's report of not sending nine parcels to David, with the event dated two days ago.

**Joint16**

第1步：Author: Henry. Record date: 2026-12-13. The record describes Henry's report of not sending nine parcels to David, with the event dated two days ago.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Joint32**

第1步：Author: Henry. Record date: 2026-12-13. The record describes Henry's report of not sending nine parcels to David, with the event dated two days ago.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_T_then_P**

第1步：Author: Henry. Record date: 2026-12-13. The record describes my report of not sending nine parcels to David, with the event dated two days ago.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Henry. Record date: 2026-12-13. The record describes Henry's report of not sending nine parcels to David, with the event dated yesterday.

joint=False，date=False，person=True，非日期事实=True，未决=False

**Sequential_P_then_T**

第1步：Author: Henry. Record date: 2026-12-13. The record describes Henry's report of not sending nine parcels to David, with the event dated yesterday.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Henry. Record date: 2026-12-13. The record describes Henry's report of not sending nine parcels to David, with the event dated two days ago.

joint=True，date=True，person=True，非日期事实=True，未决=False

## 6. joint_v1_test_iid_0076

源frame：{"view_date": "2026-10-06", "perspective": "first"}

Author: Grace. Record date: 2026-10-05. For an event dated yesterday, the record describes my report of giving five tickets to David.

目标frame：{"view_date": "2026-10-07", "perspective": "third"}

Author: Grace. Record date: 2026-10-05. For an event dated two days ago, the record describes Grace's report of giving five tickets to David.

**Joint16**

第1步：Author: Grace. Record date: 2026-10-05. For an event dated two days ago, the record describes Grace's report of giving five tickets to David.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Joint32**

第1步：Author: Grace. Record date: 2026-10-05. For an event dated two days ago, the record describes Grace's report of giving five tickets to David.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_T_then_P**

第1步：Author: Grace. Record date: 2026-10-05. For an event dated two days ago, the record describes my report of giving five tickets to David.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Grace. Record date: 2026-10-05. For an event dated two days ago, the record describes Grace's report of giving five tickets to David.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_P_then_T**

第1步：Author: Grace. Record date: 2026-10-05. For an event dated yesterday, the record describes Grace's report of giving five tickets to David.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Grace. Record date: 2026-10-05. For an event dated two days ago, the record describes Grace's report of giving five tickets to David.

joint=True，date=True，person=True，非日期事实=True，未决=False

## 7. joint_v1_test_iid_0063

源frame：{"view_date": "2026-10-12", "perspective": "first"}

Author: Frank. Record date: 2026-10-06. In the record, my plan to bring eight sensors to Bob has an event date of yesterday. This record does not establish that the event occurred.

目标frame：{"view_date": "2026-10-13", "perspective": "third"}

Author: Frank. Record date: 2026-10-06. In the record, Frank's plan to bring eight sensors to Bob has an event date of two days ago. This record does not establish that the event occurred.

**Joint16**

第1步：Author: Frank. Record date: 2026-10-06. In the record, Frank's plan to bring eight sensors to Bob has an event date of two days ago. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Joint32**

第1步：Author: Frank. Record date: 2026-10-06. In the record, Frank's plan to bring eight sensors to Bob has an event date of two days ago. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_T_then_P**

第1步：Author: Frank. Record date: 2026-10-06. In the record, my plan to bring eight sensors to Bob has an event date of two days ago. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Frank. Record date: 2026-10-06. In the record, Frank's plan to bring eight sensors to Bob has an event date of two days ago. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_P_then_T**

第1步：Author: Frank. Record date: 2026-10-06. In the record, Frank's plan to bring eight sensors to Bob has an event date of yesterday. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Frank. Record date: 2026-10-06. In the record, Frank's plan to bring eight sensors to Bob has an event date of two days ago. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

## 8. joint_v1_test_iid_0077

源frame：{"view_date": "2026-12-18", "perspective": "first"}

Author: Frank. Record date: 2026-12-14. For an event dated tomorrow, the record describes my cancelled plan to send four books to David. This record does not establish that the event occurred.

目标frame：{"view_date": "2026-12-19", "perspective": "third"}

Author: Frank. Record date: 2026-12-14. For an event dated today, the record describes Frank's cancelled plan to send four books to David. This record does not establish that the event occurred.

**Joint16**

第1步：Author: Frank. Record date: 2026-12-14. For an event dated today, the record describes Frank's cancelled plan to send four books to David. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Joint32**

第1步：Author: Frank. Record date: 2026-12-14. For an event dated today, the record describes Frank's cancelled plan to send four books to David. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_T_then_P**

第1步：Author: Frank. Record date: 2026-12-14. For an event dated today, the record describes my cancelled plan to send four books to David. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Frank. Record date: 2026-12-14. For an event dated yesterday, the record describes Frank's cancelled plan to send four books to David. This record does not establish that the event occurred.

joint=False，date=False，person=True，非日期事实=True，未决=False

**Sequential_P_then_T**

第1步：Author: Frank. Record date: 2026-12-14. For an event dated tomorrow, the record describes Frank's cancelled plan to send four books to David. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Frank. Record date: 2026-12-14. For an event dated yesterday, the record describes Frank's cancelled plan to send four books to David. This record does not establish that the event occurred.

joint=False，date=False，person=True，非日期事实=True，未决=False

## 9. joint_v1_test_iid_0059

源frame：{"view_date": "2026-12-19", "perspective": "first"}

Author: Emma. Record date: 2026-12-13. My cancelled plan to deliver nine books to Alice, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

目标frame：{"view_date": "2026-12-20", "perspective": "third"}

Author: Emma. Record date: 2026-12-13. Emma's cancelled plan to deliver nine books to Alice, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

**Joint16**

第1步：Author: Emma. Record date: 2026-12-13. Emma's cancelled plan to deliver nine books to Alice, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Joint32**

第1步：Author: Emma. Record date: 2026-12-13. Emma's cancelled plan to deliver nine books to Alice, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_T_then_P**

第1步：Author: Emma. Record date: 2026-12-13. My cancelled plan to deliver nine books to Alice, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Emma. Record date: 2026-12-13. Emma's cancelled plan to deliver nine books to Alice, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_P_then_T**

第1步：Author: Emma. Record date: 2026-12-13. Emma's cancelled plan to deliver nine books to Alice, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Emma. Record date: 2026-12-13. Emma's cancelled plan to deliver nine books to Alice, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

## 10. joint_v1_test_iid_0058

源frame：{"view_date": "2026-10-05", "perspective": "first"}

Author: Grace. Record date: 2026-10-05. My report of delivering five sensors to Bob, with the event dated today, is described in the record.

目标frame：{"view_date": "2026-10-06", "perspective": "third"}

Author: Grace. Record date: 2026-10-05. Grace's report of delivering five sensors to Bob, with the event dated yesterday, is described in the record.

**Joint16**

第1步：Author: Grace. Record date: 2026-10-05. Grace's report of delivering five sensors to Bob, with the event dated yesterday, is described in the record.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Joint32**

第1步：Author: Grace. Record date: 2026-10-05. Grace's report of delivering five sensors to Bob, with the event dated yesterday, is described in the record.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_T_then_P**

第1步：Author: Grace. Record date: 2026-10-05. My report of delivering five sensors to Bob, with the event dated yesterday, is described in the record.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Grace. Record date: 2026-10-05. Grace's report of delivering five sensors to Bob, with the event dated yesterday, is described in the record.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_P_then_T**

第1步：Author: Grace. Record date: 2026-10-05. Grace's report of delivering five sensors to Bob, with the event dated today, is described in the record.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Grace. Record date: 2026-10-05. Grace's report of delivering five sensors to Bob, with the event dated yesterday, is described in the record.

joint=True，date=True，person=True，非日期事实=True，未决=False

## 11. joint_v1_test_template_ood_0006

源frame：{"view_date": "2026-12-02", "perspective": "first"}

Author: David. Record date: 2026-11-27. As described in the record, my plan to not bring six tickets to Henry has the event dated today. This record does not establish that the event occurred.

目标frame：{"view_date": "2026-12-03", "perspective": "third"}

Author: David. Record date: 2026-11-27. As described in the record, David's plan to not bring six tickets to Henry has the event dated yesterday. This record does not establish that the event occurred.

**Joint16**

第1步：Author: David. Record date: 2026-11-27. As described in the record, David's plan to not bring six tickets to Henry has the event dated yesterday. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Joint32**

第1步：Author: David. Record date: 2026-11-27. As described in the record, David's plan to not bring six tickets to Henry has the event dated yesterday. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_T_then_P**

第1步：Author: David. Record date: 2026-11-27. As described in the record, my plan to not bring six tickets to Henry has the event dated yesterday. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: David. Record date: 2026-11-27. As described in the record, David's plan to not bring six tickets to Henry has the event dated yesterday. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_P_then_T**

第1步：Author: David. Record date: 2026-11-27. As described in the record, David's plan to not bring six tickets to Henry has the event dated today. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: David. Record date: 2026-11-27. As described in the record, David's plan to not bring six tickets to Henry has the event dated yesterday. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

## 12. joint_v1_test_template_ood_0033

源frame：{"view_date": "2026-12-08", "perspective": "first"}

Author: Alice. Record date: 2026-12-02. The event date assigned in the record to my plan to send nine tickets to Emma is yesterday. This record does not establish that the event occurred.

目标frame：{"view_date": "2026-12-09", "perspective": "third"}

Author: Alice. Record date: 2026-12-02. The event date assigned in the record to Alice's plan to send nine tickets to Emma is two days ago. This record does not establish that the event occurred.

**Joint16**

第1步：Author: Alice. Record date: 2026-12-02. The event date assigned in the record to Alice's plan to send nine tickets to Emma is two days ago. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Joint32**

第1步：Author: Alice. Record date: 2026-12-02. The event date assigned in the record to Alice's plan to send nine tickets to Emma is two days ago. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_T_then_P**

第1步：Author: Alice. Record date: 2026-12-02. The event date assigned in the record to my plan to send nine tickets to Emma is two days ago. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Alice. Record date: 2026-12-02. The event date assigned in the record to Alice's plan to send nine tickets to Emma is today. This record does not establish that the event occurred.

joint=False，date=False，person=True，非日期事实=True，未决=False

**Sequential_P_then_T**

第1步：Author: Alice. Record date: 2026-12-02. The event date assigned in the record to Alice's plan to send nine tickets to Emma is yesterday. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Alice. Record date: 2026-12-02. The event date assigned in the record to Alice's plan to send nine tickets to Emma is today. This record does not establish that the event occurred.

joint=False，date=False，person=True，非日期事实=True，未决=False

## 13. joint_v1_test_template_ood_0075

源frame：{"view_date": "2026-11-11", "perspective": "first"}

Author: Grace. Record date: 2026-11-07. It is my plan to deliver one sensor to Alice that the record describes for an event dated tomorrow. This record does not establish that the event occurred.

目标frame：{"view_date": "2026-11-12", "perspective": "third"}

Author: Grace. Record date: 2026-11-07. It is Grace's plan to deliver one sensor to Alice that the record describes for an event dated today. This record does not establish that the event occurred.

**Joint16**

第1步：Author: Grace. Record date: 2026-11-07. It is Grace's plan to deliver one sensor to Alice that the record describes for an event dated today. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Joint32**

第1步：Author: Grace. Record date: 2026-11-07. It is Grace's plan to deliver one sensor to Alice that the record describes for an event dated today. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_T_then_P**

第1步：Author: Grace. Record date: 2026-11-07. It is my plan to deliver one sensor to Alice that the record describes for an event dated today. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Grace. Record date: 2026-11-07. It is Grace's plan to deliver one sensor to Alice that the record describes for an event dated yesterday. This record does not establish that the event occurred.

joint=False，date=False，person=True，非日期事实=True，未决=False

**Sequential_P_then_T**

第1步：Author: Grace. Record date: 2026-11-07. It is Grace's plan to deliver one sensor to Alice that the record describes for an event dated tomorrow. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Grace. Record date: 2026-11-07. It is Grace's plan to deliver one sensor to Alice that the record describes for an event dated yesterday. This record does not establish that the event occurred.

joint=False，date=False，person=True，非日期事实=True，未决=False

## 14. joint_v1_test_template_ood_0009

源frame：{"view_date": "2026-11-01", "perspective": "first"}

Author: Grace. Record date: 2026-10-29. The event date assigned in the record to my plan to send eight parcels to Emma is in two days. This record does not establish that the event occurred.

目标frame：{"view_date": "2026-11-02", "perspective": "third"}

Author: Grace. Record date: 2026-10-29. The event date assigned in the record to Grace's plan to send eight parcels to Emma is tomorrow. This record does not establish that the event occurred.

**Joint16**

第1步：Author: Grace. Record date: 2026-10-29. The event date assigned in the record to Grace's plan to send eight parcels to Emma is tomorrow. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Joint32**

第1步：Author: Grace. Record date: 2026-10-29. The event date assigned in the record to Grace's plan to send eight parcels to Emma is tomorrow. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_T_then_P**

第1步：Author: Grace. Record date: 2026-10-29. The event date assigned in the record to my plan to send eight parcels to Emma is tomorrow. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Grace. Record date: 2026-10-29. The event date assigned in the record to Grace's plan to send eight parcels to Emma is in two days. This record does not establish that the event occurred.

joint=False，date=False，person=True，非日期事实=True，未决=False

**Sequential_P_then_T**

第1步：Author: Grace. Record date: 2026-10-29. The event date assigned in the record to Grace's plan to send eight parcels to Emma is in two days. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Grace. Record date: 2026-10-29. The event date assigned in the record to Grace's plan to send eight parcels to Emma is in three days. This record does not establish that the event occurred.

joint=False，date=False，person=True，非日期事实=True，未决=False

## 15. joint_v1_test_template_ood_0025

源frame：{"view_date": "2026-10-24", "perspective": "first"}

Author: Emma. Record date: 2026-10-23. What the record describes for an event dated yesterday is my report of not sending four sensors to Grace.

目标frame：{"view_date": "2026-10-25", "perspective": "third"}

Author: Emma. Record date: 2026-10-23. What the record describes for an event dated two days ago is Emma's report of not sending four sensors to Grace.

**Joint16**

第1步：Author: Emma. Record date: 2026-10-23. What the record describes for an event dated two days ago is Emma's report of not sending four sensors to Grace.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Joint32**

第1步：Author: Emma. Record date: 2026-10-23. What the record describes for an event dated two days ago is Emma's report of not sending four sensors to Grace.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_T_then_P**

第1步：Author: Emma. Record date: 2026-10-23. What the record describes for an event dated two days ago is my report of not sending four sensors to Grace.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Emma. Record date: 2026-10-23. What the record describes for an event dated two days ago is Emma's report of not sending four sensors to Grace.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_P_then_T**

第1步：Author: Emma. Record date: 2026-10-23. What the record describes for an event dated yesterday is Emma's report of not sending four sensors to Grace.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Emma. Record date: 2026-10-23. What the record describes for an event dated two days ago is Emma's report of not sending four sensors to Grace.

joint=True，date=True，person=True，非日期事实=True，未决=False

## 16. joint_v1_test_template_ood_0076

源frame：{"view_date": "2026-12-10", "perspective": "first"}

Author: Alice. Record date: 2026-12-09. It is my report of delivering one parcel to Frank that the record describes for an event dated yesterday.

目标frame：{"view_date": "2026-12-11", "perspective": "third"}

Author: Alice. Record date: 2026-12-09. It is Alice's report of delivering one parcel to Frank that the record describes for an event dated two days ago.

**Joint16**

第1步：Author: Alice. Record date: 2026-12-09. It is Alice's report of delivering one parcel to Frank that the record describes for an event dated two days ago.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Joint32**

第1步：Author: Alice. Record date: 2026-12-09. It is Alice's report of delivering one parcel to Frank that the record describes for an event dated two days ago.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_T_then_P**

第1步：Author: Alice. Record date: 2026-12-09. It is my report of delivering one parcel to Frank that the record describes for an event dated two days ago.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Alice. Record date: 2026-12-09. It is Alice's report of delivering one parcel to Frank that the record describes for an event dated yesterday.

joint=False，date=False，person=True，非日期事实=True，未决=False

**Sequential_P_then_T**

第1步：Author: Alice. Record date: 2026-12-09. It is Alice's report of delivering one parcel to Frank that the record describes for an event dated yesterday.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Alice. Record date: 2026-12-09. It is Alice's report of delivering one parcel to Frank that the record describes for an event dated two days ago.

joint=True，date=True，person=True，非日期事实=True，未决=False

## 17. joint_v1_test_template_ood_0063

源frame：{"view_date": "2026-11-23", "perspective": "first"}

Author: Grace. Record date: 2026-11-20. It is my plan to send two books to Frank that the record describes for an event dated in two days. This record does not establish that the event occurred.

目标frame：{"view_date": "2026-11-24", "perspective": "third"}

Author: Grace. Record date: 2026-11-20. It is Grace's plan to send two books to Frank that the record describes for an event dated tomorrow. This record does not establish that the event occurred.

**Joint16**

第1步：Author: Grace. Record date: 2026-11-20. It is Grace's plan to send two books to Frank that the record describes for an event dated tomorrow. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Joint32**

第1步：Author: Grace. Record date: 2026-11-20. It is Grace's plan to send two books to Frank that the record describes for an event dated tomorrow. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_T_then_P**

第1步：Author: Grace. Record date: 2026-11-20. It is my plan to send two books to Frank that the record describes for an event dated tomorrow. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Grace. Record date: 2026-11-20. It is Grace's plan to send two books to Frank that the record describes for an event dated in three days. This record does not establish that the event occurred.

joint=False，date=False，person=True，非日期事实=True，未决=False

**Sequential_P_then_T**

第1步：Author: Grace. Record date: 2026-11-20. It is Grace's plan to send two books to Frank that the record describes for an event dated in two days. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Grace. Record date: 2026-11-20. It is Grace's plan to send two books to Frank that the record describes for an event dated in three days. This record does not establish that the event occurred.

joint=False，date=False，person=True，非日期事实=True，未决=False

## 18. joint_v1_test_template_ood_0077

源frame：{"view_date": "2026-12-09", "perspective": "first"}

Author: Frank. Record date: 2026-12-03. It is my cancelled plan to bring seven books to David that the record describes for an event dated yesterday. This record does not establish that the event occurred.

目标frame：{"view_date": "2026-12-10", "perspective": "third"}

Author: Frank. Record date: 2026-12-03. It is Frank's cancelled plan to bring seven books to David that the record describes for an event dated two days ago. This record does not establish that the event occurred.

**Joint16**

第1步：Author: Frank. Record date: 2026-12-03. It is Frank's cancelled plan to bring seven books to David that the record describes for an event dated two days ago. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Joint32**

第1步：Author: Frank. Record date: 2026-12-03. It is Frank's cancelled plan to bring seven books to David that the record describes for an event dated two days ago. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_T_then_P**

第1步：Author: Frank. Record date: 2026-12-03. It is my cancelled plan to bring seven books to David that the record describes for an event dated two days ago. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Frank. Record date: 2026-12-03. It is Frank's cancelled plan to bring seven books to David that the record describes for an event dated two days ago. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_P_then_T**

第1步：Author: Frank. Record date: 2026-12-03. It is Frank's cancelled plan to bring seven books to David that the record describes for an event dated yesterday. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Frank. Record date: 2026-12-03. It is Frank's cancelled plan to bring seven books to David that the record describes for an event dated two days ago. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

## 19. joint_v1_test_template_ood_0059

源frame：{"view_date": "2026-12-17", "perspective": "first"}

Author: David. Record date: 2026-12-13. The event date assigned in the record to my cancelled plan to bring two parcels to Frank is tomorrow. This record does not establish that the event occurred.

目标frame：{"view_date": "2026-12-18", "perspective": "third"}

Author: David. Record date: 2026-12-13. The event date assigned in the record to David's cancelled plan to bring two parcels to Frank is today. This record does not establish that the event occurred.

**Joint16**

第1步：Author: David. Record date: 2026-12-13. The event date assigned in the record to David's cancelled plan to bring two parcels to Frank is today. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Joint32**

第1步：Author: David. Record date: 2026-12-13. The event date assigned in the record to David's cancelled plan to bring two parcels to Frank is today. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_T_then_P**

第1步：Author: David. Record date: 2026-12-13. The event date assigned in the record to my cancelled plan to bring two parcels to Frank is today. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: David. Record date: 2026-12-13. The event date assigned in the record to David's cancelled plan to bring two parcels to Frank is tomorrow. This record does not establish that the event occurred.

joint=False，date=False，person=True，非日期事实=True，未决=False

**Sequential_P_then_T**

第1步：Author: David. Record date: 2026-12-13. The event date assigned in the record to David's cancelled plan to bring two parcels to Frank is tomorrow. This record does not establish that the event occurred.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: David. Record date: 2026-12-13. The event date assigned in the record to David's cancelled plan to bring two parcels to Frank is tomorrow. This record does not establish that the event occurred.

joint=False，date=False，person=True，非日期事实=True，未决=False

## 20. joint_v1_test_template_ood_0058

源frame：{"view_date": "2026-11-28", "perspective": "first"}

Author: Henry. Record date: 2026-11-28. The event date assigned in the record to my report of sending eight books to Alice is today.

目标frame：{"view_date": "2026-11-29", "perspective": "third"}

Author: Henry. Record date: 2026-11-28. The event date assigned in the record to Henry's report of sending eight books to Alice is yesterday.

**Joint16**

第1步：Author: Henry. Record date: 2026-11-28. The event date assigned in the record to Henry's report of sending eight books to Alice is yesterday.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Joint32**

第1步：Author: Henry. Record date: 2026-11-28. The event date assigned in the record to Henry's report of sending eight books to Alice is yesterday.

joint=True，date=True，person=True，非日期事实=True，未决=False

**Sequential_T_then_P**

第1步：Author: Henry. Record date: 2026-11-28. The event date assigned in the record to my report of sending eight books to Alice is yesterday.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Henry. Record date: 2026-11-28. The event date assigned in the record to Henry's report of sending eight books to Alice is today.

joint=False，date=False，person=True，非日期事实=True，未决=False

**Sequential_P_then_T**

第1步：Author: Henry. Record date: 2026-11-28. The event date assigned in the record to Henry's report of sending eight books to Alice is today.

joint=True，date=True，person=True，非日期事实=True，未决=False

第2步：Author: Henry. Record date: 2026-11-28. The event date assigned in the record to Henry's report of sending eight books to Alice is today.

joint=False，date=False，person=True，非日期事实=True，未决=False
