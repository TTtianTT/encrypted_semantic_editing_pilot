# First-seed matched M benefit: assistant review

This is a partial observation from T5Gemma emotion seed42/H0, not a three-seed conclusion or independent human annotation. All 64 fixed full-text/mask U held-state core candidates are retained in the source matrix; M succeeds on18 and S on0. The JSONL saves the first lexicographic M-success/S-failure illustration, rather than selecting a seed or estimating prevalence from this example.

World emotion_0124 has current target Carol's negative evaluation of the key, Alice's strongly positive evaluation, a blue key and2 copies. The operation is minus: Carol must become strongly negative. Current full text, semantic state/anchor, mask length54 and edited depth1 match for S and M, with the same immutable U source.

M outputs “Carol strongly dislikes the key”; S outputs “Carol dislikes the key” and thus leaves the target unchanged. Both preserve Alice's evaluation, identity, object, color and quantity. The emitted M text is grammatical and the contrast represents a correct target change, rather than an isolated sentiment word. This validates the saved illustrative benefit. It does not independently adjudicate all18 successes. Second split and seeds43/44 remain pending at review time; failures and previous single-seed successful latent continuation counterexample remain in their separate artifacts.
