#!/bin/bash
for i in 0 1 2 3 4 5 6 7 8 9 _all
do
	brainome data/cifar10_train$i.csv -measureonly > brainome_out/$i.txt
done
