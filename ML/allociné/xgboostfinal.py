# -*- coding: utf-8 -*-
"""
Script complet pour préparer les données, entraîner et évaluer un modèle LightGBM
optimisé par Optuna pour prédire de manière précise la partie haute (top 20 %)
des films (entrées France S‑1).

Étapes :
- Lecture : modele3v16.csv
- Pré‑traitements et features dérivées (sans Youtube buzz)
- Encodages catégoriels (Count + Target) + ordinal pour petites catégories
- Transformation `log1p` de la cible
- Validation chronologique (TimeSeriesSplit 5 folds) avec test réduit au top 20 % films
- Métriques : RMSE_log + RMSE/MAE/R²/Spearman + Top 10 % capture
- Sauvegarde : joblib, pickle, metrics JSON

Requirements : pandas, numpy, lightgbm, optuna, category_encoders, scikit‑learn>=1.8, scipy
"""

import re, json, pickle, pathlib, warnings
import numpy as np, pandas as pd
from scipy.stats import spearmanr
import lightgbm as lgb, optuna
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder
from category_encoders import CountEncoder, TargetEncoder
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import root_mean_squared_error as rmse, r2_score, mean_absolute_error

warnings.filterwarnings("ignore")

# ------------------------------------------------------------
# 0) Chargement et conversion
# ------------------------------------------------------------
df = pd.read_csv("modele3v16.csv")

def to_int(txt):
    if isinstance(txt, str):
        txt = re.sub(r"[^\d]", "", txt)
        return int(txt) if txt else np.nan
    return int(txt) if not pd.isna(txt) else np.nan

df["number_entrances_fr"] = df["number_entrances_fr"].apply(to_int)

# ------------------------------------------------------------
# 1) Feature engineering
# ------------------------------------------------------------
df["sortie"]   = pd.to_datetime(df["sortie"], format="%d/%m/%Y", errors="coerce")
df["month"]    = df["sortie"].dt.month
df["quarter"]  = df["sortie"].dt.quarter
df["vacances"] = df["month"].isin([7, 8, 12, 1, 2]).astype("int8")

# Listes de colonnes
num_cols   = [
    "average_fr_director", "total_average_actors", "popularity_productor",
    "popularity_actors", "sum_popularity_actors", "duration", "year",
    "month", "quarter", "vacances"
]
cat_short  = ["genre", "country_production", "public", "distributeur"]
cat_long   = ["directors", "actors", "writer"]

# Cible log-transformée
y_raw = df["number_entrances_fr"].values
threshold = np.nanpercentile(y_raw, 80)        # top 20%
mask_top20 = y_raw >= threshold
y_log   = np.log1p(y_raw)

# ------------------------------------------------------------
# 2) Pré‑processing
# ------------------------------------------------------------
ord_enc = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
ce      = CountEncoder(cols=cat_long)
te      = TargetEncoder(cols=cat_long, smoothing=0.3)

preproc = ColumnTransformer([
    ("num", "passthrough", num_cols),
    ("cat_short", ord_enc, cat_short),
    ("count_long", ce, cat_long),
    ("target_long", te, cat_long),
], remainder="drop")

# ------------------------------------------------------------
# 3) Métriques cohérentes
# ------------------------------------------------------------
from sklearn.metrics import root_mean_squared_error as rmse, r2_score, mean_absolute_error
from scipy.stats import spearmanr

def inv_log(x): return np.expm1(x)

def fold_metrics(y_true_log, y_pred_log):
    rmse_log = rmse(y_true_log, y_pred_log)
    yt = inv_log(y_true_log); yp = inv_log(y_pred_log)
    rmse_lin = rmse(yt, yp)
    mae_lin  = mean_absolute_error(yt, yp)
    r2_lin   = r2_score(yt, yp)
    rho, _   = spearmanr(yt, yp)
    k = max(int(len(yp)*0.10), 1)
    capture = yt[np.argsort(-yp)[:k]].sum() / yt.sum()
    return rmse_log, rmse_lin, mae_lin, r2_lin, rho, capture

# ------------------------------------------------------------
# 4) Objective Optuna (LightGBM Tweedie)
# ------------------------------------------------------------
def objective(trial):
    params = dict(
        objective="tweedie",
        tweedie_variance_power=1.2,
        metric="rmse",
        boosting_type="gbdt",
        device_type="gpu",
        verbosity=-1,
        learning_rate=trial.suggest_float("lr", 0.01, 0.15, log=True),
        num_leaves=trial.suggest_int("leaves", 64, 256),
        max_depth=trial.suggest_int("depth", 4, 10),
        feature_fraction=trial.suggest_float("ff", 0.6, 1.0),
        bagging_fraction=trial.suggest_float("bf", 0.7, 1.0),
        bagging_freq=trial.suggest_int("bfreq", 1, 6),
        min_data_in_leaf=trial.suggest_int("min_leaf", 50, 500),
        n_estimators=trial.suggest_int("n_estimators", 800, 2000, step=200),
    )
    cv = TimeSeriesSplit(n_splits=5)
    errs = []
    for tr, te in cv.split(df):
        X_tr, X_te = df.iloc[tr], df.iloc[te]
        y_tr, y_te = y_log[tr], y_log[te]
        # Test sur top20%
        mask_te = mask_top20[te]
        X_te = X_te.iloc[mask_te]; y_te = y_te[mask_te]
        # Pré‑processing
        X_tr_t = preproc.fit_transform(X_tr, y_tr)
        X_te_t = preproc.transform(X_te)
        # Poids accentuant les hits
        w_tr = np.clip((inv_log(y_tr)/threshold)**0.6, 1, 20)
        model = lgb.LGBMRegressor(**params)
        model.fit(X_tr_t, y_tr, sample_weight=w_tr)
        preds = model.predict(X_te_t)
        errs.append(rmse(y_te, preds))
    return float(np.mean(errs))

study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=42))
study.optimize(objective, n_trials=120, timeout=90*60)
best = study.best_params
best.update(
    objective="tweedie", tweedie_variance_power=1.2,
    metric="rmse", device_type="gpu", boosting_type="gbdt", verbosity=-1
)
print("Best params:", best)

# ------------------------------------------------------------
# 5) CV détaillée top20%
# ------------------------------------------------------------
cv = TimeSeriesSplit(n_splits=5)
metrics = []
for tr, te in cv.split(df):
    X_tr, X_te = df.iloc[tr], df.iloc[te]
    y_tr, y_te = y_log[tr], y_log[te]
    mask_te = mask_top20[te]
    X_te = X_te.iloc[mask_te]; y_te = y_te[mask_te]
    X_tr_t = preproc.fit_transform(X_tr, y_tr)
    X_te_t = preproc.transform(X_te)
    w_tr = np.clip((inv_log(y_tr)/threshold)**0.6, 1, 20)
    mdl = lgb.LGBMRegressor(**best)
    mdl.fit(X_tr_t, y_tr, sample_weight=w_tr)
    preds = mdl.predict(X_te_t)
    metrics.append(fold_metrics(y_te, preds))
cv_df = pd.DataFrame(metrics, columns=["RMSE_log","RMSE","MAE","R2","Spearman","Top10%_Capture"])
cv_mean = cv_df.mean()
print("\n===== CV top20% =====")
for k,v in cv_mean.items():
    print(f"{k:18s}: {v*100:.1f}%" if k=="Top10%_Capture" else f"{k:18s}: {v:,.0f}")

# ------------------------------------------------------------
# 6) Entraînement final & export
# ------------------------------------------------------------
X_full = preproc.fit_transform(df, y_log)
w_full = np.clip((inv_log(y_log)/threshold)**0.6, 1, 20)
final = lgb.LGBMRegressor(**best)
final.fit(X_full, y_log, sample_weight=w_full)

pathlib.Path("models").mkdir(exist_ok=True)
joblib.dump(final, "models/lgb_boxoffice_top20.joblib")
with open("models/lgb_boxoffice_top20.pkl","wb") as f: pickle.dump(final, f)
with open("models/lgb_boxoffice_top20_metrics.json","w") as f:
    json.dump(cv_mean.round(4).to_dict(), f, indent=2)

print("\n✅ Modèle top20% entraîné et enregistré !")
