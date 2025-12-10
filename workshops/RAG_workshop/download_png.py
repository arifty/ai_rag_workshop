# Use pillow to draw a PNG manually for a downloadable file
from PIL import Image, ImageDraw, ImageFont

# Define the diagram content
diagram = """
                         ┌─────────────────────────────┐
                         │    End User (Chatbot UI)    │
                         │  or SNowflake Plugin        │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │         AI Chatbot           │
                         │ (OpenAI / Agentic Workflow)  │
                         └──────────────┬───────────────┘
                                        │  Natural Language
                                        │  → SQL reasoning
                                        ▼
                   ┌────────────────────────────────────────┐
                   │        Snowflake MCP Connector         │
                   │ - Secure API access                    │
                   │ - Execute SHOW/SELECT on Query History │
                   └───────────────────┬────────────────────┘
                                       │
                                       ▼
                         ┌──────────────────────────────┐
                         │     Snowflake Data Cloud     │
                         │ - QUERY_HISTORY              │
                         │ - WAREHOUSE_HISTORY          │
                         │ - Execution details          │
                         └──────────────────────────────┘


                         ┌──────────────────────────────┐
                         │   AI Recommender Logic       │
                         │ - Rule-based cost calculation│
                         │ - Runtime estimation         │
                         │ - Upsize/Downsize strategy   │
                         └──────────────────────────────┘
                                        │
                                        ▼
                          ┌────────────────────────────┐
                          │  Recommendation Output     │
                          │ - Suggested warehouse size │
                          │ - Time saved               │
                          │ - Cost saved               │
                          └────────────────────────────┘
"""

# Create blank image (size adjusted for the diagram)
img = Image.new("RGB", (800, 1000), "white")
draw = ImageDraw.Draw(img)

# Use a basic font
try:
    font = ImageFont.truetype("arial.ttf", 18)
except:
    font = ImageFont.load_default()

# Draw text
# Starting coordinates (50, 50) and fill color black, with 10 spacing
draw.multiline_text((50, 50), diagram, fill="black", font=font, spacing=10)

# Save file to a local path
filepath = "Snowflake_Architecture_Diagram.png"
img.save(filepath)

print(f"Diagram saved successfully to: {filepath}")