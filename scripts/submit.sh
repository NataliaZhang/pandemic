# for competition graph submission
python3 -m scripts.submit \
  --graph graphs/RR.5.1.json \
  --strategy cluster_boundary_takeover_spectral \
  --top-m 2.0 \
  --seed 2 

# for testing on generated graphs
python3 -m scripts.submit \
  --graph graphs/gen/ER_n1000_pauto_seed0.json \
  --strategy cluster_boundary_takeover_spectral \
  --top-m 2.0 \
  --seed 2 
