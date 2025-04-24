
# train_boxoffice_two_stage.py
# -*- coding: utf-8 -*-
"""
Pipeline en deux étapes robuste :
1. Classification des films « hits » (top 20 %)
2. Régression du nombre d’entrées (log1p) sur les hits uniquement

Gestion des folds sans hits dans le test.
"""
import re, json, pickle, pathlib, warnings
import numpy as np, pandas as pd
from scipy.stats import spearmanr
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import (roc_auc_score, recall_score,
                             root_mean_squared_error as rmse,
                             mean_absolute_error, r2_score)
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder
from sklearn.ensemble import RandomForestClassifier
import lightgbm as lgb
from category_encoders import CountEncoder, TargetEncoder
import joblib

warnings.filterwarnings("ignore")

# 1) Chargement et préparation
# ------------------------------------------------------------
df = pd.read_csv("modele3v17.csv", dtype={"actors":str, "directors":str, "distributeur":str})
import ast

def to_int(txt):
    if isinstance(txt,str):
        t=re.sub(r"[^\d]","",txt)
        return int(t) if t else np.nan
    return int(txt) if not pd.isna(txt) else np.nan

df['number_entrances_fr'] = df['number_entrances_fr'].apply(to_int)
# Les features historiques sont déjà dans modele3v17
# Date features
df['sortie']   = pd.to_datetime(df['sortie'],format="%d/%m/%Y",errors='coerce')
df['month']    = df['sortie'].dt.month
df['quarter']  = df['sortie'].dt.quarter
df['vacances'] = df['month'].isin([7,8,12,1,2]).astype('int8')

# Cibles
y_raw = df['number_entrances_fr'].values
threshold = np.nanpercentile(y_raw,80)
mask_hit = (y_raw >= threshold).astype(int)
y_log = np.log1p(y_raw)

# Colonnes pour preprocessing
num_cols = [
    'average_fr_director','total_average_actors','popularity_productor',
    'popularity_actors','sum_popularity_actors','duration','year',
    'month','quarter','vacances',
    'actors_avg_top3','actors_count_top3',
    'director_avg','director_count',
    'dist_avg','dist_count'
]
cat_short = ['genre','country_production','public','distributeur']
cat_long  = ['directors','actors','writer']

# Preprocessing pipeline
ord_enc = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
ce = CountEncoder(cols=cat_long)
te = TargetEncoder(cols=cat_long, smoothing=0.3)
preproc = ColumnTransformer([
    ('num',        'passthrough', num_cols),
    ('cat_short',  ord_enc,       cat_short),
    ('count_long', ce,            cat_long),
    ('target_long',te,            cat_long),
], remainder='drop')

# Métriques helper
def inv_log(x): return np.expm1(x)

def fold_reg_metrics(y_true_log, y_pred_log):
    rmse_log = rmse(y_true_log, y_pred_log)
    yt = inv_log(y_true_log); yp = inv_log(y_pred_log)
    rmse_lin = rmse(yt, yp)
    mae_lin  = mean_absolute_error(yt, yp)
    r2_lin   = r2_score(yt, yp)
    rho, _   = spearmanr(yt, yp)
    k = max(int(len(yp)*0.10),1)
    capture = yt[np.argsort(-yp)[:k]].sum() / yt.sum()
    return rmse_log, rmse_lin, mae_lin, r2_lin, rho, capture

# 2) CV chrono 2-étapes
# ------------------------------------------------------------
clf_scores = []
reg_scores = []
tss = TimeSeriesSplit(n_splits=5)

for tr_idx, te_idx in tss.split(df):
    X_tr, X_te = df.iloc[tr_idx], df.iloc[te_idx]
    y_hit_tr, y_hit_te = mask_hit[tr_idx], mask_hit[te_idx]
    y_log_tr, y_log_te = y_log[tr_idx], y_log[te_idx]

    # Preprocessing complet
    X_tr_t = preproc.fit_transform(X_tr, y_log_tr)
    X_te_t = preproc.transform(X_te)

    # -- Étape 1: Classification des hits
    if np.any(y_hit_tr == 1) and np.any(y_hit_te == 1):
        clf = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)
        clf.fit(X_tr_t, y_hit_tr)
        prob = clf.predict_proba(X_te_t)[:,1]
        auc = roc_auc_score(y_hit_te, prob)
        # recall at 70% percentile threshold
        thresh = np.percentile(prob[y_hit_te==1], 70)
        pred_hit = (prob >= thresh).astype(int)
        rec = recall_score(y_hit_te, pred_hit)
        clf_scores.append((auc, rec))
    else:
        # Pas de hits dans train ou test : on skip ce fold
        continue

    # -- Étape 2: Régression sur hits
    hit_tr_idx = np.where(y_hit_tr == 1)[0]
    hit_te_idx = np.where(pred_hit == 1)[0]
    if len(hit_tr_idx) > 0 and len(hit_te_idx) > 0:
        X_r_tr = X_tr_t[hit_tr_idx]; y_r_tr = y_log_tr[hit_tr_idx]
        X_r_te = X_te_t[hit_te_idx]; y_r_te = y_log_te[hit_te_idx]
        model = lgb.LGBMRegressor(objective='regression_l2', metric='rmse', device='gpu')
        model.fit(X_r_tr, y_r_tr)
        preds = model.predict(X_r_te)
        reg_scores.append(fold_reg_metrics(y_r_te, preds))
    # fin de fold

# Moyennes CV
mean_auc = np.mean([a for a,_ in clf_scores])
mean_rec = np.mean([r for _,r in clf_scores])
mean_reg = np.mean(reg_scores, axis=0)  # unpack metrics tuple
print(f"CV Classif => AUC: {mean_auc:.3f}, Recall_hit: {mean_rec:.3f}")
print(f"CV Régr => RMSE_log: {mean_reg[0]:.3f}, RMSE_lin: {mean_reg[1]:,.0f}, MAE: {mean_reg[2]:,.0f}, R2: {mean_reg[3]:.3f}, Spearman: {mean_reg[4]:.3f}, Top10%_Capture: {mean_reg[5]*100:.1f}%")

# 3) Entraînement final
# ------------------------------------------------------------
# Preproc full
X_full_t = preproc.fit_transform(df, y_log)
# Classif final
clf_final = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)
clf_final.fit(X_full_t, mask_hit)
# Reg final sur hits
hit_full_idx = np.where(mask_hit == 1)[0]
X_rf = X_full_t[hit_full_idx]; y_rf = y_log[hit_full_idx]
reg_final = lgb.LGBMRegressor(objective='regression_l2', metric='rmse', device='gpu')
reg_final.fit(X_rf, y_rf)

# Sauvegardes
pathlib.Path('models').mkdir(exist_ok=True)
joblib.dump(clf_final, 'models/clf_hits.joblib')
joblib.dump(reg_final, 'models/reg_hits.joblib')
with open('models/two_stage_metrics.json','w') as f:
    json.dump({
        'auc': round(mean_auc,4),
        'recall': round(mean_rec,4),
        'rmse_log': round(mean_reg[0],4),
        'rmse_lin': int(mean_reg[1]),
        'mae': int(mean_reg[2])
    }, f, indent=2)


