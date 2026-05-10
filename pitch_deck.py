from fpdf import FPDF

class PitchDeck(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(0, 80, 40)
        self.cell(0, 10, 'PLOGGING LEAGUE BERLIN', align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_font('Helvetica', '', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, 'Samsung Solve for Tomorrow -- Germany 2025', align='C', new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, 'Gerson Japhet Fumbuka | ephatatalithacumi@gmail.com | INTI International University', align='C')

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(0, 100, 50)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(0, 150, 80)
        self.line(10, self.get_y(), 120, self.get_y())
        self.ln(4)

    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 6, text)
        self.ln(2)

pdf = PitchDeck()
pdf.add_page()

# Slide 1: Title
pdf.set_font('Helvetica', 'B', 24)
pdf.set_text_color(0, 60, 30)
pdf.cell(0, 40, '', new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 15, 'PLOGGING LEAGUE BERLIN', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.set_font('Helvetica', '', 14)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 10, 'AI-Powered Environmental Sports Platform', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.ln(10)
pdf.set_font('Helvetica', '', 11)
pdf.cell(0, 8, 'Samsung Solve for Tomorrow -- Germany 2025', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, 'Gerson Japhet Fumbuka, PhD Candidate', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, 'INTI International University & Colleges, Malaysia', align='C', new_x="LMARGIN", new_y="NEXT")

# Slide 2: Idea & Challenge
pdf.add_page()
pdf.section_title('1. IDEA & CHALLENGE')
pdf.body_text('''IDEA: Plogging League Berlin transforms city cleanup into a gamified, AI-driven sport where runners compete in teams across 12 real Berlin districts, earning points for collecting litter.

CHALLENGE: Urban litter costs Berlin over 50 million euros annually in cleanup operations. Citizen engagement in environmental action remains low because individual impact is invisible and unrewarding. Existing cleanup initiatives lack real-time feedback, persistent recognition, and accessibility for non-German speakers and non-readers.

Berlin generates over 14,000 tons of street litter yearly. Current cleanup relies on municipal services with limited citizen participation. Plogging League makes environmental action visible, competitive, and accessible to all.''')

# Slide 3: Solution & Technology
pdf.add_page()
pdf.section_title('2. SOLUTION & TECHNOLOGY')
pdf.body_text('''PLATFORM FEATURES:
- Agent-Based Simulation: 60 AI ploggers navigate Berlin's 12 Bezirke using motivational AI algorithms
- Real-Time Hex Mapping: Berlin districts visualized as dynamic hex tiles that rise with litter and sink when cleaned
- Multi-Agent Animation: 4 team-colored ploggers with synchronized sound effects (footsteps, dings, celebrations)
- Persistent Global Leaderboard: SQLite database storing all-time scores across sessions
- PDF Impact Reports: Downloadable environmental summaries with CO2 offset calculations
- Multilingual Audio Instructions: 5 languages (English, German, Swahili, Swedish, Korean) for accessibility
- Cloud Deployment: Streamlit Cloud with automated GitHub CI/CD pipelines

TECHNOLOGY STACK:
Python (Streamlit, NumPy, Pandas, Matplotlib) | MoviePy + FFmpeg for AI animation | SQLite for persistence | gTTS for text-to-speech | Git/GitHub for version control | Plotly for geospatial visualization''')

# Slide 4: Impact & Value
pdf.add_page()
pdf.section_title('3. IMPACT & VALUE')
pdf.body_text('''ENVIRONMENTAL IMPACT:
- Gamifies litter collection across Berlin's 12 districts
- Makes cleanup data visible through real-time hex maps
- Tracks CO2 offset and environmental metrics per session
- Encourages consistent environmental action through persistent scoring

SOCIAL IMPACT:
- 5-language audio instructions lower barriers for immigrants, elderly, and non-readers
- Team competition builds community engagement
- Combines fitness (plogging) with environmental stewardship
- Free and accessible via any web browser

EDUCATIONAL IMPACT:
- Visual hex maps show real-time environmental state
- Downloadable PDF reports with detailed metrics
- Demonstrates AI/ML concepts through accessible simulation

SCALABILITY:
- Platform can deploy for any city worldwide by changing district configurations
- Proven model working for Berlin, adaptable to Hamburg, Munich, Seoul, Nairobi
- Low infrastructure cost (cloud-hosted, zero server maintenance)''')

# Slide 5: Feasibility & Outlook
pdf.add_page()
pdf.section_title('4. FEASIBILITY & OUTLOOK')
pdf.body_text('''CURRENT STAGE: Working prototype deployed on Streamlit Cloud
- Live at: https://plogging-league-sim-gj2vuwg38m92hzffkn4nrp.streamlit.app
- 12 real Berlin districts mapped
- Multi-agent AI simulation operational
- Persistent database with global leaderboard
- 5-language audio instructions
- AI-generated plogging animation with sound effects
- Downloadable impact reports

FUTURE ROADMAP:
Phase 1 (3 months): Mobile-responsive layout, real GPS integration
Phase 2 (6 months): Partnership with Berliner Stadtreinigung (BSR) for verified cleanup data
Phase 3 (12 months): Expansion to all 16 German federal states
Phase 4 (24 months): Global city deployment, corporate CSR partnerships

REVENUE MODEL:
- Freemium for individuals and community teams
- B2B subscriptions for corporate CSR programs
- Municipal contracts for city data dashboards
- Ethical sponsorships from outdoor and sustainability brands''')

# Slide 6: Team
pdf.add_page()
pdf.section_title('5. TEAM')
pdf.body_text('''PROJECT LEAD:
Gerson Japhet Fumbuka
PhD Candidate -- INTI International University & Colleges, Nilai, Malaysia
Contact: ephatatalithacumi@gmail.com

BACKGROUND:
- Advanced programming skills (Python, Streamlit, SQLite, AI/ML)
- Experience in agent-based modeling and simulation
- Expertise in environmental data visualization
- Multilingual communicator (English, Swahili, German)

ACKNOWLEDGMENTS:
- Built with open-source technologies
- Deployed on Streamlit Cloud (free tier)
- Berlin district data from OpenStreetMap
- Inspired by the Swedish plogging movement''')

# Slide 7: Thank You
pdf.add_page()
pdf.set_font('Helvetica', 'B', 22)
pdf.set_text_color(0, 80, 40)
pdf.cell(0, 60, '', new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 15, 'THANK YOU', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.ln(10)
pdf.set_font('Helvetica', '', 13)
pdf.set_text_color(60, 60, 60)
pdf.cell(0, 10, 'Plogging League Berlin', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 10, 'Sweat for the planet. Run, collect, connect.', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.ln(15)
pdf.set_font('Helvetica', '', 10)
pdf.cell(0, 8, 'Live Demo: https://plogging-league-sim-gj2vuwg38m92hzffkn4nrp.streamlit.app', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, 'Contact: ephatatalithacumi@gmail.com', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, 'INTI International University & Colleges, Malaysia', align='C')

pdf.output('Samsung_SFT_Plogging_League_Berlin.pdf')
print("Pitch deck generated: Samsung_SFT_Plogging_League_Berlin.pdf")
