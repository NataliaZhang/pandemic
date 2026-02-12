# for competition graph submission
python -m scripts.submit \
  --graph graphs/RR.5.1.json \
  --strategy top_degree_no_repeat \
  --top-m 2.0 \
  --seed 2 

# for testing on generated graphs
python -m scripts.submit \
  --graph graphs/gen/ER_n1000_pauto_seed0.json \
  --strategy top_degree_no_repeat \
  --top-m 2.0 \
  --seed 2 