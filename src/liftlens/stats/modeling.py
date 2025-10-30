from typing import Any

import pandas as pd
import statsmodels.formula.api as smf
from loguru import logger
from numpy.linalg import LinAlgError


def ancova(
    df: pd.DataFrame, outcome_col: str, baseline_col: str, group_col: str = "group"
) -> dict[str, Any]:
    """
    Analysis of Covariance (ANCOVA) with baseline as covariate.
    """
    df = df.copy()
    df["treatment"] = (df[group_col] == "treatment").astype(int)

    formula = f"{outcome_col} ~ treatment + {baseline_col}"
    model = smf.ols(formula, data=df).fit()

    coef = model.params["treatment"]
    se = model.bse["treatment"]
    p_value = model.pvalues["treatment"]
    ci = model.conf_int().loc["treatment"].tolist()

    result = {
        "method": "ANCOVA",
        "coefficient": float(coef),
        "std_error": float(se),
        "p_value": float(p_value),
        "ci_95": [float(ci[0]), float(ci[1])],
        "r_squared": float(model.rsquared),
        "significant": p_value < 0.05,
    }
    logger.info(f"ANCOVA: β={coef:.4f}, p={p_value:.3f}, R²={model.rsquared:.3f}")
    return result


def ols_regression(
    df: pd.DataFrame, outcome_col: str, predictors: list[str], group_col: str = "group"
) -> dict[str, Any]:
    """
    General OLS with treatment and covariates.
    """
    df = df.copy()
    df["treatment"] = (df[group_col] == "treatment").astype(int)
    predictors = ["treatment"] + [p for p in predictors if p != group_col]

    formula = f"{outcome_col} ~ " + " + ".join(predictors)
    model = smf.ols(formula, data=df).fit()

    result = {
        "method": "OLS",
        "coefficients": {k: float(v) for k, v in model.params.items()},
        "p_values": {k: float(v) for k, v in model.pvalues.items()},
        "r_squared": float(model.rsquared),
        "adj_r_squared": float(model.rsquared_adj),
        "summary": model.summary().as_text(),
    }
    logger.info(
        f"OLS: R²={model.rsquared:.3f}, treatment p={model.pvalues['treatment']:.3f}"
    )
    return result


def mixed_effects(
    df: pd.DataFrame,
    outcome_col: str,
    fixed_effects: list[str],
    random_effect: str,
    group_col: str = "group",
) -> dict[str, Any]:
    """
    Linear Mixed-Effects Model (LMM) with random intercept.
    Requires: pip install statsmodels
    """
    try:
        import statsmodels.formula.api as smf
    except ImportError:
        logger.error("statsmodels not available for mixed effects")
        return {"error": "statsmodels required"}

    df = df.copy()
    df["treatment"] = (df[group_col] == "treatment").astype(int)
    fixed = ["treatment"] + fixed_effects
    formula = f"{outcome_col} ~ " + " + ".join(fixed) + f" + (1|{random_effect})"

    try:
        model = smf.mixedlm(formula, data=df, groups=df[random_effect]).fit()
    except (LinAlgError, ValueError) as e:
        logger.error(f"MixedLM failed: {e}")
        return {"error": str(e)}

    result = {
        "method": "Mixed-Effects",
        "fixed_effects": {
            k: float(v) for k, v in model.params.items() if not k.startswith("Group")
        },
        "random_var": float(model.cov_re.iloc[0, 0]),
        "significant": model.pvalues["treatment"] < 0.05,
    }
    logger.info(f"LMM: treatment p={model.pvalues['treatment']:.3f}")
    return result


def gam_model(
    df: pd.DataFrame,
    outcome_col: str,
    smooth_terms: list[str],
    group_col: str = "group",
) -> dict[str, Any]:
    """
    Generalized Additive Model (GAM) with smooth splines.
    Requires: pip install pygam
    """
    try:
        from pygam import LinearGAM, s
    except ImportError:
        logger.error("pygam not installed")
        return {"error": "pygam required"}

    df = df.copy()
    df["treatment"] = (df[group_col] == "treatment").astype(int)
    X = df[["treatment"] + smooth_terms].values
    y = df[outcome_col].values

    terms = [s(i) for i in range(1, len(smooth_terms) + 1)]
    gam = LinearGAM(terms).fit(X, y)

    treatment_effect = gam.coef_[0]
    result = {
        "method": "GAM",
        "treatment_effect": float(treatment_effect),
        "partial_dependencies": [
            gam.partial_dependence(term=i) for i in range(len(smooth_terms))
        ],
    }
    logger.info(f"GAM: treatment effect = {treatment_effect:.4f}")
    return result
