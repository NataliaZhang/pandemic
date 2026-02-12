## set up
Download sample_graphs.zip from piazza, and unzip it in the root of the repository.

## strategy
Implement new strategies in strategies/baselines.py, and add command-line arguments in scripts/submit.py as needed.

## run
Use `scripts/submit.sh` to run your strategy on the sample graph. You can change the graph, strategy, and random seed. The output will be written to `submissions/`.

Use `scripts/simulate_submissions.sh` to simulate a competition between two submissions. You can change the submission paths as needed.

## store
Do not change the output submission directory `submissions/` and the graph path `graphs/`. We rely on these for inferring the path.