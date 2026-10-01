# G16 能力约束下的固定来源修复与留出迁移复验

1. **选择结果：seed42→step50，seed43→step25，seed44→step25；没有选择失败。** 原始计数核验最早合格，step0不选，全部F仍训练到200。

2. **所选模型在IID逐seed保住40-cell自然能力和旧yesterday all3，并达到自身两步修复工作标准。** guard原子macro为99.70%, 100.00%, 99.86%；最低cell为96.88%, 100.00%, 94.38%；旧all3均160/160，自身full2为160/160, 153/160, 160/160。这是已监督任务的新世界运行检查，不是新长度泛化。

3. **未读取U的规则选择后，IID留出U仍得到正向迁移。** guard为156/160, 160/160, 160/160，P/N各seed均0/160；三个seed均达到U≥90%的工作目标，逐seed配对world CI支持改善。相对P和N的均值改变量均为+99.167 pp [95% world CI +98.333, +99.792]; seed SD 1.443 pp。这仅是G15已考察过的精确F2 final200生产者在新世界上的复验。

4. **没有guard相对final200的能力保持优势；G15的seed44 IID末段退化没有在本轮重现。** F-final的全部IID自然cell均160/160，旧all3均160/160，U与自身full2均为158/160, 160/160, 160/160。guard−final的原子macro为-0.146 pp [95% world CI -0.219, -0.089]; seed SD 0.149 pp，U为-0.417 pp [95% world CI -1.250, +0.417]; seed SD 0.722 pp，full2为-1.042 pp [95% world CI -2.292, +0.208]; seed SD 2.954 pp。两个版本均通过三seed IID工作目标，不能据此宣称guard更优或必要。

**边界：三个guard的OOD自然macro为94.50%、91.00%、91.95%，最低cell为73.13%、75.00%、53.13%，均未通过能力标准。** OOD U为115/160、160/160、160/160，self full2为159/160、160/160、160/160；seed42迁移有改善但未达U≥90%。final的OOD只有seed44通过完整工作目标。IID guard对G-today仅81/160、124/160、30/160，虽P均160/160且U很高，也不能称普遍来源互换。三个IID guard的全部固定来源同时成功仅81/160、124/160、30/160。

|seed|split|版本|实际步|macro|min-cell|旧all3|固定P|U|旧G|self1|self2 endpoint|full2|C/N|完整工作目标|配对改善区间支持|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|42|iid|F-final|200|100.00%|100.00%|160/160|160/160|158/160|126/160|160/160|158/160|158/160|160/160|True|True|
|42|template_ood|F-final|200|96.72%|75.00%|108/108|129/160|101/160|153/160|160/160|128/160|128/160|160/160|False|True|
|42|iid|F-guard|50|99.70%|96.88%|160/160|160/160|156/160|81/160|160/160|160/160|160/160|160/160|True|True|
|42|template_ood|F-guard|50|94.50%|73.12%|108/108|160/160|115/160|152/160|159/160|159/160|159/160|160/160|False|True|
|42|iid|N-final|200|100.00%|100.00%|160/160|0/160|0/160|0/160|160/160|0/160|0/160|160/160|False|False|
|42|template_ood|N-final|200|99.36%|85.00%|108/108|0/160|0/160|0/160|160/160|0/160|0/160|160/160|False|False|
|42|iid|P|0|100.00%|100.00%|160/160|0/160|0/160|0/160|160/160|0/160|0/160|160/160|False|False|
|42|template_ood|P|0|97.78%|75.00%|108/108|0/160|0/160|0/160|160/160|0/160|0/160|160/160|False|False|
|43|iid|F-final|200|100.00%|100.00%|160/160|160/160|160/160|153/160|160/160|160/160|160/160|160/160|True|True|
|43|template_ood|F-final|200|94.28%|75.00%|120/120|160/160|160/160|119/160|160/160|160/160|160/160|160/160|False|True|
|43|iid|F-guard|25|100.00%|100.00%|160/160|160/160|160/160|124/160|160/160|153/160|153/160|160/160|True|True|
|43|template_ood|F-guard|25|91.00%|75.00%|120/120|160/160|160/160|111/160|160/160|160/160|160/160|160/160|False|True|
|43|iid|N-final|200|100.00%|100.00%|160/160|0/160|0/160|0/160|160/160|0/160|0/160|160/160|False|False|
|43|template_ood|N-final|200|99.03%|81.25%|120/120|0/160|0/160|0/160|160/160|0/160|0/160|160/160|False|False|
|43|iid|P|0|100.00%|100.00%|160/160|0/160|0/160|0/160|160/160|0/160|0/160|160/160|False|False|
|43|template_ood|P|0|97.09%|79.38%|120/120|0/160|0/160|0/160|160/160|0/160|0/160|160/160|False|False|
|44|iid|F-final|200|100.00%|100.00%|160/160|160/160|160/160|122/160|160/160|160/160|160/160|160/160|True|True|
|44|template_ood|F-final|200|99.45%|90.00%|119/119|160/160|160/160|123/160|160/160|160/160|160/160|160/160|True|True|
|44|iid|F-guard|25|99.86%|94.38%|160/160|160/160|160/160|30/160|160/160|160/160|160/160|160/160|True|True|
|44|template_ood|F-guard|25|91.95%|53.12%|119/119|160/160|160/160|43/160|160/160|160/160|160/160|160/160|False|True|
|44|iid|N-final|200|100.00%|100.00%|160/160|0/160|0/160|0/160|160/160|0/160|0/160|160/160|False|False|
|44|template_ood|N-final|200|99.06%|85.62%|119/119|0/160|0/160|0/160|160/160|0/160|0/160|160/160|False|False|
|44|iid|P|0|100.00%|100.00%|160/160|0/160|0/160|0/160|160/160|0/160|0/160|160/160|False|False|
|44|template_ood|P|0|98.77%|88.12%|119/119|0/160|0/160|0/160|160/160|0/160|0/160|160/160|False|False|

## 配对差与不确定性

|seed|split|contrast|metric|n|delta pp|CI95 pp|seed SD pp|
|---|---|---|---|---|---|---|---|
|42|iid|F-final minus N-final|U|160|98.75|[96.875,100.0]|NA|
|42|iid|F-final minus N-final|P_source|160|100.0|[100.0,100.0]|NA|
|42|iid|F-final minus N-final|G_source|160|78.75|[72.5,85.0]|NA|
|42|iid|F-final minus N-final|self_full|160|98.75|[96.875,100.0]|NA|
|42|iid|F-final minus N-final|atomic_macro|40 cells;160 worlds/status|0.0|[0.0,0.0]|NA|
|42|iid|F-final minus N-final|old_all3|160|0.0|[0.0,0.0]|NA|
|42|iid|F-guard minus F-final|U|160|-1.25|[-3.75,1.25]|NA|
|42|iid|F-guard minus F-final|P_source|160|0.0|[0.0,0.0]|NA|
|42|iid|F-guard minus F-final|G_source|160|-28.125|[-35.625,-21.25]|NA|
|42|iid|F-guard minus F-final|self_full|160|1.25|[0.0,3.125]|NA|
|42|iid|F-guard minus F-final|atomic_macro|40 cells;160 worlds/status|-0.296875|[-0.484375,-0.1558593750000021]|NA|
|42|iid|F-guard minus F-final|old_all3|160|0.0|[0.0,0.0]|NA|
|42|iid|F-guard minus N-final|U|160|97.5|[95.0,99.375]|NA|
|42|iid|F-guard minus N-final|P_source|160|100.0|[100.0,100.0]|NA|
|42|iid|F-guard minus N-final|G_source|160|50.625|[43.125,58.12500000000001]|NA|
|42|iid|F-guard minus N-final|self_full|160|100.0|[100.0,100.0]|NA|
|42|iid|F-guard minus N-final|atomic_macro|40 cells;160 worlds/status|-0.296875|[-0.484375,-0.1558593750000021]|NA|
|42|iid|F-guard minus N-final|old_all3|160|0.0|[0.0,0.0]|NA|
|42|iid|F-guard minus P|U|160|97.5|[95.0,99.375]|NA|
|42|iid|F-guard minus P|P_source|160|100.0|[100.0,100.0]|NA|
|42|iid|F-guard minus P|G_source|160|50.625|[43.125,58.12500000000001]|NA|
|42|iid|F-guard minus P|self_full|160|100.0|[100.0,100.0]|NA|
|42|iid|F-guard minus P|atomic_macro|40 cells;160 worlds/status|-0.296875|[-0.484375,-0.1558593750000021]|NA|
|42|iid|F-guard minus P|old_all3|160|0.0|[0.0,0.0]|NA|
|42|iid|F-final minus P|U|160|98.75|[96.875,100.0]|NA|
|42|iid|F-final minus P|P_source|160|100.0|[100.0,100.0]|NA|
|42|iid|F-final minus P|G_source|160|78.75|[72.5,85.0]|NA|
|42|iid|F-final minus P|self_full|160|98.75|[96.875,100.0]|NA|
|42|iid|F-final minus P|atomic_macro|40 cells;160 worlds/status|0.0|[0.0,0.0]|NA|
|42|iid|F-final minus P|old_all3|160|0.0|[0.0,0.0]|NA|
|42|template_ood|F-final minus N-final|U|160|63.125|[55.625,70.625]|NA|
|42|template_ood|F-final minus N-final|P_source|160|80.625|[74.375,86.875]|NA|
|42|template_ood|F-final minus N-final|G_source|160|95.625|[92.5,98.125]|NA|
|42|template_ood|F-final minus N-final|self_full|160|80.0|[73.125,86.25]|NA|
|42|template_ood|F-final minus N-final|atomic_macro|40 cells;160 worlds/status|-2.6406250000000004|[-3.125,-2.171875]|NA|
|42|template_ood|F-final minus N-final|old_all3|108|0.0|[0.0,0.0]|NA|
|42|template_ood|F-guard minus F-final|U|160|8.75|[4.375,13.125]|NA|
|42|template_ood|F-guard minus F-final|P_source|160|19.375|[13.125,25.624999999999996]|NA|
|42|template_ood|F-guard minus F-final|G_source|160|-0.625|[-4.375,3.125]|NA|
|42|template_ood|F-guard minus F-final|self_full|160|19.375|[13.750000000000002,25.624999999999996]|NA|
|42|template_ood|F-guard minus F-final|atomic_macro|40 cells;160 worlds/status|-2.21875|[-2.7035156250000005,-1.7500000000000002]|NA|
|42|template_ood|F-guard minus F-final|old_all3|108|0.0|[0.0,0.0]|NA|
|42|template_ood|F-guard minus N-final|U|160|71.875|[64.375,78.75]|NA|
|42|template_ood|F-guard minus N-final|P_source|160|100.0|[100.0,100.0]|NA|
|42|template_ood|F-guard minus N-final|G_source|160|95.0|[91.25,98.125]|NA|
|42|template_ood|F-guard minus N-final|self_full|160|99.375|[98.125,100.0]|NA|
|42|template_ood|F-guard minus N-final|atomic_macro|40 cells;160 worlds/status|-4.859375000000001|[-5.6410156250000005,-4.093359375000002]|NA|
|42|template_ood|F-guard minus N-final|old_all3|108|0.0|[0.0,0.0]|NA|
|42|template_ood|F-guard minus P|U|160|71.875|[64.375,78.75]|NA|
|42|template_ood|F-guard minus P|P_source|160|100.0|[100.0,100.0]|NA|
|42|template_ood|F-guard minus P|G_source|160|95.0|[91.25,98.125]|NA|
|42|template_ood|F-guard minus P|self_full|160|99.375|[98.125,100.0]|NA|
|42|template_ood|F-guard minus P|atomic_macro|40 cells;160 worlds/status|-3.28125|[-3.9218750000000004,-2.608984375000002]|NA|
|42|template_ood|F-guard minus P|old_all3|108|0.0|[0.0,0.0]|NA|
|42|template_ood|F-final minus P|U|160|63.125|[55.625,70.625]|NA|
|42|template_ood|F-final minus P|P_source|160|80.625|[74.375,86.875]|NA|
|42|template_ood|F-final minus P|G_source|160|95.625|[92.5,98.125]|NA|
|42|template_ood|F-final minus P|self_full|160|80.0|[73.125,86.25]|NA|
|42|template_ood|F-final minus P|atomic_macro|40 cells;160 worlds/status|-1.0625|[-1.4847656250000003,-0.609375]|NA|
|42|template_ood|F-final minus P|old_all3|108|0.0|[0.0,0.0]|NA|
|43|iid|F-final minus N-final|U|160|100.0|[100.0,100.0]|NA|
|43|iid|F-final minus N-final|P_source|160|100.0|[100.0,100.0]|NA|
|43|iid|F-final minus N-final|G_source|160|95.625|[91.875,98.75]|NA|
|43|iid|F-final minus N-final|self_full|160|100.0|[100.0,100.0]|NA|
|43|iid|F-final minus N-final|atomic_macro|40 cells;160 worlds/status|0.0|[0.0,0.0]|NA|
|43|iid|F-final minus N-final|old_all3|160|0.0|[0.0,0.0]|NA|
|43|iid|F-guard minus F-final|U|160|0.0|[0.0,0.0]|NA|
|43|iid|F-guard minus F-final|P_source|160|0.0|[0.0,0.0]|NA|
|43|iid|F-guard minus F-final|G_source|160|-18.125|[-24.375,-12.5]|NA|
|43|iid|F-guard minus F-final|self_full|160|-4.375|[-7.5,-1.25]|NA|
|43|iid|F-guard minus F-final|atomic_macro|40 cells;160 worlds/status|0.0|[0.0,0.0]|NA|
|43|iid|F-guard minus F-final|old_all3|160|0.0|[0.0,0.0]|NA|
|43|iid|F-guard minus N-final|U|160|100.0|[100.0,100.0]|NA|
|43|iid|F-guard minus N-final|P_source|160|100.0|[100.0,100.0]|NA|
|43|iid|F-guard minus N-final|G_source|160|77.5|[71.25,83.75]|NA|
|43|iid|F-guard minus N-final|self_full|160|95.625|[92.5,98.75]|NA|
|43|iid|F-guard minus N-final|atomic_macro|40 cells;160 worlds/status|0.0|[0.0,0.0]|NA|
|43|iid|F-guard minus N-final|old_all3|160|0.0|[0.0,0.0]|NA|
|43|iid|F-guard minus P|U|160|100.0|[100.0,100.0]|NA|
|43|iid|F-guard minus P|P_source|160|100.0|[100.0,100.0]|NA|
|43|iid|F-guard minus P|G_source|160|77.5|[71.25,83.75]|NA|
|43|iid|F-guard minus P|self_full|160|95.625|[92.5,98.75]|NA|
|43|iid|F-guard minus P|atomic_macro|40 cells;160 worlds/status|0.0|[0.0,0.0]|NA|
|43|iid|F-guard minus P|old_all3|160|0.0|[0.0,0.0]|NA|
|43|iid|F-final minus P|U|160|100.0|[100.0,100.0]|NA|
|43|iid|F-final minus P|P_source|160|100.0|[100.0,100.0]|NA|
|43|iid|F-final minus P|G_source|160|95.625|[91.875,98.75]|NA|
|43|iid|F-final minus P|self_full|160|100.0|[100.0,100.0]|NA|
|43|iid|F-final minus P|atomic_macro|40 cells;160 worlds/status|0.0|[0.0,0.0]|NA|
|43|iid|F-final minus P|old_all3|160|0.0|[0.0,0.0]|NA|
|43|template_ood|F-final minus N-final|U|160|100.0|[100.0,100.0]|NA|
|43|template_ood|F-final minus N-final|P_source|160|100.0|[100.0,100.0]|NA|
|43|template_ood|F-final minus N-final|G_source|160|74.375|[67.5,81.25]|NA|
|43|template_ood|F-final minus N-final|self_full|160|100.0|[100.0,100.0]|NA|
|43|template_ood|F-final minus N-final|atomic_macro|40 cells;160 worlds/status|-4.75|[-5.562499999999999,-3.9843749999999996]|NA|
|43|template_ood|F-final minus N-final|old_all3|120|0.0|[0.0,0.0]|NA|
|43|template_ood|F-guard minus F-final|U|160|0.0|[0.0,0.0]|NA|
|43|template_ood|F-guard minus F-final|P_source|160|0.0|[0.0,0.0]|NA|
|43|template_ood|F-guard minus F-final|G_source|160|-5.0|[-8.75,-1.875]|NA|
|43|template_ood|F-guard minus F-final|self_full|160|0.0|[0.0,0.0]|NA|
|43|template_ood|F-guard minus F-final|atomic_macro|40 cells;160 worlds/status|-3.28125|[-3.875000000000001,-2.7343750000000004]|NA|
|43|template_ood|F-guard minus F-final|old_all3|120|0.0|[0.0,0.0]|NA|
|43|template_ood|F-guard minus N-final|U|160|100.0|[100.0,100.0]|NA|
|43|template_ood|F-guard minus N-final|P_source|160|100.0|[100.0,100.0]|NA|
|43|template_ood|F-guard minus N-final|G_source|160|69.375|[62.5,76.25]|NA|
|43|template_ood|F-guard minus N-final|self_full|160|100.0|[100.0,100.0]|NA|
|43|template_ood|F-guard minus N-final|atomic_macro|40 cells;160 worlds/status|-8.03125|[-9.1875,-6.859375000000001]|NA|
|43|template_ood|F-guard minus N-final|old_all3|120|0.0|[0.0,0.0]|NA|
|43|template_ood|F-guard minus P|U|160|100.0|[100.0,100.0]|NA|
|43|template_ood|F-guard minus P|P_source|160|100.0|[100.0,100.0]|NA|
|43|template_ood|F-guard minus P|G_source|160|69.375|[62.5,76.25]|NA|
|43|template_ood|F-guard minus P|self_full|160|100.0|[100.0,100.0]|NA|
|43|template_ood|F-guard minus P|atomic_macro|40 cells;160 worlds/status|-6.093750000000001|[-7.0785156250000005,-5.15625]|NA|
|43|template_ood|F-guard minus P|old_all3|120|0.0|[0.0,0.0]|NA|
|43|template_ood|F-final minus P|U|160|100.0|[100.0,100.0]|NA|
|43|template_ood|F-final minus P|P_source|160|100.0|[100.0,100.0]|NA|
|43|template_ood|F-final minus P|G_source|160|74.375|[67.5,81.25]|NA|
|43|template_ood|F-final minus P|self_full|160|100.0|[100.0,100.0]|NA|
|43|template_ood|F-final minus P|atomic_macro|40 cells;160 worlds/status|-2.8125|[-3.3437499999999996,-2.280859375000002]|NA|
|43|template_ood|F-final minus P|old_all3|120|0.0|[0.0,0.0]|NA|
|44|iid|F-final minus N-final|U|160|100.0|[100.0,100.0]|NA|
|44|iid|F-final minus N-final|P_source|160|100.0|[100.0,100.0]|NA|
|44|iid|F-final minus N-final|G_source|160|76.25|[69.375,82.5]|NA|
|44|iid|F-final minus N-final|self_full|160|100.0|[100.0,100.0]|NA|
|44|iid|F-final minus N-final|atomic_macro|40 cells;160 worlds/status|0.0|[0.0,0.0]|NA|
|44|iid|F-final minus N-final|old_all3|160|0.0|[0.0,0.0]|NA|
|44|iid|F-guard minus F-final|U|160|0.0|[0.0,0.0]|NA|
|44|iid|F-guard minus F-final|P_source|160|0.0|[0.0,0.0]|NA|
|44|iid|F-guard minus F-final|G_source|160|-57.49999999999999|[-65.625,-49.375]|NA|
|44|iid|F-guard minus F-final|self_full|160|0.0|[0.0,0.0]|NA|
|44|iid|F-guard minus F-final|atomic_macro|40 cells;160 worlds/status|-0.14062500000000003|[-0.23437500000000003,-0.06250000000000001]|NA|
|44|iid|F-guard minus F-final|old_all3|160|0.0|[0.0,0.0]|NA|
|44|iid|F-guard minus N-final|U|160|100.0|[100.0,100.0]|NA|
|44|iid|F-guard minus N-final|P_source|160|100.0|[100.0,100.0]|NA|
|44|iid|F-guard minus N-final|G_source|160|18.75|[13.125,25.0]|NA|
|44|iid|F-guard minus N-final|self_full|160|100.0|[100.0,100.0]|NA|
|44|iid|F-guard minus N-final|atomic_macro|40 cells;160 worlds/status|-0.14062500000000003|[-0.23437500000000003,-0.06250000000000001]|NA|
|44|iid|F-guard minus N-final|old_all3|160|0.0|[0.0,0.0]|NA|
|44|iid|F-guard minus P|U|160|100.0|[100.0,100.0]|NA|
|44|iid|F-guard minus P|P_source|160|100.0|[100.0,100.0]|NA|
|44|iid|F-guard minus P|G_source|160|18.75|[13.125,25.0]|NA|
|44|iid|F-guard minus P|self_full|160|100.0|[100.0,100.0]|NA|
|44|iid|F-guard minus P|atomic_macro|40 cells;160 worlds/status|-0.14062500000000003|[-0.23437500000000003,-0.06250000000000001]|NA|
|44|iid|F-guard minus P|old_all3|160|0.0|[0.0,0.0]|NA|
|44|iid|F-final minus P|U|160|100.0|[100.0,100.0]|NA|
|44|iid|F-final minus P|P_source|160|100.0|[100.0,100.0]|NA|
|44|iid|F-final minus P|G_source|160|76.25|[69.375,82.5]|NA|
|44|iid|F-final minus P|self_full|160|100.0|[100.0,100.0]|NA|
|44|iid|F-final minus P|atomic_macro|40 cells;160 worlds/status|0.0|[0.0,0.0]|NA|
|44|iid|F-final minus P|old_all3|160|0.0|[0.0,0.0]|NA|
|44|template_ood|F-final minus N-final|U|160|100.0|[100.0,100.0]|NA|
|44|template_ood|F-final minus N-final|P_source|160|100.0|[100.0,100.0]|NA|
|44|template_ood|F-final minus N-final|G_source|160|76.875|[70.0,82.51562499999991]|NA|
|44|template_ood|F-final minus N-final|self_full|160|100.0|[100.0,100.0]|NA|
|44|template_ood|F-final minus N-final|atomic_macro|40 cells;160 worlds/status|0.390625|[0.14062500000000003,0.6253906249999979]|NA|
|44|template_ood|F-final minus N-final|old_all3|119|0.0|[0.0,0.0]|NA|
|44|template_ood|F-guard minus F-final|U|160|0.0|[0.0,0.0]|NA|
|44|template_ood|F-guard minus F-final|P_source|160|0.0|[0.0,0.0]|NA|
|44|template_ood|F-guard minus F-final|G_source|160|-50.0|[-57.49999999999999,-41.875]|NA|
|44|template_ood|F-guard minus F-final|self_full|160|0.0|[0.0,0.0]|NA|
|44|template_ood|F-guard minus F-final|atomic_macro|40 cells;160 worlds/status|-7.5|[-8.484765625000001,-6.484375000000001]|NA|
|44|template_ood|F-guard minus F-final|old_all3|119|0.0|[0.0,0.0]|NA|
|44|template_ood|F-guard minus N-final|U|160|100.0|[100.0,100.0]|NA|
|44|template_ood|F-guard minus N-final|P_source|160|100.0|[100.0,100.0]|NA|
|44|template_ood|F-guard minus N-final|G_source|160|26.875|[20.625,33.75]|NA|
|44|template_ood|F-guard minus N-final|self_full|160|100.0|[100.0,100.0]|NA|
|44|template_ood|F-guard minus N-final|atomic_macro|40 cells;160 worlds/status|-7.109375|[-8.03125,-6.171875]|NA|
|44|template_ood|F-guard minus N-final|old_all3|119|0.0|[0.0,0.0]|NA|
|44|template_ood|F-guard minus P|U|160|100.0|[100.0,100.0]|NA|
|44|template_ood|F-guard minus P|P_source|160|100.0|[100.0,100.0]|NA|
|44|template_ood|F-guard minus P|G_source|160|26.875|[20.625,33.75]|NA|
|44|template_ood|F-guard minus P|self_full|160|100.0|[100.0,100.0]|NA|
|44|template_ood|F-guard minus P|atomic_macro|40 cells;160 worlds/status|-6.812500000000001|[-7.687500000000001,-5.9375]|NA|
|44|template_ood|F-guard minus P|old_all3|119|0.0|[0.0,0.0]|NA|
|44|template_ood|F-final minus P|U|160|100.0|[100.0,100.0]|NA|
|44|template_ood|F-final minus P|P_source|160|100.0|[100.0,100.0]|NA|
|44|template_ood|F-final minus P|G_source|160|76.875|[70.0,82.51562499999991]|NA|
|44|template_ood|F-final minus P|self_full|160|100.0|[100.0,100.0]|NA|
|44|template_ood|F-final minus P|atomic_macro|40 cells;160 worlds/status|0.6875000000000001|[0.43750000000000006,0.953125]|NA|
|44|template_ood|F-final minus P|old_all3|119|0.0|[0.0,0.0]|NA|
|mean|iid|F-final minus N-final|U|{"42": 160, "43": 160, "44": 160}|99.58333333333333|[98.95833333333334,100.0]|0.7216878364870296|
|mean|iid|F-final minus N-final|P_source|{"42": 160, "43": 160, "44": 160}|100.0|[100.0,100.0]|0.0|
|mean|iid|F-final minus N-final|G_source|{"42": 160, "43": 160, "44": 160}|83.54166666666667|[79.58333333333334,87.29687499999999]|10.538866558284788|
|mean|iid|F-final minus N-final|self_full|{"42": 160, "43": 160, "44": 160}|99.58333333333333|[98.95833333333334,100.0]|0.7216878364870296|
|mean|iid|F-final minus N-final|atomic_macro|{"42": "40 cells;160 worlds/status", "43": "40 cells;160 worlds/status", "44": "40 cells;160 worlds/status"}|0.0|[0.0,0.0]|0.0|
|mean|iid|F-final minus N-final|old_all3|{"42": 160, "43": 160, "44": 160}|0.0|[0.0,0.0]|0.0|
|mean|iid|F-guard minus F-final|U|{"42": 160, "43": 160, "44": 160}|-0.4166666666666667|[-1.25,0.4166666666666667]|0.7216878364870323|
|mean|iid|F-guard minus F-final|P_source|{"42": 160, "43": 160, "44": 160}|0.0|[0.0,0.0]|0.0|
|mean|iid|F-guard minus F-final|G_source|{"42": 160, "43": 160, "44": 160}|-34.583333333333336|[-39.375,-30.416666666666664]|20.46656317834856|
|mean|iid|F-guard minus F-final|self_full|{"42": 160, "43": 160, "44": 160}|-1.0416666666666665|[-2.291666666666667,0.2083333333333333]|2.95363476640788|
|mean|iid|F-guard minus F-final|atomic_macro|{"42": "40 cells;160 worlds/status", "43": "40 cells;160 worlds/status", "44": "40 cells;160 worlds/status"}|-0.14583333333333334|[-0.21874999999999997,-0.08854166666666666]|0.1485060148894089|
|mean|iid|F-guard minus F-final|old_all3|{"42": 160, "43": 160, "44": 160}|0.0|[0.0,0.0]|0.0|
|mean|iid|F-guard minus N-final|U|{"42": 160, "43": 160, "44": 160}|99.16666666666667|[98.33333333333334,99.79166666666667]|1.4433756729740657|
|mean|iid|F-guard minus N-final|P_source|{"42": 160, "43": 160, "44": 160}|100.0|[100.0,100.0]|0.0|
|mean|iid|F-guard minus N-final|G_source|{"42": 160, "43": 160, "44": 160}|48.95833333333333|[44.16666666666667,53.95833333333334]|29.410439614758115|
|mean|iid|F-guard minus N-final|self_full|{"42": 160, "43": 160, "44": 160}|98.54166666666667|[97.5,99.58333333333333]|2.52590742770461|
|mean|iid|F-guard minus N-final|atomic_macro|{"42": "40 cells;160 worlds/status", "43": "40 cells;160 worlds/status", "44": "40 cells;160 worlds/status"}|-0.14583333333333334|[-0.21874999999999997,-0.08854166666666666]|0.1485060148894089|
|mean|iid|F-guard minus N-final|old_all3|{"42": 160, "43": 160, "44": 160}|0.0|[0.0,0.0]|0.0|
|mean|iid|F-guard minus P|U|{"42": 160, "43": 160, "44": 160}|99.16666666666667|[98.33333333333334,99.79166666666667]|1.4433756729740657|
|mean|iid|F-guard minus P|P_source|{"42": 160, "43": 160, "44": 160}|100.0|[100.0,100.0]|0.0|
|mean|iid|F-guard minus P|G_source|{"42": 160, "43": 160, "44": 160}|48.95833333333333|[44.16666666666667,53.95833333333334]|29.410439614758115|
|mean|iid|F-guard minus P|self_full|{"42": 160, "43": 160, "44": 160}|98.54166666666667|[97.5,99.58333333333333]|2.52590742770461|
|mean|iid|F-guard minus P|atomic_macro|{"42": "40 cells;160 worlds/status", "43": "40 cells;160 worlds/status", "44": "40 cells;160 worlds/status"}|-0.14583333333333334|[-0.21874999999999997,-0.08854166666666666]|0.1485060148894089|
|mean|iid|F-guard minus P|old_all3|{"42": 160, "43": 160, "44": 160}|0.0|[0.0,0.0]|0.0|
|mean|iid|F-final minus P|U|{"42": 160, "43": 160, "44": 160}|99.58333333333333|[98.95833333333334,100.0]|0.7216878364870296|
|mean|iid|F-final minus P|P_source|{"42": 160, "43": 160, "44": 160}|100.0|[100.0,100.0]|0.0|
|mean|iid|F-final minus P|G_source|{"42": 160, "43": 160, "44": 160}|83.54166666666667|[79.58333333333334,87.29687499999999]|10.538866558284788|
|mean|iid|F-final minus P|self_full|{"42": 160, "43": 160, "44": 160}|99.58333333333333|[98.95833333333334,100.0]|0.7216878364870296|
|mean|iid|F-final minus P|atomic_macro|{"42": "40 cells;160 worlds/status", "43": "40 cells;160 worlds/status", "44": "40 cells;160 worlds/status"}|0.0|[0.0,0.0]|0.0|
|mean|iid|F-final minus P|old_all3|{"42": 160, "43": 160, "44": 160}|0.0|[0.0,0.0]|0.0|
|mean|template_ood|F-final minus N-final|U|{"42": 160, "43": 160, "44": 160}|87.70833333333333|[85.20833333333333,90.20833333333333]|21.28979117636745|
|mean|template_ood|F-final minus N-final|P_source|{"42": 160, "43": 160, "44": 160}|93.54166666666667|[91.45833333333333,95.625]|11.186161465548999|
|mean|template_ood|F-final minus N-final|G_source|{"42": 160, "43": 160, "44": 160}|82.29166666666667|[79.16666666666666,85.41666666666666]|11.614466553971962|
|mean|template_ood|F-final minus N-final|self_full|{"42": 160, "43": 160, "44": 160}|93.33333333333333|[91.04166666666667,95.41666666666666]|11.547005383792513|
|mean|template_ood|F-final minus N-final|atomic_macro|{"42": "40 cells;160 worlds/status", "43": "40 cells;160 worlds/status", "44": "40 cells;160 worlds/status"}|-2.3333333333333335|[-2.7188802083333337,-1.9427083333333335]|2.584052529256774|
|mean|template_ood|F-final minus N-final|old_all3|{"42": 108, "43": 120, "44": 119}|0.0|[0.0,0.0]|0.0|
|mean|template_ood|F-guard minus F-final|U|{"42": 160, "43": 160, "44": 160}|2.9166666666666665|[1.4583333333333333,4.375]|5.051814855409225|
|mean|template_ood|F-guard minus F-final|P_source|{"42": 160, "43": 160, "44": 160}|6.458333333333334|[4.375,8.541666666666666]|11.186161465548999|
|mean|template_ood|F-guard minus F-final|G_source|{"42": 160, "43": 160, "44": 160}|-18.541666666666668|[-21.463541666666668,-15.416666666666668]|27.3313960187425|
|mean|template_ood|F-guard minus F-final|self_full|{"42": 160, "43": 160, "44": 160}|6.458333333333334|[4.583333333333334,8.541666666666666]|11.186161465548999|
|mean|template_ood|F-guard minus F-final|atomic_macro|{"42": "40 cells;160 worlds/status", "43": "40 cells;160 worlds/status", "44": "40 cells;160 worlds/status"}|-4.333333333333334|[-4.906510416666667,-3.7811197916666677]|2.793395764268524|
|mean|template_ood|F-guard minus F-final|old_all3|{"42": 108, "43": 120, "44": 119}|0.0|[0.0,0.0]|0.0|
|mean|template_ood|F-guard minus N-final|U|{"42": 160, "43": 160, "44": 160}|90.625|[88.125,92.91666666666667]|16.237976320958225|
|mean|template_ood|F-guard minus N-final|P_source|{"42": 160, "43": 160, "44": 160}|100.0|[100.0,100.0]|0.0|
|mean|template_ood|F-guard minus N-final|G_source|{"42": 160, "43": 160, "44": 160}|63.74999999999999|[60.83333333333334,66.875]|34.409074021252|
|mean|template_ood|F-guard minus N-final|self_full|{"42": 160, "43": 160, "44": 160}|99.79166666666667|[99.375,100.0]|0.3608439182435148|
|mean|template_ood|F-guard minus N-final|atomic_macro|{"42": "40 cells;160 worlds/status", "43": "40 cells;160 worlds/status", "44": "40 cells;160 worlds/status"}|-6.666666666666667|[-7.531380208333334,-5.781119791666667]|1.63162212390257|
|mean|template_ood|F-guard minus N-final|old_all3|{"42": 108, "43": 120, "44": 119}|0.0|[0.0,0.0]|0.0|
|mean|template_ood|F-guard minus P|U|{"42": 160, "43": 160, "44": 160}|90.625|[88.125,92.91666666666667]|16.237976320958225|
|mean|template_ood|F-guard minus P|P_source|{"42": 160, "43": 160, "44": 160}|100.0|[100.0,100.0]|0.0|
|mean|template_ood|F-guard minus P|G_source|{"42": 160, "43": 160, "44": 160}|63.74999999999999|[60.83333333333334,66.875]|34.409074021252|
|mean|template_ood|F-guard minus P|self_full|{"42": 160, "43": 160, "44": 160}|99.79166666666667|[99.375,100.0]|0.3608439182435148|
|mean|template_ood|F-guard minus P|atomic_macro|{"42": "40 cells;160 worlds/status", "43": "40 cells;160 worlds/status", "44": "40 cells;160 worlds/status"}|-5.395833333333334|[-6.13046875,-4.629817708333336]|1.8662120447133907|
|mean|template_ood|F-guard minus P|old_all3|{"42": 108, "43": 120, "44": 119}|0.0|[0.0,0.0]|0.0|
|mean|template_ood|F-final minus P|U|{"42": 160, "43": 160, "44": 160}|87.70833333333333|[85.20833333333333,90.20833333333333]|21.28979117636745|
|mean|template_ood|F-final minus P|P_source|{"42": 160, "43": 160, "44": 160}|93.54166666666667|[91.45833333333333,95.625]|11.186161465548999|
|mean|template_ood|F-final minus P|G_source|{"42": 160, "43": 160, "44": 160}|82.29166666666667|[79.16666666666666,85.41666666666666]|11.614466553971962|
|mean|template_ood|F-final minus P|self_full|{"42": 160, "43": 160, "44": 160}|93.33333333333333|[91.04166666666667,95.41666666666666]|11.547005383792513|
|mean|template_ood|F-final minus P|atomic_macro|{"42": "40 cells;160 worlds/status", "43": "40 cells;160 worlds/status", "44": "40 cells;160 worlds/status"}|-1.0625|[-1.3385416666666663,-0.7968750000000002]|1.7500000000000002|
|mean|template_ood|F-final minus P|old_all3|{"42": 108, "43": 120, "44": 119}|0.0|[0.0,0.0]|0.0|

三个seed共享世界，2000次共享world paired bootstrap按split分开；原子按status分层抽整个世界，保留该世界全部cell、40cell等权。Wilson区间在逐cell/source/self/maintenance表；0/1退化bootstrap不表示总体无不确定性。CI只包括固定模型的世界抽样，不包括完整训练/选择随机性，也不是480独立训练。

## 数据、选择及工程边界

新g16 namespace，2880事实世界、训练1536/开发384；每split480确认世界中主路径只有160plan。history来源复用G15已审计清单并补G15世界，只有有SHA/可访问范围无重合声明。模板OOD8–11保留词汇，非开放语言。所有状态的自由文本、gold、解析和错误类型在逐seed完整archive，不将解析未决当确认事实错误。

候选25/50/75/100/125/150/175/200，step0不允许选；全部128 dev主世界、每status128世界的40cell监测。C/P入口独立固定，覆盖<64选择失败。只选最早合格且不可修改，全部NF训练完、全局选择锁后才加载U/推断新确认。N只有final200。F-D是固定P续步，不能当更新自身full2；自身两步不参与开发选择，也不称全新长度/概念。

F-final−N-final是等200步训练来源对照；F-guard−F-final是同轨迹检查点比较；F-guard−N/P包含来源和选择两因素，不能唯一归因。guard=final同SHA复用推断、差0，不虚增证据；guard缺失记NA且完整目标分母仍3。

完整C只看冻结E/P/G/U当前全文、EOS/事实和P/G/U同mask。自然mask单列、不替换。自身分母raw160；重编码只用自由输出，不给gold，不作为纯latent结果或独立重复证据。旧yesterday H2固定构造/续步只是维护，非新自身三步链。

CPU G15退化审计、选择器/RNG/梯度/状态流/恢复/统计单测、单卡smoke、冻结hash和缓存proof有记录。没有O、架构/优化设置搜索、probe或新长链。科学目标通过与所有实验完成分开。

资源：{"limit_gpu_hours": 4, "actual_gpu_hours": 2.073611111111111, "requested_gpu_hours": 3.4, "max_concurrent_gpus": 2, "allocation_only": true, "steps_not_double_counted": true, "within_limits": true}

作业、失败/偏离见slurm_jobs.csv/engineering_deviations.json。Slurm语法仅依据[数组官方文档](https://slurm.schedmd.com/job_array.html)、[sbatch](https://slurm.schedmd.com/sbatch.html)、[srun](https://slurm.schedmd.com/srun.html)。

## 逐seed失败cell与重点转换

低于90%的全部cell如下，完整40cell与Wilson另见atomic_by_cell.csv。IID各guard无不合格cell，OOD不得以macro覆盖局部失败。

|seed|split|版本|status|offset→next|perspective|joint n/N|
|---|---|---|---|---|---|---|
|42|template_ood|F-final|recorded_plan|0→-1|first|127/160|
|42|template_ood|F-final|recorded_plan|0→-1|third|135/160|
|42|template_ood|F-final|reported_cancelled|0→-1|first|124/160|
|42|template_ood|F-final|reported_cancelled|0→-1|third|129/160|
|42|template_ood|F-final|reported_completed|0→-1|first|120/160|
|42|template_ood|F-final|reported_completed|0→-1|third|120/160|
|42|template_ood|F-guard|recorded_plan|-2→-3|first|119/160|
|42|template_ood|F-guard|recorded_plan|-2→-3|third|120/160|
|42|template_ood|F-guard|reported_cancelled|-2→-3|first|132/160|
|42|template_ood|F-guard|reported_cancelled|-2→-3|third|142/160|
|42|template_ood|F-guard|reported_completed|-2→-3|first|117/160|
|42|template_ood|F-guard|reported_completed|-2→-3|third|120/160|
|42|template_ood|F-guard|reported_completed|0→-1|first|124/160|
|42|template_ood|F-guard|reported_completed|0→-1|third|127/160|
|42|template_ood|N-final|reported_completed|0→-1|first|136/160|
|42|template_ood|P|recorded_plan|2→1|third|143/160|
|42|template_ood|P|reported_cancelled|0→-1|first|143/160|
|42|template_ood|P|reported_cancelled|2→1|first|141/160|
|42|template_ood|P|reported_completed|0→-1|first|120/160|
|42|template_ood|P|reported_completed|0→-1|third|123/160|
|43|template_ood|F-final|recorded_plan|-3→-4|first|120/160|
|43|template_ood|F-final|recorded_plan|-1→-2|third|136/160|
|43|template_ood|F-final|recorded_plan|0→-1|first|121/160|
|43|template_ood|F-final|recorded_plan|0→-1|third|122/160|
|43|template_ood|F-final|reported_cancelled|0→-1|first|127/160|
|43|template_ood|F-final|reported_cancelled|0→-1|third|127/160|
|43|template_ood|F-final|reported_completed|-3→-4|first|121/160|
|43|template_ood|F-final|reported_completed|0→-1|first|120/160|
|43|template_ood|F-final|reported_completed|0→-1|third|122/160|
|43|template_ood|F-guard|recorded_plan|-3→-4|first|122/160|
|43|template_ood|F-guard|recorded_plan|-1→-2|first|120/160|
|43|template_ood|F-guard|recorded_plan|-1→-2|third|120/160|
|43|template_ood|F-guard|recorded_plan|0→-1|first|120/160|
|43|template_ood|F-guard|recorded_plan|0→-1|third|120/160|
|43|template_ood|F-guard|reported_cancelled|-1→-2|first|120/160|
|43|template_ood|F-guard|reported_cancelled|-1→-2|third|120/160|
|43|template_ood|F-guard|reported_cancelled|0→-1|first|120/160|
|43|template_ood|F-guard|reported_cancelled|0→-1|third|120/160|
|43|template_ood|F-guard|reported_completed|-3→-4|first|125/160|
|43|template_ood|F-guard|reported_completed|-1→-2|first|125/160|
|43|template_ood|F-guard|reported_completed|-1→-2|third|120/160|
|43|template_ood|F-guard|reported_completed|0→-1|first|120/160|
|43|template_ood|F-guard|reported_completed|0→-1|third|120/160|
|43|template_ood|N-final|recorded_plan|-3→-4|first|130/160|
|43|template_ood|N-final|reported_completed|-3→-4|first|130/160|
|43|template_ood|P|recorded_plan|-3→-4|first|127/160|
|43|template_ood|P|recorded_plan|0→-1|first|143/160|
|43|template_ood|P|recorded_plan|0→-1|third|140/160|
|43|template_ood|P|reported_completed|-3→-4|first|127/160|
|43|template_ood|P|reported_completed|0→-1|first|142/160|
|43|template_ood|P|reported_completed|0→-1|third|142/160|
|44|template_ood|F-guard|recorded_plan|-1→-2|first|120/160|
|44|template_ood|F-guard|recorded_plan|-1→-2|third|120/160|
|44|template_ood|F-guard|recorded_plan|0→-1|first|143/160|
|44|template_ood|F-guard|recorded_plan|2→1|first|91/160|
|44|template_ood|F-guard|recorded_plan|2→1|third|85/160|
|44|template_ood|F-guard|reported_cancelled|-1→-2|first|120/160|
|44|template_ood|F-guard|reported_cancelled|-1→-2|third|120/160|
|44|template_ood|F-guard|reported_cancelled|2→1|first|130/160|
|44|template_ood|F-guard|reported_cancelled|2→1|third|113/160|
|44|template_ood|F-guard|reported_completed|-1→-2|first|143/160|
|44|template_ood|F-guard|reported_completed|-1→-2|third|138/160|
|44|template_ood|F-guard|reported_completed|0→-1|first|129/160|
|44|template_ood|F-guard|reported_completed|0→-1|third|135/160|
|44|template_ood|N-final|recorded_plan|2→1|first|140/160|
|44|template_ood|N-final|recorded_plan|2→1|third|137/160|
|44|template_ood|P|recorded_plan|2→1|third|141/160|

重点转换保留原权重：

|seed|split|版本|status|offset→next|perspective|joint n/N|
|---|---|---|---|---|---|---|
|42|iid|F-final|recorded_plan|0→-1|first|160/160|
|42|iid|F-final|recorded_plan|1→0|first|160/160|
|42|iid|F-final|reported_cancelled|2→1|third|160/160|
|42|template_ood|F-final|recorded_plan|0→-1|first|127/160|
|42|template_ood|F-final|recorded_plan|1→0|first|160/160|
|42|template_ood|F-final|reported_cancelled|2→1|third|159/160|
|42|iid|F-guard|recorded_plan|0→-1|first|160/160|
|42|iid|F-guard|recorded_plan|1→0|first|160/160|
|42|iid|F-guard|reported_cancelled|2→1|third|160/160|
|42|template_ood|F-guard|recorded_plan|0→-1|first|155/160|
|42|template_ood|F-guard|recorded_plan|1→0|first|159/160|
|42|template_ood|F-guard|reported_cancelled|2→1|third|151/160|
|42|iid|N-final|recorded_plan|0→-1|first|160/160|
|42|iid|N-final|recorded_plan|1→0|first|160/160|
|42|iid|N-final|reported_cancelled|2→1|third|160/160|
|42|template_ood|N-final|recorded_plan|0→-1|first|159/160|
|42|template_ood|N-final|recorded_plan|1→0|first|160/160|
|42|template_ood|N-final|reported_cancelled|2→1|third|160/160|
|42|iid|P|recorded_plan|0→-1|first|160/160|
|42|iid|P|recorded_plan|1→0|first|160/160|
|42|iid|P|reported_cancelled|2→1|third|160/160|
|42|template_ood|P|recorded_plan|0→-1|first|158/160|
|42|template_ood|P|recorded_plan|1→0|first|160/160|
|42|template_ood|P|reported_cancelled|2→1|third|158/160|
|43|iid|F-final|recorded_plan|0→-1|first|160/160|
|43|iid|F-final|recorded_plan|1→0|first|160/160|
|43|iid|F-final|reported_cancelled|2→1|third|160/160|
|43|template_ood|F-final|recorded_plan|0→-1|first|121/160|
|43|template_ood|F-final|recorded_plan|1→0|first|160/160|
|43|template_ood|F-final|reported_cancelled|2→1|third|160/160|
|43|iid|F-guard|recorded_plan|0→-1|first|160/160|
|43|iid|F-guard|recorded_plan|1→0|first|160/160|
|43|iid|F-guard|reported_cancelled|2→1|third|160/160|
|43|template_ood|F-guard|recorded_plan|0→-1|first|120/160|
|43|template_ood|F-guard|recorded_plan|1→0|first|160/160|
|43|template_ood|F-guard|reported_cancelled|2→1|third|160/160|
|43|iid|N-final|recorded_plan|0→-1|first|160/160|
|43|iid|N-final|recorded_plan|1→0|first|160/160|
|43|iid|N-final|reported_cancelled|2→1|third|160/160|
|43|template_ood|N-final|recorded_plan|0→-1|first|160/160|
|43|template_ood|N-final|recorded_plan|1→0|first|160/160|
|43|template_ood|N-final|reported_cancelled|2→1|third|160/160|
|43|iid|P|recorded_plan|0→-1|first|160/160|
|43|iid|P|recorded_plan|1→0|first|160/160|
|43|iid|P|reported_cancelled|2→1|third|160/160|
|43|template_ood|P|recorded_plan|0→-1|first|143/160|
|43|template_ood|P|recorded_plan|1→0|first|160/160|
|43|template_ood|P|reported_cancelled|2→1|third|160/160|
|44|iid|F-final|recorded_plan|0→-1|first|160/160|
|44|iid|F-final|recorded_plan|1→0|first|160/160|
|44|iid|F-final|reported_cancelled|2→1|third|160/160|
|44|template_ood|F-final|recorded_plan|0→-1|first|160/160|
|44|template_ood|F-final|recorded_plan|1→0|first|160/160|
|44|template_ood|F-final|reported_cancelled|2→1|third|158/160|
|44|iid|F-guard|recorded_plan|0→-1|first|160/160|
|44|iid|F-guard|recorded_plan|1→0|first|160/160|
|44|iid|F-guard|reported_cancelled|2→1|third|160/160|
|44|template_ood|F-guard|recorded_plan|0→-1|first|143/160|
|44|template_ood|F-guard|recorded_plan|1→0|first|160/160|
|44|template_ood|F-guard|reported_cancelled|2→1|third|113/160|
|44|iid|N-final|recorded_plan|0→-1|first|160/160|
|44|iid|N-final|recorded_plan|1→0|first|160/160|
|44|iid|N-final|reported_cancelled|2→1|third|160/160|
|44|template_ood|N-final|recorded_plan|0→-1|first|160/160|
|44|template_ood|N-final|recorded_plan|1→0|first|160/160|
|44|template_ood|N-final|reported_cancelled|2→1|third|149/160|
|44|iid|P|recorded_plan|0→-1|first|160/160|
|44|iid|P|recorded_plan|1→0|first|160/160|
|44|iid|P|reported_cancelled|2→1|third|160/160|
|44|template_ood|P|recorded_plan|0→-1|first|160/160|
|44|template_ood|P|recorded_plan|1→0|first|160/160|
|44|template_ood|P|reported_cancelled|2→1|third|153/160|

## 三seed均值与sample SD

|版本|split|metric|mean%|sample SD pp|seed values|
|---|---|---|---|---|---|
|F-final|iid|atomic_macro|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|F-final|iid|old_all3|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|F-final|iid|U|99.583|0.722|{"42": 0.9875, "43": 1.0, "44": 1.0}|
|F-final|iid|P_source|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|F-final|iid|G_source|83.542|10.539|{"42": 0.7875, "43": 0.95625, "44": 0.7625}|
|F-final|iid|self_full|99.583|0.722|{"42": 0.9875, "43": 1.0, "44": 1.0}|
|F-final|template_ood|atomic_macro|96.818|2.587|{"42": 0.9671875, "43": 0.9428124999999999, "44": 0.99453125}|
|F-final|template_ood|old_all3|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|F-final|template_ood|U|87.708|21.290|{"42": 0.63125, "43": 1.0, "44": 1.0}|
|F-final|template_ood|P_source|93.542|11.186|{"42": 0.80625, "43": 1.0, "44": 1.0}|
|F-final|template_ood|G_source|82.292|11.614|{"42": 0.95625, "43": 0.74375, "44": 0.76875}|
|F-final|template_ood|self_full|93.333|11.547|{"42": 0.8, "43": 1.0, "44": 1.0}|
|F-guard|iid|atomic_macro|99.854|0.149|{"42": 0.99703125, "43": 1.0, "44": 0.99859375}|
|F-guard|iid|old_all3|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|F-guard|iid|U|99.167|1.443|{"42": 0.975, "43": 1.0, "44": 1.0}|
|F-guard|iid|P_source|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|F-guard|iid|G_source|48.958|29.410|{"42": 0.50625, "43": 0.775, "44": 0.1875}|
|F-guard|iid|self_full|98.542|2.526|{"42": 1.0, "43": 0.95625, "44": 1.0}|
|F-guard|template_ood|atomic_macro|92.484|1.809|{"42": 0.945, "43": 0.91, "44": 0.91953125}|
|F-guard|template_ood|old_all3|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|F-guard|template_ood|U|90.625|16.238|{"42": 0.71875, "43": 1.0, "44": 1.0}|
|F-guard|template_ood|P_source|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|F-guard|template_ood|G_source|63.750|34.409|{"42": 0.95, "43": 0.69375, "44": 0.26875}|
|F-guard|template_ood|self_full|99.792|0.361|{"42": 0.99375, "43": 1.0, "44": 1.0}|
|N-final|iid|atomic_macro|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|N-final|iid|old_all3|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|N-final|iid|U|0.000|0.000|{"42": 0.0, "43": 0.0, "44": 0.0}|
|N-final|iid|P_source|0.000|0.000|{"42": 0.0, "43": 0.0, "44": 0.0}|
|N-final|iid|G_source|0.000|0.000|{"42": 0.0, "43": 0.0, "44": 0.0}|
|N-final|iid|self_full|0.000|0.000|{"42": 0.0, "43": 0.0, "44": 0.0}|
|N-final|template_ood|atomic_macro|99.151|0.181|{"42": 0.99359375, "43": 0.9903125, "44": 0.990625}|
|N-final|template_ood|old_all3|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|N-final|template_ood|U|0.000|0.000|{"42": 0.0, "43": 0.0, "44": 0.0}|
|N-final|template_ood|P_source|0.000|0.000|{"42": 0.0, "43": 0.0, "44": 0.0}|
|N-final|template_ood|G_source|0.000|0.000|{"42": 0.0, "43": 0.0, "44": 0.0}|
|N-final|template_ood|self_full|0.000|0.000|{"42": 0.0, "43": 0.0, "44": 0.0}|
|P|iid|atomic_macro|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|P|iid|old_all3|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|P|iid|U|0.000|0.000|{"42": 0.0, "43": 0.0, "44": 0.0}|
|P|iid|P_source|0.000|0.000|{"42": 0.0, "43": 0.0, "44": 0.0}|
|P|iid|G_source|0.000|0.000|{"42": 0.0, "43": 0.0, "44": 0.0}|
|P|iid|self_full|0.000|0.000|{"42": 0.0, "43": 0.0, "44": 0.0}|
|P|template_ood|atomic_macro|97.880|0.840|{"42": 0.9778125, "43": 0.9709375, "44": 0.98765625}|
|P|template_ood|old_all3|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|P|template_ood|U|0.000|0.000|{"42": 0.0, "43": 0.0, "44": 0.0}|
|P|template_ood|P_source|0.000|0.000|{"42": 0.0, "43": 0.0, "44": 0.0}|
|P|template_ood|G_source|0.000|0.000|{"42": 0.0, "43": 0.0, "44": 0.0}|
|P|template_ood|self_full|0.000|0.000|{"42": 0.0, "43": 0.0, "44": 0.0}|
|F-final|iid|atomic_min_cell|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|F-final|iid|self_first|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|F-final|iid|self_endpoint2|99.583|0.722|{"42": 0.9875, "43": 1.0, "44": 1.0}|
|F-final|iid|natural_today|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|F-final|iid|all_fixed4|83.125|10.843|{"42": 0.775, "43": 0.95625, "44": 0.7625}|
|F-final|iid|today_C_coverage|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|F-final|iid|old_C_coverage|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|F-final|template_ood|atomic_min_cell|80.000|8.660|{"42": 0.75, "43": 0.75, "44": 0.9}|
|F-final|template_ood|self_first|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|F-final|template_ood|self_endpoint2|93.333|11.547|{"42": 0.8, "43": 1.0, "44": 1.0}|
|F-final|template_ood|natural_today|85.000|13.125|{"42": 0.79375, "43": 0.75625, "44": 1.0}|
|F-final|template_ood|all_fixed4|70.833|8.393|{"42": 0.6125, "43": 0.74375, "44": 0.76875}|
|F-final|template_ood|today_C_coverage|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|F-final|template_ood|old_C_coverage|72.292|4.161|{"42": 0.675, "43": 0.75, "44": 0.74375}|
|F-guard|iid|atomic_min_cell|97.083|2.818|{"42": 0.96875, "43": 1.0, "44": 0.94375}|
|F-guard|iid|self_first|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|F-guard|iid|self_endpoint2|98.542|2.526|{"42": 1.0, "43": 0.95625, "44": 1.0}|
|F-guard|iid|natural_today|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|F-guard|iid|all_fixed4|48.958|29.410|{"42": 0.50625, "43": 0.775, "44": 0.1875}|
|F-guard|iid|today_C_coverage|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|F-guard|iid|old_C_coverage|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|F-guard|template_ood|atomic_min_cell|67.083|12.125|{"42": 0.73125, "43": 0.75, "44": 0.53125}|
|F-guard|template_ood|self_first|99.792|0.361|{"42": 0.99375, "43": 1.0, "44": 1.0}|
|F-guard|template_ood|self_endpoint2|99.792|0.361|{"42": 0.99375, "43": 1.0, "44": 1.0}|
|F-guard|template_ood|natural_today|87.083|11.116|{"42": 0.96875, "43": 0.75, "44": 0.89375}|
|F-guard|template_ood|all_fixed4|51.875|28.174|{"42": 0.66875, "43": 0.69375, "44": 0.19375}|
|F-guard|template_ood|today_C_coverage|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|F-guard|template_ood|old_C_coverage|72.292|4.161|{"42": 0.675, "43": 0.75, "44": 0.74375}|
|N-final|iid|atomic_min_cell|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|N-final|iid|self_first|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|N-final|iid|self_endpoint2|0.000|0.000|{"42": 0.0, "43": 0.0, "44": 0.0}|
|N-final|iid|natural_today|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|N-final|iid|all_fixed4|0.000|0.000|{"42": 0.0, "43": 0.0, "44": 0.0}|
|N-final|iid|today_C_coverage|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|N-final|iid|old_C_coverage|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|N-final|template_ood|atomic_min_cell|83.958|2.366|{"42": 0.85, "43": 0.8125, "44": 0.85625}|
|N-final|template_ood|self_first|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|N-final|template_ood|self_endpoint2|0.000|0.000|{"42": 0.0, "43": 0.0, "44": 0.0}|
|N-final|template_ood|natural_today|99.792|0.361|{"42": 0.99375, "43": 1.0, "44": 1.0}|
|N-final|template_ood|all_fixed4|0.000|0.000|{"42": 0.0, "43": 0.0, "44": 0.0}|
|N-final|template_ood|today_C_coverage|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|N-final|template_ood|old_C_coverage|72.292|4.161|{"42": 0.675, "43": 0.75, "44": 0.74375}|
|P|iid|atomic_min_cell|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|P|iid|self_first|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|P|iid|self_endpoint2|0.000|0.000|{"42": 0.0, "43": 0.0, "44": 0.0}|
|P|iid|natural_today|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|P|iid|all_fixed4|0.000|0.000|{"42": 0.0, "43": 0.0, "44": 0.0}|
|P|iid|today_C_coverage|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|P|iid|old_C_coverage|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|P|template_ood|atomic_min_cell|80.833|6.683|{"42": 0.75, "43": 0.79375, "44": 0.88125}|
|P|template_ood|self_first|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|P|template_ood|self_endpoint2|0.000|0.000|{"42": 0.0, "43": 0.0, "44": 0.0}|
|P|template_ood|natural_today|96.042|5.807|{"42": 0.9875, "43": 0.89375, "44": 1.0}|
|P|template_ood|all_fixed4|0.000|0.000|{"42": 0.0, "43": 0.0, "44": 0.0}|
|P|template_ood|today_C_coverage|100.000|0.000|{"42": 1.0, "43": 1.0, "44": 1.0}|
|P|template_ood|old_C_coverage|72.292|4.161|{"42": 0.675, "43": 0.75, "44": 0.74375}|

## 控制、分母与运行账

**边界：三个guard的OOD自然macro为94.50%、91.00%、91.95%，最低cell为73.13%、75.00%、53.13%，均未通过能力标准。** OOD U为115/160、160/160、160/160，self full2为159/160、160/160、160/160；seed42迁移有改善但未达U≥90%。final的OOD只有seed44通过完整工作目标。IID guard对G-today仅81/160、124/160、30/160，虽P均160/160且U很高，也不能称普遍来源互换。三个IID guard的全部固定来源同时成功仅81/160、124/160、30/160。

|display ID|raw allocation|state|exit|start|end|GPU h|
|---|---|---|---|---|---|---|
|2520|2520|COMPLETED|0:0|2026-10-02T00:14:43|2026-10-02T00:16:55|0.03666666666666667|
|2521_0|2522|COMPLETED|0:0|2026-10-02T00:18:26|2026-10-02T00:39:58|0.35888888888888887|
|2521_1|2523|COMPLETED|0:0|2026-10-02T00:18:27|2026-10-02T00:53:41|0.5872222222222222|
|2521_2|2521|COMPLETED|0:0|2026-10-02T00:39:58|2026-10-02T01:01:27|0.35805555555555557|
|2524_0|2525|COMPLETED|0:0|2026-10-02T01:03:31|2026-10-02T01:15:34|0.20083333333333334|
|2524_1|2526|COMPLETED|0:0|2026-10-02T01:03:31|2026-10-02T01:15:36|0.2013888888888889|
|2524_2|2524|COMPLETED|0:0|2026-10-02T01:15:34|2026-10-02T01:35:24|0.33055555555555555|

实际/申请/峰值GPU：{"limit_gpu_hours": 4, "actual_gpu_hours": 2.073611111111111, "requested_gpu_hours": 3.4, "max_concurrent_gpus": 2, "allocation_only": true, "steps_not_double_counted": true, "within_limits": true}。型号NVIDIA B300 SXM6 AC；Slurm step显存峰值3396M，PyTorch allocator峰值1574852096 bytes，两者口径单列。step仅用于显存核验，不重复计费。没有GPU重试或科学配置偏离。

CPU单测11项通过，smoke64条历史输出/评分对齐；冻结/缓存/保存恢复/RNG插入检查通过。原始训练入口P/旧昨日各512/512，dev各128/128；选择最早合格的全40cell计数见selection_table.csv。科学锁、旧工件与所有大cache哈希核验通过。

12个事前hash世界见CASES.md；补充G-source边界是公开规则的事后描述见BOUNDARY_CASES.md，不影响估计或选择。完整自由文本/事实/解析/错误与首次失败在逐seed gzip；没有把解析未决称为确认事实错误。

交付仅本轮路径；大cache/候选/optimizer与基础BART留本地，路径/SHA见artifact_manifest.json。导出step标签按已有actual_updates规范化，保留legacy_final_interface_step；这些锁后CPU格式调整不改文本/计分/分母/模型或科学锁。完整复现顺序与本次命令见REPRODUCTION_RESULTS.md。
