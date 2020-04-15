# Project1 Starter Code

## Code overview
- `language.txt` is a text file specifying the programming language in which the assignment is completed. *This is the very first thing you should edit*
- `project2_py` is a folder with starter code for completing the project in python
    - `project2_py/project2.py` contains the function `optimize` in which your code must be written.
    - `project2_py/helpers.py` contains optimization problems, random search, and test functions.
- `project2_jl` is a folder with starter code for completing the project in Julia.
    - `project2_jl/project2.jl` contains the function `optimize` in which your code must be written.
    - `project2_jl/helpers.jl` contains optimization problems, random search, and test functions.
- `localtest.py` runs tests on `project2_py`
- `localtest.jl` runs tests on `project2_jl`
- `make_submission.sh` is a shell script which will create a zip file for submission to gradescope (Unix).
- `make_submission_gitbash.sh` is a shell script which will create a zip file for submission to gradescope (Windows GitBash).
- `make_submission.bat` is a batch script to create a zip file for submission to gradescope (Windows Command Prompt)


## Rules
In this project, you will be implementing a function `optimize` that minimizes a function with a limited number of evaluations.
- We provide you a function `f(x)`, it's gradient `g(x)`, a function evaluating the constraints `c(x)`, and a number of allowed evaluations `n`.
- Each call to `f` counts as one evaluation, each call to `g` counts as two evaluations, and each call to `c` counts as one evaluation.
- The only external libraries allowed for your implementation of `optimize` are `numpy` in Python and `Statistics` and `Distributions` in Julia.
- You can use different optimization strategies for each problem, since we pass you a string `prob` in the call to `optimize`.
- You can base your algorithm on those found in the book or online, but you must give credit.
- Although you may discuss your algorithm with others, you must not share code.


## Deliverables

### Choose a programming language
First, pick either Julia1.2+ or Python3.6+ as a programming language. Depending on your choice, go to `language.txt` and change `notalanguage` to either `julia` or `python`.

### Complete the required code
Second, if you chose Julia, go to `project2_jl/project2.jl` and complete the function `optimize`. If you chose Python, go to `project2_py/project2.py` and complete the function `optimize`.
To get full credit on a given problem, your implementation must outperform random search on 55% of random seeds.

### Test your completed code
Third, if you chose Julia test your completed code by running:
`julia localtest.jl`
If you chose Python, test your completed code by running:
`python3 localtest.py`
You should see `Pass: optimize does better than random search on [problem].` for all the simple problems.

### Prepare your README.pdf
In addition to the programming aspect, you are also required to submit (also on gradescope) a PDF writeup, worth 50% of the assignment. It should contain the following information:
- A description of the method(s) you chose.
- Plots showing the path taken by your algorithm for simple problems 1 and 2. Show the path taken from three different starting points of your choice, as well as the objective and constraints contours.
- Convergence plots for the three simple functions described above (from any initial point of your choice).

### Create the code submission
Fourth, create the zip file for your submission by running
`bash ./make_submission.sh`

### Submit on Gradescope
- Submit the created zip file `project2.zip` on `Gradescope/AA222/Project 2`
- Submit your README.pdf on `Gradescope/AA222/Project 2 Writeup`


## FAQ

#### My strategy involves randomness. Are the score averaged with different random seeds?
Yes! The scores are averaged over 500 runs with different seeds.

#### Where are the Hessians?
We are not providing the Hessian function for you to use. But feel free to estimate it with calls to f and g. The cost would depend on the number of calls to f and g you end up making.

#### How many submission can we make?
Unlimited!

#### Can we exceed the max number of evaluations when making the plots for the README?
Yes! In python, you can get around the assertion error by calling the `problem.nolimit()` method to allow infinite evaluations.

#### How long does the autograder take to grade?
It shouldn't take more than 5 minutes to grade. If your submission times-out during grading, please contact us on Piazza.

#### How are leaderboard scores computed?
All of the problems are designed to have an optimal value of 0. The closer you are to 0, the closer you are to winning! The total score is the sum of all 5 problems (all of the problems are weighted the same).

#### Can I write code outside of the `optimize` function?
Yes, you can organize your code however you want as long as, at the end of the day, optimize works as described. Note that if you decide to create additional files, please make sure to import/include (python/julia respectively) them in your project2 file, or else they won’t be available to the autograder.

#### Can I change the starter code files?
Yes, they are not used in the autograder, so you have complete ownership over them!

#### Do I have to manually keep track of how many times the functions have been called?
Nope, we've decided to be very generous and provide a method for doing just that!

- In Julia:
`count(f)` will return how many times the function `f` has been called. For convenience, `count(f, g)` will give `count(f) + 2*count(g) + count(c)`. Ex:
```julia
function optimize(f, g, c, x0, n, prob)
    while count(f, g, c) < n
        # ... do some optimization
    end
    return x_best
end
```

- In Python: the `optimize` function has additional input argument `count`, which takes no arguments and evaluates to `f + 2g`. Ex:
```python
def optimize(f, g, c, x0, n, count, prob):
    while count() < n:
        # ... do some optimization
    return x_best
```

#### My README plots require an optimization path, but optimize only returns the optimum itself!
`optimize` is geared towards the autograder's evaluation of your method, so it only returns the final point. However, if you're coding with the README in mind (which is a good idea!), you may want to design your code in a way that is conducive to both requirements by writing methods thats collect the optimization history. See the following julia example:
```julia
function optimize(f, g, c, x0, n, prob)
    if prob == "simple1"
        x_history = some_method(f, g, c, x0, n)
    else
        x_history = some_other_method(f, g, c, x0, n)
    end
    return last(x_history)
end
```
