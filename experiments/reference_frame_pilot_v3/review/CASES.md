# 配对案例（便利抽样，不估计频率）

尚无真人审核；下列自动判定保留未决状态。


## G2_early_G3_correct


### v3_confirmation_test_iid_0009 / plus_plus

源：Author: Grace. Record date: 2026-12-04. My plan to deliver eight sensors to David, with the event dated tomorrow, is described in the record. This record does not establish that the event occurred.

框架：[{"view_date": "2026-12-08", "perspective": "first"}, {"view_date": "2026-12-09", "perspective": "first"}, {"view_date": "2026-12-10", "perspective": "first"}]


G2 第1步：Author: Grace. Record date: 2026-12-04. My plan to deliver eight sensors to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

目标：Author: Grace. Record date: 2026-12-04. My plan to deliver eight sensors to David, with the event dated today, is described in the record. This record does not establish that the event occurred.

joint=False；unresolved=False


G2 第2步：Author: Grace. Record date: 2026-12-04. My plan to deliver eight sensors to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

目标：Author: Grace. Record date: 2026-12-04. My plan to deliver eight sensors to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

joint=True；unresolved=False


G3 第1步：Author: Grace. Record date: 2026-12-04. My plan to deliver eight sensors to David, with the event dated today, is described in the record. This record does not establish that the event occurred.

目标：Author: Grace. Record date: 2026-12-04. My plan to deliver eight sensors to David, with the event dated today, is described in the record. This record does not establish that the event occurred.

joint=True；unresolved=False


G3 第2步：Author: Grace. Record date: 2026-12-04. My plan to deliver eight sensors to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

目标：Author: Grace. Record date: 2026-12-04. My plan to deliver eight sensors to David, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

joint=True；unresolved=False


### v3_confirmation_test_iid_0010 / plus_plus

源：Author: David. Record date: 2026-11-27. My report of bringing seven parcels to Henry, with the event dated two days ago, is described in the record.

框架：[{"view_date": "2026-11-29", "perspective": "first"}, {"view_date": "2026-11-30", "perspective": "first"}, {"view_date": "2026-12-01", "perspective": "first"}]


G2 第1步：Author: David. Record date: 2026-11-27. My report of bringing seven parcels to Henry, with the event dated four days ago, is described in the record.

目标：Author: David. Record date: 2026-11-27. My report of bringing seven parcels to Henry, with the event dated three days ago, is described in the record.

joint=False；unresolved=False


G2 第2步：Author: David. Record date: 2026-11-27. My report of bringing seven parcels to Henry, with the event dated four days ago, is described in the record.

目标：Author: David. Record date: 2026-11-27. My report of bringing seven parcels to Henry, with the event dated four days ago, is described in the record.

joint=True；unresolved=False


G3 第1步：Author: David. Record date: 2026-11-27. My report of bringing seven parcels to Henry, with the event dated three days ago, is described in the record.

目标：Author: David. Record date: 2026-11-27. My report of bringing seven parcels to Henry, with the event dated three days ago, is described in the record.

joint=True；unresolved=False


G3 第2步：Author: David. Record date: 2026-11-27. My report of bringing seven parcels to Henry, with the event dated four days ago, is described in the record.

目标：Author: David. Record date: 2026-11-27. My report of bringing seven parcels to Henry, with the event dated four days ago, is described in the record.

joint=True；unresolved=False


### v3_confirmation_test_iid_0011 / plus_plus

源：Author: Frank. Record date: 2026-12-07. My cancelled plan to bring six sensors to Carol, with the event dated tomorrow, is described in the record. This record does not establish that the event occurred.

框架：[{"view_date": "2026-12-11", "perspective": "first"}, {"view_date": "2026-12-12", "perspective": "first"}, {"view_date": "2026-12-13", "perspective": "first"}]


G2 第1步：Author: Frank. Record date: 2026-12-07. My cancelled plan to bring six sensors to Carol, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

目标：Author: Frank. Record date: 2026-12-07. My cancelled plan to bring six sensors to Carol, with the event dated today, is described in the record. This record does not establish that the event occurred.

joint=False；unresolved=False


G2 第2步：Author: Frank. Record date: 2026-12-07. My cancelled plan to bring six sensors to Carol, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

目标：Author: Frank. Record date: 2026-12-07. My cancelled plan to bring six sensors to Carol, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

joint=True；unresolved=False


G3 第1步：Author: Frank. Record date: 2026-12-07. My cancelled plan to bring six sensors to Carol, with the event dated today, is described in the record. This record does not establish that the event occurred.

目标：Author: Frank. Record date: 2026-12-07. My cancelled plan to bring six sensors to Carol, with the event dated today, is described in the record. This record does not establish that the event occurred.

joint=True；unresolved=False


G3 第2步：Author: Frank. Record date: 2026-12-07. My cancelled plan to bring six sensors to Carol, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

目标：Author: Frank. Record date: 2026-12-07. My cancelled plan to bring six sensors to Carol, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

joint=True；unresolved=False


## G3_first_restored_later_failed


### v3_confirmation_test_template_ood_0011 / plus_plus

源：Author: Emma. Record date: 2026-10-18. The event date assigned in the record to my cancelled plan to bring two parcels to David is in two days. This record does not establish that the event occurred.

框架：[{"view_date": "2026-10-21", "perspective": "first"}, {"view_date": "2026-10-22", "perspective": "first"}, {"view_date": "2026-10-23", "perspective": "first"}]


G2 第1步：Author: Emma. Record date: 2026-10-18. The event date assigned in the record to my cancelled plan to bring two parcels to David is in two days. This record does not establish that the event occurred.

目标：Author: Emma. Record date: 2026-10-18. The event date assigned in the record to my cancelled plan to bring two parcels to David is tomorrow. This record does not establish that the event occurred.

joint=False；unresolved=False


G2 第2步：Author: Emma. Record date: 2026-10-18. The event date assigned in the record to my cancelled plan to bring two parcels to David is in two days. This record does not establish that the event occurred.

目标：Author: Emma. Record date: 2026-10-18. The event date assigned in the record to my cancelled plan to bring two parcels to David is today. This record does not establish that the event occurred.

joint=False；unresolved=False


G3 第1步：Author: Emma. Record date: 2026-10-18. The event date assigned in the record to my cancelled plan to bring two parcels to David is tomorrow. This record does not establish that the event occurred.

目标：Author: Emma. Record date: 2026-10-18. The event date assigned in the record to my cancelled plan to bring two parcels to David is tomorrow. This record does not establish that the event occurred.

joint=True；unresolved=False


G3 第2步：Author: Emma. Record date: 2026-10-18. The event date assigned in the record to my cancelled plan to bring two parcels to David is tomorrow. This record does not establish that the event occurred.

目标：Author: Emma. Record date: 2026-10-18. The event date assigned in the record to my cancelled plan to bring two parcels to David is today. This record does not establish that the event occurred.

joint=False；unresolved=False


### v3_confirmation_test_template_ood_0027 / plus_plus

源：Author: David. Record date: 2026-11-01. It is my plan to give two parcels to Henry that the record describes for an event dated today. This record does not establish that the event occurred.

框架：[{"view_date": "2026-11-06", "perspective": "first"}, {"view_date": "2026-11-07", "perspective": "first"}, {"view_date": "2026-11-08", "perspective": "first"}]


G2 第1步：Author: David. Record date: 2026-11-01. It is my plan to give two parcels to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.

目标：Author: David. Record date: 2026-11-01. It is my plan to give two parcels to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.

joint=True；unresolved=False


G2 第2步：Author: David. Record date: 2026-11-01. It is my plan to give two parcels to Henry that the record describes for an event dated two days ago. This record does not establish that the event occurred.

目标：Author: David. Record date: 2026-11-01. It is my plan to give two parcels to Henry that the record describes for an event dated two days ago. This record does not establish that the event occurred.

joint=True；unresolved=False


G3 第1步：Author: David. Record date: 2026-11-01. It is my plan to give two parcels to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.

目标：Author: David. Record date: 2026-11-01. It is my plan to give two parcels to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.

joint=True；unresolved=False


G3 第2步：Author: David. Record date: 2026-11-01. It is my plan to give two parcels to Henry that the record describes yesterday. This record does not establish that the event occurred. This track does not indicate that the three event occurred

目标：Author: David. Record date: 2026-11-01. It is my plan to give two parcels to Henry that the record describes for an event dated two days ago. This record does not establish that the event occurred.

joint=False；unresolved=True


### v3_confirmation_test_template_ood_0028 / plus_plus

源：Author: Carol. Record date: 2026-11-14. It is my report of bringing six parcels to Bob that the record describes for an event dated today.

框架：[{"view_date": "2026-11-14", "perspective": "first"}, {"view_date": "2026-11-15", "perspective": "first"}, {"view_date": "2026-11-16", "perspective": "first"}]


G2 第1步：Author: Carol. Record date: 2026-11-14. It is my report of bringing six parcels to Bob that the record describes for an event dated yesterday.

目标：Author: Carol. Record date: 2026-11-14. It is my report of bringing six parcels to Bob that the record describes for an event dated yesterday.

joint=True；unresolved=False


G2 第2步：Author: Carol. Record date: 2026-11-14. It is my report of bringing six parcels to Bob that the record describes for an event dated two days ago.

目标：Author: Carol. Record date: 2026-11-14. It is my report of bringing six parcels to Bob that the record describes for an event dated two days ago.

joint=True；unresolved=False


G3 第1步：Author: Carol. Record date: 2026-11-14. It is my report of bringing six parcels to Bob that the record describes for an event dated yesterday.

目标：Author: Carol. Record date: 2026-11-14. It is my report of bringing six parcels to Bob that the record describes for an event dated yesterday.

joint=True；unresolved=False


G3 第2步：Author: Carol. Record date: 2026-11-14. It is my report of bringing six parcels to Bob that the record describes yesterday. It will tomorrow.

目标：Author: Carol. Record date: 2026-11-14. It is my report of bringing six parcels to Bob that the record describes for an event dated two days ago.

joint=False；unresolved=True


## cross_operator_recovered


### v3_confirmation_test_iid_0000 / plus_person

源：Author: Carol. Record date: 2026-11-06. The record describes my plan to not give four sensors to Frank, with the event dated tomorrow. This record does not establish that the event occurred.

框架：[{"view_date": "2026-11-10", "perspective": "first"}, {"view_date": "2026-11-11", "perspective": "first"}, {"view_date": "2026-11-11", "perspective": "third"}]


G2 第1步：Author: Carol. Record date: 2026-11-06. The record describes my plan to not give four sensors to Frank, with the event dated yesterday. This record does not establish that the event occurred.

目标：Author: Carol. Record date: 2026-11-06. The record describes my plan to not give four sensors to Frank, with the event dated today. This record does not establish that the event occurred.

joint=False；unresolved=False


G2 第2步：Author: Carol. Record date: 2026-11-06. The record describes Carol's plan to not give four sensors to Frank, with the event dated yesterday. This record does not establish that the event occurred.

目标：Author: Carol. Record date: 2026-11-06. The record describes Carol's plan to not give four sensors to Frank, with the event dated today. This record does not establish that the event occurred.

joint=False；unresolved=False


G3 第1步：Author: Carol. Record date: 2026-11-06. The record describes my plan to not give four sensors to Frank, with the event dated today. This record does not establish that the event occurred.

目标：Author: Carol. Record date: 2026-11-06. The record describes my plan to not give four sensors to Frank, with the event dated today. This record does not establish that the event occurred.

joint=True；unresolved=False


G3 第2步：Author: Carol. Record date: 2026-11-06. The record describes Carol's plan to not give four sensors to Frank, with the event dated today. This record does not establish that the event occurred.

目标：Author: Carol. Record date: 2026-11-06. The record describes Carol's plan to not give four sensors to Frank, with the event dated today. This record does not establish that the event occurred.

joint=True；unresolved=False


### v3_confirmation_test_iid_0004 / plus_person

源：Author: Bob. Record date: 2026-10-22. For an event dated two days ago, the record describes my report of delivering nine tickets to Carol.

框架：[{"view_date": "2026-10-24", "perspective": "first"}, {"view_date": "2026-10-25", "perspective": "first"}, {"view_date": "2026-10-25", "perspective": "third"}]


G2 第1步：Author: Bob. Record date: 2026-10-22. For an event dated four days ago, the record describes my report of delivering nine tickets to Carol.

目标：Author: Bob. Record date: 2026-10-22. For an event dated three days ago, the record describes my report of delivering nine tickets to Carol.

joint=False；unresolved=False


G2 第2步：Author: Bob. Record date: 2026-10-22. For an event dated two days ago, the record describes Bob's report of delivering nine tickets to Carol.

目标：Author: Bob. Record date: 2026-10-22. For an event dated three days ago, the record describes Bob's report of delivering nine tickets to Carol.

joint=False；unresolved=False


G3 第1步：Author: Bob. Record date: 2026-10-22. For an event dated three days ago, the record describes my report of delivering nine tickets to Carol.

目标：Author: Bob. Record date: 2026-10-22. For an event dated three days ago, the record describes my report of delivering nine tickets to Carol.

joint=True；unresolved=False


G3 第2步：Author: Bob. Record date: 2026-10-22. For an event dated three days ago, the record describes Bob's report of delivering nine tickets to Carol.

目标：Author: Bob. Record date: 2026-10-22. For an event dated three days ago, the record describes Bob's report of delivering nine tickets to Carol.

joint=True；unresolved=False


### v3_confirmation_test_iid_0006 / plus_person

源：Author: Frank. Record date: 2026-12-12. According to the record, my plan to not deliver seven tickets to Emma concerns an event dated tomorrow. This record does not establish that the event occurred.

框架：[{"view_date": "2026-12-16", "perspective": "first"}, {"view_date": "2026-12-17", "perspective": "first"}, {"view_date": "2026-12-17", "perspective": "third"}]


G2 第1步：Author: Frank. Record date: 2026-12-12. According to the record, my plan to not deliver seven tickets to Emma concerns an event dated yesterday. This record does not establish that the event occurred.

目标：Author: Frank. Record date: 2026-12-12. According to the record, my plan to not deliver seven tickets to Emma concerns an event dated today. This record does not establish that the event occurred.

joint=False；unresolved=False


G2 第2步：Author: Frank. Record date: 2026-12-12. According to the record, Frank's plan to not deliver seven tickets to Emma concerns an event dated yesterday. This record does not establish that the event occurred.

目标：Author: Frank. Record date: 2026-12-12. According to the record, Frank's plan to not deliver seven tickets to Emma concerns an event dated today. This record does not establish that the event occurred.

joint=False；unresolved=False


G3 第1步：Author: Frank. Record date: 2026-12-12. According to the record, my plan to not deliver seven tickets to Emma concerns an event dated today. This record does not establish that the event occurred.

目标：Author: Frank. Record date: 2026-12-12. According to the record, my plan to not deliver seven tickets to Emma concerns an event dated today. This record does not establish that the event occurred.

joint=True；unresolved=False


G3 第2步：Author: Frank. Record date: 2026-12-12. According to the record, Frank's plan to not deliver seven tickets to Emma concerns an event dated today. This record does not establish that the event occurred.

目标：Author: Frank. Record date: 2026-12-12. According to the record, Frank's plan to not deliver seven tickets to Emma concerns an event dated today. This record does not establish that the event occurred.

joint=True；unresolved=False


## cross_operator_failed


### v3_confirmation_test_iid_0023 / plus_person

源：Author: Alice. Record date: 2026-12-14. The event is dated in two days in the record describing my cancelled plan to give nine tickets to David. This record does not establish that the event occurred.

框架：[{"view_date": "2026-12-17", "perspective": "first"}, {"view_date": "2026-12-18", "perspective": "first"}, {"view_date": "2026-12-18", "perspective": "third"}]


G2 第1步：Author: Alice. Record date: 2026-12-14. The event is dated in two days in the record describing my cancelled plan to give nine tickets to David. This record does not establish that the event occurred.

目标：Author: Alice. Record date: 2026-12-14. The event is dated tomorrow in the record describing my cancelled plan to give nine tickets to David. This record does not establish that the event occurred.

joint=False；unresolved=False


G2 第2步：Author: Alice. Record date: 2026-12-14. The event is dated in two days in the record describing Alice's cancelled plan to give nine tickets to David. This record does not establish that the event occurred.

目标：Author: Alice. Record date: 2026-12-14. The event is dated tomorrow in the record describing Alice's cancelled plan to give nine tickets to David. This record does not establish that the event occurred.

joint=False；unresolved=False


G3 第1步：Author: Alice. Record date: 2026-12-14. The event is dated tomorrow in the record describing my cancelled plan to give nine tickets to David. This record does not establish that the event occurred.

目标：Author: Alice. Record date: 2026-12-14. The event is dated tomorrow in the record describing my cancelled plan to give nine tickets to David. This record does not establish that the event occurred.

joint=True；unresolved=False


G3 第2步：Author: Alice. Record date: 2026-12-14. The event is dated tomorrow in two days in the record describing Alice's cancelled plan to give nine tickets to David. This record does not establish that the event occurred.

目标：Author: Alice. Record date: 2026-12-14. The event is dated tomorrow in the record describing Alice's cancelled plan to give nine tickets to David. This record does not establish that the event occurred.

joint=False；unresolved=True


### v3_confirmation_test_template_ood_0007 / plus_person

源：Author: Bob. Record date: 2026-11-20. As described in the record, my report of not bringing three books to David has the event dated two days ago.

框架：[{"view_date": "2026-11-22", "perspective": "first"}, {"view_date": "2026-11-23", "perspective": "first"}, {"view_date": "2026-11-23", "perspective": "third"}]


G2 第1步：Author: Bob. Record date: 2026-11-20. As described in the record, my report of not bringing three books to David has the event dated four days ago.

目标：Author: Bob. Record date: 2026-11-20. As described in the record, my report of not bringing three books to David has the event dated three days ago.

joint=False；unresolved=False


G2 第2步：Author: Bob. Record date: 2026-11-20. As described in the record, Bob's report of not bringing three books to David has the event dated four days ago.

目标：Author: Bob. Record date: 2026-11-20. As described in the record, Bob's report of not bringing three books to David has the event dated three days ago.

joint=False；unresolved=False


G3 第1步：Author: Bob. Record date: 2026-11-20. As described in the record, my report of not bringing three books to David has the event dated three days ago.

目标：Author: Bob. Record date: 2026-11-20. As described in the record, my report of not bringing three books to David has the event dated three days ago.

joint=True；unresolved=False


G3 第2步：Author: Bob. Record date: 2026-11-20. As described in the record, Bob's report of not bringing three books to David has the event dated dated three days ago.

目标：Author: Bob. Record date: 2026-11-20. As described in the record, Bob's report of not bringing three books to David has the event dated three days ago.

joint=False；unresolved=True


### v3_confirmation_test_template_ood_0010 / plus_person

源：Author: Henry. Record date: 2026-10-30. The event date assigned in the record to my report of bringing five sensors to Carol is two days ago.

框架：[{"view_date": "2026-11-01", "perspective": "first"}, {"view_date": "2026-11-02", "perspective": "first"}, {"view_date": "2026-11-02", "perspective": "third"}]


G2 第1步：Author: Henry. Record date: 2026-10-30. The event date assigned in the record to my report of bringing five sensors to Carol is four days ago.

目标：Author: Henry. Record date: 2026-10-30. The event date assigned in the record to my report of bringing five sensors to Carol is three days ago.

joint=False；unresolved=False


G2 第2步：Author: Henry. Record date: 2026-10-30. The event date assigned in the record to Henry's report of bringing five sensors to Carol is four days ago.

目标：Author: Henry. Record date: 2026-10-30. The event date assigned in the record to Henry's report of bringing five sensors to Carol is three days ago.

joint=False；unresolved=False


G3 第1步：Author: Henry. Record date: 2026-10-30. The event date assigned in the record to my report of bringing five sensors to Carol is four days ago.

目标：Author: Henry. Record date: 2026-10-30. The event date assigned in the record to my report of bringing five sensors to Carol is three days ago.

joint=False；unresolved=False


G3 第2步：Author: Henry. Record date: 2026-10-30. The event date assigned in the record to Henry's report of bringing five sensors to Carol is four days ago.

目标：Author: Henry. Record date: 2026-10-30. The event date assigned in the record to Henry's report of bringing five sensors to Carol is three days ago.

joint=False；unresolved=False


## G3_fact_damage


### v3_confirmation_test_template_ood_0013 / plus_minus

源：Author: Bob. Record date: 2026-11-15. What the record describes for an event dated two days ago is my report of not delivering seven parcels to Grace.

框架：[{"view_date": "2026-11-17", "perspective": "first"}, {"view_date": "2026-11-18", "perspective": "first"}, {"view_date": "2026-11-17", "perspective": "first"}]


G2 第1步：Author: Bob. Record date: 2026-11-15. What the record describes for an event dated four days ago is my report of not delivering seven parcels to Grace.

目标：Author: Bob. Record date: 2026-11-15. What the record describes for an event dated three days ago is my report of not delivering seven parcels to Grace.

joint=False；unresolved=False


G2 第2步：Author: Bob. Record date: four two two two days.

目标：Author: Bob. Record date: 2026-11-15. What the record describes for an event dated two days ago is my report of not delivering seven parcels to Grace.

joint=False；unresolved=True


G3 第1步：Author: Bob. Record date: 2026-11-15. What the record describes for an event dated three days ago is my report of not delivering seven parcels to Grace.

目标：Author: Bob. Record date: 2026-11-15. What the record describes for an event dated three days ago is my report of not delivering seven parcels to Grace.

joint=True；unresolved=False


G3 第2步：Author: Bob. Record date: 2026-11-15. What the record describes for an event dated three days ago is my report of not delivering four parcels to Grace.

目标：Author: Bob. Record date: 2026-11-15. What the record describes for an event dated two days ago is my report of not delivering seven parcels to Grace.

joint=False；unresolved=False


### v3_confirmation_test_template_ood_0050 / minus_plus

源：Author: Alice. Record date: 2026-11-12. What the record describes for an event dated tomorrow is my cancelled plan to not bring two parcels to Henry. This record does not establish that the event occurred.

框架：[{"view_date": "2026-11-16", "perspective": "first"}, {"view_date": "2026-11-15", "perspective": "first"}, {"view_date": "2026-11-16", "perspective": "first"}]


G2 第1步：Author: Alice. Record date: 2026-11-12. What the record describes for an event dated in two days is my cancelled plan to not bring two parcels to Henry. This record does not establish that the event occurred.

目标：Author: Alice. Record date: 2026-11-12. What the record describes for an event dated in two days is my cancelled plan to not bring two parcels to Henry. This record does not establish that the event occurred.

joint=True；unresolved=False


G2 第2步：Author: Alice. Record date: 2026-11-12. What the record describes for an event dated today is my cancelled plan to not bring two parcels to Henry. This record does not establish that the event occurred.

目标：Author: Alice. Record date: 2026-11-12. What the record describes for an event dated tomorrow is my cancelled plan to not bring two parcels to Henry. This record does not establish that the event occurred.

joint=False；unresolved=False


G3 第1步：Author: Alice. Record date: 2026-11-12. What the record describes for an event dated in two days is my cancelled plan to not bring two parcels to Henry. This record does not establish that the event occurred.

目标：Author: Alice. Record date: 2026-11-12. What the record describes for an event dated in two days is my cancelled plan to not bring two parcels to Henry. This record does not establish that the event occurred.

joint=True；unresolved=False


G3 第2步：Author: Alice. Record date: 2026-11-12. What the record describes for an event dated today is my cancelled plan to not bring three parcels to Henry. This record does not establish that the event occurred.

目标：Author: Alice. Record date: 2026-11-12. What the record describes for an event dated tomorrow is my cancelled plan to not bring two parcels to Henry. This record does not establish that the event occurred.

joint=False；unresolved=False


## G3_unresolved


### v3_confirmation_test_template_ood_0003 / T_plus_third

源：Author: David. Record date: 2026-10-02. It is David's plan to bring two parcels to Henry that the record describes for an event dated in two days. This record does not establish that the event occurred.

框架：[{"view_date": "2026-10-05", "perspective": "third"}, {"view_date": "2026-10-06", "perspective": "third"}]


G2 第1步：Author: David. Record date: 2026-10-02. It is David's plan to bring two parcels to Henry that the record describes for an event dated in two days. This record does not establish that the event occurred.

目标：Author: David. Record date: 2026-10-02. It is David's plan to bring two parcels to Henry that the record describes for an event dated tomorrow. This record does not establish that the event occurred.

joint=False；unresolved=False


G3 第1步：Author: David. Record date: 2026-10-02. It is David's plan to bring two parcels to Henry that the record describes for an event dated tomorrow that the note describes for this record does not establish that the event occurred.

目标：Author: David. Record date: 2026-10-02. It is David's plan to bring two parcels to Henry that the record describes for an event dated tomorrow. This record does not establish that the event occurred.

joint=False；unresolved=True


### v3_confirmation_test_template_ood_0063 / T_plus_third

源：Author: Emma. Record date: 2026-10-23. It is Emma's plan to give six parcels to Frank that the record describes for an event dated in two days. This record does not establish that the event occurred.

框架：[{"view_date": "2026-10-26", "perspective": "third"}, {"view_date": "2026-10-27", "perspective": "third"}]


G2 第1步：Author: Emma. Record date: 2026-10-23. It is Emma's plan to give six parcels to Frank that the record describes for an event dated in two days. This record does not establish that the event occurred.

目标：Author: Emma. Record date: 2026-10-23. It is Emma's plan to give six parcels to Frank that the record describes for an event dated tomorrow. This record does not establish that the event occurred.

joint=False；unresolved=False


G3 第1步：Author: Emma. Record date: 2026-10-23. It is Emma's plan to give six parcels to Frank that the record describes for an event dated tomorrow that the Record does not establish that the event occurred. This record does not indicate that the Event occurred.

目标：Author: Emma. Record date: 2026-10-23. It is Emma's plan to give six parcels to Frank that the record describes for an event dated tomorrow. This record does not establish that the event occurred.

joint=False；unresolved=True


### v3_confirmation_test_template_ood_0027 / plus_plus

源：Author: David. Record date: 2026-11-01. It is my plan to give two parcels to Henry that the record describes for an event dated today. This record does not establish that the event occurred.

框架：[{"view_date": "2026-11-06", "perspective": "first"}, {"view_date": "2026-11-07", "perspective": "first"}, {"view_date": "2026-11-08", "perspective": "first"}]


G2 第1步：Author: David. Record date: 2026-11-01. It is my plan to give two parcels to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.

目标：Author: David. Record date: 2026-11-01. It is my plan to give two parcels to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.

joint=True；unresolved=False


G2 第2步：Author: David. Record date: 2026-11-01. It is my plan to give two parcels to Henry that the record describes for an event dated two days ago. This record does not establish that the event occurred.

目标：Author: David. Record date: 2026-11-01. It is my plan to give two parcels to Henry that the record describes for an event dated two days ago. This record does not establish that the event occurred.

joint=True；unresolved=False


G3 第1步：Author: David. Record date: 2026-11-01. It is my plan to give two parcels to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.

目标：Author: David. Record date: 2026-11-01. It is my plan to give two parcels to Henry that the record describes for an event dated yesterday. This record does not establish that the event occurred.

joint=True；unresolved=False


G3 第2步：Author: David. Record date: 2026-11-01. It is my plan to give two parcels to Henry that the record describes yesterday. This record does not establish that the event occurred. This track does not indicate that the three event occurred

目标：Author: David. Record date: 2026-11-01. It is my plan to give two parcels to Henry that the record describes for an event dated two days ago. This record does not establish that the event occurred.

joint=False；unresolved=True
