python -m sim.gen_graph --type ER --n 1000 --seed 0
python -m sim.gen_graph --type PA --n 1000 --m 2 --seed 0
python -m sim.gen_graph --type SSBM --n 1000 --k-blocks 5 --p-in 0.05 --p-out 0.005 --seed 0