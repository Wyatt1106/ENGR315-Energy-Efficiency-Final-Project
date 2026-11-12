"""ENGR 315: Question 3 -- relationship between heating and cooling load.

Run: python question3_analysis.py
Keep data/ENB2012_data.xlsx beside this script's folder as provided.
Outputs are saved in results/. Add --show to also display the plot window.
"""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Save figures reliably, including on computers without a display.
import matplotlib.pyplot as plt
from scipy.stats import linregress


def analyze(data_path, output_dir):
    """Read the data, fit cooling = slope * heating + intercept, and save outputs."""
    if not data_path.is_file():
        raise FileNotFoundError(
            f'Dataset not found: {data_path}\n'
            'Place ENB2012_data.xlsx inside the data folder next to this script.'
        )
    raw = pd.read_excel(data_path, engine='openpyxl')
    raw.columns = raw.columns.astype(str).str.strip()
    required = ['Y1', 'Y2']
    if not set(required).issubset(raw.columns):
        raise ValueError('The spreadsheet must include Y1 and Y2 column headers.')
    # Remove spreadsheet padding, but retain legitimate repeated load pairs.
    nonempty = raw.dropna(how='all').copy()
    loads = nonempty[required].apply(pd.to_numeric, errors='coerce')
    valid = np.isfinite(loads.to_numpy()).all(axis=1)
    clean = loads.loc[valid].copy()
    if len(clean) < 3 or clean['Y1'].nunique() < 2 or clean['Y2'].nunique() < 2:
        raise ValueError('At least 3 usable rows and variation in both loads are required.')
    x = clean['Y1'].to_numpy(dtype=float)
    y = clean['Y2'].to_numpy(dtype=float)
    fit = linregress(x, y)
    predicted = fit.slope * x + fit.intercept
    residual = y - predicted
    r_squared = 1 - np.sum(residual**2) / np.sum((y - np.mean(y))**2)
    rmse = np.sqrt(np.mean(residual**2))
    output_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        'ENGR 315 -- The Energizing Engineers',
        'QUESTION 3: What relationship exists between heating and cooling load?',
        '=' * 72,
        f'Spreadsheet rows read: {len(raw)}',
        f'Completely empty rows removed: {len(raw) - len(nonempty)}',
        f'Rows excluded for missing/non-numeric/non-finite Y1 or Y2: {len(nonempty) - len(clean)}',
        f'Configurations analyzed: {len(clean)}',
        f'Duplicate full records (reported, retained): {int(nonempty.duplicated().sum())}',
        '',
        f'Mean heating load: {np.mean(x):.6f}',
        f'Mean cooling load: {np.mean(y):.6f}',
        f'Pearson correlation (r): {fit.rvalue:.6f}',
        f'Slope: {fit.slope:.6f}',
        f'Intercept: {fit.intercept:.6f}',
        f'R-squared: {r_squared:.6f}',
        f'RMSE: {rmse:.6f}',
        '',
        f'Cooling load = {fit.slope:.6f} * heating load + {fit.intercept:.6f}',
        f'The fitted line explains {100 * r_squared:.2f}% of cooling-load variation in this dataset.',
        'RMSE is measured on the same configurations used to fit the line.',
        'Load units: original dataset units; the UCI variable table gives no units.',
        'These results describe simulated configurations and do not prove causation.',
    ]
    report = '\n'.join(lines) + '\n'
    print(report)
    (output_dir / 'question3_output.txt').write_text(report, encoding='utf-8')
    pd.DataFrame({
        'heating_load': x, 'cooling_load': y,
        'fitted_cooling_load': predicted, 'residual': residual,
    }).to_csv(output_dir / 'question3_predictions.csv', index=False)
    plt.rcParams.update({'font.size': 11})
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)
    axes[0].scatter(x, y, s=19, alpha=0.55, color='#3268a0', label='Simulated configurations')
    line_x = np.linspace(x.min(), x.max(), 200)
    axes[0].plot(line_x, fit.slope * line_x + fit.intercept,
                 color='#ce572c', linewidth=2.2, label='Linear fit')
    axes[0].set(title='Heating Load vs. Cooling Load',
                xlabel='Heating load (dataset units)', ylabel='Cooling load (dataset units)')
    axes[0].text(0.04, 0.96, f'r = {fit.rvalue:.4f}\nR² = {r_squared:.4f}\nRMSE = {rmse:.4f}',
                 transform=axes[0].transAxes, va='top',
                 bbox=dict(facecolor='white', alpha=0.9, edgecolor='#dddddd'))
    axes[0].legend(loc='lower right', fontsize=9)
    axes[1].scatter(predicted, residual, s=19, alpha=0.55, color='#3268a0')
    axes[1].axhline(0, color='#ce572c', linewidth=1.6)
    axes[1].set(title='Residuals vs. Fitted Cooling Load',
                xlabel='Fitted cooling load (dataset units)',
                ylabel='Actual minus fitted load (dataset units)')
    for ax in axes:
        ax.grid(alpha=0.2)
    fig.savefig(output_dir / 'question3_plots.png', dpi=220)
    plt.close(fig)
    # Render the exact printed text for a readable output image in the README.
    fig = plt.figure(figsize=(12, 8), facecolor='#f6f8fa')
    fig.text(0.035, 0.96, report, va='top', family='monospace', fontsize=10, color='#182532')
    fig.savefig(output_dir / 'question3_output.png', dpi=170, bbox_inches='tight')
    plt.close(fig)
    print(f'Files saved in: {output_dir}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--show', action='store_true', help='Open the saved plot in an image viewer.')
    args = parser.parse_args()
    base = Path(__file__).resolve().parent
    analyze(base / 'data' / 'ENB2012_data.xlsx', base / 'results')
    if args.show:
        import webbrowser
        webbrowser.open((base / 'results' / 'question3_plots.png').as_uri())


if __name__ == '__main__':
    main()
