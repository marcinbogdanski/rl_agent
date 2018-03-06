import numpy as np

from .agent_base import AgentBase
from .approximators import KerasApproximator


import pdb


class AgentSARSA(AgentBase):
    """Simple SARSA Agent

    See base class doc for how to use Agents in general.
    """

    def __init__(self,
        state_space,
        action_space,
        discount,
        start_learning_at,

        q_fun_approx,
        policy):
        """
        Params:
            state_space: gym.spaces object describing state space
            action_space: gym.spaces object describing action space
            discount: per-step reward discount, usually gamma in literature
            start_learning_at: postpone any learning until this time step,
                               use e.g. to pre-fill replay memory with random
        """
        super().__init__(
            state_space, action_space,
            discount, start_learning_at)

        #
        #   Initialize Q-function approximator
        #
        self.Q = q_fun_approx
        self.Q.set_state_action_spaces(state_space, action_space)

        #
        #   Initialize Policy Module
        #
        self.policy = policy
        self.policy.set_state_action_spaces(state_space, action_space)
        self.policy.link(self)  # Policy may need access to Q-approx etc.


    def reset(self):
        """Reset after episode completed. Can be called manually if required"""
        super().reset()
        self.policy.reset()


    def next_step(self, done):
        super().next_step(done)
        self.policy.next_step(self._curr_total_step)


    def log(self, episode, step, total_step):
        super().log(episode, step, total_step)
        if self.Q is not None:
            self.Q.log(episode, step, total_step)


    def learn(self):
        """Perform learning. See Agent doc for call order."""
        self._eval_td_online()


    def _eval_td_online(self):
        if len(self._trajectory) >= 2:
            self._eval_td_t(len(self._trajectory) - 2)  # Eval next-to last state


    def _eval_td_t(self, t):
        """TD update state-value for single state in trajectory

        This assumesss time step t+1 is availalbe in the trajectory

        For online updates:
            Call with t equal to previous time step

        For offline updates:
            Iterate trajectory from t=0 to t=T-1 and call for every t

        Params:
            t (int [t, T-1]) - time step in trajectory,
                    0 is initial state; T-1 is last non-terminal state

        """

        # Shortcuts for more compact notation:

        St = self._trajectory[t].observation      # evaluated state tuple (x, y)
        At = self._trajectory[t].action
        St_1 = self._trajectory[t+1].observation  # next state tuple (x, y)
        Rt_1 = self._trajectory[t+1].reward       # next step reward
        done = self._trajectory[t+1].done

        if self._curr_total_step < self._start_learning_at:
            # no lerninng during initial random phase
            return


        #
        #   SARSA
        #
        if done:
            Tt = Rt_1
        else:
            At_1 = self._trajectory[t+1].action
            if At_1 is None:
                At_1 = self.policy.pick_action(St_1)
            Tt = Rt_1 + self._discount * self.Q.estimate(St_1, At_1)                

        self.Q.train(St, At, Tt)
            

    def get_fingerprint(self):
        weights_sum = self.Q.get_weights_fingerprint()

        fingerprint = weights_sum \
                      + self._debug_cum_state \
                      + self._debug_cum_action \
                      + self._debug_cum_reward \
                      + self._debug_cum_done

        return fingerprint, weights_sum, self._debug_cum_state, \
                self._debug_cum_action, self._debug_cum_reward, \
                self._debug_cum_done
