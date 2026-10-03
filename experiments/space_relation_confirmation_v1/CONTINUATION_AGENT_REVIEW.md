# 空间关系确认：当前正确而续步失败的固定案例

目前只审阅P的seed42/43、首个固定test世界space_0120、三种预定轨迹的第二步，共六例。第三seed和正式N/S/M尚未完成，不能写成全轮结论。每例当前与gold重编码续步正确；latent续步存在错误关系或必要信息缺失。

- seed42 / forward: Expected back. Output explicitly remains left and replaces David with an unrelated observer/path clause; color and quantity remain.

- seed42 / reverse: Required parcel/observer spatial relation is missing. David, parcel, black and six copies remain. The remaining declarative body is grammatical; raw grammar=false is a controlled task-completeness proxy, not an independent grammar error.

- seed42 / inverse: Expected restored front. Output explicitly says right; David, parcel, black and six copies remain. Clear target-relation mismatch.

- seed43 / forward: Expected back. Output repeats left, omits black/six-copies facts and does not terminate.

- seed43 / reverse: A behind-me fragment occurs, but the named observer, parcel identity and quantity relation are missing in the damaged memberId/and-I fragment. Do not classify this as a clear wrong direction solely from its relation word.

- seed43 / inverse: Expected restored front. Output repeats right, corrupts the observer identity and omits facts without termination.

seed42的inverse是仅目标关系错而身份/事实保持的清楚反例。reverse的剩余正文语法正常，只丢失任务所需空间关系；原grammar=false不是独立通用语法裁定。gold重编码mask为43，latent为44，所以此对照证明具体续步失败与自然原子能力并存，不能单独证明纯来源因果效应。同mask/depth来源比较另用预先固定P/Q/U矩阵。六例是同一世界的重复轨迹/seed，由Codex助手审阅，不是独立人工标注；其余未解析输出仍单列未知。
