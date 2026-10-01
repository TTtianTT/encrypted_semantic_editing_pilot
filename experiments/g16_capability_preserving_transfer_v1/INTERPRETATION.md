# G16 结果解释

1. **选择结果：seed42→step50，seed43→step25，seed44→step25；没有选择失败。** 原始计数核验最早合格，step0不选，全部F仍训练到200。

2. **所选模型在IID逐seed保住40-cell自然能力和旧yesterday all3，并达到自身两步修复工作标准。** guard原子macro为99.70%, 100.00%, 99.86%；最低cell为96.88%, 100.00%, 94.38%；旧all3均160/160，自身full2为160/160, 153/160, 160/160。这是已监督任务的新世界运行检查，不是新长度泛化。

3. **未读取U的规则选择后，IID留出U仍得到正向迁移。** guard为156/160, 160/160, 160/160，P/N各seed均0/160；三个seed均达到U≥90%的工作目标，逐seed配对world CI支持改善。相对P和N的均值改变量均为+99.167 pp [95% world CI +98.333, +99.792]; seed SD 1.443 pp。这仅是G15已考察过的精确F2 final200生产者在新世界上的复验。

4. **没有guard相对final200的能力保持优势；G15的seed44 IID末段退化没有在本轮重现。** F-final的全部IID自然cell均160/160，旧all3均160/160，U与自身full2均为158/160, 160/160, 160/160。guard−final的原子macro为-0.146 pp [95% world CI -0.219, -0.089]; seed SD 0.149 pp，U为-0.417 pp [95% world CI -1.250, +0.417]; seed SD 0.722 pp，full2为-1.042 pp [95% world CI -2.292, +0.208]; seed SD 2.954 pp。两个版本均通过三seed IID工作目标，不能据此宣称guard更优或必要。

**边界：三个guard的OOD自然macro为94.50%、91.00%、91.95%，最低cell为73.13%、75.00%、53.13%，均未通过能力标准。** OOD U为115/160、160/160、160/160，self full2为159/160、160/160、160/160；seed42迁移有改善但未达U≥90%。final的OOD只有seed44通过完整工作目标。IID guard对G-today仅81/160、124/160、30/160，虽P均160/160且U很高，也不能称普遍来源互换。三个IID guard的全部固定来源同时成功仅81/160、124/160、30/160。


主要正结果是固定来源F补训在三个既有初始化上、新的IID世界中，同时保持自然/旧yesterday能力并迁移到U。等200步F-final−N-final的IID U与self full2均为+99.583 pp [95% world CI +98.958, +100.000]; seed SD 0.722 pp；原子macro和旧all3差均0。N不处理这些编辑态today，不能用自然单步成功替代两步修复。

guard−final在OOD的U与self改善主要来自seed42，但三个guard的OOD自然能力更差：原子macro差-4.333 pp [95% world CI -4.907, -3.781]; seed SD 2.793 pp；U差+2.917 pp [95% world CI +1.458, +4.375]; seed SD 5.052 pp；self差+6.458 pp [95% world CI +4.583, +8.542]; seed SD 11.186 pp。这不能被写成整体能力保持成功。guard−N/P含来源训练与更新步两个因素；训练仍完整200步，实际算力没有节省。

今天主C在每seed/split均160/160，E/P/G/U当前全文与事实正确、正常结束；全部producer mask逐元素相同，自然mask也在本数据160/160相同。G-source与U-source的IID差异因而不能由本数据的mask差异解释；内部原因没有测量。旧yesterday C独立：IID均160，OOD依seed为108、120、119，all3条件均满分，但gate-and-next仅108/160、120/160、119/160。未匹配输出完整保留，不把这些分母强行合并或跨seed逐行等同。

IID各版本自然today→yesterday及真实当前输出重编码均160/160，reset与自然E的token/mask/memory逐元素一致，重复不是独立证据。OOD有自然技能边界：guard自然today续步155/160、120/160、143/160；不能描述为“只不认识编辑态”。重编码仅用真实自由输出，first错时full不会被gold修正。

CPU G15审计未发现确定标签/配额/状态错配，梯度冲突未测量。G15小step150诊断没有被当作完整确认，未重新推断step150 U。本轮F-final新IID成功表明固定补训可在本设置达成目标；不能证明G15退化的唯一机制、普通过拟合、必然任务冲突或不可能性。

完整工作目标通过是经验阈值，不是总体保证。U的配对world区间只包括固定模型的世界抽样，选择/完整训练随机性不在其中；三个seed共有世界不是480个独立训练。Wilson逐比例保留，160/160的95% Wilson下界约97.66%，0/160上界约2.34%；退化bootstrap[0,0]不表示总体零不确定性。

完成全部6条200步训练、3条不可变selection和3seed确认；没有未完成实验、工程重试或科学配置偏离。实际2.073611 GPU小时、申请3.40、峰值2；7 allocations均COMPLETED/0:0。旧工件SHA不变，科学锁不变。finalize/publish仅为锁后CPU交付格式和报告助手，不改变推断/选择/统计；导出step使用已有actual_updates并保留legacy_final_interface_step。

最小剩余问题是OOD自然技能与G-today来源的有限兼容性，当前数据没有提供唯一内部解释。本轮不自动追加训练或扩展实验。
