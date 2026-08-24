class QLearningEngine:
    def __init__(self, alpha: float = 0.1, gamma: float = 0.9):
        self.alpha = alpha
        self.gamma = gamma
        self.failed_link_penalty = 1000.0  # Large penalty for failures
        self.loop_penalty = 500.0          # Penalty for routing loops
        
    def calculate_update(self, current_q: float, link_cost: float, min_next_q: float) -> float:
        """
        Bellman equation implementation for cost minimization.
        Updates the local Q-value based on the immediate cost and estimated future cost.
        """
        if link_cost == float('inf'):
            # Failed link detected, apply maximum penalty
            return (1 - self.alpha) * current_q + self.alpha * self.failed_link_penalty
            
        # Normal update for cost minimization
        # Q(s,a) = (1-alpha)*Q(s,a) + alpha*(cost + gamma * min(Q(s', a')))
        new_q = (1 - self.alpha) * current_q + self.alpha * (link_cost + self.gamma * min_next_q)
        return new_q