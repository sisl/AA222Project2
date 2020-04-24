
"""
    localtest.jl -- Feel free to modify anything you like in this file!

You can call this file as a script at the command line, or `include` it from within a julia session.

Example command-line usage:

    julia --color=yes localtest.jl                  # Evaluate all simple functions the default number of times (500):
    julia --color=yes localtest.jl 2000             # Evaluate all simple functions a custom number of times (2000 in this case):
    julia --color=yes localtest.jl simple1          # Evaluate only simple1 the default number of times:
    julia --color=yes localtest.jl simple3 2000     # Evaluate only simple3 a custom number of times:
"""

# Include the other relevant files:
include(joinpath("project2_jl", "helpers.jl"))
include(joinpath("project2_jl", "project2.jl"))

if length(ARGS) == 0
    # Default
    K = 500
    probnames = sort(collect(keys(PROBS)))
elseif length(ARGS) == 1
    # One input argument can be either evaluation count or function name, so
    # have to test for both. If it's not an integer it's got to be a function name
    K = tryparse(Int, ARGS[1])
    if K === nothing
        K = 500
        probnames = [ARGS[1]]
    else
        probnames = sort(collect(keys(PROBS)))
    end
elseif length(ARGS) == 2
    # Two inputs can come in at any order, so try both
    K = tryparse(Int, ARGS[1])
    if K === nothing
        K = tryparse(Int, ARGS[2])
        if K === nothing
            throw(ArgumentError("Can't detect which input is intended to be the evaluation count. Make sure it's an integer"))
        end
        probnames = [ARGS[1]]
    else
        probnames = [ARGS[2]]
    end
else
    throw(ArgumentError("Too many command-line inputs to localtest.jl"))
end

# This is the same random search implemented in the autograder.
# We take normally distributed random steps away from x0 and
# pick the best one. If we're infeasible, we at least try to minimize the penalty
function autograder_random_search(f, c, x0, n)
    empty!(COUNTERS)
    y_best = Inf
    x_best = x0
    p_best = Inf

    # helper function to compute the maximum constraint violation
    function p_max(x)
        cx = c(x)
        max(maximum(cx), zero(eltype(cx)))
    end

    while count(f) + count(c) < n-2
        x = x0 + randn(length(x0))
        px = p_max(x)

        if px <= 0
            p_best = min(p_best, px)
            y = f(x)
            if y < y_best
                y_best = y
                x_best = x
            end
        else
            if px < p_best
                p_best = px
                x_best = x
            end
        end
    end

    return x_best
end


function K_random_searches(f, c, x0, n, K, seed = 42)
    scores = zeros(K)
    for i in 1:K
        Random.seed!(seed+i)
        x_star = autograder_random_search(f, c, x0(), n)
        scores[i] = f(x_star)

        seed += 1
    end
    return scores
end

function compare_optimize_to_random(probname, K)
    f, g, c, x0, n = PROBS[probname]

    # Use a consistent random number stream for the comparison
    seed = 43

    random_scores = K_random_searches(f, c, x0, n, K, seed)
    scores, n_evals = main(probname, K, optimize, seed)

    if maximum(n_evals) > n
        @warn "Problem $probname saw $(maximum(n_evals)) out of $n allowed calls, which will be an automatic 0 on Gradescope"
    end

    # lower is better
    better = scores .< random_scores

    return mean(better)
end


printstyled("\nTesting $K times\n\n", bold = true)
for nm in probnames
    try
        better_percent = 100 * compare_optimize_to_random(nm, K)

        if better_percent > 55
            printstyled("Pass: optimize does better than random search $(better_percent)% of the time on $(nm)!\n", color = :green)
        else
            printstyled("Fail: optimize only beat random search $(better_percent)% of the time on $nm.\n", color = :red)
        end

    catch e
        println("ERROR IN PROBLEM $nm")
        showerror(stdout, e, catch_backtrace())
    end
end


