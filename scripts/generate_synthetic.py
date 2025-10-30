
#!/usr/bin/env python3
"""
Enhanced synthetic data generator with heterogeneity, CUPED, and strata.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger


def generate_data(
    n_users: int = 2000,
    effect_size: float = 0.08,
    heterogeneity: bool = True,
    strata_col: str = "country",
    noise_level: float = 10.0,
    seed: int = 42
) -> pd.DataFrame:
    np.random.seed(seed)
    logger.info(f"Generating {n_users:,} users with effect={effect_size}")

    # User features
    user_id = [f"user_{i:06d}" for i in range(n_users)]
    country = np.random.choice(["US", "EU", "ASIA"], n_users, p=[0.5, 0.3, 0.2])
    baseline = np.clip(np.random.normal(100, 20, n_users), 0, None)

    df = pd.DataFrame({"user_id": user_id, "country": country, "baseline": baseline})

    # Stratified randomization
    df["stratum"] = pd.qcut(df["baseline"], 4, labels=False)
    df["group"] = "control"
    for s in df["stratum"].unique():
        idx = df[df["stratum"] == s].index
        treat_idx = np.random.choice(idx, size=len(idx)//2, replace=False)
        df.loc[treat_idx, "group"] = "treatment"

    # Heterogeneity in treatment effect
    base_effect = effect_size
    if heterogeneity:
        country_effects = {"US": 1.2, "EU": 0.9, "ASIA": 1.1}
        df["effect"] = df["country"].map(country_effects) * base_effect
    else:
        df["effect"] = base_effect

    # Outcome with noise
    noise = np.random.normal(0, noise_level, n_users)
    df["outcome"] = df["baseline"] * (1 + df["group"].map({"control": 0, "treatment": 1}) * df["effect"]) + noise
    df["outcome"] = df["outcome"].clip(lower=0)

    df = df.drop(columns=["stratum", "effect"])
    logger.info(f"Generated data: control={len(df[df['group']=='control'])}, treatment={len(df[df['group']=='treatment'])}")
    return df


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic A/B test data")
    parser.add_argument("--n_users", type=int, default=2000, help="Number of users")
    parser.add_argument("--effect_size", type=float, default=0.08, help="Average treatment effect")
    parser.add_argument("--heterogeneity", action="store_true", help="Enable country-level HTE")
    parser.add_argument("--output", type=str, default="data/synthetic_data.csv", help="Output path")
    args = parser.parse_args()

    df = generate_data(
        n_users=args.n_users,
        effect_size=args.effect_size,
        heterogeneity=args.heterogeneity
    )

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    logger.success(f"Synthetic data saved to {args.output}")


if __name__ == "__main__":
    main()



