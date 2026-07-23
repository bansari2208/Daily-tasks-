import base64
from PIL import Image
import io
import re

img_path = r"C:\Users\SVI\.gemini\antigravity\brain\d16a44ed-fb6b-4a14-b3ba-fb32182040ce\cute_3d_robot_career_1779092368944.png"
app_path = r"c:\Users\SVI\Desktop\Ai carrer mentor 2\app.py"

print("Opening image...")
with Image.open(img_path) as img:
    img = img.convert("RGB")
    wpercent = (800 / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((800, hsize), Image.Resampling.LANCZOS)
    
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=70)
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

data_uri = f"data:image/jpeg;base64,{img_str}"

print("Reading app.py...")
with open(app_path, "r", encoding="utf-8") as f:
    content = f.read()

new_content = re.sub(r'<img src="https://images\.unsplash\.com[^"]+" />', f'<img src="{data_uri}" />', content)

print("Writing app.py...")
with open(app_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Updated app.py successfully!")
