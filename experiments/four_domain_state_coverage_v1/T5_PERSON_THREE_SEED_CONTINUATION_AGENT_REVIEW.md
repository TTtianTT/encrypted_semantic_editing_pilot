# Person continuation: three-seed assistant review

This uses completed P core trajectory shards, while N/S/M of seeds43/44 are still evaluating at review time. No independent human annotation. Core step2 eligibility requires an actually correct preceding latent output and correct gold-reencode next output. Each seed has96 eligible rows from32 worlds×3 paths, and0 strict next successes; parsed slot mismatch counts43/63/32 and unresolved counts53/33/64 for42/43/44. The category counts do not independently adjudicate every row.

The nine saved cases use first lexicographic world person_0120 and every eligible path for every seed. The fixed event is Grace giving Carol a white parcel owned by Henry,4 copies. Current outputs correctly bind “Grace gives me your parcel” under Speaker Carol/Listener Henry, or “you give Carol my parcel” under Speaker Henry/Listener Grace. All gold-reencode controls produce the required new context and preserve roles/facts.

| Seed/path | Inspected next-output failure |
|---|---|
|42/forward|Repeats the correct current text; does not rotate Carol/Henry to Henry/Grace. Event roles/facts remain correct.|
|42/reverse|Retains Henry/Grace and truncates the event to “you”; required Carol/Henry and complete event are absent.|
|42/inverse|Uses Henry/Carol instead of restored Grace/Carol. “Grace gives you my parcel” still preserves all event identities/facts under the actual emitted context.|
|43/forward|Same unchanged-context failure as42/forward.|
|43/reverse|Same stale-context and event-loss failure as42/reverse.|
|43/inverse|Same wrong-context, correct-event-identity failure as42/inverse.|
|44/forward|Speaker is the ungrounded label “me”; multiple incomplete/conflicting transfer clauses appear, and color/quantity disappear.|
|44/reverse|Retains the wrong Henry/Grace context. “I give Grace my parcel” explicitly adds Henry→Grace instead of the fixed Grace→Carol event, with other incomplete/ambiguous clauses and missing facts.|
|44/inverse|Uses Henry/Carol instead of restored Grace/Carol. Two repeated Grace→Carol clauses preserve the original roles, but “You give me your parcel” adds Carol→Henry with Carol as owner, and another clause adds Carol→Henry. Color/quantity are missing.|

These cases establish current-correct/next-failure existence in all3 T5Gemma seeds. Context-anchor failure, participant-changing added events, and content loss are distinct findings; unknown “she” references in seed44 are not forced into unique semantic labels. A correct original-event clause embedded among new contradictory/extra events does not establish preservation of the whole controlled world. Current latent mask48 versus gold-reencode46 remains an interface confound: these examples are not a mask-matched causal mechanism test. Same-current-text provenance tests are separately controlled in the source matrix.
