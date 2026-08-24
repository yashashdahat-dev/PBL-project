from dataclasses import dataclass

@dataclass
class ConstellationConfig:
    num_planes: int = 4
    sats_per_plane: int = 4
    isl_capacity_mbps: float = 1000.0
    base_isl_reliability: float = 0.999
    congestion_threshold: float = 0.8

@dataclass
class QLearningConfig:
    alpha: float = 0.1
    gamma: float = 0.9
    epsilon: float = 0.2
    epsilon_decay: float = 0.995

@dataclass
class SimulationConfig:
    max_steps: int = 1000
    seed: int = 42

class Config:
    network = ConstellationConfig()
    learning = QLearningConfig()
    sim = SimulationConfig()