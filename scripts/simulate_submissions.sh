# check submissions for available graphs
# run submit.sh to generate submissions

python -m scripts.simulate_submissions \
  --sub1 submissions/RR.5.1/top_degree_no_repeat_topm2.0_seed0.txt \
  --sub2 submissions/RR.5.1/top_degree_no_repeat_topm1.2_seed0.txt

python -m scripts.simulate_submissions \
  --sub1 submissions/ER_n1000_pauto_seed0/top_degree_no_repeat_topm1.0_seed2.txt \
  --sub2 submissions/ER_n1000_pauto_seed0/top_degree_no_repeat_topm2.0_seed2.txt