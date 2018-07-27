# 原有代码

- SmartClayV3.ino：wyt写的，用来采集数据
- KNNexample.py：一个使用KNN的例子，很简单，与项目无关

# 我新增的代码

- KNNLearn.py：原有的分类器代码基础上，我增加了三种简单的机器学习方法，同时将代码提取成了一个函数；可以跟原来给的代码对比一下
- classify.py：分类入口，可以直接运行看usage
- autotest.sh：用来测试已有的数据
- evaluate/：原有数据，里面有我新增的把一组数据集合到一起的脚本merge.py
- ardu/：今天早上写的代码
- result/：测试结果
- models/：保存机器学习的模型
