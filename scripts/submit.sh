# for competition graph submission

# top degree random tie strategy
python3 -m scripts.submit \
  --graph graphs/J.20.31.json \
  --strategy top_degree_random_tie \
  --top-m 1.0 \
  --seed 2 

python3 -m scripts.submit \
  --graph graphs/J.20.31.json \
  --strategy top_degree_random_tie \
  --top-m 3.0 \
  --seed 2

python3 -m scripts.submit \
  --graph graphs/J.20.31.json \
  --strategy top_degree_avoid \
  --top-m 3.0 \
  --seed 2

python3 -m scripts.submit \
  --graph graphs/J.20.31.json \
  --strategy top_degree_avoid \
  --top-m 4.0 \
  --seed 2

python3 -m scripts.submit \
  --graph graphs/J.20.31.json \
  --strategy random_k \
  --seed 2

# # degree cluster strategy
# python3 -m scripts.submit \
#   --graph graphs/J.20.31.json \
#   --strategy degree_cluster \
#   --seed 2 

# # edge cluster strategy
# python3 -m scripts.submit \
#   --graph graphs/J.20.31.json \
#   --strategy edge_cluster \
#   --seed 2 

# # for testing on generated graphs
# python3 -m scripts.submit \
#   --graph graphs/gen/SSBM_n210_k5_pin0.05_pout0.005_seed0.json \
#   --strategy degree_cluster \
#   --top-m 2.0 \
#   --seed 2 

# python3 -m scripts.submit \
#   --graph graphs/gen/SSBM_n210_k5_pin0.05_pout0.005_seed0.json \
#   --strategy edge_cluster \
#   --top-m 2.0 \
#   --seed 2 

# python3 -m scripts.submit \
#   --graph graphs/gen/SSBM_n210_k5_pin0.05_pout0.005_seed0.json \
#   --strategy top_degree_random_tie \
#   --top-m 2.0 \
#   --seed 2 