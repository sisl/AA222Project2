#
# File: helpers.py
#

# this file defines the optimization problems, random search, and test

from tqdm import tqdm
import numpy as np

class OptimizationProblem:

    @property
    def xdim(self):
        # dimension of x
        return self._xdim

    @property
    def prob(self):
        # problem name
        return self._prob
    
    @property
    def n(self):
        # number of allowed evaluations
        return self._n
    
    def _reset(self):
        self._ctr = 0

    def count(self):
        return self._ctr

    def nolimit(self):
        # sets n to inf, useful for plotting/debugging
        self._n = np.inf
        
    def x0(self):
        '''
        Returns:
            x0 (np.array): (xdim,) randomly initialized x
        '''
        return np.random.randn(self.xdim)

    def f(self, x):
        '''Evaluate f
        Args:
            x (np.array): input
        Returns:
            f (float): evaluation
        '''
        self._ctr += 1
        assert self._ctr <= self.n, 'Number of allowed function calls exceeded.'

        return self._wrapped_f(x)
    
    def _wrapped_f(self, x):
        raise NotImplementedError

    def g(self, x):
        '''Evaluate jacobian of f
        Args:
            x (np.array): input
        Returns:
            jac (np.array): jacobian of f wrt x
        '''
        self._ctr += 2
        assert self._ctr <= self.n, 'Number of allowed function calls exceeded.'

        return self._wrapped_g(x)

class ConstrainedOptimizationProblem(OptimizationProblem):

    @property
    def cdim(self):
        # number of constraints
        return self._cdim

    @property
    def nc(self):
        # number of allowed constraint evals
        return self._nc

    def _reset(self):
        self._ctr = 0

    def count(self):
        return self._ctr

    def nolimit(self):
        # sets n to inf, useful for plotting/debugging
        self._n = np.inf

    def c(self, x):
        '''Evaluate constraints
        Args:
            x (np.array): input
        Returns:
            c (np.array): (cdim,) evaluation of constraints
        '''
        self._ctr += 1
        assert self._ctr <= self.n, 'Number of allowed function calls exceeded.'

        return self._wrapped_c(x)

    def _wrapped_c(self, x):
        raise NotImplementedError


class Simple1(ConstrainedOptimizationProblem):
    
    def __init__(self):
        self._xdim = 2
        self._cdim = 2
        self._prob = 'simple1'
        self._n = 2000
        self._reset()

    def x0(self):
        return np.random.rand(self._xdim) * 2.0

    def _wrapped_f(self, x):
        return -x[0] * x[1]

    def _wrapped_g(self, x):
        return np.array([
            -x[1],
            -x[0],
                ])

    def _wrapped_c(self,x):
        return np.array([
            x[0] + x[1]**2 - 1,
            -x[0] - x[1]
            ])



class Simple2(ConstrainedOptimizationProblem):

    def __init__(self):
        self._xdim = 2
        self._cdim = 2
        self._prob = 'simple2'
        self._n = 2000
        self._reset()

    def x0(self):
        return np.random.rand(self._xdim) * 2.0 - 1.0

    def _wrapped_f(self, x):
        return 100 * (x[1] - x[0]**2)**2 + (1-x[0])**2

    def _wrapped_g(self, x):
        return np.array([
            2*(-1 + x[0] + 200*x[0]**3 - 200*x[0]*x[1]),
            200*(-x[0]**2 + x[1])
                ])

    def _wrapped_c(self,x):
        return np.array([
            (x[0]-1)**3 - x[1] + 1,
            x[0] + x[1] - 2,
            ])


class Simple3(ConstrainedOptimizationProblem):

    def __init__(self):
        self._xdim = 3
        self._cdim = 1
        self._prob = 'simple3'
        self._n = 2000
        self._reset()

    def x0(self):
        b = 2.0 * np.array([1.0, -1.0, 0.0])
        a = -2.0 * np.array([1.0, -1.0, 0.0])
        return np.random.rand(3) * (b-a) + a

    def _wrapped_f(self, x):
        return x[0] - 2*x[1] + x[2]

    def _wrapped_g(self, x):
        return np.array([1., -2., 1.])

    def _wrapped_c(self, x):
        return np.array([x[0]**2 + x[1]**2 + x[2]**2 - 1.])


def max_constraint_violation(c_of_x):
    """
    Returns the maximum constraint violation in c(x).
    Args:
        c_of_x (np.array): (cdim,) c(x)
    Returns:
        mcv (float): maximum constraint violation in c(x). 
    """
    return max(np.maximum(c_of_x, 0))


def optimize_random(f, g, c, x0, n, count, prob):
    """ Optimizer using random search.
    Args:
        f (function): Function to be optimized
        g (function): Gradient function for `f`
        c (function): Function evaluating constraints
        x0 (np.array): Initial position to start from
        n (int): Number of evaluations allowed. Remember `f` and `c` cost 1 and `g` costs 2
        count (function): takes no arguments are reutrns current count
        prob (str): Name of the problem. So you can use a different strategy 
                 for each problem. `prob` can be `simple1`,`simple2`,`simple3`,
                 `secret1` or `secret2`
    Returns:
        x_best (np.array): best selection of variables found
    """
    
    best_x = None
    best_f = np.inf
    best_mcv = np.inf

    while count() < n-2:
        
        x = x0 + np.random.randn(*x0.shape)

        # evaluate f and maximum constraint violation at each x
        f_x = f(x)
        c_x = c(x)
        mcv_x = max_constraint_violation(c_x)

        if mcv_x <= best_mcv:
            if mcv_x < best_mcv:
                # this x is more feasible
                best_x = x
                best_f = f_x
                best_mcv = mcv_x
            else:
                # equally feasible, so compare f
                if f_x < best_f:
                    best_x = x
                    best_f = f_x
                    best_mcv = mcv_x

    return best_x


def get_score(test, x):
    # computes score of x on a ConstrainedOptimizationProblem

    p = test()
    p.nolimit()

    f = p.f
    c = p.c

    # helper function to compute the quadratic penalty
    p_quad = lambda x: np.sum(np.clip(c(x),0, np.inf)**2)

    score = f(x)
    score += (p_quad(x)>0)*1e7

    return score


def test_optimize(optimize):
    '''
    Tests optimize to ensure it returns a+b
    Args:
        optimize (function): function for adding a+b
    '''

    for test in [Simple1, Simple2, Simple3]:

        p = test()
        print('Testing on %s...' % p.prob)

        # test optimize
        print('Testing optimize...')
        xvals_opt = []
        for seed in tqdm(range(500)):
            p = test()
            np.random.seed(seed)
            x0 = p.x0()
            xb = optimize(p.f, p.g, p.c, x0, p.n, p.count, p.prob)
            xvals_opt.append(xb)

        # test random
        print('Testing random search...')
        xvals_random = []
        for seed in tqdm(range(500)):
            p = test()
            np.random.seed(seed)
            x0 = p.x0()
            xb = optimize_random(p.f, p.g, p.c, x0, p.n, p.count, p.prob)
            xvals_random.append(xb)

        # compare xvals
        better = []
        for (xb_rand, xb_opt) in zip(xvals_random, xvals_opt):
            if np.any(np.isnan(xb_opt)):
                print('Warning: NaN returned by optimizer. Leaderboard score will be 0.')
                better.append(False)
            else:
                better.append(get_score(test, xb_opt) < get_score(test, xb_rand))

        better = np.array(better)

        # to pass, optimize must find a better optimimum than random
        # search over at least 55% of seeds.
        frac = np.mean(better)
        if frac > 0.55:
            print('Pass: optimize does better than random search on %s %.3f pct of the time.' % (p.prob,frac*100))
        else:
            print('Fail: optimize is only random search on %s %.3f pct of the time.' % (p.prob,frac*100))

    return
    

