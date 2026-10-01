# G14 同一today状态的生产者—接收者交叉诊断

完成seed=[42, 43, 44]；未完成seed=[]。零新增训练，固定T0/F3 final200/F2 final200，最长两次编辑。

1. iid，同正确today/同mask的F3来源差：fixed_Q_G=78.75pp，world bootstrap95%CI[75.21,82.08]；fixed_Q_R=0.00pp，world bootstrap95%CI[0.00,0.00]。正确互换还需看两来源同时成功，零差不等于正确互换。
2. iid，F3的G→R条件续步均值=0.00%，R→G=21.25%；G→G=100.00%，R→R=0.00%。具体逐世界分层见下表，不唯一归因内部机制。
3. iid，F2对应GG/GR/RG/RR均值=100.00%/44.79%/20.21%/0.00%；F2/F3直接差异只用同seed共同C，详见共同cohort和配对差表。
4. iid，F3自然today输入G/R接收均值=100.00%/100.00%；真实输出重编码G→R/R→R=100.00%/100.00%。C上重编码token/mask/encoder memory与自然输入逐元素一致；自然mask差异和全160世界技能另列，不用于筛除主C。
1. template_ood，同正确today/同mask的F3来源差：fixed_Q_G=69.38pp，world bootstrap95%CI[62.50,75.83]；fixed_Q_R=0.00pp，world bootstrap95%CI[0.00,0.00]。正确互换还需看两来源同时成功，零差不等于正确互换。
2. template_ood，F3的G→R条件续步均值=0.00%，R→G=2.29%；G→G=71.67%，R→R=0.00%。具体逐世界分层见下表，不唯一归因内部机制。
3. template_ood，F2对应GG/GR/RG/RR均值=71.67%/21.88%/3.96%/0.00%；F2/F3直接差异只用同seed共同C，详见共同cohort和配对差表。
4. template_ood，F3自然today输入G/R接收均值=78.75%/97.08%；真实输出重编码G→R/R→R=97.08%/97.08%。C上重编码token/mask/encoder memory与自然输入逐元素一致；自然mask差异和全160世界技能另列，不用于筛除主C。

固定 G 时，生产者变化在三个 seed 上均降低续步正确率；固定 F3 时，两路编辑态均失败，因此来源差为零不代表正确互换。F2 也存在自身两步失败，但旧来源接收能力具有强烈 seed 差异。IID 自然及真实输出重编码控制全部恢复，所有自然/编辑 mask 也相同；OOD 仍有自然技能与解析边界。详见 [结果解释与固定案例](INTERPRETATION.md)。本轮不能据此判定普通样本过拟合或表示有内在缺陷。

## 主交叉矩阵

每格联合成功k/C；匹配n/原始160。F3主对象、F2预设自然态继续训练对照。所有C由第一步正确全文/EOS/事实及G/R mask一致性决定，未使用任何下一步结果。

|R|seed|split|n/N|G→G|G→R|R→G|R→R|
|---|---|---|---|---|---|---|---|
|F3|42|iid|160/160|160/160 (100.00%)|0/160 (0.00%)|76/160 (47.50%)|0/160 (0.00%)|
|F3|42|template_ood|160/160|110/160 (68.75%)|0/160 (0.00%)|9/160 (5.62%)|0/160 (0.00%)|
|F3|43|iid|160/160|160/160 (100.00%)|0/160 (0.00%)|4/160 (2.50%)|0/160 (0.00%)|
|F3|43|template_ood|160/160|120/160 (75.00%)|0/160 (0.00%)|0/160 (0.00%)|0/160 (0.00%)|
|F3|44|iid|160/160|160/160 (100.00%)|0/160 (0.00%)|22/160 (13.75%)|0/160 (0.00%)|
|F3|44|template_ood|160/160|114/160 (71.25%)|0/160 (0.00%)|2/160 (1.25%)|0/160 (0.00%)|
|F2|42|iid|160/160|160/160 (100.00%)|86/160 (53.75%)|37/160 (23.12%)|0/160 (0.00%)|
|F2|42|template_ood|160/160|110/160 (68.75%)|35/160 (21.88%)|12/160 (7.50%)|0/160 (0.00%)|
|F2|43|iid|160/160|160/160 (100.00%)|0/160 (0.00%)|60/160 (37.50%)|0/160 (0.00%)|
|F2|43|template_ood|160/160|120/160 (75.00%)|0/160 (0.00%)|7/160 (4.38%)|0/160 (0.00%)|
|F2|44|iid|160/160|160/160 (100.00%)|129/160 (80.62%)|0/160 (0.00%)|0/160 (0.00%)|
|F2|44|template_ood|160/160|114/160 (71.25%)|70/160 (43.75%)|0/160 (0.00%)|0/160 (0.00%)|

## 固定接收者：逐世界配对四类

|R|seed|split|Q|C|两源都对|仅旧源对|仅新源对|两源都错|来源差pp|
|---|---|---|---|---|---|---|---|---|---|
|F2|42|iid|G|160|37|123|0|0|76.875|
|F2|42|iid|R|160|0|86|0|74|53.75|
|F2|42|template_ood|G|160|10|100|2|48|61.25000000000001|
|F2|42|template_ood|R|160|0|35|0|125|21.875|
|F3|42|iid|G|160|76|84|0|0|52.5|
|F3|42|iid|R|160|0|0|0|160|0.0|
|F3|42|template_ood|G|160|9|101|0|50|63.125|
|F3|42|template_ood|R|160|0|0|0|160|0.0|
|F2|43|iid|G|160|60|100|0|0|62.5|
|F2|43|iid|R|160|0|0|0|160|0.0|
|F2|43|template_ood|G|160|7|113|0|40|70.625|
|F2|43|template_ood|R|160|0|0|0|160|0.0|
|F3|43|iid|G|160|4|156|0|0|97.5|
|F3|43|iid|R|160|0|0|0|160|0.0|
|F3|43|template_ood|G|160|0|120|0|40|75.0|
|F3|43|template_ood|R|160|0|0|0|160|0.0|
|F2|44|iid|G|160|0|160|0|0|100.0|
|F2|44|iid|R|160|0|129|0|31|80.625|
|F2|44|template_ood|G|160|0|114|0|46|71.25|
|F2|44|template_ood|R|160|0|70|0|90|43.75|
|F3|44|iid|G|160|22|138|0|0|86.25|
|F3|44|iid|R|160|0|0|0|160|0.0|
|F3|44|template_ood|G|160|2|112|0|46|70.0|
|F3|44|template_ood|R|160|0|0|0|160|0.0|

## 原始分母：第一步及两步完整轨迹

此处不要求全文严格进入C；两步成功为first_joint AND next_joint。gate-and-next /160另表，不等同全部世界两步准确率。

|R|seed|split|first G|first R|GG full|GR full|RG full|RR full|
|---|---|---|---|---|---|---|---|---|
|F2|42|iid|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|86/160 (53.75%)|37/160 (23.12%)|0/160 (0.00%)|
|F2|42|template_ood|160/160 (100.00%)|160/160 (100.00%)|110/160 (68.75%)|35/160 (21.88%)|12/160 (7.50%)|0/160 (0.00%)|
|F3|42|iid|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|0/160 (0.00%)|76/160 (47.50%)|0/160 (0.00%)|
|F3|42|template_ood|160/160 (100.00%)|160/160 (100.00%)|110/160 (68.75%)|0/160 (0.00%)|9/160 (5.62%)|0/160 (0.00%)|
|F2|43|iid|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|0/160 (0.00%)|60/160 (37.50%)|0/160 (0.00%)|
|F2|43|template_ood|160/160 (100.00%)|160/160 (100.00%)|120/160 (75.00%)|0/160 (0.00%)|7/160 (4.38%)|0/160 (0.00%)|
|F3|43|iid|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|0/160 (0.00%)|4/160 (2.50%)|0/160 (0.00%)|
|F3|43|template_ood|160/160 (100.00%)|160/160 (100.00%)|120/160 (75.00%)|0/160 (0.00%)|0/160 (0.00%)|0/160 (0.00%)|
|F2|44|iid|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|129/160 (80.62%)|0/160 (0.00%)|0/160 (0.00%)|
|F2|44|template_ood|160/160 (100.00%)|160/160 (100.00%)|114/160 (71.25%)|70/160 (43.75%)|0/160 (0.00%)|0/160 (0.00%)|
|F3|44|iid|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|0/160 (0.00%)|22/160 (13.75%)|0/160 (0.00%)|
|F3|44|template_ood|160/160 (100.00%)|160/160 (100.00%)|114/160 (71.25%)|0/160 (0.00%)|2/160 (1.25%)|0/160 (0.00%)|

## gate-and-next /原始160

|R|seed|split|GG|GR|RG|RR|
|---|---|---|---|---|---|---|
|F2|42|iid|160/160 (100.00%)|86/160 (53.75%)|37/160 (23.12%)|0/160 (0.00%)|
|F2|42|template_ood|110/160 (68.75%)|35/160 (21.88%)|12/160 (7.50%)|0/160 (0.00%)|
|F3|42|iid|160/160 (100.00%)|0/160 (0.00%)|76/160 (47.50%)|0/160 (0.00%)|
|F3|42|template_ood|110/160 (68.75%)|0/160 (0.00%)|9/160 (5.62%)|0/160 (0.00%)|
|F2|43|iid|160/160 (100.00%)|0/160 (0.00%)|60/160 (37.50%)|0/160 (0.00%)|
|F2|43|template_ood|120/160 (75.00%)|0/160 (0.00%)|7/160 (4.38%)|0/160 (0.00%)|
|F3|43|iid|160/160 (100.00%)|0/160 (0.00%)|4/160 (2.50%)|0/160 (0.00%)|
|F3|43|template_ood|120/160 (75.00%)|0/160 (0.00%)|0/160 (0.00%)|0/160 (0.00%)|
|F2|44|iid|160/160 (100.00%)|129/160 (80.62%)|0/160 (0.00%)|0/160 (0.00%)|
|F2|44|template_ood|114/160 (71.25%)|70/160 (43.75%)|0/160 (0.00%)|0/160 (0.00%)|
|F3|44|iid|160/160 (100.00%)|0/160 (0.00%)|22/160 (13.75%)|0/160 (0.00%)|
|F3|44|template_ood|114/160 (71.25%)|0/160 (0.00%)|2/160 (1.25%)|0/160 (0.00%)|

## 自然与真实输出重编码控制

|R|seed|split|mode|P→Q|next k/C|raw next/160|raw two-step/160|
|---|---|---|---|---|---|---|---|
|F2|42|iid|natural|E→G|160/160 (100.00%)|160/160 (100.00%)|natural单步控制|
|F2|42|iid|natural|E→R|160/160 (100.00%)|160/160 (100.00%)|natural单步控制|
|F2|42|iid|reencode|G→G|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F2|42|iid|reencode|G→R|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F2|42|iid|reencode|R→G|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F2|42|iid|reencode|R→R|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F2|42|template_ood|natural|E→G|120/160 (75.00%)|120/160 (75.00%)|natural单步控制|
|F2|42|template_ood|natural|E→R|128/160 (80.00%)|128/160 (80.00%)|natural单步控制|
|F2|42|template_ood|reencode|G→G|120/160 (75.00%)|120/160 (75.00%)|120/160 (75.00%)|
|F2|42|template_ood|reencode|G→R|128/160 (80.00%)|128/160 (80.00%)|128/160 (80.00%)|
|F2|42|template_ood|reencode|R→G|120/160 (75.00%)|120/160 (75.00%)|120/160 (75.00%)|
|F2|42|template_ood|reencode|R→R|128/160 (80.00%)|128/160 (80.00%)|128/160 (80.00%)|
|F3|42|iid|natural|E→G|160/160 (100.00%)|160/160 (100.00%)|natural单步控制|
|F3|42|iid|natural|E→R|160/160 (100.00%)|160/160 (100.00%)|natural单步控制|
|F3|42|iid|reencode|G→G|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F3|42|iid|reencode|G→R|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F3|42|iid|reencode|R→G|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F3|42|iid|reencode|R→R|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F3|42|template_ood|natural|E→G|120/160 (75.00%)|120/160 (75.00%)|natural单步控制|
|F3|42|template_ood|natural|E→R|157/160 (98.12%)|157/160 (98.12%)|natural单步控制|
|F3|42|template_ood|reencode|G→G|120/160 (75.00%)|120/160 (75.00%)|120/160 (75.00%)|
|F3|42|template_ood|reencode|G→R|157/160 (98.12%)|157/160 (98.12%)|157/160 (98.12%)|
|F3|42|template_ood|reencode|R→G|120/160 (75.00%)|120/160 (75.00%)|120/160 (75.00%)|
|F3|42|template_ood|reencode|R→R|157/160 (98.12%)|157/160 (98.12%)|157/160 (98.12%)|
|F2|43|iid|natural|E→G|160/160 (100.00%)|160/160 (100.00%)|natural单步控制|
|F2|43|iid|natural|E→R|160/160 (100.00%)|160/160 (100.00%)|natural单步控制|
|F2|43|iid|reencode|G→G|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F2|43|iid|reencode|G→R|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F2|43|iid|reencode|R→G|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F2|43|iid|reencode|R→R|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F2|43|template_ood|natural|E→G|122/160 (76.25%)|122/160 (76.25%)|natural单步控制|
|F2|43|template_ood|natural|E→R|153/160 (95.62%)|153/160 (95.62%)|natural单步控制|
|F2|43|template_ood|reencode|G→G|122/160 (76.25%)|122/160 (76.25%)|122/160 (76.25%)|
|F2|43|template_ood|reencode|G→R|153/160 (95.62%)|153/160 (95.62%)|153/160 (95.62%)|
|F2|43|template_ood|reencode|R→G|122/160 (76.25%)|122/160 (76.25%)|122/160 (76.25%)|
|F2|43|template_ood|reencode|R→R|153/160 (95.62%)|153/160 (95.62%)|153/160 (95.62%)|
|F3|43|iid|natural|E→G|160/160 (100.00%)|160/160 (100.00%)|natural单步控制|
|F3|43|iid|natural|E→R|160/160 (100.00%)|160/160 (100.00%)|natural单步控制|
|F3|43|iid|reencode|G→G|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F3|43|iid|reencode|G→R|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F3|43|iid|reencode|R→G|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F3|43|iid|reencode|R→R|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F3|43|template_ood|natural|E→G|122/160 (76.25%)|122/160 (76.25%)|natural单步控制|
|F3|43|template_ood|natural|E→R|149/160 (93.12%)|149/160 (93.12%)|natural单步控制|
|F3|43|template_ood|reencode|G→G|122/160 (76.25%)|122/160 (76.25%)|122/160 (76.25%)|
|F3|43|template_ood|reencode|G→R|149/160 (93.12%)|149/160 (93.12%)|149/160 (93.12%)|
|F3|43|template_ood|reencode|R→G|122/160 (76.25%)|122/160 (76.25%)|122/160 (76.25%)|
|F3|43|template_ood|reencode|R→R|149/160 (93.12%)|149/160 (93.12%)|149/160 (93.12%)|
|F2|44|iid|natural|E→G|160/160 (100.00%)|160/160 (100.00%)|natural单步控制|
|F2|44|iid|natural|E→R|160/160 (100.00%)|160/160 (100.00%)|natural单步控制|
|F2|44|iid|reencode|G→G|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F2|44|iid|reencode|G→R|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F2|44|iid|reencode|R→G|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F2|44|iid|reencode|R→R|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F2|44|template_ood|natural|E→G|136/160 (85.00%)|136/160 (85.00%)|natural单步控制|
|F2|44|template_ood|natural|E→R|160/160 (100.00%)|160/160 (100.00%)|natural单步控制|
|F2|44|template_ood|reencode|G→G|136/160 (85.00%)|136/160 (85.00%)|136/160 (85.00%)|
|F2|44|template_ood|reencode|G→R|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F2|44|template_ood|reencode|R→G|136/160 (85.00%)|136/160 (85.00%)|136/160 (85.00%)|
|F2|44|template_ood|reencode|R→R|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F3|44|iid|natural|E→G|160/160 (100.00%)|160/160 (100.00%)|natural单步控制|
|F3|44|iid|natural|E→R|160/160 (100.00%)|160/160 (100.00%)|natural单步控制|
|F3|44|iid|reencode|G→G|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F3|44|iid|reencode|G→R|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F3|44|iid|reencode|R→G|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F3|44|iid|reencode|R→R|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F3|44|template_ood|natural|E→G|136/160 (85.00%)|136/160 (85.00%)|natural单步控制|
|F3|44|template_ood|natural|E→R|160/160 (100.00%)|160/160 (100.00%)|natural单步控制|
|F3|44|template_ood|reencode|G→G|136/160 (85.00%)|136/160 (85.00%)|136/160 (85.00%)|
|F3|44|template_ood|reencode|G→R|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|
|F3|44|template_ood|reencode|R→G|136/160 (85.00%)|136/160 (85.00%)|136/160 (85.00%)|
|F3|44|template_ood|reencode|R→R|160/160 (100.00%)|160/160 (100.00%)|160/160 (100.00%)|

|R|seed|split|自然重构exact/160|自然mask==源mask/160|C|C上reset==natural实例|
|---|---|---|---|---|---|---|
|F2|42|iid|160/160|160/160|160|320/320 (100.00%)|
|F2|42|template_ood|160/160|160/160|160|320/320 (100.00%)|
|F3|42|iid|160/160|160/160|160|320/320 (100.00%)|
|F3|42|template_ood|160/160|160/160|160|320/320 (100.00%)|
|F2|43|iid|160/160|160/160|160|320/320 (100.00%)|
|F2|43|template_ood|160/160|160/160|160|320/320 (100.00%)|
|F3|43|iid|160/160|160/160|160|320/320 (100.00%)|
|F3|43|template_ood|160/160|160/160|160|320/320 (100.00%)|
|F2|44|iid|160/160|160/160|160|320/320 (100.00%)|
|F2|44|template_ood|160/160|160/160|160|320/320 (100.00%)|
|F3|44|iid|160/160|160/160|160|320/320 (100.00%)|
|F3|44|template_ood|160/160|160/160|160|320/320 (100.00%)|

自然完整接口对照保留自身mask，未做跨来源mask覆盖。自然模式的raw_reconstruction_and_next指重构加一次编辑，不是两次语义编辑轨迹。自然重构正确且mask相同的C子集附在per_seed_results.csv，不能替代主C。相同文本控制输出不能作为额外独立样本。

## 三seed均值与sample SD

|R|split|metric|seed N|mean|SD|
|---|---|---|---|---|---|
|F2|iid|latent_GG_conditional|3|100.00%|0.00%|
|F2|iid|latent_GG_raw_two|3|100.00%|0.00%|
|F2|iid|latent_GR_conditional|3|44.79%|41.05%|
|F2|iid|latent_GR_raw_two|3|44.79%|41.05%|
|F2|iid|latent_RG_conditional|3|20.21%|18.92%|
|F2|iid|latent_RG_raw_two|3|20.21%|18.92%|
|F2|iid|latent_RR_conditional|3|0.00%|0.00%|
|F2|iid|latent_RR_raw_two|3|0.00%|0.00%|
|F2|iid|natural_EG_conditional|3|100.00%|0.00%|
|F2|iid|natural_EG_raw_reconstruction_and_next|3|100.00%|0.00%|
|F2|iid|natural_ER_conditional|3|100.00%|0.00%|
|F2|iid|natural_ER_raw_reconstruction_and_next|3|100.00%|0.00%|
|F2|iid|reencode_GG_conditional|3|100.00%|0.00%|
|F2|iid|reencode_GG_raw_two|3|100.00%|0.00%|
|F2|iid|reencode_GR_conditional|3|100.00%|0.00%|
|F2|iid|reencode_GR_raw_two|3|100.00%|0.00%|
|F2|iid|reencode_RG_conditional|3|100.00%|0.00%|
|F2|iid|reencode_RG_raw_two|3|100.00%|0.00%|
|F2|iid|reencode_RR_conditional|3|100.00%|0.00%|
|F2|iid|reencode_RR_raw_two|3|100.00%|0.00%|
|F2|iid|paired_QG_both_success|3|20.21%|18.92%|
|F2|iid|paired_QG_old_only|3|79.79%|18.92%|
|F2|iid|paired_QG_new_only|3|0.00%|0.00%|
|F2|iid|paired_QG_both_fail|3|0.00%|0.00%|
|F2|iid|paired_QR_both_success|3|0.00%|0.00%|
|F2|iid|paired_QR_old_only|3|44.79%|41.05%|
|F2|iid|paired_QR_new_only|3|0.00%|0.00%|
|F2|iid|paired_QR_both_fail|3|55.21%|41.05%|
|F2|template_ood|latent_GG_conditional|3|71.67%|3.15%|
|F2|template_ood|latent_GG_raw_two|3|71.67%|3.15%|
|F2|template_ood|latent_GR_conditional|3|21.88%|21.88%|
|F2|template_ood|latent_GR_raw_two|3|21.88%|21.88%|
|F2|template_ood|latent_RG_conditional|3|3.96%|3.77%|
|F2|template_ood|latent_RG_raw_two|3|3.96%|3.77%|
|F2|template_ood|latent_RR_conditional|3|0.00%|0.00%|
|F2|template_ood|latent_RR_raw_two|3|0.00%|0.00%|
|F2|template_ood|natural_EG_conditional|3|78.75%|5.45%|
|F2|template_ood|natural_EG_raw_reconstruction_and_next|3|78.75%|5.45%|
|F2|template_ood|natural_ER_conditional|3|91.88%|10.51%|
|F2|template_ood|natural_ER_raw_reconstruction_and_next|3|91.88%|10.51%|
|F2|template_ood|reencode_GG_conditional|3|78.75%|5.45%|
|F2|template_ood|reencode_GG_raw_two|3|78.75%|5.45%|
|F2|template_ood|reencode_GR_conditional|3|91.88%|10.51%|
|F2|template_ood|reencode_GR_raw_two|3|91.88%|10.51%|
|F2|template_ood|reencode_RG_conditional|3|78.75%|5.45%|
|F2|template_ood|reencode_RG_raw_two|3|78.75%|5.45%|
|F2|template_ood|reencode_RR_conditional|3|91.88%|10.51%|
|F2|template_ood|reencode_RR_raw_two|3|91.88%|10.51%|
|F2|template_ood|paired_QG_both_success|3|3.54%|3.21%|
|F2|template_ood|paired_QG_old_only|3|68.12%|4.88%|
|F2|template_ood|paired_QG_new_only|3|0.42%|0.72%|
|F2|template_ood|paired_QG_both_fail|3|27.92%|2.60%|
|F2|template_ood|paired_QR_both_success|3|0.00%|0.00%|
|F2|template_ood|paired_QR_old_only|3|21.88%|21.88%|
|F2|template_ood|paired_QR_new_only|3|0.00%|0.00%|
|F2|template_ood|paired_QR_both_fail|3|78.12%|21.88%|
|F3|iid|latent_GG_conditional|3|100.00%|0.00%|
|F3|iid|latent_GG_raw_two|3|100.00%|0.00%|
|F3|iid|latent_GR_conditional|3|0.00%|0.00%|
|F3|iid|latent_GR_raw_two|3|0.00%|0.00%|
|F3|iid|latent_RG_conditional|3|21.25%|23.42%|
|F3|iid|latent_RG_raw_two|3|21.25%|23.42%|
|F3|iid|latent_RR_conditional|3|0.00%|0.00%|
|F3|iid|latent_RR_raw_two|3|0.00%|0.00%|
|F3|iid|natural_EG_conditional|3|100.00%|0.00%|
|F3|iid|natural_EG_raw_reconstruction_and_next|3|100.00%|0.00%|
|F3|iid|natural_ER_conditional|3|100.00%|0.00%|
|F3|iid|natural_ER_raw_reconstruction_and_next|3|100.00%|0.00%|
|F3|iid|reencode_GG_conditional|3|100.00%|0.00%|
|F3|iid|reencode_GG_raw_two|3|100.00%|0.00%|
|F3|iid|reencode_GR_conditional|3|100.00%|0.00%|
|F3|iid|reencode_GR_raw_two|3|100.00%|0.00%|
|F3|iid|reencode_RG_conditional|3|100.00%|0.00%|
|F3|iid|reencode_RG_raw_two|3|100.00%|0.00%|
|F3|iid|reencode_RR_conditional|3|100.00%|0.00%|
|F3|iid|reencode_RR_raw_two|3|100.00%|0.00%|
|F3|iid|paired_QG_both_success|3|21.25%|23.42%|
|F3|iid|paired_QG_old_only|3|78.75%|23.42%|
|F3|iid|paired_QG_new_only|3|0.00%|0.00%|
|F3|iid|paired_QG_both_fail|3|0.00%|0.00%|
|F3|iid|paired_QR_both_success|3|0.00%|0.00%|
|F3|iid|paired_QR_old_only|3|0.00%|0.00%|
|F3|iid|paired_QR_new_only|3|0.00%|0.00%|
|F3|iid|paired_QR_both_fail|3|100.00%|0.00%|
|F3|template_ood|latent_GG_conditional|3|71.67%|3.15%|
|F3|template_ood|latent_GG_raw_two|3|71.67%|3.15%|
|F3|template_ood|latent_GR_conditional|3|0.00%|0.00%|
|F3|template_ood|latent_GR_raw_two|3|0.00%|0.00%|
|F3|template_ood|latent_RG_conditional|3|2.29%|2.95%|
|F3|template_ood|latent_RG_raw_two|3|2.29%|2.95%|
|F3|template_ood|latent_RR_conditional|3|0.00%|0.00%|
|F3|template_ood|latent_RR_raw_two|3|0.00%|0.00%|
|F3|template_ood|natural_EG_conditional|3|78.75%|5.45%|
|F3|template_ood|natural_EG_raw_reconstruction_and_next|3|78.75%|5.45%|
|F3|template_ood|natural_ER_conditional|3|97.08%|3.55%|
|F3|template_ood|natural_ER_raw_reconstruction_and_next|3|97.08%|3.55%|
|F3|template_ood|reencode_GG_conditional|3|78.75%|5.45%|
|F3|template_ood|reencode_GG_raw_two|3|78.75%|5.45%|
|F3|template_ood|reencode_GR_conditional|3|97.08%|3.55%|
|F3|template_ood|reencode_GR_raw_two|3|97.08%|3.55%|
|F3|template_ood|reencode_RG_conditional|3|78.75%|5.45%|
|F3|template_ood|reencode_RG_raw_two|3|78.75%|5.45%|
|F3|template_ood|reencode_RR_conditional|3|97.08%|3.55%|
|F3|template_ood|reencode_RR_raw_two|3|97.08%|3.55%|
|F3|template_ood|paired_QG_both_success|3|2.29%|2.95%|
|F3|template_ood|paired_QG_old_only|3|69.38%|5.96%|
|F3|template_ood|paired_QG_new_only|3|0.00%|0.00%|
|F3|template_ood|paired_QG_both_fail|3|28.33%|3.15%|
|F3|template_ood|paired_QR_both_success|3|0.00%|0.00%|
|F3|template_ood|paired_QR_old_only|3|0.00%|0.00%|
|F3|template_ood|paired_QR_new_only|3|0.00%|0.00%|
|F3|template_ood|paired_QR_both_fail|3|100.00%|0.00%|

## 配对差与固定模型世界bootstrap

来源差为A_GQ−A_RQ；接收者差为A_PG−A_PR。2000次同世界配对抽样，跨seed/方法共享原始世界draw再限制到事前C；空cohort NA、空抽样显式计数并省略，无分母替换。CI只反映固定模型的世界抽样不确定性；三个seed不能覆盖全部训练随机性，也不是480次独立训练。每比例Wilson95在per_seed_results/current_results/source_paired_counts.csv；全零/全一的退化bootstrap不是总体无不确定性证明。

|kind|R|split|seed|contrast|n|delta pp|seed SD pp (mean rows)|CI95 pp|empty draws|
|---|---|---|---|---|---|---|---|---|---|
|source|F2|iid|42|fixed_Q_G|160|76.875|NA|[70.0,83.125]|0|
|source|F2|iid|42|fixed_Q_R|160|53.75|NA|[46.25,61.875]|0|
|receiver|F2|iid|42|fixed_P_G|160|46.25|NA|[38.125,53.75]|0|
|receiver|F2|iid|42|fixed_P_R|160|23.125|NA|[16.875,30.0]|0|
|source|F2|template_ood|42|fixed_Q_G|160|61.25000000000001|NA|[53.125,69.375]|0|
|source|F2|template_ood|42|fixed_Q_R|160|21.875|NA|[15.625,28.749999999999996]|0|
|receiver|F2|template_ood|42|fixed_P_G|160|46.875|NA|[38.125,55.00000000000001]|0|
|receiver|F2|template_ood|42|fixed_P_R|160|7.5|NA|[3.75,11.875]|0|
|source|F2|iid|43|fixed_Q_G|160|62.5|NA|[55.625,70.0]|0|
|source|F2|iid|43|fixed_Q_R|160|0.0|NA|[0.0,0.0]|0|
|receiver|F2|iid|43|fixed_P_G|160|100.0|NA|[100.0,100.0]|0|
|receiver|F2|iid|43|fixed_P_R|160|37.5|NA|[30.0,44.375]|0|
|source|F2|template_ood|43|fixed_Q_G|160|70.625|NA|[63.125,77.5]|0|
|source|F2|template_ood|43|fixed_Q_R|160|0.0|NA|[0.0,0.0]|0|
|receiver|F2|template_ood|43|fixed_P_G|160|75.0|NA|[68.125,81.25]|0|
|receiver|F2|template_ood|43|fixed_P_R|160|4.375|NA|[1.25,7.5]|0|
|source|F2|iid|44|fixed_Q_G|160|100.0|NA|[100.0,100.0]|0|
|source|F2|iid|44|fixed_Q_R|160|80.625|NA|[74.375,86.26562499999993]|0|
|receiver|F2|iid|44|fixed_P_G|160|19.375|NA|[13.734375000000002,25.624999999999996]|0|
|receiver|F2|iid|44|fixed_P_R|160|0.0|NA|[0.0,0.0]|0|
|source|F2|template_ood|44|fixed_Q_G|160|71.25|NA|[63.74999999999999,78.125]|0|
|source|F2|template_ood|44|fixed_Q_R|160|43.75|NA|[36.25,51.87500000000001]|0|
|receiver|F2|template_ood|44|fixed_P_G|160|27.500000000000004|NA|[20.625,34.375]|0|
|receiver|F2|template_ood|44|fixed_P_R|160|0.0|NA|[0.0,0.0]|0|
|source|F3|iid|42|fixed_Q_G|160|52.5|NA|[45.0,60.0]|0|
|source|F3|iid|42|fixed_Q_R|160|0.0|NA|[0.0,0.0]|0|
|receiver|F3|iid|42|fixed_P_G|160|100.0|NA|[100.0,100.0]|0|
|receiver|F3|iid|42|fixed_P_R|160|47.5|NA|[40.0,55.00000000000001]|0|
|source|F3|template_ood|42|fixed_Q_G|160|63.125|NA|[55.625,70.625]|0|
|source|F3|template_ood|42|fixed_Q_R|160|0.0|NA|[0.0,0.0]|0|
|receiver|F3|template_ood|42|fixed_P_G|160|68.75|NA|[61.25000000000001,76.25]|0|
|receiver|F3|template_ood|42|fixed_P_R|160|5.625|NA|[2.5,9.375]|0|
|source|F3|iid|43|fixed_Q_G|160|97.5|NA|[95.0,99.375]|0|
|source|F3|iid|43|fixed_Q_R|160|0.0|NA|[0.0,0.0]|0|
|receiver|F3|iid|43|fixed_P_G|160|100.0|NA|[100.0,100.0]|0|
|receiver|F3|iid|43|fixed_P_R|160|2.5|NA|[0.625,5.0]|0|
|source|F3|template_ood|43|fixed_Q_G|160|75.0|NA|[68.125,81.25]|0|
|source|F3|template_ood|43|fixed_Q_R|160|0.0|NA|[0.0,0.0]|0|
|receiver|F3|template_ood|43|fixed_P_G|160|75.0|NA|[68.125,81.25]|0|
|receiver|F3|template_ood|43|fixed_P_R|160|0.0|NA|[0.0,0.0]|0|
|source|F3|iid|44|fixed_Q_G|160|86.25|NA|[80.625,91.25]|0|
|source|F3|iid|44|fixed_Q_R|160|0.0|NA|[0.0,0.0]|0|
|receiver|F3|iid|44|fixed_P_G|160|100.0|NA|[100.0,100.0]|0|
|receiver|F3|iid|44|fixed_P_R|160|13.750000000000002|NA|[8.75,19.375]|0|
|source|F3|template_ood|44|fixed_Q_G|160|70.0|NA|[62.5,76.875]|0|
|source|F3|template_ood|44|fixed_Q_R|160|0.0|NA|[0.0,0.0]|0|
|receiver|F3|template_ood|44|fixed_P_G|160|71.25|NA|[63.74999999999999,78.125]|0|
|receiver|F3|template_ood|44|fixed_P_R|160|1.25|NA|[0.0,3.125]|0|
|F3-F2|F3-F2|iid|42|GG|160|0.0|NA|[0.0,0.0]|0|
|F3-F2|F3-F2|iid|42|GR|160|-53.75|NA|[-61.875,-46.25]|0|
|F3-F2|F3-F2|iid|42|RG|160|24.375|NA|[18.125,31.25]|0|
|F3-F2|F3-F2|iid|42|RR|160|0.0|NA|[0.0,0.0]|0|
|F3-F2|F3-F2|template_ood|42|GG|160|0.0|NA|[0.0,0.0]|0|
|F3-F2|F3-F2|template_ood|42|GR|160|-21.875|NA|[-28.749999999999996,-15.625]|0|
|F3-F2|F3-F2|template_ood|42|RG|160|-1.875|NA|[-7.5,3.75]|0|
|F3-F2|F3-F2|template_ood|42|RR|160|0.0|NA|[0.0,0.0]|0|
|F3-F2|F3-F2|iid|43|GG|160|0.0|NA|[0.0,0.0]|0|
|F3-F2|F3-F2|iid|43|GR|160|0.0|NA|[0.0,0.0]|0|
|F3-F2|F3-F2|iid|43|RG|160|-35.0|NA|[-41.875,-27.500000000000004]|0|
|F3-F2|F3-F2|iid|43|RR|160|0.0|NA|[0.0,0.0]|0|
|F3-F2|F3-F2|template_ood|43|GG|160|0.0|NA|[0.0,0.0]|0|
|F3-F2|F3-F2|template_ood|43|GR|160|0.0|NA|[0.0,0.0]|0|
|F3-F2|F3-F2|template_ood|43|RG|160|-4.375|NA|[-7.5,-1.25]|0|
|F3-F2|F3-F2|template_ood|43|RR|160|0.0|NA|[0.0,0.0]|0|
|F3-F2|F3-F2|iid|44|GG|160|0.0|NA|[0.0,0.0]|0|
|F3-F2|F3-F2|iid|44|GR|160|-80.625|NA|[-86.265625,-74.375]|0|
|F3-F2|F3-F2|iid|44|RG|160|13.750000000000002|NA|[8.75,19.375]|0|
|F3-F2|F3-F2|iid|44|RR|160|0.0|NA|[0.0,0.0]|0|
|F3-F2|F3-F2|template_ood|44|GG|160|0.0|NA|[0.0,0.0]|0|
|F3-F2|F3-F2|template_ood|44|GR|160|-43.75|NA|[-51.87500000000001,-36.25]|0|
|F3-F2|F3-F2|template_ood|44|RG|160|1.25|NA|[0.0,3.125]|0|
|F3-F2|F3-F2|template_ood|44|RR|160|0.0|NA|[0.0,0.0]|0|
|source|F2|iid|mean|fixed_Q_G|{"42": 160, "43": 160, "44": 160}|79.79166666666667|18.919373888512624|[76.875,82.91666666666666]|0|
|source|F2|iid|mean|fixed_Q_R|{"42": 160, "43": 160, "44": 160}|44.791666666666664|41.052240600646066|[41.66666666666667,47.70833333333333]|0|
|receiver|F2|iid|mean|fixed_P_G|{"42": 160, "43": 160, "44": 160}|55.208333333333336|41.052240600646066|[52.29166666666667,58.333333333333336]|0|
|receiver|F2|iid|mean|fixed_P_R|{"42": 160, "43": 160, "44": 160}|20.208333333333332|18.919373888512624|[17.083333333333332,23.125000000000004]|0|
|source|F2|template_ood|mean|fixed_Q_G|{"42": 160, "43": 160, "44": 160}|67.70833333333334|5.601804024895309|[60.83333333333334,73.95833333333334]|0|
|source|F2|template_ood|mean|fixed_Q_R|{"42": 160, "43": 160, "44": 160}|21.875|21.875|[18.125,25.625000000000004]|0|
|receiver|F2|template_ood|mean|fixed_P_G|{"42": 160, "43": 160, "44": 160}|49.79166666666667|23.883942478856653|[43.958333333333336,55.625]|0|
|receiver|F2|template_ood|mean|fixed_P_R|{"42": 160, "43": 160, "44": 160}|3.9583333333333335|3.7673211083385674|[2.5,5.625]|0|
|source|F3|iid|mean|fixed_Q_G|{"42": 160, "43": 160, "44": 160}|78.75|23.418742493993992|[75.20833333333333,82.08333333333334]|0|
|source|F3|iid|mean|fixed_Q_R|{"42": 160, "43": 160, "44": 160}|0.0|0.0|[0.0,0.0]|0|
|receiver|F3|iid|mean|fixed_P_G|{"42": 160, "43": 160, "44": 160}|100.0|0.0|[100.0,100.0]|0|
|receiver|F3|iid|mean|fixed_P_R|{"42": 160, "43": 160, "44": 160}|21.25|23.418742493993992|[17.916666666666668,24.791666666666664]|0|
|source|F3|template_ood|mean|fixed_Q_G|{"42": 160, "43": 160, "44": 160}|69.375|5.96212000885591|[62.500000000000014,75.83333333333333]|0|
|source|F3|template_ood|mean|fixed_Q_R|{"42": 160, "43": 160, "44": 160}|0.0|0.0|[0.0,0.0]|0|
|receiver|F3|template_ood|mean|fixed_P_G|{"42": 160, "43": 160, "44": 160}|71.66666666666667|3.1457643480294792|[64.58333333333334,78.125]|0|
|receiver|F3|template_ood|mean|fixed_P_R|{"42": 160, "43": 160, "44": 160}|2.2916666666666665|2.9536347664078804|[1.0416666666666665,3.75]|0|
|F3-F2|F3-F2|iid|mean|GG|{"42": 160, "43": 160, "44": 160}|0.0|0.0|[0.0,0.0]|0|
|F3-F2|F3-F2|iid|mean|GR|{"42": 160, "43": 160, "44": 160}|-44.791666666666664|41.052240600646066|[-47.70833333333333,-41.66666666666667]|0|
|F3-F2|F3-F2|iid|mean|RG|{"42": 160, "43": 160, "44": 160}|1.0416666666666672|31.661869154131335|[-2.291666666666667,4.583333333333334]|0|
|F3-F2|F3-F2|iid|mean|RR|{"42": 160, "43": 160, "44": 160}|0.0|0.0|[0.0,0.0]|0|
|F3-F2|F3-F2|template_ood|mean|GG|{"42": 160, "43": 160, "44": 160}|0.0|0.0|[0.0,0.0]|0|
|F3-F2|F3-F2|template_ood|mean|GR|{"42": 160, "43": 160, "44": 160}|-21.875|21.875|[-25.625000000000004,-18.125]|0|
|F3-F2|F3-F2|template_ood|mean|RG|{"42": 160, "43": 160, "44": 160}|-1.6666666666666667|2.8182810955143087|[-3.7552083333333335,0.625]|0|
|F3-F2|F3-F2|template_ood|mean|RR|{"42": 160, "43": 160, "44": 160}|0.0|0.0|[0.0,0.0]|0|

## F2/F3共同匹配集合

|seed|split|cell|intersection n|F3 k|F2 k|
|---|---|---|---|---|---|
|42|iid|GG|160|160|160|
|42|iid|GR|160|0|86|
|42|iid|RG|160|76|37|
|42|iid|RR|160|0|0|
|42|iid|all four correctness patterns identical|160|71|NA|
|42|template_ood|GG|160|110|110|
|42|template_ood|GR|160|0|35|
|42|template_ood|RG|160|9|12|
|42|template_ood|RR|160|0|0|
|42|template_ood|all four correctness patterns identical|160|119|NA|
|43|iid|GG|160|160|160|
|43|iid|GR|160|0|0|
|43|iid|RG|160|4|60|
|43|iid|RR|160|0|0|
|43|iid|all four correctness patterns identical|160|104|NA|
|43|template_ood|GG|160|120|120|
|43|template_ood|GR|160|0|0|
|43|template_ood|RG|160|0|7|
|43|template_ood|RR|160|0|0|
|43|template_ood|all four correctness patterns identical|160|153|NA|
|44|iid|GG|160|160|160|
|44|iid|GR|160|0|129|
|44|iid|RG|160|22|0|
|44|iid|RR|160|0|0|
|44|iid|all four correctness patterns identical|160|30|NA|
|44|template_ood|GG|160|114|114|
|44|template_ood|GR|160|0|70|
|44|template_ood|RG|160|2|0|
|44|template_ood|RR|160|0|0|
|44|template_ood|all four correctness patterns identical|160|90|NA|

## GG正确且RR错误世界的描述性定位

这个分层使用第二步结果，仅描述，绝不是匹配门槛。没有该类世界则n=0/NA；不存在类别显式absent。

|R|seed|split|subset n|GR|RG|k|描述|
|---|---|---|---|---|---|---|---|
|F2|42|iid|160|False|True|1|receiver-update failure on both tested edited sources|
|F2|42|iid|160|True|False|50|new producer state incompatible with both tested recipients|
|F2|42|iid|160|False|False|73|either endpoint change breaks old success|
|F2|42|iid|160|True|True|36|specific producer/receiver pairing incompatibility|
|F2|42|template_ood|110|False|True|0|receiver-update failure on both tested edited sources|
|F2|42|template_ood|110|True|False|22|new producer state incompatible with both tested recipients|
|F2|42|template_ood|110|False|False|78|either endpoint change breaks old success|
|F2|42|template_ood|110|True|True|10|specific producer/receiver pairing incompatibility|
|F3|42|iid|160|False|True|76|receiver-update failure on both tested edited sources|
|F3|42|iid|160|True|False|0|new producer state incompatible with both tested recipients|
|F3|42|iid|160|False|False|84|either endpoint change breaks old success|
|F3|42|iid|160|True|True|0|specific producer/receiver pairing incompatibility|
|F3|42|template_ood|110|False|True|9|receiver-update failure on both tested edited sources|
|F3|42|template_ood|110|True|False|0|new producer state incompatible with both tested recipients|
|F3|42|template_ood|110|False|False|101|either endpoint change breaks old success|
|F3|42|template_ood|110|True|True|0|specific producer/receiver pairing incompatibility|
|F2|43|iid|160|False|True|60|receiver-update failure on both tested edited sources|
|F2|43|iid|160|True|False|0|new producer state incompatible with both tested recipients|
|F2|43|iid|160|False|False|100|either endpoint change breaks old success|
|F2|43|iid|160|True|True|0|specific producer/receiver pairing incompatibility|
|F2|43|template_ood|120|False|True|7|receiver-update failure on both tested edited sources|
|F2|43|template_ood|120|True|False|0|new producer state incompatible with both tested recipients|
|F2|43|template_ood|120|False|False|113|either endpoint change breaks old success|
|F2|43|template_ood|120|True|True|0|specific producer/receiver pairing incompatibility|
|F3|43|iid|160|False|True|4|receiver-update failure on both tested edited sources|
|F3|43|iid|160|True|False|0|new producer state incompatible with both tested recipients|
|F3|43|iid|160|False|False|156|either endpoint change breaks old success|
|F3|43|iid|160|True|True|0|specific producer/receiver pairing incompatibility|
|F3|43|template_ood|120|False|True|0|receiver-update failure on both tested edited sources|
|F3|43|template_ood|120|True|False|0|new producer state incompatible with both tested recipients|
|F3|43|template_ood|120|False|False|120|either endpoint change breaks old success|
|F3|43|template_ood|120|True|True|0|specific producer/receiver pairing incompatibility|
|F2|44|iid|160|False|True|0|receiver-update failure on both tested edited sources|
|F2|44|iid|160|True|False|129|new producer state incompatible with both tested recipients|
|F2|44|iid|160|False|False|31|either endpoint change breaks old success|
|F2|44|iid|160|True|True|0|specific producer/receiver pairing incompatibility|
|F2|44|template_ood|114|False|True|0|receiver-update failure on both tested edited sources|
|F2|44|template_ood|114|True|False|70|new producer state incompatible with both tested recipients|
|F2|44|template_ood|114|False|False|44|either endpoint change breaks old success|
|F2|44|template_ood|114|True|True|0|specific producer/receiver pairing incompatibility|
|F3|44|iid|160|False|True|22|receiver-update failure on both tested edited sources|
|F3|44|iid|160|True|False|0|new producer state incompatible with both tested recipients|
|F3|44|iid|160|False|False|138|either endpoint change breaks old success|
|F3|44|iid|160|True|True|0|specific producer/receiver pairing incompatibility|
|F3|44|template_ood|114|False|True|2|receiver-update failure on both tested edited sources|
|F3|44|template_ood|114|True|False|0|new producer state incompatible with both tested recipients|
|F3|44|template_ood|114|False|False|112|either endpoint change breaks old success|
|F3|44|template_ood|114|True|True|0|specific producer/receiver pairing incompatibility|

改变生产者或接收者的实际行为差异只约束这两个已测试固定接收者。即使新状态两边都失败，也不证明语义丢失、对所有可能接收者不可用或latent编辑不可能。模板OOD共享既有词汇，不等同开放自然语言。没有按结果调整的高/低阈值，没有新训练、第三步或长链扩展。

## 工程复现、数据、资源和工件

历史复现每seed每split16世界：3模型×2步×32=192次逐文本/评分/EOS/有效长度核对；三个seed共576次。它们只用于工程复现，不加入320新世界确认统计。seed42 smoke仅历史世界；正式seed先复现再确认。完整历史清单和比对在data/history_batches.json、data/history_expected.jsonl、history_reproduction_s*.json。

新IID160/OOD160，三seed及F2/F3共用；数据主seed20261001，完整事实身份/全部合法日期人称render及可访问历史manifest去重范围、SHA、实际命名叶子RNG见data/manifest.json。检查点来自G13实际映射并核验全部旧artifact manifest SHA；从未选择best或回退。

未通过当前匹配的世界仍有完整输出/评分；没有补样本。每条包含current/next原文、gold、joint/exact、可靠解析事实/日期偏差、错误类型、mask/IDs/memory hashes、实际mask和有效长度。error_counts.csv分开未决/明确日期错/非日期事实错/二者皆错/格式差异；relative_date_errors.csv只统计可解析日期，不将所有失败称为推进过头。

12个事前hash案例见CASES.md/cases.jsonl，不按错误或成功选择。完整逐例记录per_example.jsonl.gz，解压得所需plain文件；精确本地路径/hash见per_example_manifest.json。大型完整FP32状态缓存留local/，data/confirm_s*_states.json记录实际路径/sha；不上传模型、重复旧checkpoint或latent。冻结前后、缓存保存重放、输入不变、当前门槛独立、零optimizer/backward在smoke_test.json和seed_s*_complete.json。

所有GPU经sbatch+srun，单卡smoke结束后一个array0–2%2；索引显式映射seed，内部顺序，无CUDA_VISIBLE_DEVICES覆盖。分区B300q/default account/QOS/exclude node01沿G13核验环境，官方语法参考：[job arrays](https://slurm.schedmd.com/job_array.html)、[sbatch](https://slurm.schedmd.com/sbatch.html)、[srun](https://slurm.schedmd.com/srun.html)。请求walltime仅据smoke吞吐量确定，科学规模不变。

实际/请求allocation预算：{"limit_gpu_hours": 4, "actual_gpu_hours": 0.12861111111111112, "requested_gpu_hours": 1.0, "max_concurrent_gpus": 2, "allocation_only": true, "steps_not_double_counted": true, "measured_concurrency": true, "within_limits": true}

|JobID|raw ID|state|exit|start|end|GPU hours|
|---|---|---|---|---|---|---|
|2447|2447|COMPLETED|0:0|2026-10-01T16:19:30|2026-10-01T16:20:33|0.0175|
|2449_0|2450|COMPLETED|0:0|2026-10-01T16:26:05|2026-10-01T16:28:00|0.03194444444444444|
|2449_1|2451|COMPLETED|0:0|2026-10-01T16:26:05|2026-10-01T16:28:57|0.04777777777777778|
|2449_2|2449|COMPLETED|0:0|2026-10-01T16:28:00|2026-10-01T16:29:53|0.03138888888888889|

偏离/失败记录：[{"event": "daemon restart before any GPU submission", "response": "checked process/job/submission state; reran same CPU suite because prior tool output delivery interrupted", "new_GPU_retry": false, "scientific_change": false, "data_changed": false}]。未完成seed=[]。没有因结果不好重试或追加科学实验。
