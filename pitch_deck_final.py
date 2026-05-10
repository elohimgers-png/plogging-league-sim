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
pdf.cell(0, 10, 'World-Class Health, Fitness & Environmental Platform', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.ln(10)
pdf.set_font('Helvetica', '', 11)
pdf.cell(0, 8, 'Samsung Solve for Tomorrow -- Germany 2025', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, 'Gerson Japhet Fumbuka, PhD Candidate', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, 'INTI International University & Colleges, Malaysia', align='C', new_x="LMARGIN", new_y="NEXT")

# Slide 2: Idea & Challenge
pdf.add_page()
pdf.section_title('1. IDEA & CHALLENGE')
pdf.body_text('''IDEA: Plogging League Berlin transforms city cleanup into a gamified, AI-driven sport where runners compete in teams across 12 real Berlin districts, earning points for collecting litter. Beyond environmental action, the platform integrates comprehensive health features: preventive check-ins, mental wellbeing tracking, chronic condition support, physician alerts, and outdoor gym integration.

CHALLENGE: Urban litter costs Berlin over 50 million euros annually. Citizen engagement in environmental action remains low because individual impact is invisible. Existing health apps are disconnected from environmental action. Vulnerable populations -- elderly, immigrants, chronic condition patients -- lack accessible tools that combine fitness, health monitoring, and community connection.

Berlin generates over 14,000 tons of street litter yearly. 30% of German adults have hypertension. 6.7 million Germans have diabetes. Loneliness is a growing public health crisis. Plogging League Berlin addresses ALL of these simultaneously.''')

# Slide 3: Solution & Technology
pdf.add_page()
pdf.section_title('2. SOLUTION & TECHNOLOGY')
pdf.body_text('''PLATFORM FEATURES:

SIMULATION & GAMIFICATION:
- Agent-based simulation with 60 AI ploggers across 12 real Berlin districts
- Real-time hex tile mapping showing litter density per district
- 4-team competition system (Red Rangers, Green Guardians, Black Knights, Yellow Storm)
- Multi-agent AI animation with synchronized sound effects
- Persistent global leaderboard using SQLite database

HEALTH HUB:
- Preventive check-ins: Balance test, Flexibility test, Reaction time test
- Mood Mapper: Before/after exercise mood tracking with Berlin park suggestions
- Chronic Condition Support: Tailored plans for diabetes, hypertension, and rehabilitation
- Physician Alert System: Automated health summaries sent to doctors with user consent
- Outdoor Gym Stations: 12 real Berlin fitness parks with exercise logging

ACCESSIBILITY:
- 5-language audio instructions (English, German, Swahili, Swedish, Korean)
- Custom SVG plogger logo and responsive mobile layout
- PDF impact reports with environmental metrics
- All data anonymized and shared only with explicit consent

TECHNOLOGY STACK:
Python (Streamlit, NumPy, Pandas, Matplotlib) | MoviePy + FFmpeg for AI animation | SQLite for persistence | gTTS for multilingual text-to-speech | Git/GitHub for CI/CD | Streamlit Cloud deployment''')

# Slide 4: Impact & Value
pdf.add_page()
pdf.section_title('3. IMPACT & VALUE')
pdf.body_text('''ENVIRONMENTAL IMPACT:
- Gamifies litter collection across Berlin's 12 Bezirke
- Real-time hex map visualization of city cleanliness
- CO2 offset tracking per session
- Encourages consistent environmental action through persistent scoring

HEALTH IMPACT:
- Preventive health screening: balance, flexibility, reaction time
- Mental wellbeing: mood tracking with community connection suggestions
- Chronic disease management: tailored exercise plans for diabetes, hypertension, rehab
- Physician connectivity: automated health summaries for early intervention
- Outdoor fitness: 12 real Berlin gym stations integrated into plogging routes

SOCIAL IMPACT:
- 5-language audio instructions break barriers for immigrants, elderly, non-readers
- Team competition builds community engagement
- Walking group connections combat loneliness
- Combines fitness with environmental stewardship
- Free and accessible via any web browser

SCALABILITY:
- Platform can deploy for any city worldwide by changing district configurations
- Proven model for Berlin, adaptable to Hamburg, Munich, Seoul, Nairobi
- Low infrastructure cost (cloud-hosted, zero server maintenance)
- Open-source ready for community contributions''')

# Slide 5: Feasibility & Outlook
pdf.add_page()
pdf.section_title('4. FEASIBILITY & OUTLOOK')
pdf.body_text('''CURRENT STAGE: Fully functional prototype deployed on Streamlit Cloud
- Live at: https://plogging-league-sim-gj2vuwg38m92hzffkn4nrp.streamlit.app
- 12 real Berlin districts mapped
- Multi-agent AI simulation operational
- Complete health ecosystem (preventive, mental, chronic, physician alerts, outdoor gym)
- 5-language audio instructions
- AI-generated plogging animation with sound effects
- Downloadable impact reports
- Persistent global database with cross-session leaderboard

FUTURE ROADMAP:
Phase 1 (3 months): Real GPS integration, mobile app, partnership with Berliner Stadtreinigung (BSR)
Phase 2 (6 months): Wearable integration (Fitbit, Apple Watch), real-time health data streaming
Phase 3 (12 months): Expansion to all 16 German federal states, corporate wellness partnerships
Phase 4 (24 months): Global city deployment, AI-powered personalized health coaching

REVENUE MODEL:
- Freemium for individuals and community teams
- B2B subscriptions for corporate CSR and employee wellness programs
- Municipal contracts for city data dashboards and public health insights
- Ethical sponsorships from outdoor, fitness, and sustainability brands''')

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
- Expertise in environmental data visualization and health informatics
- Multilingual communicator (English, Swahili, and working knowledge of German)

ACKNOWLEDGMENTS:
- Built with open-source technologies
- Deployed on Streamlit Cloud (free tier)
- Berlin district data from OpenStreetMap
- Outdoor gym locations from real Berlin fitness parks
- Inspired by the Swedish plogging movement (Erik Ahlstrom, 2016)''')

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
pdf.cell(0, 8, 'Source Code: https://github.com/elohimgers-png/plogging-league-sim', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, 'Contact: ephatatalithacumi@gmail.com', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, 'INTI International University & Colleges, Malaysia', align='C')

pdf.output('Samsung_SFT_Plogging_League_Berlin_FINAL.pdf')
print("FINAL Pitch Deck generated: Samsung_SFT_Plogging_League_Berlin_FINAL.pdf")
