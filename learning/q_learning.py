from intent.mission_intent import IntentVector


class QLearningEngine:
    """
    I-MACSI Q-Learning Engine with Dynamic Reward Shaping.

    Unlike fixed-reward RL, the reward function is continuously
    modulated by the active Mission Intent Vector so that the swarm
    optimises for mission success rather than raw network metrics.
    """

    def __init__(self, alpha: float = 0.1, gamma: float = 0.9):
        self.alpha = alpha
        self.gamma = gamma
        self.failed_link_penalty = 1000.0  # Large penalty for failures
        self.loop_penalty = 500.0          # Penalty for routing loops
        
    def calculate_update(self, current_q: float, link_cost: float, min_next_q: float,
                         intent: IntentVector = None) -> float:
        """
        Bellman equation with I-MACSI dynamic reward shaping.

        The intent vector modulates the effective cost by adding
        mission-specific bonuses / penalties on top of the base link cost.
        
        Args:
            current_q:  Current Q-value for (state, action).
            link_cost:  Base intent-weighted link cost from IntentRouter.
            min_next_q: Estimated future cost from the next node.
            intent:     Active IntentVector (optional; enables reward shaping).
        """
        if link_cost == float('inf'):
            # Failed link detected, apply maximum penalty
            return (1 - self.alpha) * current_q + self.alpha * self.failed_link_penalty

        # ---- I-MACSI: Dynamic Reward Shaping ----
        shaped_cost = link_cost

        if intent is not None:
            # Security bonus: reward encrypted paths for secure missions
            if intent.w_security > 0.1:
                # Reward is negative cost reduction (incentivise secure links)
                shaped_cost -= intent.w_security * 0.05

            # Energy penalty: penalise high-power paths for energy-sensitive missions
            if intent.w_energy > 0.1:
                shaped_cost += intent.w_energy * 0.03

            # Compute bonus: reward offloading to less-loaded neighbors
            if intent.w_compute > 0.1:
                shaped_cost -= intent.w_compute * 0.04

            # Coverage bonus: reward geographic diversity (inter-plane hops)
            if intent.w_coverage > 0.1:
                shaped_cost -= intent.w_coverage * 0.03

            # High-priority mission urgency: amplify cost signal
            if intent.priority >= 8:
                shaped_cost *= 1.15  # Make the agent learn faster for critical missions

            # Ensure non-negative
            shaped_cost = max(0.0, shaped_cost)

        # Normal Bellman update for cost minimization
        # Q(s,a) = (1-alpha)*Q(s,a) + alpha*(cost + gamma * min(Q(s', a')))
        new_q = (1 - self.alpha) * current_q + self.alpha * (shaped_cost + self.gamma * min_next_q)
        return new_q