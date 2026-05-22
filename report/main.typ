#import "@local/assignment:0.1.0": report

#show: report.with(
  course_code: "CSC262",
  course_name: "Artificial Intelligence",
  doc_type: "Report",
  assignment_no: "",
  assignment_title: "exRES Project Report",
  authors: (
    (name: "Ahmad Ali", reg: "FA24-BSE-012"),
    (name: "Abdul Kareem", reg: "FA24-BSE-123"),
    (name: "Muneeb Jillani Ijaz", reg: "FA24-BSE-147"),
    (name: "Muhammad Haris", reg: "FA24-BSE-177"),
  ),
  instructor: "Mr. Jawad Hassan",
  date: datetime.today().display("[month repr:long] [day], [year]"),
  show_toc: true,
)

#set page(numbering: "1")
#counter(page).update(1)

#show link: underline

= Introduction
The English Premier League is one of the most popular football leagues in the world, and predicting the standings of the season is a challenging task. The project aims to use machine learning techniques to analyze historical data and make predictions about the individual match outcomes across a season and derive the final standings of the league by aggregating predicted results. The project involves data preprocessing, feature engineering, model selection, and evaluation. The goal is to develop a model that can accurately predict the final standings of the English Premier League based on historical match data.

*exRES* is a machine learning project to predict the standings of the 2024/2025 season of the English Premier League using historical data. exRES is short for Expected Result and takes inspiration from other football terms like Expected Goals (xG) and Expected Assists (xA).
// Problem Statement
= Dataset
This project uses the #link("https://github.com/xgabora/Club-Football-Match-Data-2000-2025/")[Club Football Match Data 2000-2025] dataset available on GitHub. The dataset contains match data from of 25 years from many football leagues, including the English Premier League.
The dataset is in the form of a `csv` file with over 230K records making it one of the largest free football datasets available. It contains full match data starting from 2000/01 and till the latest complete season (2024/25).

== Citation
*Author*: Adam Gábor \
*ORCID*: https://orcid.org/0009-0001-9252-5976 \
*Affiliation*: Faculty of Informatics and Information Technologies, Slovak University of Technology in Bratislava \
*Year*: 2025 \

= Data Preprocessing
The dataset was preprocessed to extract the required data for the English Premier League, filtering missing values and normalizing numerical features. The latest, complete season (2024/25) in the dataset was used as the validation set for the model while the rest was used for training.

== Shape of the Dataset
The original dataset contained 230,557 rows and 48 columns.
Here's a list of the columns in the dataset categorized into different types:
// - Match Metadata: `Division`, `MatchDate`, `MatchTime`, `HomeTeam`, `AwayTeam`
// - Predictive Features: `HomeElo`, `AwayElo`, `Form3Home`, `Form5Home`, `Form3Away`, `Form5Away`
// - Match Result: `FTHome`, `FTAway`, `FTResult`, `HTHome`, `HTAway`, `HTResult`
// - Match Statistics: `HomeShots`, `AwayShots`, `HomeTarget`, `AwayTarget`, `HomeFouls`, `AwayFouls`, `HomeCorners`, `AwayCorners`, `HomeYellow`, `AwayYellow`, `HomeRed`, `AwayRed`
// - Betting Odds: `OddHome`, `OddDraw`, `OddAway`, `MaxHome`, `MaxDraw`, `MaxAway`, `Over25`, `Under25`, `MaxOver25`, `MaxUnder25`, `HandiSize`, `HandiHome`, `HandiAway`, `C_LTH`, `C_LTA`, `C_VHD`, `C_VAD`, `C_HTB`, `C_PHB`

#table(
  columns: 3,
  align: (auto, auto, auto),
  table.header(
    [*Category*],
    table.cell(colspan: 2)[*Columns*],
  ),
  // table.header[*Category*][table.cell(colspan: 2)][*Column Name*],
  table.cell(rowspan: 3, align: left + horizon)[Match Metadata],
  [Division], [HomeTeam],
  [MatchTime], [AwayTeam],
  [MatchDate], [],
  table.cell(rowspan: 3, align: left + horizon)[Predictive Features],
  [HomeElo], [AwayElo],
  [Form3Home], [Form5Home],
  [Form3Away], [Form5Away],
  table.cell(rowspan: 3, align: left + horizon)[Match Result],
  [FTHome], [HTHome],
  [FTAway], [HTAway],
  [FTResult], [HTResult],
  table.cell(rowspan: 6, align: left + horizon)[Match Statistics],
  [HomeShots], [AwayShots],
  [HomeTarget], [AwayTarget],
  [HomeFouls], [AwayFouls],
  [HomeCorners], [AwayCorners],
  [HomeYellow], [AwayYellow],
  [HomeRed], [AwayRed],
  table.cell(rowspan: 10, align: left + horizon)[Betting Odds],
  [OddHome], [OddDraw],
  [OddAway], [MaxHome],
  [MaxDraw], [MaxAway],
  [Over25], [Under25],
  [MaxOver25], [MaxUnder25],
  [HandiSize], [HandiHome],
  [HandiAway], [C_LTH],
  [C_LTA], [C_VHD],
  [C_VAD], [C_HTB],
  [C_PHB], [],
)



// #table(
//   columns: 2,
//   align: (left, left),
//   table.header[*Category*][*Column Name*],
//   table.cell(rowspan: 5, align: left + horizon)[Match Metadata],
//   [Division], [MatchDate], [MatchTime], [HomeTeam], [AwayTeam],
//   table.cell(rowspan: 6, align: left + horizon)[Predictive Features],
//   [HomeElo], [AwayElo], [Form3Home], [Form5Home], [Form3Away], [Form5Away],
//   table.cell(rowspan: 6, align: left + horizon)[Match Result],
//   [FTHome], [FTAway], [FTResult], [HTHome], [HTAway], [HTResult],
//   table.cell(rowspan: 12, align: left + horizon)[Match Statistics],
//   [HomeShots], [AwayShots], [HomeTarget], [AwayTarget], [HomeFouls], [AwayFouls],
//   [HomeCorners], [AwayCorners], [HomeYellow], [AwayYellow], [HomeRed], [AwayRed],
//   table.cell(rowspan: 19, align: left + horizon)[Betting Odds],
//   [OddHome], [OddDraw], [OddAway], [MaxHome], [MaxDraw], [MaxAway],
//   [Over25], [Under25], [MaxOver25], [MaxUnder25], [HandiSize], [HandiHome], [HandiAway],
//   [C_LTH], [C_LTA], [C_VHD], [C_VAD], [C_HTB], [C_PHB],
// )

// (230557, 48)





== Filtering the Data

The dataset contained data from many football leagues all around the world. The first step was to filter the data to include only matches from the English Premier League. This was done by selecting records matching the `Division` column with the value "E0".

```py
epl = matches[matches["Division"] == "E0"].copy()
```

The first two seasons in the dataset (2000/01 and 2001/02) had missing values betting odds making it impossible to compute normalized implied probablity features which are important for the model, so they were removed from the dataset.

Many columns were dropped from the dataset as they were not relevant for the model. These include match metadata, match statistics, and some betting odds.

== Validation Set
The latest complete season in the dataset (2024/25) was used as the validation set for the model. It was separated from the training data to evaluate the model's performance on unseen data. It has 380 matches which is the standard number of matches in a Premier League season (20 teams playing 38 matches each). No data from this season was used during training to ensure a fair evaluation of the model.

== Computing Derived Features
Some features were derived from the existing data to provide more information to the model. These include:
- `EloDifference`: Computed from the difference of `HomeElo` and `AwayElo`.
- `Form3Difference`: Computed from the difference of `Form3Home` and `Form3Away`.
- `Form5Difference`: Computed from the difference of `Form5Home` and `Form5Away`.
- `NormProbHome`, `NormProbDraw`, `NormProbAway`: Normalized probabilities computed from the betting odds as the raw implied probabilities from the odds do not sum to 1 due to the bookmaker's margin. Normalization was done by dividing each implied probability by the sum of all three implied probabilities.

== Final Dataset
After preprocessing, these two datasets were generated:
- Training Set: (8270, 16)
- Validation Set: (380, 16)

The following columns are in the final dataset:
+ `MatchDate`
+ `HomeTeam`
+ `AwayTeam`
+ `HomeElo`
+ `AwayElo`
+ `EloDifference`
+ `Form3Home`
+ `Form3Away`
+ `Form3Difference`
+ `Form5Home`
+ `Form5Away`
+ `Form5Difference`
+ `NormProbHome`
+ `NormProbDraw`
+ `NormProbAway`
+ `FTResult`

= Model

Match outcome prediction is framed as a multiclass classification problem. Each match is assigned one of three labels: Home Win (H), Away Win (A), or Draw (D). Three models of increasing complexity are trained and evaluated — Logistic Regression, Random Forest, and XGBoost — each trained under two feature set configurations. This progressive approach allows the contribution of individual feature groups to be isolated and compared.

== Target Encoding

The target variable `FTResult` is a categorical string column containing the values `H`, `D`, and `A`. Scikit-learn's `LabelEncoder` was used to map these to integer labels prior to training. The encoder sorts classes alphabetically, producing the following mapping:

#table(
  columns: 2,
  align: (left, center),
  table.header([*Label*], [*Encoded Value*]),
  [`A` — Away Win], [0],
  [`D` — Draw], [1],
  [`H` — Home Win], [2],
)

The encoder was fitted exclusively on the training set and applied to the validation set using the same mapping to prevent any information from the validation season influencing the encoding.

== Feature Sets

Two feature sets were defined to measure the isolated contribution of betting market data to predictive performance.

*Feature Set A — No Odds* contains only football-derived features: Elo ratings, derived Elo difference, rolling form over three and five matches, and derived form differences, alongside one-hot encoded home and away team identities. This set answers the question of how well football statistics alone can predict outcomes.

*Feature Set B — With Odds* extends Feature Set A with three normalised implied probability features: `NormProbHome`, `NormProbDraw`, and `NormProbAway`. These encode the pre-match betting market's assessment of each outcome. This set measures how much predictive power the market contributes beyond raw football statistics.

All three models were trained independently under both feature sets, producing six trained models in total.

== Preprocessing Pipeline

A separate preprocessing pipeline was constructed for each model family using scikit-learn's `Pipeline` and `ColumnTransformer` abstractions. This guarantees that all transformations are fitted on training data only and applied consistently to the validation set, preventing preprocessing leakage.

=== Categorical Features

The `HomeTeam` and `AwayTeam` columns were encoded using `OneHotEncoder`. The encoder was configured with `handle_unknown="ignore"`, which silently zeroes out the encoded vector for any team name not seen during training. This is necessary because the 2024/25 season included promoted clubs with no representation in the training data.

For Logistic Regression, `drop="first"` was applied to remove one redundant dummy column per categorical feature, avoiding the dummy variable trap in a linear model. For tree-based models, no column was dropped, as decision trees are invariant to linear dependence between features.

=== Numeric Features

A `SimpleImputer` with median strategy was applied to all numeric features. Two matches in the validation set had missing Elo values due to a promoted club lacking a recorded rating snapshot for the season's opening fixtures. The median Elo from the training set was used to fill these values.

For Logistic Regression, imputation was followed by `StandardScaler` to standardise all numeric features to zero mean and unit variance. Logistic Regression is sensitive to feature scale, and without standardisation, features with larger ranges would disproportionately influence the decision boundary. Tree-based models are scale-invariant and received imputed features without standardisation.

== Logistic Regression

Logistic Regression is a linear probabilistic classifier. For multiclass problems, the multinomial (softmax) formulation is used, which models the probability of each class jointly rather than through a series of binary decisions.

Given a feature vector $bold(x)$ and a weight matrix $bold(W)$, the probability assigned to class $k$ is:

$ P(y = k | bold(x)) = frac(e^(bold(w)_k^top bold(x)), sum_(j=1)^(K) e^(bold(w)_j^top bold(x))) $

where $K = 3$ is the number of classes and $bold(w)_k$ is the weight vector for class $k$. The model is trained by minimising the cross-entropy loss with L2 regularisation:

$ cal(L) = - sum_(i=1)^(N) log P(y_i | bold(x)_i) + frac(lambda, 2) ||bold(W)||_F^2 $

The regularisation strength is controlled by the parameter $C = 1/lambda$. A value of $C = 1.0$ was used, applying moderate regularisation to reduce overfitting without heavily constraining the model.

Logistic Regression serves as the interpretable baseline in this study. Despite its simplicity, it is known to perform competitively on well-engineered tabular features and provides a lower-bound reference against which ensemble methods are compared.

#table(
  columns: 2,
  align: (left, left),
  table.header([*Hyperparameter*], [*Value*]),
  [`C` (inverse regularisation strength)], [`1.0`],
  [`max_iter`], [`1000`],
  [`random_state`], [`42`],
)

== Random Forest

Random Forest is an ensemble learning method that constructs a large number of decision trees during training and aggregates their predictions. Each tree is trained on a bootstrap sample of the training data (sampling with replacement), and at each split node, only a random subset of features is considered. This combination of bagging and random feature selection decorrelates the individual trees, reducing variance and improving generalisation over a single decision tree.

For a classification task, the final prediction is determined by majority vote across all trees:

$ hat(y) = "mode" { h_1(bold(x)), h_2(bold(x)), dots, h_T(bold(x)) } $

where $T$ is the number of trees and $h_t$ is the prediction of the $t$-th tree. Probability estimates are obtained by averaging the per-class vote proportions across all trees.

Random Forest handles non-linear feature interactions naturally without requiring feature scaling, making it well suited to the mixed numerical and categorical structure of the feature set. The `min_samples_leaf=5` constraint requires each leaf node to contain at least five training samples, providing a form of regularisation that prevents individual trees from memorising noise.

#table(
  columns: 2,
  align: (left, left),
  table.header([*Hyperparameter*], [*Value*]),
  [`n_estimators`], [`300`],
  [`min_samples_leaf`], [`5`],
  [`n_jobs`], [`-1` (all available cores)],
  [`random_state`], [`42`],
)

== XGBoost

XGBoost (Extreme Gradient Boosting) is a gradient boosted decision tree framework. Unlike Random Forest, which builds trees independently in parallel, gradient boosting constructs trees sequentially. Each new tree is trained to correct the residual errors left by the ensemble of all previous trees. This makes boosting particularly effective at capturing complex non-linear patterns in structured tabular data.

The objective function optimised at each boosting round is:

$ cal(L)^((t)) = sum_(i=1)^N l(y_i, hat(y)_i^((t-1)) + f_t(bold(x)_i)) + Omega(f_t) $

where $f_t$ is the tree added at round $t$, $l$ is the per-sample loss, and $Omega$ is a regularisation term penalising tree complexity:

$ Omega(f) = gamma T + frac(1, 2) lambda ||bold(w)||^2 $

Here $T$ is the number of leaf nodes and $bold(w)$ are the leaf weights. This explicit regularisation distinguishes XGBoost from classical gradient boosting and helps control overfitting.

For the three-class prediction task, the `multi:softprob` objective was used, which produces calibrated probability estimates for all three outcome classes simultaneously. The learning rate was set conservatively at `0.05` to allow more boosting rounds without overfitting, and subsampling was applied at both the row (`subsample=0.8`) and feature (`colsample_bytree=0.8`) levels to further regularise the model.

#table(
  columns: 2,
  align: (left, left),
  table.header([*Hyperparameter*], [*Value*]),
  [`n_estimators`], [`300`],
  [`max_depth`], [`4`],
  [`learning_rate`], [`0.05`],
  [`subsample`], [`0.8`],
  [`colsample_bytree`], [`0.8`],
  [`objective`], [`multi:softprob`],
  [`num_class`], [`3`],
  [`random_state`], [`42`],
)

XGBoost is the most expressive of the three models and is expected to achieve the strongest performance on tabular data. It handles sparse one-hot encoded inputs efficiently and does not require feature scaling, making it a natural fit for the combined categorical and numerical feature structure of this dataset.

= Training & Testing

== Temporal Validation Strategy

A strict chronological split was used to separate training and validation data. All matches from the 2002/03 season through the 2023/24 season were used for training, and the complete 2024/25 season was reserved exclusively for validation. No data from the validation season was used at any stage of training, preprocessing, or feature computation.

This approach is essential for sports prediction tasks. A random train/test split — the default in most machine learning workflows — would allow future match results to appear in the training set, artificially inflating performance metrics. The chronological split simulates a realistic forecasting scenario: the model is trained on everything it could have known before the 2024/25 season began, and evaluated on a future season it has never seen.

#table(
  columns: 3,
  align: (left, center, center),
  table.header([*Split*], [*Seasons*], [*Matches*]),
  [Training], [2002/03 – 2023/24], [8,270],
  [Validation], [2024/25], [380],
)

== Class Distribution

The target variable exhibits class imbalance across both splits. Home wins are the most frequent outcome, draws the least frequent.

#table(
  columns: 4,
  align: (left, center, center, center),
  table.header([*Split*], [*Home Win (H)*], [*Away Win (A)*], [*Draw (D)*]),
  [Training], [3,806 (46.0%)], [2,441 (29.5%)], [2,023 (24.5%)],
  [Validation], [155 (40.8%)], [132 (34.7%)], [93 (24.5%)],
)

The draw class is consistently underrepresented in both splits. This imbalance has significant consequences for model behaviour, discussed further in Section 6.

== Training Process

Each of the six model configurations — three model architectures across two feature sets — was trained independently on the full training set. All preprocessing transformations (one-hot encoding, imputation, scaling) were fitted on training data only and applied to the validation set without refitting. This is enforced by wrapping all transformations inside scikit-learn `Pipeline` objects, which prevent any information from the validation set influencing the fitted transformers.

All models used fixed random seeds (`random_state=42`) to ensure fully reproducible results. No cross-validation was performed during training; the temporal structure of the data makes standard $k$-fold cross-validation inappropriate, as it would mix future seasons into past training folds.

== Evaluation Metrics

Four metrics were used to evaluate each model:

*Accuracy* measures the proportion of correctly predicted outcomes across all 380 validation matches. While intuitive, accuracy alone is insufficient given class imbalance — a model predicting only home wins achieves 40.8% accuracy without learning any meaningful patterns.

*Macro F1-Score* computes the F1-score for each class independently and averages them with equal weight. This penalises models that ignore minority classes (particularly draws) and is a more honest measure of overall performance under imbalance.

*Log-Loss* evaluates the quality of predicted probabilities rather than hard class assignments. Lower log-loss indicates that the model assigns higher probability to the correct outcome. This metric is particularly important when comparing against the bookmaker baseline, which produces well-calibrated probability estimates.

*Classification Report* provides per-class precision, recall, and F1-score, making it possible to identify which outcome types the model handles well and which it fails on.

== Baselines

Two baselines were established to contextualise model performance.

*Always Home Win* predicts a home win for every match regardless of features. Given EPL home win rates, this achieves approximately 40.8% accuracy on the validation set. Any model failing to exceed this is not learning useful signal.

*Bookmaker Baseline* predicts whichever outcome carries the highest normalised implied probability. This represents the upper performance bound for the with-odds feature set — bookmakers employ highly optimised prediction systems, and a machine learning model adding odds as features must beat this baseline to claim it is extracting information beyond what the market already knows.

= Results & Evaluation

== Summary of Results

The table below summarises the performance of all six models alongside the two baselines on the 2024/25 validation season.

#table(
  columns: 4,
  align: (left, center, center, center),
  table.header([*Model*], [*Accuracy*], [*Macro F1*], [*Log-Loss*]),
  [Always Home Win (baseline)], [0.4079], [0.1931], [—],
  [Bookmaker Best Prob (baseline)], [0.5421], [0.4063], [0.9706],
  [Logistic Regression — No Odds], [0.5000], [0.3840], [1.0167],
  [Random Forest — No Odds], [0.5000], [0.3758], [1.0010],
  [XGBoost — No Odds], [0.4895], [0.3702], [1.0150],
  [Logistic Regression — With Odds], [0.5237], [0.4058], [0.9838],
  [Random Forest — With Odds], [0.5316], [0.4087], [0.9786],
  [*XGBoost — With Odds*], [*0.5395*], [*0.4203*], [*0.9809*],
)

== Effect of Betting Odds Features

Adding the normalised implied probability features (Feature Set B) consistently improved performance across all three models. Accuracy improved by 2.4–4.0 percentage points depending on the model, and macro F1 improved by 0.03–0.05. This confirms that betting market odds encode meaningful predictive information beyond what Elo ratings and rolling form capture alone.

However, no model in Feature Set B surpassed the bookmaker baseline. The best model, XGBoost with odds, achieved 53.95% accuracy against the bookmaker's 54.21% — a gap of 0.26 percentage points. On log-loss, the bookmaker (0.9706) outperformed XGBoost (0.9809), indicating that the bookmaker's probabilities are better calibrated than the model's. This is expected: bookmakers continuously update their odds using far richer information including injuries, squad rotation, and live market sentiment, none of which are available in the feature set.

The no-odds models remain meaningful in isolation. Achieving 50% accuracy without any market information — against a home-win baseline of 40.8% — demonstrates that Elo and form carry genuine predictive signal.

== Model Comparison

XGBoost was the strongest performer in both feature sets, though the margins over Logistic Regression were small. In the no-odds configuration, Logistic Regression and Random Forest matched each other exactly at 50.0% accuracy, with XGBoost marginally behind at 48.95%. This is consistent with known behaviour on well-engineered tabular features where linear models are competitive. The added expressiveness of tree ensembles provides a clearer advantage once odds features are included.

== Draw Prediction

Draw prediction was consistently poor across all models. The table below shows per-class recall for XGBoost under both feature sets.

#table(
  columns: 4,
  align: (left, center, center, center),
  table.header([*Model*], [*Recall (A)*], [*Recall (D)*], [*Recall (H)*]),
  [XGBoost — No Odds], [0.44], [0.01], [0.82],
  [XGBoost — With Odds], [0.56], [0.02], [0.83],
  [Bookmaker Baseline], [0.58], [0.00], [0.84],
)

Draw recall was effectively zero across all models, including the bookmaker baseline, which predicted no draws whatsoever. This is not a failure specific to this implementation — draw prediction is a well-documented challenge in football analytics. Draws are low-frequency, low-signal events that depend on factors (tight tactical setups, late equalisers, deliberate game management) not captured by pre-match statistics. Models under class imbalance naturally minimise loss by avoiding minority class predictions.

== Confusion Matrices

The confusion matrices for the best model under each feature set are shown below. Rows represent actual outcomes, columns represent predicted outcomes, with classes ordered A, D, H.

*XGBoost — No Odds*

#table(
  columns: 4,
  align: (center, center, center, center),
  table.header([], [*Pred A*], [*Pred D*], [*Pred H*]),
  [*Act A*], [58], [7], [67],
  [*Act D*], [30], [1], [62],
  [*Act H*], [25], [3], [127],
)

*XGBoost — With Odds*

#table(
  columns: 4,
  align: (center, center, center, center),
  table.header([], [*Pred A*], [*Pred D*], [*Pred H*]),
  [*Act A*], [74], [5], [53],
  [*Act D*], [32], [2], [59],
  [*Act H*], [21], [5], [129],
)

Adding odds features notably improves away win detection — correct away predictions increase from 58 to 74. The draw column remains near-empty in both configurations. The model with odds also reduces false home predictions for actual away results (67 → 53), indicating that implied probabilities help correct the model's home-win bias.

== Predicted League Standings

Using the best-performing model (XGBoost — With Odds), predictions were generated for all 380 matches of the 2024/25 season. Points were awarded according to standard rules (3 for a win, 1 for a draw, 0 for a loss) and teams were ranked by total predicted points.

#table(
  columns: 5,
  align: (center, left, center, center, center),
  table.header([*Actual Pos*], [*Team*], [*Actual Pts*], [*Pred Pos*], [*Pred Pts*]),
  [1], [Liverpool], [84], [2], [105],
  [2], [Arsenal], [74], [3], [103],
  [3], [Man City], [71], [1], [105],
  [4], [Chelsea], [69], [5], [89],
  [5], [Aston Villa], [66], [7], [65],
  [6], [Newcastle], [66], [4], [89],
  [7], [Nott'm Forest], [65], [11], [55],
  [8], [Brighton], [61], [9], [59],
  [9], [Brentford], [56], [12], [54],
  [10], [Bournemouth], [56], [8], [60],
  [11], [Fulham], [54], [13], [54],
  [12], [Crystal Palace], [53], [14], [48],
  [13], [Everton], [48], [16], [27],
  [14], [West Ham], [43], [15], [34],
  [15], [Man United], [42], [6], [66],
  [16], [Wolves], [42], [17], [21],
  [17], [Tottenham], [38], [10], [57],
  [18], [Leicester], [25], [19], [13],
  [19], [Ipswich], [22], [20], [8],
  [20], [Southampton], [12], [18], [16],
)

Predicted points are uniformly inflated relative to actual points. This is a direct consequence of the model's near-zero draw recall — draws award one point to each team, whereas predicted wins award three. Since the model converts most draws into home or away wins, total points across the table are systematically overstated. This does not affect rank ordering and is a known limitation of outcome-level prediction without margin estimation.

The Spearman rank correlation between predicted and actual final positions was *0.8496* ($p < 0.001$), indicating a strong positive relationship between the model's predicted season order and the true final standings.

== Notable Prediction Errors

Two clubs showed substantial positional errors.

*Manchester United* were predicted to finish 6th but finished 15th, a difference of nine positions. The model's Elo and historical team encoding rated United as a top-six club — which they were for the preceding decade. The 2024/25 season saw a significant underperformance relative to historical expectations, including a mid-season managerial change that the model had no mechanism to anticipate. This is a fundamental limitation of pre-season static models: they cannot capture within-season structural deterioration.

*Tottenham Hotspur* were predicted 10th but finished 17th, a difference of seven positions. A similar effect applies — Tottenham's historical Elo overstates their 2024/25 competitiveness.

*Nottingham Forest* were predicted 11th but finished 7th, the third largest error in the opposite direction. Forest overperformed relative to their historical standing, a result the model could not anticipate.

== Summary of Findings

The following conclusions can be drawn from the experimental results:

+ Betting market odds are the dominant predictive signal. Adding normalised implied probabilities improved accuracy by 3–4 percentage points across all models.
+ Football statistics alone carry genuine signal. No-odds models achieved 50% accuracy against a 40.8% home-win baseline, confirming that Elo and form are informative features.
+ No machine learning model surpassed the bookmaker baseline, which achieved 54.21% accuracy and the lowest log-loss. The best model (XGBoost with odds) reached 53.95% accuracy — a gap of 0.26 percentage points.
+ Draw prediction is effectively unsolved. No model exceeded 2% draw recall. This is consistent with the broader literature on football prediction and reflects the inherently low-signal nature of drawn matches.
+ The model successfully reconstructed the broad shape of the 2024/25 season, achieving a Spearman rank correlation of 0.85 between predicted and actual final standings. All three clubs that were ultimately relegated appeared in the bottom four of the predicted table.

