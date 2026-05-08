# impact_report.py — Generate Plogging League Impact Report PDF
from fpdf import FPDF
import datetime
import os

class ImpactReport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(0, 80, 40)
        self.cell(0, 12, 'PLOGGING LEAGUE', align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_font('Helvetica', 'I', 11)
        self.set_text_color(80, 80, 80)
        self.cell(0, 8, 'Impact Report', align='C', new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} | Plogging League Sim', align='C')

def generate_report(stats, team_scores, hex_map_path=None):
    pdf = ImpactReport()
    pdf.add_page()
    
    # Mission statement
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(0, 60, 30)
    pdf.cell(0, 10, 'MISSION: Cleaner Streets, Healthier Communities', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    
    # Stats box
    pdf.set_fill_color(230, 255, 240)
    pdf.set_draw_color(0, 120, 60)
    pdf.rect(15, pdf.get_y(), 180, 50, style='DF')
    
    y_start = pdf.get_y() + 5
    pdf.set_xy(20, y_start)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(0, 50, 30)
    pdf.cell(170, 8, 'SESSION SUMMARY', align='C')
    
    pdf.set_xy(20, y_start + 12)
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(40, 40, 40)
    
    metrics = [
        f"Total Distance Jogged: {stats.get('distance', 0):.2f} km",
        f"Total Litter Collected: {stats.get('collected', 0)} items",
        f"Clean Points Earned: {stats.get('points', 0)} CP",
        f"City Clean Score: {stats.get('clean_score', 0):.1f}%",
        f"Simulation Day: {stats.get('day', 0)} | Hour: {stats.get('hour', 0)}"
    ]
    
    for i, metric in enumerate(metrics):
        pdf.set_xy(25, y_start + 12 + i * 7)
        pdf.cell(165, 7, f"  {metric}")
    
    pdf.set_y(y_start + 55)
    pdf.ln(5)
    
    # Team Leaderboard
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(0, 50, 30)
    pdf.cell(0, 10, 'TEAM LEADERBOARD', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    
    # Table header
    pdf.set_fill_color(0, 100, 50)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(15, 9, 'Rank', border=1, fill=True, align='C')
    pdf.cell(110, 9, 'Team', border=1, fill=True, align='C')
    pdf.cell(50, 9, 'Points (CP)', border=1, fill=True, align='C', new_x="LMARGIN", new_y="NEXT")
    
    # Table rows
    for rank, (team, points) in enumerate(team_scores, 1):
        if rank == 1:
            pdf.set_fill_color(255, 215, 0)
        elif rank == 2:
            pdf.set_fill_color(192, 192, 192)
        elif rank == 3:
            pdf.set_fill_color(205, 133, 63)
        else:
            pdf.set_fill_color(240, 240, 240)
        
        pdf.set_text_color(30, 30, 30)
        pdf.set_font('Helvetica', '', 11)
        pdf.cell(15, 8, str(rank), border=1, fill=True, align='C')
        pdf.cell(110, 8, team, border=1, fill=True, align='C')
        pdf.cell(50, 8, str(points), border=1, fill=True, align='C', new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(8)
    
    # Hex Map image (if available)
    if hex_map_path and os.path.exists(hex_map_path):
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(0, 50, 30)
        pdf.cell(0, 8, 'CITY HEX MAP', align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)
        pdf.image(hex_map_path, x=25, w=160)
        pdf.ln(5)
    
    # Environmental Impact
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(0, 50, 30)
    pdf.cell(0, 10, 'ENVIRONMENTAL IMPACT', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    collected = stats.get('collected', 0)
    co2_offset = collected * 0.05  # ~50g CO2 saved per item not landfilled
    plastic_bottles = int(collected * 0.4)
    cans = int(collected * 0.3)
    wrappers = collected - plastic_bottles - cans
    
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(50, 50, 50)
    impacts = [
        f"  Estimated CO2 Offset: {co2_offset:.2f} kg",
        f"  Plastic Bottles Diverted: {plastic_bottles}",
        f"  Aluminum Cans Recycled: {cans}",
        f"  Wrappers Removed: {wrappers}",
        f"  Equivalent trees planted: {co2_offset * 0.1:.1f}"
    ]
    for impact in impacts:
        pdf.cell(0, 7, impact, new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(5)
    
    # Thank you
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(0, 80, 40)
    pdf.cell(0, 10, 'THANK YOU FOR PLOGGING!', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, 'Every piece of litter collected makes our planet cleaner.', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, 'Share your impact: #PloggingLeague', align='C')
    
    # Save
    filename = f"plogging_impact_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

if __name__ == "__main__":
    # Test with sample data
    stats = {'distance': 3.69, 'collected': 15, 'points': 150, 'clean_score': 63.0, 'day': 0, 'hour': 4}
    team_scores = [("Red Rangers", 1806), ("Green Guardians", 2090), ("Black Knights", 1308), ("Yellow Storm", 1562)]
    report = generate_report(stats, team_scores)
    print(f"Report generated: {report}")
