import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pdfkit
from fetch_stats1 import fetch_team_data
from compare_teams1 import compare_teams
from standings_scraper1 import get_standings, analyze_standings
from datetime import datetime

# --- Configure wkhtmltopdf path ---
LOCAL_WKHTMLTOPDF = os.path.join(os.getcwd(), "bin", "wkhtmltopdf.exe")
if os.path.exists(LOCAL_WKHTMLTOPDF):
    PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf=LOCAL_WKHTMLTOPDF)
else:
    try:
        PDFKIT_CONFIG = pdfkit.configuration()  # will use system path
    except Exception:
        PDFKIT_CONFIG = None
        print("⚠ wkhtmltopdf not found. Please install it or place it in ./bin/")

# --- Report & plots directories ---
REPORTS_DIR = "reports"
PLOTS_DIR = os.path.join(REPORTS_DIR, "plots")
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

def generate_pdf_report(team1, team2, df_all, standings_df, plots):
    report_path = os.path.join(
        REPORTS_DIR,
        f"{team1.replace(' ', '_')}_vs_{team2.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    )

    html_content = f"""
    <html>
        <head>
            <title>Team Comparison Report: {team1} vs {team2}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333366; }}
                h2 {{ color: #666699; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                img {{ max-width: 100%; height: auto; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <h1>Team Comparison Report: {team1} vs {team2}</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <h2>Player Role Analysis</h2>
            {df_all.to_html(index=False)}
            
            <h2>League Standings</h2>
            {standings_df.to_html(index=False)}
            
            <h2>Visualizations</h2>
    """

    for plot_name, plot_path in plots.items():
        html_content += f"""
            <h3>{plot_name}</h3>
            <img src="{plot_path}">
        """

    html_content += """
        </body>
    </html>
    """

    temp_html = os.path.join(REPORTS_DIR, "temp_report.html")
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    if PDFKIT_CONFIG:
        try:
            pdfkit.from_file(temp_html, report_path, configuration=PDFKIT_CONFIG)
            print(f"✅ Report saved to: {report_path}")
        except Exception as e:
            print(f"❌ Error generating PDF: {e}")
    else:
        print("❌ wkhtmltopdf not configured. PDF not generated.")

    if os.path.exists(temp_html):
        os.remove(temp_html)

def save_plots(team1, team2, df_all):
    plots = {}

    guards = df_all[df_all["Pos"] == "G"]
    if not guards.empty:
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x="APG", y="PPG", hue="Team", data=guards, s=100)
        plt.title("Guard Performance: PPG vs. APG")
        plot_path = os.path.join(PLOTS_DIR, "guards_ppg_apg.png")
        plt.savefig(plot_path)
        plots["Guard Performance"] = plot_path
        plt.close()

    forwards = df_all[df_all["Role"] == "Forward"]
    if not forwards.empty:
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x="RPG", y="PPG", hue="Team", data=forwards, s=100)
        plt.title("Forward Performance: RPG vs. PPG")
        plot_path = os.path.join(PLOTS_DIR, "forwards_rpg_ppg.png")
        plt.savefig(plot_path)
        plots["Forward Performance"] = plot_path
        plt.close()

    bigs = df_all[df_all["Role"] == "Big"]
    if not bigs.empty:
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x="RPG", y="PPG", hue="Team", data=bigs, s=100)
        plt.title("Bigs Performance: RPG vs. PPG")
        plot_path = os.path.join(PLOTS_DIR, "bigs_rpg_ppg.png")
        plt.savefig(plot_path)
        plots["Bigs Performance"] = plot_path
        plt.close()

    return plots

if __name__ == "__main__":
    team_one = "Los Angeles Lakers"
    team_two = "Boston Celtics"

    df_team1 = fetch_team_data(team_one)
    df_team2 = fetch_team_data(team_two)

    if df_team1.empty or df_team2.empty:
        print("❌ Failed to fetch data for one or both teams. Check team names or try later.")
        exit(1)

    df_comparison = compare_teams(df_team1, df_team2)
    if df_comparison is None or df_comparison.empty:
        print("❌ No valid data to compare.")
        exit(1)

    df_standings = get_standings("NBA")
    if df_standings.empty:
        print("⚠ No standings data available.")
    else:
        df_analyzed_standings = analyze_standings(df_standings, "NBA")

    report_plots = save_plots(team_one, team_two, df_comparison)
    generate_pdf_report(team_one, team_two, df_comparison, df_analyzed_standings, report_plots)