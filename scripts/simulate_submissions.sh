# check submissions for available graphs
# run submit.sh to generate submissions

python3 -m scripts.simulate_submissions \
  --sub1 submissions/J.10.30/top_degree_random_tie_topm5.0_seed2.txt \
  --sub2 submissions/J.10.30/top_degree_random_tie_topm3.0_seed2.txt \
  --sub3 submissions/J.10.30/top_degree_random_tie_topm1.0_seed2.txt \
  --sub4 submissions/J.10.30/degree_cluster_seed2.txt 

# python3 -m scripts.simulate_submissions \
#   --sub1 submissions/RR.10.30/top_degree_random_tie_topm1.4_seed2.txt \
#   --sub2 submissions/RR.10.30/top_degree_random_tie_topm1.0_seed2.txt \
#   --sub3 submissions/RR.10.30/degree_cluster_seed2.txt \
#   --sub4 submissions/RR.10.30/edge_cluster_seed2.txt \
#   --sub5 submissions/RR.10.30/random_k_seed2.txt \
#   --sub6 submissions/RR.10.30/top_degree_random_tie_topm2.0_seed2.txt

# python3 -m scripts.simulate_submissions \
#   --sub1 submissions/RR.10.50/top_degree_random_tie_topm1.4_seed2.txt \
#   --sub2 submissions/RR.10.50/edge_cluster_seed2.txt

# python3 -m scripts.simulate_submissions \
#   --sub1 submissions/RR.10.50/degree_cluster_seed2.txt \
#   --sub2 submissions/RR.10.50/edge_cluster_seed2.txt

# # for testing on generated graphs
# python3 -m scripts.simulate_submissions \
#   --sub1 submissions/SSBM_n210_k5_pin0.05_pout0.005_seed0/degree_cluster_seed2.txt \
#   --sub2 submissions/SSBM_n210_k5_pin0.05_pout0.005_seed0/top_degree_random_tie_topm2.0_seed2.txt \
#   --graph graphs/gen/SSBM_n210_k5_pin0.05_pout0.005_seed0.json