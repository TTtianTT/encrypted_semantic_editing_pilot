# 固定空间确认续步案例：助手审阅

固定首个test世界space_0120，三个seed与forward/reverse/inverse路径，共九例；没有按下一步结果筛选。全部当前与gold-reencode续步正确，latent续步失败。

- space_relation_confirmation_v1/t5gemma/s42/space_0120/forward: Expected back. Output explicitly remains left and replaces David with an unrelated observer/path clause; color and quantity remain.

- space_relation_confirmation_v1/t5gemma/s42/space_0120/reverse: Required parcel/observer spatial relation is missing. David, parcel, black and six copies remain. The remaining declarative body is grammatical; raw grammar=false is a controlled task-completeness proxy, not an independent grammar error.

- space_relation_confirmation_v1/t5gemma/s42/space_0120/inverse: Expected restored front. Output explicitly says right; David, parcel, black and six copies remain. Clear target-relation mismatch.

- space_relation_confirmation_v1/t5gemma/s43/space_0120/forward: Expected back. Output repeats left, omits black/six-copies facts and does not terminate.

- space_relation_confirmation_v1/t5gemma/s43/space_0120/reverse: A behind-me fragment occurs, but the named observer, parcel identity and quantity relation are missing in the damaged memberId/and-I fragment. Do not classify this as a clear wrong direction solely from its relation word.

- space_relation_confirmation_v1/t5gemma/s43/space_0120/inverse: Expected restored front. Output repeats right, corrupts the observer identity and omits facts without termination.

- space_relation_confirmation_v1/t5gemma/s44/space_0120/forward: Expected back. Repeated right clauses replace the required relation; named observer and black/six-copies facts are lost, and output does not terminate.

- space_relation_confirmation_v1/t5gemma/s44/space_0120/reverse: Damaged multilingual/repeated behind-me and right-behind-me fragments do not express the required David/parcel relation or black/six-copies facts. Do not infer a wrong direction solely from the fragments.

- space_relation_confirmation_v1/t5gemma/s44/space_0120/inverse: Expected restored front. Repeated of-me/I-know fragments omit the named observer, parcel relation and facts; output does not terminate.

这是存在性案例检查，不是独立人工标注或九个独立世界。解析的grammar标签还包括受控信息完整性；seed42/reverse仅缺关系，不是正文不合语法。latent/gold重编码mask长度44/43不同，不能作为同mask干预。正式N/S/M状态单独报告。
