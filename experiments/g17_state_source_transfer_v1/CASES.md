# G17 twelve pre-hash-selected worlds

Chosen before inference; all anchors and receivers, including failure/nonmatch. No error-selected main cases.

## seed42 iid g17_iid_0116

Current anchor 2; gold next: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated tomorrow. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated in two days. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; parse_unresolved; output: Author: Frank. Record date: tomorrow. This record contains an account of my plan to not give six tickets to Grace, with the event dated in three days. This claim does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated in two days. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; parse_unresolved; output: Author: Frank. Record date: tomorrow tomorrow. The record contains an account of my plan to not give six tickets to Grace, with the event dated tomorrow. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated in two days. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated in three days. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated in two days. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated tomorrow. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated in two days. This record does not establish that the event occurred.

- G→P: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated tomorrow. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated in two days. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated in two days. This record does not establish that the event occurred.

Current anchor 0; gold next: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated yesterday. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated today. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

- P→F: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated yesterday. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated today. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated today. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated today. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated yesterday. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated today. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

Current anchor -1; gold next: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated yesterday. This record does not establish that the event occurred.

- P→P: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

- P→N: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

- P→F: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated yesterday. This record does not establish that the event occurred.

- U→P: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

- U→N: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated yesterday. This record does not establish that the event occurred.

- G→P: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

- G→N: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

- G→F: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

Current anchor -2; gold next: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated three days ago. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

- U→F: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-12-05. The record contains an account of my plan to not give six tickets to Grace, with the event dated two days ago. This record does not establish that the event occurred.

## seed42 iid g17_iid_0122

Current anchor 2; gold next: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated tomorrow. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated in two days. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated in three days. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated in two days. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; parse_unresolved; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated tomorrow tomorrow. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated in two days. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated in three days. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated in two days. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated tomorrow. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated in two days. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; parse_unresolved; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated tomorrow dated in three days. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated in two days. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; parse_unresolved; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated tomorrow? This record does not establish that the event occurred.

Current anchor 0; gold next: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated yesterday. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated today. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated today. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

- P→F: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated yesterday. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated today. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated today. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated today. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated yesterday. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated today. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

- G→F: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated yesterday. This record does not establish that the event occurred.

Current anchor -1; gold next: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated yesterday. This record does not establish that the event occurred.

- P→P: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

- P→N: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

- P→F: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated yesterday. This record does not establish that the event occurred.

- U→P: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

- U→N: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated yesterday. This record does not establish that the event occurred.

- G→P: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

- G→N: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

- G→F: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

Current anchor -2; gold next: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated three days ago. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

- U→F: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-12-03. According to the record, my plan to not bring five tickets to David concerns an event dated two days ago. This record does not establish that the event occurred.

## seed42 template_ood g17_template_ood_0045

Current anchor 2; gold next: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated tomorrow. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated in two days. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated in three days. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated in two days. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; parse_unresolved; output: Author: Frank. Record date: tomorrow-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated tomorrow. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated in two days. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated in three days. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated in two days. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated tomorrow. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated in two days. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated in two days. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated in two days. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated in two days. This record does not establish that the event occurred.

Current anchor 0; gold next: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated yesterday. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated today. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated today. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- P→F: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated yesterday. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated today. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated today. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated today. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated yesterday. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated today. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- G→F: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated yesterday. This record does not establish that the event occurred.

Current anchor -1; gold next: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated yesterday. This record does not establish that the event occurred.

- P→P: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- P→N: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- P→F: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated yesterday. This record does not establish that the event occurred.

- U→P: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- U→N: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated yesterday. This record does not establish that the event occurred.

- G→P: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- G→N: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- G→F: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

Current anchor -2; gold next: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated three days ago. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- U→F: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-10. It is my plan to send eight sensors to Alice that the record describes for an event dated two days ago. This record does not establish that the event occurred.

## seed42 template_ood g17_template_ood_0129

Current anchor 2; gold next: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated tomorrow. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated in two days. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated in three days. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated in two days. This record does not establish that the event occurred.

- P→F: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated tomorrow. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated in two days. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated in three days. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated in two days. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated tomorrow. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated in two days. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated in two days. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated in two days. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated in two days. This record does not establish that the event occurred.

Current anchor 0; gold next: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated yesterday. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated today. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated today. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- P→F: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated yesterday. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated today. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated today. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated today. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated yesterday. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated today. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- G→F: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated yesterday. This record does not establish that the event occurred.

Current anchor -1; gold next: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated yesterday. This record does not establish that the event occurred.

- P→P: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- P→N: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- P→F: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated yesterday. This record does not establish that the event occurred.

- U→P: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- U→N: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated yesterday. This record does not establish that the event occurred.

- G→P: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- G→N: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- G→F: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

Current anchor -2; gold next: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated three days ago. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- U→F: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-11-17. It is my plan to send nine parcels to Frank that the record describes for an event dated two days ago. This record does not establish that the event occurred.

## seed43 iid g17_iid_0091

Current anchor 2; gold next: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated tomorrow, is described in the record. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated in two days, is described in the record. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated in two days, is described in the record. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated in two days, is described in the record. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated in two days, is described in the record. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated in two days, is described in the record. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated in two days, is described in the record. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated in two days, is described in the record. This record does not establish that the event occurred.

- U→F: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated in two days, is described in the record. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated in two days, is described in the record. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated in two days, is described in the record. This record does not establish that the event occurred.

Current anchor 0; gold next: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.

- P→F: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated today, is described in the record. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

- G→F: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

Current anchor -1; gold next: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

- P→P: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

- P→N: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

- P→F: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

- U→P: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

- U→N: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated yesterday, is described in the record. This record does not establish that the event occurred.

- G→P: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

- G→N: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

- G→F: joint=True; exact=True; EOS=True; success; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

Current anchor -2; gold next: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated three days ago, is described in the record. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

- U→F: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; date_error; output: Author: Frank. Record date: 2026-10-30. My plan to send two sensors to Henry, with the event dated two days ago, is described in the record. This record does not establish that the event occurred.

## seed43 iid g17_iid_0070

Current anchor 2; gold next: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated tomorrow. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated in two days. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated in two days. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated in two days. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated in two days. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated in two days. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated in two days. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated in two days. This record does not establish that the event occurred.

- U→F: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated in two days. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated in two days. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated today. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated today. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated in two days. This record does not establish that the event occurred.

Current anchor 0; gold next: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated yesterday. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated today. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated today. This record does not establish that the event occurred.

- P→F: joint=True; exact=True; EOS=True; success; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated yesterday. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated today. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated today. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated today. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated yesterday. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated today. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

- G→F: joint=True; exact=True; EOS=True; success; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated yesterday. This record does not establish that the event occurred.

Current anchor -1; gold next: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated yesterday. This record does not establish that the event occurred.

- P→P: joint=True; exact=True; EOS=True; success; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

- P→N: joint=True; exact=True; EOS=True; success; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

- P→F: joint=True; exact=True; EOS=True; success; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated yesterday. This record does not establish that the event occurred.

- U→P: joint=True; exact=True; EOS=True; success; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

- U→N: joint=True; exact=True; EOS=True; success; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated yesterday. This record does not establish that the event occurred.

- G→P: joint=True; exact=True; EOS=True; success; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

- G→N: joint=True; exact=True; EOS=True; success; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

- G→F: joint=True; exact=True; EOS=True; success; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

Current anchor -2; gold next: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated three days ago. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

- U→F: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-10-11. The subject of the record is my plan to not give six books to David, with the event dated two days ago. This record does not establish that the event occurred.

## seed43 template_ood g17_template_ood_0080

Current anchor 2; gold next: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated tomorrow is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Alice. Record date: 2026-11-06. What the record describes for an event dated in two days is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated in two days is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated in two days is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated in two days is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Alice. Record date: 2026-11-06. What the record describes for an event dated in two days is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated in two days is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated in two days is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- U→F: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated in two days is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Alice. Record date: 2026-11-06. What the record describes for an event dated in two days is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated today is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated in two days is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated in two days is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

Current anchor 0; gold next: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated yesterday is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Alice. Record date: 2026-11-06. What the record describes for an event dated today is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated today is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated today is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- P→F: joint=True; exact=True; EOS=True; success; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated yesterday is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Alice. Record date: 2026-11-06. What the record describes for an event dated today is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated today is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated today is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated yesterday is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Alice. Record date: 2026-11-06. What the record describes for an event dated today is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated two days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated two days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- G→F: joint=True; exact=True; EOS=True; success; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated yesterday is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

Current anchor -1; gold next: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated two days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Alice. Record date: 2026-11-06. What the record describes for an event dated yesterday is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- P→P: joint=True; exact=True; EOS=True; success; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated two days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- P→N: joint=True; exact=True; EOS=True; success; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated two days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- P→F: joint=True; exact=True; EOS=True; success; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated two days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Alice. Record date: 2026-11-06. What the record describes for an event dated yesterday is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- U→P: joint=True; exact=True; EOS=True; success; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated two days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- U→N: joint=True; exact=True; EOS=True; success; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated two days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated two days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Alice. Record date: 2026-11-06. What the record describes for an event dated yesterday is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- G→P: joint=True; exact=True; EOS=True; success; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated two days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- G→N: joint=True; exact=True; EOS=True; success; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated two days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- G→F: joint=True; exact=True; EOS=True; success; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated two days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

Current anchor -2; gold next: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated three days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Alice. Record date: 2026-11-06. What the record describes for an event dated two days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated two days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; parse_unresolved; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated two days days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated two days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Alice. Record date: 2026-11-06. What the record describes for an event dated two days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated two days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated two days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- U→F: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated two days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Alice. Record date: 2026-11-06. What the record describes for an event dated two days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated two days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated two days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; date_error; output: Author: Alice. Record date: 2026-11-06. What the record describes for an event dated two days ago is my plan to not deliver five sensors to Emma. This record does not establish that the event occurred.

## seed43 template_ood g17_template_ood_0012

Current anchor 2; gold next: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated tomorrow is my plan to not bring four sensors to David. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Bob. Record date: 2026-10-27. What the record describes for an event dated in two days is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated in two days is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated in two days is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated in two days is my plan to not bring four sensors to David. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Bob. Record date: 2026-10-27. What the record describes for an event dated in two days is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated in two days is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated in two days is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- U→F: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated in two days is my plan to not bring four sensors to David. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Bob. Record date: 2026-10-27. What the record describes for an event dated in two days is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated today is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated in two days is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated in two days is my plan to not bring four sensors to David. This record does not establish that the event occurred.

Current anchor 0; gold next: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated yesterday is my plan to not bring four sensors to David. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Bob. Record date: 2026-10-27. What the record describes for an event dated today is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated today is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated today is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- P→F: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated yesterday is my plan to not bring four sensors to David. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Bob. Record date: 2026-10-27. What the record describes for an event dated today is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated today is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated today is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated yesterday is my plan to not bring four sensors to David. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Bob. Record date: 2026-10-27. What the record describes for an event dated today is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated two days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated two days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- G→F: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated yesterday is my plan to not bring four sensors to David. This record does not establish that the event occurred.

Current anchor -1; gold next: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated two days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Bob. Record date: 2026-10-27. What the record describes for an event dated yesterday is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- P→P: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated two days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- P→N: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated two days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- P→F: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated two days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Bob. Record date: 2026-10-27. What the record describes for an event dated yesterday is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- U→P: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated two days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- U→N: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated two days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated two days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Bob. Record date: 2026-10-27. What the record describes for an event dated yesterday is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- G→P: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated two days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- G→N: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated two days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- G→F: joint=True; exact=True; EOS=True; success; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated two days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

Current anchor -2; gold next: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated three days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Bob. Record date: 2026-10-27. What the record describes for an event dated two days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated two days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; parse_unresolved; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated two days days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated two days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Bob. Record date: 2026-10-27. What the record describes for an event dated two days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated two days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated two days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- U→F: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated two days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Bob. Record date: 2026-10-27. What the record describes for an event dated two days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated two days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated two days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; date_error; output: Author: Bob. Record date: 2026-10-27. What the record describes for an event dated two days ago is my plan to not bring four sensors to David. This record does not establish that the event occurred.

## seed44 iid g17_iid_0052

Current anchor 2; gold next: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated tomorrow. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated in two days. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated in two days. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; parse_unresolved; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated four days. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated in two days. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated in two days. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; parse_unresolved; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; parse_unresolved; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days. This record does not establish that the event occurred.

- U→F: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated in two days. This record does not establish that the event occurred.

Producer G, C=False, current=Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated tomorrow. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; parse_unresolved; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated four days. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; parse_unresolved; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated four days. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated yesterday. This record does not establish that the event occurred.

Current anchor 0; gold next: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated yesterday. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated today. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

- P→F: joint=True; exact=True; EOS=True; success; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated yesterday. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated today. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated today. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated today. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated yesterday. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated today. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

- G→F: joint=True; exact=True; EOS=True; success; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated yesterday. This record does not establish that the event occurred.

Current anchor -1; gold next: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated yesterday. This record does not establish that the event occurred.

- P→P: joint=True; exact=True; EOS=True; success; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

- P→N: joint=True; exact=True; EOS=True; success; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

- P→F: joint=True; exact=True; EOS=True; success; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated yesterday. This record does not establish that the event occurred.

- U→P: joint=True; exact=True; EOS=True; success; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

- U→N: joint=True; exact=True; EOS=True; success; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

- U→F: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated yesterday. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated yesterday. This record does not establish that the event occurred.

- G→P: joint=True; exact=True; EOS=True; success; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

- G→N: joint=True; exact=True; EOS=True; success; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

- G→F: joint=True; exact=True; EOS=True; success; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

Current anchor -2; gold next: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated three days ago. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

- U→F: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-19. The record contains an account of my plan to not bring two sensors to Bob, with the event dated two days ago. This record does not establish that the event occurred.

## seed44 iid g17_iid_0079

Current anchor 2; gold next: Author: Emma. Record date: 2026-10-04. The event is dated tomorrow in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Emma. Record date: 2026-10-04. The event is dated in two days in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-04. The event is dated in two days in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-04. The event is dated in two days in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-04. The event is dated in two days in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Emma. Record date: 2026-10-04. The event is dated in two days in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-04. The event is dated in two days in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-04. The event is dated in two days in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- U→F: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-04. The event is dated in two days in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Emma. Record date: 2026-10-04. The event is dated in two days in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-04. The event is dated in two days in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-04. The event is dated in two days in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-04. The event is dated in two days in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

Current anchor 0; gold next: Author: Emma. Record date: 2026-10-04. The event is dated yesterday in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Emma. Record date: 2026-10-04. The event is dated today in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- P→F: joint=True; exact=True; EOS=True; success; output: Author: Emma. Record date: 2026-10-04. The event is dated yesterday in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Emma. Record date: 2026-10-04. The event is dated today in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-04. The event is dated today in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-04. The event is dated today in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: Emma. Record date: 2026-10-04. The event is dated yesterday in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Emma. Record date: 2026-10-04. The event is dated today in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- G→F: joint=True; exact=True; EOS=True; success; output: Author: Emma. Record date: 2026-10-04. The event is dated yesterday in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

Current anchor -1; gold next: Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Emma. Record date: 2026-10-04. The event is dated yesterday in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- P→P: joint=True; exact=True; EOS=True; success; output: Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- P→N: joint=True; exact=True; EOS=True; success; output: Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- P→F: joint=True; exact=True; EOS=True; success; output: Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Emma. Record date: 2026-10-04. The event is dated yesterday in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- U→P: joint=True; exact=True; EOS=True; success; output: Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- U→N: joint=True; exact=True; EOS=True; success; output: Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Emma. Record date: 2026-10-04. The event is dated yesterday in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- G→P: joint=True; exact=True; EOS=True; success; output: Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- G→N: joint=True; exact=True; EOS=True; success; output: Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- G→F: joint=True; exact=True; EOS=True; success; output: Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

Current anchor -2; gold next: Author: Emma. Record date: 2026-10-04. The event is dated three days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- U→F: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; date_error; output: Author: Emma. Record date: 2026-10-04. The event is dated two days ago in the record describing my plan to send eight parcels to Frank. This record does not establish that the event occurred.

## seed44 template_ood g17_template_ood_0083

Current anchor 2; gold next: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is tomorrow. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is in two days. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is in two days. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is in two days. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; date_error; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is in two days. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is in two days. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is in two days. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is in two days. This record does not establish that the event occurred.

- U→F: joint=False; exact=False; EOS=True; date_error; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is in two days. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is in two days. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is in two days. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is in two days. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; date_error; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is in two days. This record does not establish that the event occurred.

Current anchor 0; gold next: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is yesterday. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is today. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is two days ago. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is two days ago. This record does not establish that the event occurred.

- P→F: joint=True; exact=True; EOS=True; success; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is yesterday. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is today. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is today. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is today. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is yesterday. This record does not establish that the event occurred.

Producer G, C=True, current=Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is today. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is two days ago. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is two days ago. This record does not establish that the event occurred.

- G→F: joint=True; exact=True; EOS=True; success; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is yesterday. This record does not establish that the event occurred.

Current anchor -1; gold next: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is two days ago. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is yesterday. This record does not establish that the event occurred.

- P→P: joint=True; exact=True; EOS=True; success; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is two days ago. This record does not establish that the event occurred.

- P→N: joint=True; exact=True; EOS=True; success; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is two days ago. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; date_error; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is yesterday. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is yesterday. This record does not establish that the event occurred.

- U→P: joint=True; exact=True; EOS=True; success; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is two days ago. This record does not establish that the event occurred.

- U→N: joint=True; exact=True; EOS=True; success; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is two days ago. This record does not establish that the event occurred.

- U→F: joint=False; exact=False; EOS=True; date_error; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is yesterday. This record does not establish that the event occurred.

Producer G, C=False, current=Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is today. This record does not establish that the event occurred.

- G→P: joint=True; exact=True; EOS=True; success; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is two days ago. This record does not establish that the event occurred.

- G→N: joint=True; exact=True; EOS=True; success; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is two days ago. This record does not establish that the event occurred.

- G→F: joint=True; exact=True; EOS=True; success; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is two days ago. This record does not establish that the event occurred.

Current anchor -2; gold next: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is three days ago. This record does not establish that the event occurred.

Producer P, C=True, current=Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is two days ago. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; parse_unresolved; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is 2026. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; parse_unresolved; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is 2026. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; date_error; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is two days ago. This record does not establish that the event occurred.

Producer U, C=True, current=Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is two days ago. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is two days ago. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is two days ago. This record does not establish that the event occurred.

- U→F: joint=False; exact=False; EOS=True; date_error; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is two days ago. This record does not establish that the event occurred.

Producer G, C=False, current=Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is today. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; parse_unresolved; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is 2026. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is two days ago. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; date_error; output: Author: Grace. Record date: 2026-11-25. The event date assigned in the record to my plan to give eight parcels to Alice is two days ago. This record does not establish that the event occurred.

## seed44 template_ood g17_template_ood_0127

Current anchor 2; gold next: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is tomorrow. This record does not establish that the event occurred.

Producer P, C=True, current=Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is in two days. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is in two days. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is in two days. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; date_error; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is in two days. This record does not establish that the event occurred.

Producer U, C=True, current=Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is in two days. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is in two days. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is in two days. This record does not establish that the event occurred.

- U→F: joint=False; exact=False; EOS=True; date_error; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is in two days. This record does not establish that the event occurred.

Producer G, C=True, current=Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is in two days. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is in two days. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is in two days. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; date_error; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is in two days. This record does not establish that the event occurred.

Current anchor 0; gold next: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is yesterday. This record does not establish that the event occurred.

Producer P, C=True, current=Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is today. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; date_error; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is two days ago. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; date_error; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is two days ago. This record does not establish that the event occurred.

- P→F: joint=True; exact=True; EOS=True; success; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is yesterday. This record does not establish that the event occurred.

Producer U, C=True, current=Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is today. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; date_error; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is today. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is today. This record does not establish that the event occurred.

- U→F: joint=True; exact=True; EOS=True; success; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is yesterday. This record does not establish that the event occurred.

Producer G, C=True, current=Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is today. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; date_error; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is two days ago. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; date_error; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is two days ago. This record does not establish that the event occurred.

- G→F: joint=True; exact=True; EOS=True; success; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is yesterday. This record does not establish that the event occurred.

Current anchor -1; gold next: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is two days ago. This record does not establish that the event occurred.

Producer P, C=True, current=Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is yesterday. This record does not establish that the event occurred.

- P→P: joint=True; exact=True; EOS=True; success; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is two days ago. This record does not establish that the event occurred.

- P→N: joint=True; exact=True; EOS=True; success; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is two days ago. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; date_error; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is yesterday. This record does not establish that the event occurred.

Producer U, C=True, current=Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is yesterday. This record does not establish that the event occurred.

- U→P: joint=True; exact=True; EOS=True; success; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is two days ago. This record does not establish that the event occurred.

- U→N: joint=True; exact=True; EOS=True; success; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is two days ago. This record does not establish that the event occurred.

- U→F: joint=False; exact=False; EOS=True; date_error; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is yesterday. This record does not establish that the event occurred.

Producer G, C=False, current=Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is today. This record does not establish that the event occurred.

- G→P: joint=True; exact=True; EOS=True; success; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is two days ago. This record does not establish that the event occurred.

- G→N: joint=True; exact=True; EOS=True; success; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is two days ago. This record does not establish that the event occurred.

- G→F: joint=True; exact=True; EOS=True; success; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is two days ago. This record does not establish that the event occurred.

Current anchor -2; gold next: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is three days ago. This record does not establish that the event occurred.

Producer P, C=True, current=Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is two days ago. This record does not establish that the event occurred.

- P→P: joint=False; exact=False; EOS=True; parse_unresolved; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is 2026. This record does not establish that the event occurred.

- P→N: joint=False; exact=False; EOS=True; parse_unresolved; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is 2026. This record does not establish that the event occurred.

- P→F: joint=False; exact=False; EOS=True; date_error; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is two days ago. This record does not establish that the event occurred.

Producer U, C=True, current=Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is two days ago. This record does not establish that the event occurred.

- U→P: joint=False; exact=False; EOS=True; parse_unresolved; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is 2026. This record does not establish that the event occurred.

- U→N: joint=False; exact=False; EOS=True; date_error; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is two days ago. This record does not establish that the event occurred.

- U→F: joint=False; exact=False; EOS=True; date_error; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is two days ago. This record does not establish that the event occurred.

Producer G, C=False, current=Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is today. This record does not establish that the event occurred.

- G→P: joint=False; exact=False; EOS=True; parse_unresolved; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is 2026. This record does not establish that the event occurred.

- G→N: joint=False; exact=False; EOS=True; parse_unresolved; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is 2026. This record does not establish that the event occurred.

- G→F: joint=False; exact=False; EOS=True; parse_unresolved; output: Author: David. Record date: 2026-10-12. The event date assigned in the record to my plan to bring three books to Frank is 2026. This record does not establish that the event occurred.
