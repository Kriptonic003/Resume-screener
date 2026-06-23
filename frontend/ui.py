import gradio as gr
import requests

# Design Palette
COLOR_PURPLE = "#534AB7"
COLOR_TEAL = "#008080"
COLOR_AMBER = "#FFBF00"
COLOR_RED = "#D22B2B"
COLOR_GREEN = "#2E8B57"

css = f"""
.gradio-container {{
    background-color: #FAFAFA !important;
}}
.card {{
    background-color: white;
    border: 0.5px solid #E0E0E0;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    margin-bottom: 15px;
}}
.metric-row {{
    display: flex;
    justify-content: space-between;
    gap: 15px;
}}
.metric-card {{
    flex: 1;
    text-align: center;
    background-color: white;
    border: 0.5px solid #E0E0E0;
    border-radius: 8px;
    padding: 20px;
}}
.metric-value {{
    font-size: 2.5em;
    font-weight: bold;
    margin: 10px 0;
}}
.metric-label {{
    font-size: 0.9em;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
}}

/* Colors */
.color-purple {{ color: {COLOR_PURPLE}; }}
.color-teal {{ color: {COLOR_TEAL}; }}
.color-amber {{ color: {COLOR_AMBER}; }}
.color-red {{ color: {COLOR_RED}; }}

/* Progress bars */
.skill-bar-container {{
    margin-bottom: 15px;
}}
.skill-label-row {{
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
    font-size: 0.9em;
    font-weight: 500;
}}
.progress-bg {{
    background-color: #F0F0F0;
    border-radius: 4px;
    height: 8px;
    overflow: hidden;
}}
.progress-fill {{
    background-color: {COLOR_TEAL};
    height: 100%;
    border-radius: 4px;
}}

/* Pills */
.pill-container {{
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}}
.pill {{
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.85em;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 5px;
    color: white;
}}
.pill.matched {{ background-color: {COLOR_GREEN}; }}
.pill.partial {{ background-color: {COLOR_AMBER}; color: #333; }}
.pill.missing {{ background-color: {COLOR_RED}; }}

/* Recommendation */
.recommendation-card {{
    border-left: 4px solid {COLOR_PURPLE};
    background-color: white;
    border-top: 0.5px solid #E0E0E0;
    border-right: 0.5px solid #E0E0E0;
    border-bottom: 0.5px solid #E0E0E0;
    padding: 20px;
    border-radius: 4px;
    font-size: 1.05em;
    line-height: 1.5;
}}
"""

def scan_resume(file, job_desc):
    if file is None:
        return "<div class='card'>Please upload a resume file.</div>"
    if not job_desc:
        return "<div class='card'>Please enter a job description.</div>"
        
    try:
        # FastAPI server running locally
        url = "http://127.0.0.1:8000/scan"
        
        # Prepare multipart form data
        files = {"resume": (file.name, open(file.name, "rb"))}
        data = {"job_description": job_desc}
        
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        
        result = response.json()
        
        # Build HTML
        html = f"""
        <div class="metric-row">
            <div class="metric-card">
                <div class="metric-label" style="color: {COLOR_PURPLE}">Overall Fit</div>
                <div class="metric-value color-purple">{result.get('overall_fit', 0)}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label" style="color: {COLOR_TEAL}">Skills Match</div>
                <div class="metric-value color-teal">{result.get('skills_match', 0)}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label" style="color: {COLOR_AMBER}">Experience Match</div>
                <div class="metric-value color-amber">{result.get('experience_match', 0)}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label" style="color: {COLOR_RED}">Keywords Score</div>
                <div class="metric-value color-red">{result.get('keyword_score', 0)}%</div>
            </div>
        </div>
        """
        
        # Skill Breakdown
        html += "<div class='card' style='margin-top: 20px;'><h3 style='margin-top: 0;'>Skill Breakdown</h3>"
        for skill in result.get('skill_breakdown', []):
            name = skill.get('skill', '')
            score = skill.get('score', 0)
            html += f"""
            <div class="skill-bar-container">
                <div class="skill-label-row">
                    <span>{name}</span>
                    <span>{score}%</span>
                </div>
                <div class="progress-bg">
                    <div class="progress-fill" style="width: {score}%;"></div>
                </div>
            </div>
            """
        html += "</div>"
        
        # Keywords
        html += "<div class='card'><h3 style='margin-top: 0;'>Keywords</h3><div class='pill-container'>"
        for kw in result.get('keywords', []):
            word = kw.get('word', '')
            status = kw.get('status', '')
            icon = "✓" if status == "matched" else "−" if status == "partial" else "✗"
            html += f"<div class='pill {status}'><span>{icon}</span> {word}</div>"
        html += "</div></div>"
        
        # Recommendation
        html += f"""
        <div class="recommendation-card" style="margin-top: 20px;">
            <h3 style="margin-top: 0; color: {COLOR_PURPLE};">AI Recommendation</h3>
            {result.get('recommendation', '')}
        </div>
        """
        
        return html
        
    except requests.exceptions.RequestException as e:
        return f"<div class='card' style='color: red;'>Error communicating with backend: {str(e)}</div>"
    except Exception as e:
        return f"<div class='card' style='color: red;'>An error occurred: {str(e)}</div>"

def build_ui():
    theme = gr.themes.Base(
        primary_hue="indigo",
        secondary_hue="teal",
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "sans-serif"]
    )
    
    with gr.Blocks(css=css, theme=theme) as app:
        gr.Markdown("# 📄 AI Resume Screener", elem_classes=["card"])
        
        with gr.Row():
            with gr.Column():
                resume_file = gr.File(label="Upload Resume (PDF, DOCX)", file_types=[".pdf", ".docx"], type="filepath")
            with gr.Column():
                job_description = gr.Textbox(label="Paste Job Description", lines=10, placeholder="Enter the job description here...")
                
        scan_button = gr.Button("Scan Resume", variant="primary", elem_id="scan-btn")
        
        # Hack to override primary button color
        app.load(None, None, None, js="""
            function() {
                var btn = document.querySelector('#scan-btn');
                if(btn) {
                    btn.style.backgroundColor = '#534AB7';
                    btn.style.borderColor = '#534AB7';
                    btn.style.color = 'white';
                }
            }
        """)
        
        results_output = gr.HTML()
        
        scan_button.click(
            fn=scan_resume,
            inputs=[resume_file, job_description],
            outputs=[results_output]
        )
        
    return app
