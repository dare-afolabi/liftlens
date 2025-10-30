
from typing import Any

import numpy as np
from loguru import logger
from scipy import stats


class SequentialTest:
    """
    Sequential testing with alpha-spending (OBF, Pocock) or Bayesian monitoring.
    """

    def __init__(self, method: str = "obf", alpha: float = 0.05, power: float = 0.9):
        self.method = method.lower()
        self.alpha = alpha
        self.power = power
        self.look_times: list[float] = []
        self.z_scores: list[float] = []
        self.boundaries: list[float] = []
        self.stopped: bool = False
        self.decision: str | None = None

    def add_interim(self, z_score: float, look_time: float) -> dict[str, Any]:
        """
        Add interim analysis.
        look_time: proportion of total sample (0 to 1)
        """
        if self.stopped:
            raise ValueError("Test already stopped")

        self.look_times.append(look_time)
        self.z_scores.append(z_score)

        if self.method == "obf":
            boundary = self._obf_boundary(look_time)
        elif self.method == "pocock":
            boundary = self._pocock_boundary(len(self.look_times))
        else:
            raise ValueError("Method must be 'obf' or 'pocock'")

        self.boundaries.append(boundary)

        crossed = abs(z_score) > boundary
        self.stopped = crossed
        if crossed:
            self.decision = "reject" if z_score > 0 else "accept"  # simplified

        result = {
            "look": len(self.look_times),
            "look_time": look_time,
            "z_score": z_score,
            "boundary": boundary,
            "crossed": crossed,
            "stopped": self.stopped,
            "decision": self.decision
        }
        logger.info(f"Interim {result['look']}: Z={z_score:.3f}, boundary={boundary:.3f}, {'STOP' if crossed else 'continue'}")
        return result

    def _obf_boundary(self, t: float) -> float:
        """O'Brien-Fleming boundary."""
        if t <= 0 or t > 1:
            return np.inf
        return float(stats.norm.ppf(1 - self.alpha / (2 * t)))

    def _pocock_boundary(self, k: int) -> float:
        """Pocock boundary."""
        return float(stats.norm.ppf(1 - self.alpha / (2 * k)))

    def final_analysis(self, final_z: float) -> dict[str, Any]:
        """Final analysis if not stopped early."""
        if self.stopped:
            return {"error": "Test already stopped"}
        result = self.add_interim(final_z, 1.0)
        if not result["crossed"]:
            result["decision"] = "fail_to_reject"
        return result


def bayesian_monitoring(
    prior_alpha: float = 1.0,
    prior_beta: float = 1.0,
    control_conversions: int = 0,
    treatment_conversions: int = 0,
    control_n: int = 1,
    treatment_n: int = 1,
    threshold: float = 0.95
) -> dict[str, Any]:
    """
    Bayesian A/B testing: P(treatment > control) > threshold
    """
    post_alpha_c = prior_alpha + control_conversions
    post_beta_c = prior_beta + (control_n - control_conversions)
    post_alpha_t = prior_alpha + treatment_conversions
    post_beta_t = prior_beta + (treatment_n - treatment_conversions)

    # Monte Carlo estimate
    samples = 100_000
    control_samples = np.random.beta(post_alpha_c, post_beta_c, samples)
    treatment_samples = np.random.beta(post_alpha_t, post_beta_t, samples)
    prob_superior = (treatment_samples > control_samples).mean()

    result = {
        "method": "Bayesian",
        "control_rate": control_conversions / control_n,
        "treatment_rate": treatment_conversions / treatment_n,
        "prob_treatment_better": float(prob_superior),
        "stop_early": prob_superior > threshold or prob_superior < (1 - threshold),
        "recommendation": "treatment" if prob_superior > threshold else "control" if prob_superior < (1 - threshold) else "continue"
    }
    logger.info(f"Bayesian: P(treat>ctrl)={prob_superior:.3f}, {result['recommendation']}")
    return result


