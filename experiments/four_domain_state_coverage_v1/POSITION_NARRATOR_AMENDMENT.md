# Emotion: narrator's I versus historical quoted I

Added before this diagnostic's GPU phase, after some original formal test results.
The original emotion quotation challenge contrasts a named target evaluator with
quoted I; it does not fully test narrator's own I against someone else's I.
Secondary variants2/3 supply explicit Narrator=Focus actor, external first-person
stance and a fixed participantC quotation, "I dislike the OBJECT." Another named
evaluator's evaluation and objective facts are unchanged. At current level1 the
external and quoted words are identical but their speakers differ. Variant2 places
the quote last;3 places it first. Variants0/1 remain the original matched-order
multi-object fixtures. Pairs0/1 and2/3 are analyzed separately, not pooled as the
same complete semantic state.

Narrator identity is visible text and stays fixed under emotion plus/minus. Gold
records foil_narrator explicitly. No method receives an external oracle context
update; signed operation is the only extra signal. All legal natural evaluation
level conversions were atomically trained in named-subject core form; the new
first-person/quotation syntax was never trained. This is held-out language/scope,
not a completely-untrained abstract natural transition.

The independent narrator_scope_score.py validates the emitted narrator header and
maps only grammatically valid unquoted first-person stance forms to that emitted
speaker's named stance for the frozen primary scorer. Quoted I is never mapped;
quoted words/speaker must match the fixed historical utterance. This scoring
adapter does not enter decode–reencode. It never turns "I likes" or "I is neutral"
into a grammatical answer. CPU tests include wrong speaker, wrong quote, wrong
state/facts and malformed agreement. Both orders receive the unchanged dev gate;
all3seeds/all available roles get test atomic results even if this gate fails.

The same pre-existing eight-task one-GPU %2 array evaluates these fixtures, after
all earlier GPU phases. No training or checkpoint choice changes. Additional
evaluation remains within the48GPUh cap. The prior data/code/lock are archived in
protocol_revisions/position_before_narrator_emotion before regeneration. No
diagnostic model output existed when these variants were added.
