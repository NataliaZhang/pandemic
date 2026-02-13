# check submissions for available graphs
# run submit.sh to generate submissions

# python3 -m scripts.simulate_submissions \
#   --sub1 submissions/RR.10.51/top_degree_random_tie_topm1.0_seed2.txt \
#   --sub2 submissions/RR.10.51/top_degree_random_tie_topm1.4_seed2.txt 

# python3 -m scripts.simulate_submissions \
#   --sub1 submissions/RR.10.51/top_degree_random_tie_topm1.8_seed2.txt \
#   --sub2 submissions/RR.10.51/top_degree_random_tie_topm1.4_seed2.txt 


# python3 -m scripts.simulate_submissions \
#   --sub1 submissions/RR.10.51/top_degree_random_tie_topm1.0_seed2.txt \
#   --sub2 submissions/RR.10.51/degree_cluster_seed2.txt


# # for testing on generated graphs
# python3 -m scripts.simulate_submissions \
#   --sub1 submissions/SSBM_n210_k5_pin0.05_pout0.005_seed0/degree_cluster_seed2.txt \
#   --sub2 submissions/SSBM_n210_k5_pin0.05_pout0.005_seed0/top_degree_random_tie_topm2.0_seed2.txt \
#   --graph graphs/gen/SSBM_n210_k5_pin0.05_pout0.005_seed0.json

# Jungle
python3 -m scripts.simulate_submissions \
  --sub1 submissions/J.20.31/top_degree_random_tie_topm3.0_seed2.txt \
  --sub2 submissions/J.20.31/top_degree_random_tie_topm1.0_seed2.txt \
  --sub3 submissions/J.20.31/top_degree_random_tie_topm1.0_seed2.txt \
  --sub4 submissions/J.20.31/top_degree_avoid_topm4.0_seed2.txt \
  --sub5 submissions/J.20.31/random_k_seed2.txt \
  # --sub6 submissions/J.20.31/degree_cluster_seed2.txt